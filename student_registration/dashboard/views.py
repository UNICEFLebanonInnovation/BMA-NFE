# from django.http import HttpResponse
# from django.template import loader
# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

import csv
import hashlib
import json
import logging
from datetime import date, datetime, time, timedelta

from django.core.cache import cache
from django.db.models import Case, Count, F, IntegerField, OuterRef, Q, Subquery, Value, When
from django.db.models.functions import Cast, Coalesce, ExtractYear, Now, TruncDate
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from django.utils.dateparse import parse_date
from django.utils import timezone
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
import os
import markdown
import bleach
from django.conf import settings
from django.http import Http404
from django.utils.safestring import mark_safe

logger = logging.getLogger(__name__)

from student_registration.mscc.models import (
    Round,
    EducationService,
    Registration,
    EducationProgrammeAssessment,
)
from student_registration.schools.models import PartnerOrganization
from student_registration.locations.models import Center, Location


def _today():
    return timezone.now().date()


class ChartBuilderView(LoginRequiredMixin, TemplateView):
    """Interactive page for end users to create D3 charts."""

    template_name = 'dashboard/chart_builder.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        partners = PartnerOrganization.objects.all()
        centers = Center.objects.all()

        if not (user.is_superuser or user.is_staff):
            if user.partner_id:
                partners = partners.filter(id=user.partner_id)
                centers = centers.filter(partner_id=user.partner_id)
            if user.center_id:
                centers = centers.filter(id=user.center_id)

        context.update(
            {
                "partners": partners,
                "rounds": Round.objects.all(),
                "centers": centers,
                "governorates": Location.objects.filter(type_id=1),
                "cazas": Location.objects.filter(type_id=2),
                "cadasters": Location.objects.filter(type_id=3),
                "programme_types": EducationService.EDUCATION_PROGRAM,
            }
        )
        return context


class PivotDashboardView(LoginRequiredMixin, TemplateView):
    """Display a PivotTable.js dashboard for MSCC registrations."""

    template_name = 'dashboard/pivot_dashboard.html'


def pivot_data(request):
    """Return minimal MSCC registration data for the pivot table."""
    if not request.user.is_authenticated:
        return HttpResponseForbidden()

    latest_prog_type = (
        EducationProgrammeAssessment.objects.filter(
            registration=OuterRef("pk")
        )
        .order_by("-id")
        .values_list("programme_type", flat=True)[:1]
    )

    user = request.user
    qs = Registration.objects.filter(deleted=False)

    if not (user.is_superuser or user.is_staff):
        if user.partner_id:
            qs = qs.filter(partner_id=user.partner_id)
        if user.center_id:
            qs = qs.filter(center_id=user.center_id)

    qs = (
        qs.annotate(
            programme_type=Subquery(latest_prog_type),
            center_name=F("center__name"),
            partner_name=F("center__partner__name"),
            round_name=F("round__name"),
            round_year=F("round__year"),
            governorate=F("center__governorate__name"),
            caza=F("center__caza__name"),
            district=F("center__cadaster__name"),
            gender=F("child__gender"),
            nationality=F("child__nationality__name"),
        )
    )

    data = [
        {
            "center": getattr(row, "center_name", "") or "",
            "partner": getattr(row, "partner_name", "") or "",
            "governorate": getattr(row, "governorate", "") or "",
            "caza": getattr(row, "caza", "") or "",
            "district": getattr(row, "district", "") or "",
            "gender": getattr(row, "gender", "") or "",
            "nationality": getattr(row, "nationality", "") or "",
            "round": getattr(row, "round_name", "") or "",
            "round_year": getattr(row, "round_year", "") or "",
            "programme_type": getattr(row, "programme_type", "") or "",
        }
        for row in qs
    ]

    return JsonResponse(data, safe=False)


class AdvancedAnalyticsDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/advanced_analytics.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        partners = PartnerOrganization.objects.all()
        centers = Center.objects.select_related('partner').all()

        if not (user.is_superuser or user.is_staff):
            if user.partner_id:
                partners = partners.filter(id=user.partner_id)
                centers = centers.filter(partner_id=user.partner_id)
            if user.center_id:
                centers = centers.filter(id=user.center_id)

        context.update(
            {
                'partners': partners,
                'centers': centers,
                'programmes': list(EducationService.EDUCATION_PROGRAM),
                'default_partner_id': user.partner_id,
                'default_center_id': user.center_id,
            }
        )
        return context


