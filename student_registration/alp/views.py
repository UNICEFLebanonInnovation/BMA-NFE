from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView, DetailView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin
from django_tables2.export.views import ExportMixin
from django.core.exceptions import PermissionDenied
from django.contrib import messages

from .models import ALPRegistration, ALPTeacher, ALPGrading
from .forms import ALPRegistrationForm, ALPTeacherForm, ALPSchoolProfileForm
from .tables import ALPRegistrationTable, ALPTeacherTable
from .filters import ALPRegistrationFilter, ALPTeacherFilter
from .utils import user_has_alp_permission, filter_by_school

class ALPUserRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return user_has_alp_permission(self.request.user)

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

from django.views.generic import TemplateView, View
from django.http import JsonResponse
from django.db.models import Count

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
        from .models import ALPTeacher

        user = self.request.user
        instances = filter_by_school(ALPTeacher.objects.all(), user)

        schools = School.objects.all()

        if not user.is_superuser:
            schools = schools.filter(id=user.school_id)

        return {
            'total': instances.count(),
            'schools': schools,
        }

class ALPAttendanceDashboardView(LoginRequiredMixin, ALPUserRequiredMixin, TemplateView):
    template_name = 'alp/dashboard_attendance.html'

    def get_context_data(self, **kwargs):
        from student_registration.schools.models import School
        from .models import ALPAttendance

        user = self.request.user
        instances = filter_by_school(ALPAttendance.objects.all(), user)

        schools = School.objects.all()

        if not user.is_superuser:
            schools = schools.filter(id=user.school_id)

        return {
            'total': instances.count(),
            'schools': schools,
        }

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
import json
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
from django.utils import timezone
from django.db.models import Count
from django.db.models.functions import TruncDate
from student_registration.alp.models import ALPRegistration
from student_registration.alp.models import ALPAttendanceChild
from student_registration.backends.models import ExportHistory

class ALPLandingPage(LoginRequiredMixin, ALPUserRequiredMixin, TemplateView):
    template_name = 'alp/landing_page.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if settings.USE_TZ:
            today = timezone.localdate()
        else:
            today = timezone.now().date()
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
