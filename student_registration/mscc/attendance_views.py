# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import calendar
import json
from collections import OrderedDict
from django.views.generic import ListView, TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from student_registration.users.mixins import GroupRequiredMixin, group_required
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.db.models import Count, Q
from django.utils import timezone
from django.utils.encoding import force_str
from rest_framework import viewsets, mixins, permissions
from rest_framework.decorators import api_view, action

from student_registration.attendances.models import MSCCAttendance, MSCCAttendanceChild
from student_registration.attendances.serializers import MSCCAttendanceChildSerializer
from student_registration.mscc.models import EducationService, Packages, Round
from student_registration.locations.models import Center
from student_registration.schools.models import PartnerOrganization

from .utils import load_child_attendance, create_attendance
from student_registration.users.templatetags.custom_tags import has_group


def _get_service_program_mapping():
    package_rows = (
        Packages.objects
        .filter(category='Education')
        .exclude(type__isnull=True)
        .exclude(type='')
        .exclude(name__isnull=True)
        .exclude(name='')
        .values_list('type', 'name')
        .distinct()
    )

    grouped = OrderedDict()
    for package_type, package_name in sorted(package_rows, key=lambda row: (row[0], row[1])):
        grouped.setdefault(package_type, [])
        grouped[package_type].append(package_name)

    return list(grouped.items())


def _get_programme_lookups():
    service_program_mapping = _get_service_program_mapping()
    programme_category_lookup = {
        programme: category
        for category, programmes in service_program_mapping
        for programme in programmes
    }
    category_order_lookup = {
        category: index for index, (category, _programmes) in enumerate(service_program_mapping)
    }
    return programme_category_lookup, category_order_lookup


def _get_education_program_dict():
    education_packages = (
        Packages.objects
        .filter(category='Education')
        .exclude(name__isnull=True)
        .exclude(name='')
        .values_list('name', flat=True)
        .distinct()
    )
    sorted_packages = sorted(set(education_packages))

    if sorted_packages:
        return OrderedDict((name, name) for name in sorted_packages)

    return OrderedDict()


def _aggregate_attendance(queryset, *group_fields):
    """Aggregate attendance counts for the provided ``group_fields``.

    Args:
        queryset (QuerySet): Base attendance queryset to aggregate.
        *group_fields (str): Fields to group by when annotating counts.

    Returns:
        QuerySet: Aggregated queryset with ``total`` and ``absent`` counts for
        each grouping.

    This mirrors the logic used by the heatmap view to ensure the API is
    using the exact same calculations as the user-facing dashboard.
    """

    return (
        queryset
        .values(*group_fields)
        .annotate(
            total=Count('id'),
            absent=Count('id', filter=Q(attended='No'))
        )
        .order_by(*group_fields)
    )


def _parse_attendance_date(value):
    """Parse an ISO or US-style attendance date, or return None."""
    if not value:
        return None
    from datetime import datetime as _dt
    for fmt in ('%Y-%m-%d', '%m/%d/%Y'):
        try:
            return _dt.strptime(value, fmt).date()
        except (TypeError, ValueError):
            continue
    return None


def _normalise_day_off(value):
    """Return 'Yes'/'No' whatever casing the row was stored with."""
    return 'Yes' if (value or '').strip().lower() == 'yes' else 'No'


def _day_off_status(center_id, day):
    """Whether a centre was closed on ``day``, and why.

    A centre stores one attendance row per programme and section, so picking
    .last() returned whichever row happened to sort last and the closure could
    show or not show depending on the ordering. A centre is closed if any of the
    day's rows says so.
    """
    rows = MSCCAttendance.objects.filter(center_id=center_id, attendance_date=day)
    closed = rows.filter(day_off__iexact='yes').first()
    if closed:
        return 'Yes', (closed.close_reason or ''), True
    return 'No', '', rows.exists()


@login_required
def attendance_day_status(request):
    """Day-off state for a centre on one date, for the date picker to read.

    Without this the page could only ever show today's day-off flag, because it
    is rendered server-side and nothing refreshed it when the date changed.
    """
    center_id = request.GET.get('center_id') or request.user.center_id
    day = _parse_attendance_date(request.GET.get('attendance_date'))
    if not center_id or not day:
        return HttpResponseBadRequest('center_id and attendance_date are required')

    day_off, close_reason, recorded = _day_off_status(center_id, day)
    return JsonResponse({
        'day_off': day_off,
        'close_reason': close_reason,
        'recorded': recorded,
    })