DIMENSION_MAP = {
    'gender': 'child__gender',
    'nationality': 'child__nationality__name',
    'partner': 'partner__name',
    'center': 'center__name',
    'programme': 'programme',
    'age_group': 'age_group',
    'age': 'age_group',
}


def _cache_key(namespace, params, user):
    payload = {
        'namespace': namespace,
        'params': sorted(params.items()),
        'user_id': user.id,
        'partner_scope': user.partner_id,
        'center_scope': user.center_id,
        'is_superuser': user.is_superuser,
    }
    digest = hashlib.sha256(json.dumps(payload, sort_keys=True).encode('utf-8')).hexdigest()
    return f'analytics:{namespace}:{digest}'


def _with_cache(namespace, request, builder, ttl=300):
    params = request.GET.dict()
    key = _cache_key(namespace, params, request.user)
    payload = cache.get(key)
    if payload is None:
        payload = builder(params)
        cache.set(key, payload, ttl)
    return JsonResponse(payload)


def _latest_programme_subquery():
    return (
        EducationService.objects.filter(registration=OuterRef('pk'))
        .order_by('-id')
        .values_list('education_program', flat=True)[:1]
    )


def _annotate_age(queryset):
    birth_year = Case(
        When(child__birthday_year__regex=r'^\d{4}$', then=Cast('child__birthday_year', IntegerField())),
        default=Value(None),
        output_field=IntegerField(),
    )
    age_years = Case(
        When(birth_year__isnull=True, then=Value(None)),
        default=ExtractYear(Now()) - F('birth_year'),
        output_field=IntegerField(),
    )
    age_group = Case(
        When(age_years__isnull=True, then=Value('Unknown')),
        When(age_years__lte=4, then=Value('0-4')),
        When(age_years__lte=11, then=Value('5-11')),
        When(age_years__lte=14, then=Value('12-14')),
        When(age_years__lte=17, then=Value('15-17')),
        default=Value('18+'),
    )
    return queryset.annotate(birth_year=birth_year).annotate(age_years=age_years, age_group=age_group)


def analytics_base_queryset(user, params):
    qs = Registration.objects.filter(deleted=False).annotate(
        programme=Coalesce(Subquery(_latest_programme_subquery()), Value('Unknown')),
    )
    qs = _annotate_age(qs)

    if not (user.is_superuser or user.is_staff):
        if user.partner_id:
            qs = qs.filter(partner_id=user.partner_id)
        if user.center_id:
            qs = qs.filter(center_id=user.center_id)

    date_from = parse_date(params.get('date_from', ''))
    date_to = parse_date(params.get('date_to', ''))
    if date_from:
        from_dt = timezone.make_aware(datetime.combine(date_from, time.min))
        qs = qs.filter(created__gte=from_dt)
    if date_to:
        to_dt = timezone.make_aware(datetime.combine(date_to, time.max))
        qs = qs.filter(created__lte=to_dt)

    if params.get('partner_id'):
        qs = qs.filter(partner_id=params['partner_id'])
    if params.get('center_id'):
        qs = qs.filter(center_id=params['center_id'])
    if params.get('programme_id'):
        qs = qs.filter(programme=params['programme_id'])
    if params.get('nationality'):
        qs = qs.filter(child__nationality__name=params['nationality'])
    if params.get('gender'):
        qs = qs.filter(child__gender=params['gender'])
    if params.get('age_min'):
        qs = qs.filter(age_years__gte=int(params['age_min']))
    if params.get('age_max'):
        qs = qs.filter(age_years__lte=int(params['age_max']))
    return qs


@login_required
def analytics_summary(request):
    def builder(params):
        qs = analytics_base_queryset(request.user, params)
        return {
            'total_registrations': qs.count(),
            'partners': qs.values('partner_id').distinct().count(),
            'centers': qs.values('center_id').distinct().count(),
            'programmes': qs.values('programme').distinct().count(),
        }

    return _with_cache('summary', request, builder)


