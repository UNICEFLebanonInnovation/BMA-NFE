from datetime import timedelta

from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView, DetailView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin
from django_tables2.export.views import ExportMixin
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.conf import settings

from django.db.models import Count, Q
from django.utils import timezone
import json
from collections import OrderedDict

from .models import ALPAttendanceChild, ALPRegistration, ALPTeacher, ALPGrading
from .forms import ALPRegistrationForm, ALPTeacherForm, ALPSchoolProfileForm
from .tables import ALPRegistrationTable, ALPTeacherTable
from .filters import ALPRegistrationFilter, ALPTeacherFilter
from .utils import user_has_alp_permission, filter_by_school


def _current_date():
    """Return today's date without localizing a naive datetime."""
    if settings.USE_TZ:
        return timezone.localdate()
    return timezone.now().date()


class ALPUserRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return user_has_alp_permission(self.request.user)


class ALPPivotUserRequiredMixin(UserPassesTestMixin):
    """Allow ALP focal points and site administrators into ALP reporting."""

    def test_func(self):
        user = self.request.user
        return user.is_staff or user_has_alp_permission(user)

class ALPEditPermissionMixin(object):
    """
    Superadmins can see all schools info in read-only mode.
    Only school users (non-superadmins with ALP_SCHOOL group) can manage data.
    """
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_superuser:
            raise PermissionDenied("Superusers have read-only access to ALP data.")
        return super().dispatch(request, *args, **kwargs)

class RegistrationListView(LoginRequiredMixin, ALPUserRequiredMixin, ExportMixin, SingleTableMixin, FilterView):
    model = ALPRegistration
    table_class = ALPRegistrationTable
    filterset_class = ALPRegistrationFilter
    template_name = 'alp/registration_list.html'

    def get_queryset(self):
        qs = super().get_queryset()
        return filter_by_school(qs, self.request.user)

