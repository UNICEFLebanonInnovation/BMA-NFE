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
    Teacher,
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

TEACHER_DIMENSION_MAP = {
    'sex': 'sex',
    'nationality': 'nationality__name',
    'center': 'center__name',
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

def teacher_analytics_base_queryset(user, params):
    qs = Teacher.objects.all()

    if not (user.is_superuser or user.is_staff):
        if user.center_id:
            qs = qs.filter(center_id=user.center_id)
        elif user.partner_id:
            qs = qs.filter(center__partner_id=user.partner_id)

    date_from = parse_date(params.get('date_from', ''))
    date_to = parse_date(params.get('date_to', ''))
    if date_from:
        from_dt = timezone.make_aware(datetime.combine(date_from, time.min))
        qs = qs.filter(created__gte=from_dt)
    if date_to:
        to_dt = timezone.make_aware(datetime.combine(date_to, time.max))
        qs = qs.filter(created__lte=to_dt)

    if params.get('partner_id'):
        qs = qs.filter(center__partner_id=params['partner_id'])
    if params.get('center_id'):
        qs = qs.filter(center_id=params['center_id'])

    return qs


@login_required
def analytics_summary(request):
    def builder(params):
        qs = analytics_base_queryset(request.user, params)
        teacher_qs = teacher_analytics_base_queryset(request.user, params)
        return {
            'total_registrations': qs.count(),
            'total_teachers': teacher_qs.count(),
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
def analytics_teacher_breakdown(request):
    def builder(params):
        dimension = request.GET.get('dimension', 'sex')
        field = TEACHER_DIMENSION_MAP.get(dimension)
        if not field:
            return {'error': 'Invalid dimension', 'valid_dimensions': sorted(TEACHER_DIMENSION_MAP.keys())}

        qs = teacher_analytics_base_queryset(request.user, params)
        rows = qs.values(field).annotate(count=Count('id')).order_by('-count', field)
        return {
            'dimension': dimension,
            'items': [{'key': row[field] or 'Unknown', 'count': row['count']} for row in rows],
        }

    return _with_cache(f"teacher_breakdown:{request.GET.get('dimension', 'sex')}", request, builder)


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

    centers_list = list(qs)
    center_ids = [c.id for c in centers_list]

    from student_registration.mscc.models import Registration, Teacher
    from django.db.models import Count, Q

    regs_stats = {
        item['center_id']: item for item in Registration.objects.filter(center_id__in=center_ids, deleted=False).values('center_id').annotate(
            total=Count('id'),
            total_male=Count('id', filter=Q(child__gender='Male')),
            total_female=Count('id', filter=Q(child__gender='Female')),
        )
    }

    teachers_stats = {
        item['center_id']: item for item in Teacher.objects.filter(center_id__in=center_ids).values('center_id').annotate(
            total=Count('id'),
            total_male=Count('id', filter=Q(sex='Male')),
            total_female=Count('id', filter=Q(sex='Female')),
        )
    }

    data = []
    for center in centers_list:
        reg_stat = regs_stats.get(center.id, {'total': 0, 'total_male': 0, 'total_female': 0})
        teach_stat = teachers_stats.get(center.id, {'total': 0, 'total_male': 0, 'total_female': 0})

        # Calculate a simple vulnerability score based on registered children in the center
        # For this demonstration, we use a proxy if total_children exists.
        # In a real scenario, this might query PSSServices or child_vulnerability fields.
        vulnerability_score = 0
        if reg_stat['total'] > 0:
            vulnerability_score = min(10, max(1, int(reg_stat['total'] / 50)))

        data.append({
            'id': center.id,
            'name': center.name,
            'partner': center.partner.name if center.partner else 'N/A',
            'governorate': center.governorate.name if center.governorate else 'N/A',
            'caza': center.caza.name if center.caza else 'N/A',
            'cadaster': center.cadaster.name if center.cadaster else 'N/A',
            'latitude': float(center.latitude) if center.latitude is not None else None,
            'longitude': float(center.longitude) if center.longitude is not None else None,
            'total_children': reg_stat['total'],
            'total_male': reg_stat['total_male'],
            'total_female': reg_stat['total_female'],
            'total_teachers': teach_stat['total'],
            'total_teachers_male': teach_stat['total_male'],
            'total_teachers_female': teach_stat['total_female'],
            'type': center.get_type_display() if center.type else 'N/A',
            'p_code': center.p_code or 'N/A',
            'profile_url': reverse('locations:center_profile', kwargs={'pk': center.id}),
            'vulnerability_score': vulnerability_score,
            'provided_packages': list(center.provided_packages) if center.provided_packages else [],
            'programs': list(center.programs) if center.programs else [],
            'is_active': center.is_active,
            'offer_digital_learning': center.get_offer_digital_learning_display() if hasattr(center, 'get_offer_digital_learning_display') and center.offer_digital_learning else center.offer_digital_learning,
            'have_digital_hub': center.get_have_digital_hub_display() if hasattr(center, 'get_have_digital_hub_display') and center.have_digital_hub else center.have_digital_hub,
            'admin_staff_number': center.admin_staff_number,
            'cwd_accessible': center.get_cwd_accessible_display() if hasattr(center, 'get_cwd_accessible_display') and center.cwd_accessible else center.cwd_accessible,
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


WIKI_HTML_PAGES = [
    ('index', 'Home', None),
    ('end_user', 'End User Manual', None),
    ('admin', 'Administration Guide', 'Additional'),
    ('developer', 'Developer Guide', 'Additional'),
    ('system_details', 'System Overview', 'Additional'),
    ('01_project_overview', '1. Project Overview', 'Developer'),
    ('02_setup', '2. Setup & Installation', 'Developer'),
    ('03_architecture', '3. Architecture & Tech Stack', 'Developer'),
    ('04_database_schema', '4. Database Schema & Models', 'Developer'),
    ('05_django_apps', '5. Django Apps Reference', 'Developer'),
    ('06_api_urls', '6. API & URL Reference', 'Developer'),
    ('07_auth_permissions', '7. Authentication & Permissions', 'Developer'),
    ('08_admin_portal', '8. Admin Portal Guide', 'Developer'),
    ('09_celery_tasks', '9. Background Tasks (Celery)', 'Developer'),
    ('10_frontend', '10. Frontend Guide', 'Developer'),
    ('11_environment_variables', '11. Environment Variables', 'Developer'),
    ('12_deployment', '12. Deployment Guide', 'Developer'),
    ('13_testing', '13. Testing Guide', 'Developer'),
]


def _extract_wiki_content(html_text):
    """Extract inner HTML of <div id="content"> from a wiki HTML file."""
    start_tag = '<div id="content">'
    start = html_text.find(start_tag)
    if start == -1:
        return ''
    content_start = start + len(start_tag)
    depth = 1
    i = content_start
    while depth > 0 and i < len(html_text):
        next_open = html_text.find('<div', i)
        next_close = html_text.find('</div>', i)
        if next_close == -1:
            break
        if next_open != -1 and next_open < next_close:
            depth += 1
            i = next_open + 4
        else:
            depth -= 1
            if depth == 0:
                return html_text[content_start:next_close].strip()
            i = next_close + 6
    return ''


def _rewrite_wiki_links(content):
    """Rewrite bare .html hrefs in wiki content to Django guide URLs."""
    import re
    def replace_link(m):
        page = m.group(1).replace('.html', '')
        return f'href="/dashboard/guide/{page}/"'
    return re.sub(r'href="([\w\-]+\.html)"', replace_link, content)


class WikiGuidePageView(LoginRequiredMixin, TemplateView):
    template_name = 'wiki/html_page.html'

    VALID_PAGES = {p[0]: p[1] for p in WIKI_HTML_PAGES}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page_name = self.kwargs.get('page_name', 'index')

        if page_name not in self.VALID_PAGES:
            raise Http404('Guide page not found')

        file_path = os.path.join(
            str(settings.ROOT_DIR.path('docs').path('wiki_html')), f'{page_name}.html'
        )
        if not os.path.exists(file_path):
            raise Http404('Guide page not found')

        with open(file_path, 'r', encoding='utf-8') as f:
            html_text = f.read()

        raw_content = _extract_wiki_content(html_text)
        rewritten = _rewrite_wiki_links(raw_content)

        allowed_tags = [
            'a', 'abbr', 'b', 'blockquote', 'br', 'caption', 'code', 'col', 'colgroup',
            'dd', 'del', 'details', 'div', 'dl', 'dt', 'em', 'h1', 'h2', 'h3',
            'h4', 'h5', 'h6', 'hr', 'i', 'img', 'li', 'ol', 'p', 'pre',
            's', 'span', 'strong', 'sub', 'summary', 'sup', 'table', 'tbody', 'td',
            'tfoot', 'th', 'thead', 'tr', 'u', 'ul',
        ]
        allowed_attrs = {
            '*': ['class', 'id', 'title', 'style'],
            'a': ['href', 'title', 'target'],
            'img': ['src', 'alt', 'title', 'width', 'height'],
            'td': ['colspan', 'rowspan'],
            'th': ['colspan', 'rowspan', 'scope'],
            'col': ['span'],
            'colgroup': ['span'],
        }
        clean = bleach.clean(rewritten, tags=allowed_tags, attributes=allowed_attrs, strip=True)

        context['wiki_content'] = mark_safe(clean)
        context['page_name'] = page_name
        context['page_title'] = self.VALID_PAGES.get(page_name, 'Documentation')
        context['wiki_pages'] = WIKI_HTML_PAGES
        return context


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