class AttendanceView(LoginRequiredMixin,
                     GroupRequiredMixin,
                     TemplateView):

    group_required = [u"MSCC",u"MSCC_UNICEF", u"MSCC_CENTER", "MSCC_PARTNER"]
    template_name = 'mscc/attendance.html'

    def get_context_data(self, **kwargs):
        """Prepare attendance context for the current center and date.

        Args:
            **kwargs: Additional keyword arguments forwarded by
                :class:`TemplateView`.

        Returns:
            dict: Context containing attendance metadata, available programs and
            sections, and any existing attendance record for today.
        """
        from datetime import datetime
        from collections import OrderedDict

        center_id = self.request.user.center_id
        # Honour ?attendance_date=: the page lets the user pick a date, but this
        # was pinned to today, so opening a past day showed today's day-off state
        # and saving would have overwritten the stored one.
        selected = _parse_attendance_date(self.request.GET.get('attendance_date'))
        now = selected or datetime.now().date()
        attendance_date = now.strftime('%m/%d/%Y')
        attendance_date_iso = now.strftime('%Y-%m-%d')
        day_off = 'No'
        close_reason = ''
        round = Round.objects.filter(current_year=True)

        education_program_dict = _get_education_program_dict()

        class_sections = EducationService.CLASS_SECTION
        sorted_class_sections = sorted(class_sections, key=lambda x: x[1])
        class_section_dict = OrderedDict(sorted_class_sections)

        instance = None

        if center_id:
            instance = MSCCAttendance.objects.filter(center_id=center_id,
                                                 attendance_date=now).last()
            # The field's choices are 'yes'/'no' but the template compares
            # against 'Yes'/'No', so a stored day off never came back checked.
            day_off, close_reason, _recorded = _day_off_status(center_id, now)

        return {
            'instance': instance,
            'attendance_date': attendance_date,
            'attendance_date_iso': attendance_date_iso,
            'day_off': day_off,
            'close_reason': close_reason,
            'education_program': education_program_dict,
            'class_section': class_section_dict,
            'round': round
        }


@require_POST
@group_required("MSCC", "MSCC_UNICEF", "MSCC_CENTER", "MSCC_PARTNER")
def save_attendance_children(request):
    """Persist attendance for MSCC children.

    Args:
        request (HttpRequest): Request carrying JSON-encoded attendance data
            and an optional ``center_id`` query string parameter.

    Returns:
        JsonResponse | HttpResponseBadRequest: Success response containing the
        creation result or a 400 response when validation fails.

    Similar to the CLM view, this now validates the request body and ensures an
    ``HttpResponse`` is always returned even when errors occur.
    """

    body_unicode = request.body.decode("utf-8")

    if not body_unicode.strip():
        return HttpResponseBadRequest("Empty request body")

    try:
        data = json.loads(body_unicode)
    except ValueError:
        return HttpResponseBadRequest("Invalid JSON payload")

    try:
        result = create_attendance(data, request.GET.get("center_id"))
    except Exception:  # pragma: no cover - safety net
        return HttpResponseBadRequest("Failed to save attendance")

    return JsonResponse({"result": result})


class LoadAttendanceChildren(LoginRequiredMixin,
                             TemplateView):

    template_name = 'mscc/attendance_children.html'

    def get_context_data(self, **kwargs):
        from datetime import datetime

        current_date = datetime.today().date()
        attendance_date_str = self.request.GET.get("attendance_date")
        center_id = self.request.GET.get("center_id")
        education_program = self.request.GET.get("education_program")
        class_section = self.request.GET.get("class_section")
        round_id = self.request.GET.get("round_id")

        if attendance_date_str is None:
            return {'instances': [], 'new_instances': []}

        try:
            # Parse the attendance_date_str into a datetime object
            # Support both MM/DD/YYYY and YYYY-MM-DD
            if '-' in attendance_date_str:
                attendance_date = datetime.strptime(attendance_date_str, '%Y-%m-%d').date()
                # Convert back to expected format for load_child_attendance if needed
                # Actually let's just use the string we have
            else:
                attendance_date = datetime.strptime(attendance_date_str, '%m/%d/%Y').date()

            if attendance_date <= current_date and center_id:
                data = load_child_attendance(
                    center_id,
                    round_id,
                    attendance_date_str,
                    education_program,
                    class_section,
                )
            else:
                data = {'instances': [], 'new_instances': []}
        except ValueError:
            data = {'instances': [], 'new_instances': []}

        return data