class RegistrationAddView(LoginRequiredMixin, ALPUserRequiredMixin, ALPEditPermissionMixin, CreateView):
    model = ALPRegistration
    form_class = ALPRegistrationForm
    template_name = 'alp/registration_form.html'
    success_url = reverse_lazy('alp:registration_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

class RegistrationEditView(LoginRequiredMixin, ALPUserRequiredMixin, ALPEditPermissionMixin, UpdateView):
    model = ALPRegistration
    form_class = ALPRegistrationForm
    template_name = 'alp/registration_form.html'
    success_url = reverse_lazy('alp:registration_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get_queryset(self):
        qs = super().get_queryset()
        return filter_by_school(qs, self.request.user)

    def form_valid(self, form):
        form.instance.modified_by = self.request.user
        return super().form_valid(form)

class RegistrationDeleteView(LoginRequiredMixin, ALPUserRequiredMixin, ALPEditPermissionMixin, DeleteView):
    model = ALPRegistration
    template_name = 'alp/registration_confirm_delete.html'
    success_url = reverse_lazy('alp:registration_list')

    def get_queryset(self):
        qs = super().get_queryset()
        return filter_by_school(qs, self.request.user)

class TeacherListView(LoginRequiredMixin, ALPUserRequiredMixin, ExportMixin, SingleTableMixin, FilterView):
    model = ALPTeacher
    table_class = ALPTeacherTable
    filterset_class = ALPTeacherFilter
    template_name = 'alp/teacher_list.html'

    def get_queryset(self):
        qs = super().get_queryset()
        return filter_by_school(qs, self.request.user)

class TeacherAddView(LoginRequiredMixin, ALPUserRequiredMixin, ALPEditPermissionMixin, CreateView):
    model = ALPTeacher
    form_class = ALPTeacherForm
    template_name = 'alp/teacher_form.html'
    success_url = reverse_lazy('alp:teacher_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_valid(self, form):
        form.instance.owner = self.request.user
        form.instance.modified_by = self.request.user
        return super().form_valid(form)

class TeacherEditView(LoginRequiredMixin, ALPUserRequiredMixin, ALPEditPermissionMixin, UpdateView):
    model = ALPTeacher
    form_class = ALPTeacherForm
    template_name = 'alp/teacher_form.html'
    success_url = reverse_lazy('alp:teacher_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get_queryset(self):
        qs = super().get_queryset()
        return filter_by_school(qs, self.request.user)

    def form_valid(self, form):
        form.instance.modified_by = self.request.user
        return super().form_valid(form)

class TeacherDeleteView(LoginRequiredMixin, ALPUserRequiredMixin, ALPEditPermissionMixin, DeleteView):
    model = ALPTeacher
    template_name = 'alp/teacher_confirm_delete.html'
    success_url = reverse_lazy('alp:teacher_list')

    def get_queryset(self):
        qs = super().get_queryset()
        return filter_by_school(qs, self.request.user)

class SchoolProfileView(LoginRequiredMixin, ALPUserRequiredMixin, UpdateView):
    """Display a school profile and let its focal point update it."""

    form_class = ALPSchoolProfileForm
    template_name = 'alp/school_profile.html'
    success_url = reverse_lazy('alp:school_profile')

    def get_object(self, queryset=None):
        school = self.request.user.school
        if school is None:
            raise PermissionDenied("Your account is not assigned to a school.")
        return school

    def dispatch(self, request, *args, **kwargs):
        if request.method == 'POST' and request.user.is_superuser:
            raise PermissionDenied("Superusers have read-only access to ALP data.")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.modified_by = self.request.user
        messages.success(self.request, 'School information updated successfully.')
        return super().form_valid(form)

class ChildProfileView(LoginRequiredMixin, ALPUserRequiredMixin, DetailView):
    model = ALPRegistration
    template_name = 'alp/child_profile.html'
    context_object_name = 'registration'

    def get_queryset(self):
        qs = super().get_queryset()
        return filter_by_school(qs, self.request.user)

from django.views.generic import CreateView, UpdateView
from .forms import ALPGradingDynamicForm

class GradingAddView(LoginRequiredMixin, ALPUserRequiredMixin, ALPEditPermissionMixin, CreateView):
    model = ALPGrading
    form_class = ALPGradingDynamicForm
    template_name = 'alp/grading_form.html'
    success_url = reverse_lazy('alp:registration_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

class GradingEditView(LoginRequiredMixin, ALPUserRequiredMixin, ALPEditPermissionMixin, UpdateView):
    model = ALPGrading
    form_class = ALPGradingDynamicForm
    template_name = 'alp/grading_form.html'
    success_url = reverse_lazy('alp:registration_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get_queryset(self):
        qs = super().get_queryset()
        return filter_by_school(qs, self.request.user)

from django.views.generic import View
from django.http import JsonResponse
from django.db.models import Avg, Count, Q, Sum


def _alp_pivot_queryset(user):
    """Return registrations in the reporting scope of ``user``."""
    queryset = ALPRegistration.objects.filter(deleted=False)
    if user.is_superuser or user.is_staff:
        return queryset
    return filter_by_school(queryset, user)


class ALPPivotDashboardView(
        LoginRequiredMixin, ALPPivotUserRequiredMixin, TemplateView):
    """Display the interactive pivot builder using ALP registrations only."""

    template_name = 'alp/pivot_dashboard.html'


class ALPPivotDataView(LoginRequiredMixin, ALPPivotUserRequiredMixin, View):
    """Return ALP registration dimensions within the connected user's scope."""

    def get(self, request):
        queryset = _alp_pivot_queryset(request.user).values(
            'school__number',
            'school__name',
            'school__governorate__name',
            'school__district__name',
            'school__cadaster__name',
            'child__gender',
            'child__nationality__name',
            'child__birthday_year',
            'round__name',
            'programme__name',
            'registration_date',
            'have_labour',
            'labour_type',
            'labour_weekly_income',
            'source_of_identification',
            'type',
        )

        data = []
        for registration in queryset.iterator():
            registration_date = registration['registration_date']
            data.append({
                'school_number': registration['school__number'] or '',
                'school': registration['school__name'] or '',
                'governorate': registration['school__governorate__name'] or '',
                'district': registration['school__district__name'] or '',
                'cadaster': registration['school__cadaster__name'] or '',
                'gender': registration['child__gender'] or '',
                'nationality': registration['child__nationality__name'] or '',
                'birth_year': registration['child__birthday_year'] or '',
                'round': registration['round__name'] or '',
                'programme': registration['programme__name'] or '',
                'registration_date': (
                    registration_date.isoformat() if registration_date else ''
                ),
                'participates_in_work': registration['have_labour'] or '',
                'work_type': registration['labour_type'] or '',
                'weekly_income': registration['labour_weekly_income'] or '',
                'referral_source': registration['source_of_identification'] or '',
                'registration_type': registration['type'] or '',
            })

        return JsonResponse(data, safe=False)

class ALPRegistrationDashboardView(LoginRequiredMixin, ALPUserRequiredMixin, TemplateView):
    template_name = 'alp/dashboard_registration.html'

    def get_context_data(self, **kwargs):
        from student_registration.schools.models import School
        from .models import ALPRound, ALPProgram, ALPRegistration

        user = self.request.user
        instances = filter_by_school(ALPRegistration.objects.filter(deleted=False), user)

        schools = School.objects.all()
        rounds = ALPRound.objects.all()
        programmes = ALPProgram.objects.all()

        if not user.is_superuser:
            schools = schools.filter(id=user.school_id)

        return {
            'total': instances.count(),
            'schools': schools,
            'rounds': rounds,
            'programmes': programmes,
        }

class ALPDashboardDataView(LoginRequiredMixin, ALPUserRequiredMixin, View):
    def get(self, request):
        from .models import ALPRegistration
        user = request.user

        qs = filter_by_school(ALPRegistration.objects.filter(deleted=False), user)

        schools = request.GET.getlist('schools')
        if schools:
            qs = qs.filter(school_id__in=schools)

        rounds = request.GET.getlist('rounds')
        if rounds:
            qs = qs.filter(round_id__in=rounds)

        programmes = request.GET.getlist('programmes')
        if programmes:
            qs = qs.filter(programme_id__in=programmes)

        def aggregate(queryset, field):
            results = queryset.values(field).annotate(total=Count('id')).order_by(field)
            data = []
            for row in results:
                name = row.get(field) or 'N/A'
                data.append({'name': name, 'y': row['total']})
            return data

        nationality_data = aggregate(qs, 'child__nationality__name_en')
        gender_data = aggregate(qs, 'child__gender')
        round_data = aggregate(qs, 'round__name')
        programme_data = aggregate(qs, 'programme__name')

        response_data = {
            'nationality': nationality_data,
            'gender': gender_data,
            'round': round_data,
            'programme': programme_data,
        }

        return JsonResponse(response_data)

class ALPTeacherDashboardView(LoginRequiredMixin, ALPUserRequiredMixin, TemplateView):
    template_name = 'alp/dashboard_teacher.html'

    def get_context_data(self, **kwargs):
        from student_registration.schools.models import School
        from .models import (
            ALPProgram,
            ALPRegistration,
            ALPRound,
            ALPTeacher,
            ALPTeacherAttendance,
        )

        user = self.request.user
        instances = filter_by_school(ALPTeacher.objects.all(), user)

        schools = School.objects.all()
        rounds = ALPRound.objects.all()

        if not user.is_superuser:
            schools = schools.filter(id=user.school_id)

        programmes = ALPProgram.objects.all()
        selected_school = self.request.GET.get('school', '')
        selected_programme = self.request.GET.get('programme', '')
        today = _current_date()
        default_start = today - timedelta(days=180)

        try:
            start_date = timezone.datetime.strptime(
                self.request.GET.get('start_date', ''), '%Y-%m-%d'
            ).date()
        except (TypeError, ValueError):
            start_date = default_start
        try:
            end_date = timezone.datetime.strptime(
                self.request.GET.get('end_date', ''), '%Y-%m-%d'
            ).date()
        except (TypeError, ValueError):
            end_date = today

        if start_date > end_date:
            start_date, end_date = end_date, start_date

        if selected_school:
            instances = instances.filter(school_id=selected_school)
        if selected_programme:
            programme_school_ids = ALPRegistration.objects.filter(
                programme_id=selected_programme
            ).values_list('school_id', flat=True)
            instances = instances.filter(school_id__in=programme_school_ids)

        attendance = ALPTeacherAttendance.objects.filter(
            teacher__in=instances,
            date__range=(start_date, end_date),
        ).select_related('teacher__school')

        records = list(attendance.values(
            'date', 'status', 'teacher_id', 'teacher__school_id', 'teacher__school__name'
        ))
        present = sum(row['status'] == 'Present' for row in records)
        rate = round((present / len(records)) * 100, 1) if records else 0

        monthly = {}
        school_totals = {}
        for row in records:
            month = row['date'].strftime('%Y-%m') if row['date'] else 'Unknown'
            monthly.setdefault(month, {'present': 0, 'total': 0})
            monthly[month]['total'] += 1
            monthly[month]['present'] += row['status'] == 'Present'

            school_name = row['teacher__school__name'] or 'Unassigned'
            school_totals.setdefault(school_name, {'present': 0, 'total': 0})
            school_totals[school_name]['total'] += 1
            school_totals[school_name]['present'] += row['status'] == 'Present'

        trend = [
            {'month': month, 'rate': round(values['present'] / values['total'] * 100, 1)}
            for month, values in sorted(monthly.items())
        ]
        by_school = [
            {'school': name, 'rate': round(values['present'] / values['total'] * 100, 1),
             'records': values['total']}
            for name, values in sorted(school_totals.items(), key=lambda item: item[1]['total'], reverse=True)
        ]

        programme_rows = []
        for programme in programmes:
            programme_school_ids = set(ALPRegistration.objects.filter(
                programme=programme
            ).values_list('school_id', flat=True))
            relevant = [row for row in records if row['teacher__school_id'] in programme_school_ids]
            programme_present = sum(row['status'] == 'Present' for row in relevant)
            programme_rows.append({
                'programme': programme.name,
                'rate': round(programme_present / len(relevant) * 100, 1) if relevant else 0,
                'records': len(relevant),
            })

        return {
            'total': instances.count(),
            'schools': schools,
            'rounds': rounds,
        }


class ALPTeacherDashboardDataView(LoginRequiredMixin, ALPUserRequiredMixin, View):
    """Return teacher workforce indicators within the user's ALP school scope."""

    def get(self, request):
        teachers = filter_by_school(ALPTeacher.objects.all(), request.user)

        school_ids = request.GET.getlist('schools')
        if school_ids:
            teachers = teachers.filter(school_id__in=school_ids)

        round_ids = request.GET.getlist('rounds')
        if round_ids:
            teachers = teachers.filter(round_id__in=round_ids)

        total = teachers.count()
        trained = teachers.filter(
            Q(trainings__isnull=False) | Q(training_sessions_attended__gt=0)
        ).distinct().count()
        contactable = teachers.exclude(
            Q(phone_number__isnull=True) | Q(phone_number='')
        ).count()
        averages = teachers.aggregate(
            experience=Avg('years_of_experience'),
            sessions=Avg('training_sessions_attended'),
        )
        hours = teachers.aggregate(
            alp=Sum('teaching_hours_mscc'),
            private=Sum('teaching_hours_private_school'),
        )

        def percent(value):
            return round(value * 100 / total, 1) if total else 0

        def grouped(field):
            rows = teachers.values(field).annotate(y=Count('id')).order_by(field)
            return [
                {'name': row[field] or 'Not specified', 'y': row['y']}
                for row in rows
            ]

        subjects = {}
        levels = {}
        for teacher in teachers.only('subjects_provided', 'registration_level'):
            for subject in teacher.subjects_provided or []:
                if subject:
                    subjects[subject] = subjects.get(subject, 0) + 1
            for level in teacher.registration_level or []:
                if level:
                    levels[level] = levels.get(level, 0) + 1

        training_rows = (
            teachers.filter(trainings__isnull=False)
            .values('trainings__name')
            .annotate(y=Count('id', distinct=True))
            .order_by('-y', 'trainings__name')
        )

        return JsonResponse({
            'total': total,
            'schools': teachers.exclude(school_id__isnull=True).values('school_id').distinct().count(),
            'trained': trained,
            'trained_percent': percent(trained),
            'contact_percent': percent(contactable),
            'average_experience': round(averages['experience'] or 0, 1),
            'average_sessions': round(averages['sessions'] or 0, 1),
            'gender': grouped('sex'),
            'nationality': grouped('nationality__name'),
            'school': grouped('school__name'),
            'round': grouped('round__name'),
            'assignment': grouped('teacher_assignment'),
            'coaching': grouped('extra_coaching'),
            'subjects': [{'name': key, 'y': value} for key, value in subjects.items()],
            'levels': [{'name': key, 'y': value} for key, value in levels.items()],
            'trainings': [
                {'name': row['trainings__name'] or 'Not specified', 'y': row['y']}
                for row in training_rows
            ],
            'hours': [
                {'name': 'ALP', 'y': hours['alp'] or 0},
                {'name': 'Private school', 'y': hours['private'] or 0},
            ],
        })

class ALPAttendanceDashboardView(LoginRequiredMixin, ALPUserRequiredMixin, TemplateView):
    template_name = 'alp/dashboard_attendance.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        year = int(self.request.GET.get('year', timezone.now().year))
        base_qs = _alp_attendance_queryset(user).filter(
            attendance_day__attendance_date__year=year,
        )
        attendance = _aggregate_alp_attendance(base_qs, 'attendance_day__attendance_date')
        programme_attendance = _aggregate_alp_attendance(
            base_qs, 'attendance_day__attendance_date', 'attendance_day__programme__name'
        )

        programme_data = OrderedDict()
        for row in programme_attendance:
            programme = row.pop('attendance_day__programme__name') or 'Unknown'
            programme_data.setdefault(programme, []).append(row)

        years = _alp_attendance_queryset(user).dates('attendance_day__attendance_date', 'year')
        context.update({
            'attendance_json': json.dumps(list(attendance), default=str),
            'program_attendance_json': json.dumps(programme_data, default=str),
            'year': year,
            'years': [date.year for date in years],
        })
        return context


def _alp_attendance_queryset(user):
    """Return child attendance records visible to an ALP user."""
    queryset = ALPAttendanceChild.objects.all()
    if not user.is_superuser:
        queryset = queryset.filter(attendance_day__school_id=user.school_id)
    return queryset


def _aggregate_alp_attendance(queryset, *group_fields):
    """Aggregate total and absent child records for heatmap groups."""
    return (
        queryset.values(*group_fields)
        .annotate(total=Count('id'), absent=Count('id', filter=Q(attended='No')))
        .order_by(*group_fields)
    )

class ALPSchoolDashboardView(LoginRequiredMixin, ALPUserRequiredMixin, TemplateView):
    template_name = 'alp/dashboard_school.html'

    def get_context_data(self, **kwargs):
        from student_registration.schools.models import School

        user = self.request.user

        schools = School.objects.all()

        if not user.is_superuser:
            schools = schools.filter(id=user.school_id)

        return {
            'total': schools.count(),
            'schools': schools,
        }

      
class ALPSchoolGeoDataView(LoginRequiredMixin, ALPUserRequiredMixin, View):
    """Return map-ready school data within the current ALP user's scope."""

    def get(self, request):
        from django.db.models import Count
        from student_registration.schools.models import School

        schools = School.objects.select_related(
            'governorate', 'district', 'cadaster'
        ).filter(
            latitude__isnull=False, longitude__isnull=False
        ).order_by('name')

        if not request.user.is_superuser:
            if not request.user.school_id:
                return JsonResponse([], safe=False)
            schools = schools.filter(id=request.user.school_id)

        school_id = request.GET.get('school_id')
        if school_id:
            schools = schools.filter(id=school_id)

        school_list = list(schools)
        school_ids = [school.id for school in school_list]
        registration_stats = {
            row['school_id']: row['total']
            for row in ALPRegistration.objects.filter(
                school_id__in=school_ids, deleted=False
            ).values('school_id').annotate(total=Count('id'))
        }
        teacher_stats = {
            row['school_id']: row['total']
            for row in ALPTeacher.objects.filter(
                school_id__in=school_ids
            ).values('school_id').annotate(total=Count('id'))
        }

        data = [{
            'id': school.id,
            'number': school.number,
            'name': school.name,
            'type': school.get_type_display() if school.type else 'N/A',
            'governorate': (
                school.governorate.name if school.governorate else 'N/A'
            ),
            'district': school.district.name if school.district else 'N/A',
            'cadaster': school.cadaster.name if school.cadaster else 'N/A',
            'latitude': school.latitude,
            'longitude': school.longitude,
            'students': registration_stats.get(school.id, 0),
            'teachers': teacher_stats.get(school.id, 0),
            'capacity': school.school_capacity or 0,
            'cwd_accessible': (
                school.get_CWD_accessible_display()
                if school.CWD_accessible else 'N/A'
            ),
            'internet_available': (
                school.get_internet_available_display()
                if school.internet_available else 'N/A'
            ),
        } for school in school_list]

        return JsonResponse(data, safe=False)
      
      
import json
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

from django.db.models.functions import TruncDate
from student_registration.backends.models import ExportHistory

class ALPLandingPage(LoginRequiredMixin, ALPUserRequiredMixin, TemplateView):
    template_name = 'alp/landing_page.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        today = _current_date()
        week_start = today - timezone.timedelta(days=6)
        trend_start = today - timezone.timedelta(days=13)
        month_start = today.replace(day=1)

        user = self.request.user

        # apply school filtering for standard users
        registrations = ALPRegistration.objects.filter(deleted=False)
        if not user.is_superuser:
            registrations = registrations.filter(school_id=user.school_id)

        today_count = registrations.filter(created__date=today).count()
        week_count = registrations.filter(created__date__gte=week_start).count()
        schools_reporting = registrations.filter(
            created__date__gte=today - timezone.timedelta(days=30),
            school__isnull=False,
        ).values('school_id').distinct().count()

        attendance_rows = ALPAttendanceChild.objects.filter(
            attendance_day__attendance_date__gte=month_start,
            attendance_day__attendance_date__lte=today,
        )
        if not user.is_superuser:
            attendance_rows = attendance_rows.filter(attendance_day__school_id=user.school_id)

        attendance_total = attendance_rows.count()
        attendance_yes = attendance_rows.filter(attended='Yes').count()
        attendance_percent = round((attendance_yes / attendance_total) * 100) if attendance_total else 0

        trend_map = {
            row['day'].strftime('%Y-%m-%d'): row['value']
            for row in registrations.filter(created__date__gte=trend_start)
            .annotate(day=TruncDate('created'))
            .values('day')
            .annotate(value=Count('id'))
        }
        trend_data = []
        for idx in range(14):
            day = trend_start + timezone.timedelta(days=idx)
            key = day.strftime('%Y-%m-%d')
            trend_data.append({'date': key, 'value': trend_map.get(key, 0)})

        recent_exports = ExportHistory.objects.filter(
            export_type__icontains='ALP'
        ).order_by('-created')[:5]
        export_rows = []
        for export in recent_exports:
            created = export.created
            if created and timezone.is_aware(created):
                created_display = timezone.localtime(created).strftime('%Y-%m-%d %H:%M')
            elif created:
                created_display = created.strftime('%Y-%m-%d %H:%M')
            else:
                created_display = ''
            export_rows.append({
                'export_type': export.export_type,
                'created_display': created_display,
                'status': export.status,
                'file_url': export.file.url if export.file and export.file.name else '#',
            })

        context.update({
            'kpi_today': today_count,
            'kpi_week': week_count,
            'kpi_schools': schools_reporting,
            'kpi_attendance': attendance_percent,
            'trend_data': json.dumps(trend_data),
            'recent_exports': export_rows,
        })
        return context