@login_required
def analytics_trend(request):
    def builder(params):
        qs = analytics_base_queryset(request.user, params)
        days = int(params.get('days', 30))
        if not params.get('date_from') and not params.get('date_to'):
            start = _today() - timedelta(days=max(days - 1, 0))
            start_dt = timezone.make_aware(datetime.combine(start, time.min))
            qs = qs.filter(created__gte=start_dt)

        rows = (
            qs.annotate(day=TruncDate('created'))
            .values('day')
            .annotate(count=Count('id'))
            .order_by('day')
        )
        values = {item['day']: item['count'] for item in rows}
        if values:
            start_day = min(values)
            end_day = max(values)
        else:
            end_day = _today()
            start_day = end_day - timedelta(days=max(days - 1, 0))

        series = []
        cursor = start_day
        while cursor <= end_day:
            series.append({'date': cursor.isoformat(), 'count': values.get(cursor, 0)})
            cursor += timedelta(days=1)

        return {'granularity': 'day', 'series': series}

    return _with_cache('trend', request, builder)


@login_required
def analytics_breakdown(request):
    def builder(params):
        dimension = request.GET.get('dimension', 'gender')
        field = DIMENSION_MAP.get(dimension)
        if not field:
            return {'error': 'Invalid dimension', 'valid_dimensions': sorted(DIMENSION_MAP.keys())}

        qs = analytics_base_queryset(request.user, params)
        rows = qs.values(field).annotate(count=Count('id')).order_by('-count', field)
        return {
            'dimension': dimension,
            'items': [{'key': row[field] or 'Unknown', 'count': row['count']} for row in rows],
        }

    return _with_cache(f"breakdown:{request.GET.get('dimension', 'gender')}", request, builder)


@login_required
def analytics_crosstab(request):
    def builder(params):
        x = request.GET.get('x', 'partner')
        y = request.GET.get('y', 'gender')
        x_field = DIMENSION_MAP.get(x)
        y_field = DIMENSION_MAP.get(y)
        if not x_field or not y_field:
            return {'error': 'Invalid x or y dimension', 'valid_dimensions': sorted(DIMENSION_MAP.keys())}

        qs = analytics_base_queryset(request.user, params)
        rows = qs.values(x_field, y_field).annotate(count=Count('id')).order_by(x_field, y_field)
        matrix = [
            {'x': row[x_field] or 'Unknown', 'y': row[y_field] or 'Unknown', 'count': row['count']}
            for row in rows
        ]
        return {'x': x, 'y': y, 'matrix': matrix}

    namespace = f"crosstab:{request.GET.get('x', 'partner')}:{request.GET.get('y', 'gender')}"
    return _with_cache(namespace, request, builder)


@login_required
def analytics_export_csv(request):
    qs = analytics_base_queryset(request.user, request.GET.dict())
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="analytics_export.csv"'
    writer = csv.writer(response)
    writer.writerow(['registration_id', 'created_at', 'partner', 'center', 'programme', 'gender', 'nationality', 'age_group'])
    rows = qs.values_list(
        'id', 'created', 'partner__name', 'center__name', 'programme', 'child__gender', 'child__nationality__name', 'age_group'
    )[:50000]
    for row in rows.iterator(chunk_size=2000):
        writer.writerow(row)
    return response


class CentersMapView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/centers_map.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        partners = PartnerOrganization.objects.all()
        centers = Center.objects.all()

        if not (user.is_superuser or user.is_staff):
            if user.partner_id:
                partners = partners.filter(id=user.partner_id)
                centers = centers.filter(partner_id=user.partner_id)
            if user.center_id:
                centers = centers.filter(id=user.center_id)

        context.update({
            'partners': partners,
            'centers': centers,
            'default_partner_id': user.partner_id,
            'default_center_id': user.center_id,
        })
        return context


from django.urls import reverse