class LoadAttendanceChild(LoginRequiredMixin,
                          TemplateView):

    template_name = 'mscc/child_attendance_month.html'

    def get_context_data(self, **kwargs):
        from datetime import date
        from django.utils.dates import MONTHS

        child_id = kwargs["child"]
        today = date.today()

        # Both parameters are optional: fall back to the current month/year
        # instead of raising when a caller omits them.
        def _int_param(name, default):
            try:
                return int(self.request.GET.get(name))
            except (TypeError, ValueError):
                return default

        month = _int_param("month", today.month)
        year = _int_param("year", today.year)
        if not 1 <= month <= 12:
            month = today.month

        # Filter on year as well, otherwise the same month from every year of
        # the child's history is merged into one list.
        instances = MSCCAttendanceChild.objects.filter(
            child_id=child_id,
            attendance_day__attendance_date__month=month,
            attendance_day__attendance_date__year=year,
        ).order_by('attendance_day__attendance_date')

        return {
            'instances': instances,
            'nbr_attended': instances.filter(attended='Yes').count(),
            'nbr_absent': instances.filter(attended='No').count(),
            'attendance_month': MONTHS[month],
            'attendance_year': year,
        }


class AttendanceReport(LoginRequiredMixin, TemplateView):
    template_name = 'mscc/attendance_report.html'

    def get_context_data(self, **kwargs):
        from collections import OrderedDict

        context = super(AttendanceReport, self).get_context_data(**kwargs)

        context['rounds'] = Round.objects.filter(current_year=True).all()

        context['education_program'] = _get_education_program_dict()

        class_sections = EducationService.CLASS_SECTION
        sorted_class_sections = sorted(class_sections, key=lambda x: x[1])
        class_section_dict = OrderedDict(sorted_class_sections)
        context['class_section'] = class_section_dict

        user = self.request.user
        is_unicef_or_staff = user.is_staff or has_group(user, 'MSCC_UNICEF')
        is_partner_user = has_group(user, 'MSCC_PARTNER') and user.partner_id
        is_center_user = has_group(user, 'MSCC_CENTER') and user.center_id

        context['center'] = []
        context['partner'] = []

        context['show_partner_filter'] = False
        context['show_center_filter'] = False
        context['selected_partner_id'] = user.partner_id or ''
        context['selected_center_id'] = user.center_id or ''

        if is_unicef_or_staff:
            context['center'] = Center.objects.all().order_by('name')
            context['partner'] = PartnerOrganization.objects.all().order_by('name')
            context['show_partner_filter'] = True
            context['show_center_filter'] = True
            context['selected_partner_id'] = ''
            context['selected_center_id'] = ''
        elif is_center_user:
            center = Center.objects.filter(id=user.center_id).last()
            if center:
                context['selected_center_id'] = center.id
                context['selected_partner_id'] = center.partner_id or user.partner_id or ''
        elif is_partner_user:
            context['center'] = Center.objects.filter(partner_id=user.partner_id).order_by('name')
            context['show_center_filter'] = True

        return context


class AttendanceHeatmap(LoginRequiredMixin, TemplateView):
    template_name = 'mscc/attendance_heatmap.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        year = int(self.request.GET.get('year', timezone.now().year))

        base_qs = MSCCAttendanceChild.objects.filter(
            attendance_day__attendance_date__year=year
        )

        queryset = _aggregate_attendance(
            base_qs,
            'attendance_day__attendance_date',
        )

        programme_qs = _aggregate_attendance(
            base_qs,
            'attendance_day__attendance_date',
            'registration__education_service__education_program',
        )

        programme_category_lookup, category_order_lookup = _get_programme_lookups()
        programme_choices = _get_education_program_dict()
        programme_totals = {}

        for row in programme_qs:
            programme = row['registration__education_service__education_program'] or 'Unknown'
            label = programme_choices.get(programme, programme)
            category = programme_category_lookup.get(programme)

            if category is None:
                category = force_str(label) if label else 'Unknown'

            key = (category, row['attendance_day__attendance_date'])
            totals = programme_totals.setdefault(key, {'total': 0, 'absent': 0})
            totals['total'] += row['total'] or 0
            totals['absent'] += row['absent'] or 0

        programme_data = OrderedDict()

        def _programme_sort_key(item):
            (category, attendance_date), _data = item
            return (
                category_order_lookup.get(category, len(category_order_lookup)),
                attendance_date,
            )

        for (category, attendance_date), data in sorted(programme_totals.items(), key=_programme_sort_key):
            if category not in programme_data:
                programme_data[category] = []

            programme_data[category].append({
                'attendance_day__attendance_date': attendance_date,
                'total': data['total'],
                'absent': data['absent'],
            })

        years = MSCCAttendanceChild.objects.dates(
            'attendance_day__attendance_date', 'year'
        )

        context['attendance_json'] = json.dumps(list(queryset), default=str)
        context['program_attendance_json'] = json.dumps(programme_data, default=str)
        context['year'] = year
        context['years'] = [d.year for d in years]
        return context