@login_required
def centers_geo_data(request):
    """Return geographic data for all centers for mapping."""
    user = request.user
    qs = Center.objects.select_related('partner', 'governorate', 'caza', 'cadaster').filter(
        latitude__isnull=False,
        longitude__isnull=False
    )

    if not (user.is_superuser or user.is_staff):
        if user.partner_id:
            qs = qs.filter(partner_id=user.partner_id)
        elif user.center_id:
            qs = qs.filter(id=user.center_id)
        else:
            return JsonResponse([], safe=False)

    # Simple filtering
    partner_id = request.GET.get('partner_id')
    if partner_id:
        qs = qs.filter(partner_id=partner_id)

    center_id = request.GET.get('center_id')
    if center_id:
        qs = qs.filter(id=center_id)

    data = []
    for center in qs:
        # Calculate a simple vulnerability score based on registered children in the center
        # For this demonstration, we use a proxy if total_children exists.
        # In a real scenario, this might query PSSServices or child_vulnerability fields.
        vulnerability_score = 0
        if center.total_children > 0:
            vulnerability_score = min(10, max(1, int(center.total_children / 50)))

        data.append({
            'id': center.id,
            'name': center.name,
            'partner': center.partner.name if center.partner else 'N/A',
            'governorate': center.governorate.name if center.governorate else 'N/A',
            'caza': center.caza.name if center.caza else 'N/A',
            'cadaster': center.cadaster.name if center.cadaster else 'N/A',
            'latitude': float(center.latitude) if center.latitude is not None else None,
            'longitude': float(center.longitude) if center.longitude is not None else None,
            'total_children': center.total_children,
            'total_male': center.total_male,
            'total_female': center.total_female,
            'total_teachers': center.total_teachers,
            'total_teachers_male': center.total_teachers_male,
            'total_teachers_female': center.total_teachers_female,
            'type': center.get_type_display() if center.type else 'N/A',
            'p_code': center.p_code or 'N/A',
            'profile_url': reverse('locations:center_profile', kwargs={'pk': center.id}),
            'vulnerability_score': vulnerability_score,
        })

    return JsonResponse(data, safe=False)


from django.core.paginator import Paginator

@login_required
def centers_children_data(request):
    """Return list of children for the selected partner and/or center."""
    user = request.user

    qs = Registration.objects.select_related('child', 'center', 'partner').filter(deleted=False).order_by('-id')

    if not (user.is_superuser or user.is_staff):
        if user.partner_id:
            qs = qs.filter(partner_id=user.partner_id)
        if user.center_id:
            qs = qs.filter(center_id=user.center_id)

    partner_id = request.GET.get('partner_id')
    if partner_id:
        qs = qs.filter(partner_id=partner_id)

    center_id = request.GET.get('center_id')
    if center_id:
        qs = qs.filter(center_id=center_id)

    paginator = Paginator(qs, 20)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    data = []
    for reg in page_obj:
        child = reg.child
        if child:
            try:
                age = child.calculate_age
                if age and isinstance(age, tuple):
                    age = age[0]
                elif not age:
                    age = 'N/A'
            except Exception:
                age = 'N/A'

            data.append({
                'unicef_id': child.unicef_id or 'N/A',
                'name': f"{child.first_name or ''} {child.last_name or ''}".strip(),
                'gender': child.get_gender_display() if child.gender else 'N/A',
                'age': age,
                'partner': reg.partner.name if reg.partner else 'N/A',
                'center': reg.center.name if reg.center else 'N/A',
                'program': reg.programme_type if hasattr(reg, 'programme_type') else 'N/A',
            })

    return JsonResponse({
        'data': data,
        'pagination': {
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
            'current_page': page_obj.number,
            'total_pages': paginator.num_pages,
            'total_items': paginator.count
        }
    })


class WikiPageView(LoginRequiredMixin, TemplateView):
    template_name = 'wiki/page.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page_name = self.kwargs.get('page_name', 'index')

        # Ensure only allowed characters in page name to prevent path traversal
        if not page_name.replace('_', '').replace('-', '').isalnum():
            raise Http404('Invalid page name')

        file_path = os.path.join(str(settings.ROOT_DIR.path('docs').path('wiki')), f'{page_name}.md')

        if not os.path.exists(file_path):
            raise Http404('Wiki page not found')

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Convert markdown to HTML
        html_content = markdown.markdown(
            content,
            extensions=['extra', 'toc']
        )

        # Sanitize HTML to prevent XSS
        allowed_tags = [
            'a', 'abbr', 'acronym', 'b', 'blockquote', 'br', 'code',
            'dd', 'del', 'div', 'dl', 'dt', 'em', 'h1', 'h2', 'h3',
            'h4', 'h5', 'h6', 'hr', 'i', 'img', 'li', 'ol', 'p', 'pre',
            's', 'span', 'strong', 'sub', 'sup', 'table', 'tbody', 'td',
            'tfoot', 'th', 'thead', 'tr', 'tt', 'u', 'ul'
        ]
        allowed_attributes = {
            '*': ['class', 'id', 'title'],
            'a': ['href', 'title', 'target'],
            'img': ['src', 'alt', 'title', 'width', 'height'],
        }

        clean_html = bleach.clean(
            html_content,
            tags=allowed_tags,
            attributes=allowed_attributes,
            strip=True
        )

        context['wiki_content'] = mark_safe(clean_html)
        context['page_name'] = page_name
        return context