class AttendanceHeatmapViewSet(mixins.ListModelMixin,
                               viewsets.GenericViewSet):

    model = MSCCAttendanceChild
    queryset = MSCCAttendanceChild.objects.all()
    serializer_class = MSCCAttendanceChildSerializer
    permission_classes = (permissions.IsAuthenticated,)

    """Provide attendance percentages per month and per programme."""

    @action(detail=False, methods=['get'], url_path='percentage')
    def percentage(self, request, *args, **kwargs):
        year = int(self.request.GET.get('year', timezone.now().year))

        base_qs = MSCCAttendanceChild.objects.filter(
            attendance_day__attendance_date__year=year
        )

        monthly_rows = _aggregate_attendance(
            base_qs,
            'attendance_day__attendance_date__month',
        )

        monthly = []
        for row in monthly_rows:
            month = row['attendance_day__attendance_date__month']
            total = row['total'] or 0
            absent = row['absent'] or 0
            present = total - absent
            percentage = round((present * 100.0) / total, 2) if total else 0.0
            monthly.append({
                'month': month,
                'month_name': calendar.month_name[month],
                'attendance_percentage': percentage,
                'present': present,
                'absent': absent,
                'total': total,
            })

        programme_rows = _aggregate_attendance(
            base_qs,
            'attendance_day__attendance_date__month',
            'registration__education_service__education_program',
        )

        programme_category_lookup, category_order_lookup = _get_programme_lookups()
        programme_choices = _get_education_program_dict()
        programme_monthly_totals = {}

        for row in programme_rows:
            programme = row['registration__education_service__education_program'] or 'Unknown'
            label = programme_choices.get(programme, programme)
            category = programme_category_lookup.get(programme)

            if category is None:
                category = force_str(label) if label else 'Unknown'

            month = row['attendance_day__attendance_date__month']
            key = (category, month)
            total_entry = programme_monthly_totals.setdefault(key, {'total': 0, 'absent': 0})
            total_entry['total'] += row['total'] or 0
            total_entry['absent'] += row['absent'] or 0

        programme_monthly = OrderedDict()

        def _category_sort_key(item):
            (category, month), _data = item
            return (
                category_order_lookup.get(category, len(category_order_lookup)),
                month,
            )

        for (category, month), data in sorted(programme_monthly_totals.items(), key=_category_sort_key):
            total = data['total'] or 0
            absent = data['absent'] or 0
            present = total - absent
            percentage = round((present * 100.0) / total, 2) if total else 0.0

            if category not in programme_monthly:
                programme_monthly[category] = []

            programme_monthly[category].append({
                'month': month,
                'month_name': calendar.month_name[month],
                'attendance_percentage': percentage,
                'present': present,
                'absent': absent,
                'total': total,
            })

        for values in programme_monthly.values():
            values.sort(key=lambda item: item['month'])

        years = MSCCAttendanceChild.objects.dates(
            'attendance_day__attendance_date', 'year'
        )

        available_years = [d.year for d in years]
        available_years_str = ','.join(str(item) for item in available_years)

        flat_rows = []

        for entry in sorted(monthly, key=lambda item: item['month']):
            flat_rows.append({
                'record_type': 'monthly',
                'year': year,
                'available_years': available_years_str,
                'programme': '',
                **entry,
            })

        for programme, values in programme_monthly.items():
            for entry in values:
                flat_rows.append({
                    'record_type': 'programme_monthly',
                    'year': year,
                    'available_years': available_years_str,
                    'programme': programme,
                    **entry,
                })

        return JsonResponse(flat_rows, safe=False)
