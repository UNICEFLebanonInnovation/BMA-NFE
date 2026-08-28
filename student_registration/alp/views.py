from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView, DetailView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin
from django_tables2.export.views import ExportMixin
from django.core.exceptions import PermissionDenied

from .models import ALPRegistration, ALPTeacher, ALPGrading
from .forms import ALPRegistrationForm, ALPTeacherForm
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
        response = super().form_valid(form)
        teacher = form.instance
        if not teacher.unicef_id:
            from student_registration.students.utils import generate_one_unique_id
            teacher.unicef_id = generate_one_unique_id(
                f"T-{teacher.pk}",
                teacher.first_name,
                teacher.father_name,
                teacher.last_name,
                "", # No mother name collected for teachers
                "1980-01-01", # Default fallback if no dob is collected
                "LEB", # Default fallback
                teacher.sex
            )
            teacher.save()
        return response

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
        response = super().form_valid(form)
        teacher = form.instance
        if not teacher.unicef_id:
            from student_registration.students.utils import generate_one_unique_id
            teacher.unicef_id = generate_one_unique_id(
                f"T-{teacher.pk}",
                teacher.first_name,
                teacher.father_name,
                teacher.last_name,
                "", # No mother name collected for teachers
                "1980-01-01", # Default fallback if no dob is collected
                "LEB", # Default fallback
                teacher.sex
            )
            teacher.save()
        return response

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

class TeacherDeleteView(LoginRequiredMixin, ALPUserRequiredMixin, ALPEditPermissionMixin, DeleteView):
    model = ALPTeacher
    template_name = 'alp/teacher_confirm_delete.html'
    success_url = reverse_lazy('alp:teacher_list')

    def get_queryset(self):
        qs = super().get_queryset()
        return filter_by_school(qs, self.request.user)

class SchoolProfileView(LoginRequiredMixin, ALPUserRequiredMixin, TemplateView):
    template_name = 'alp/school_profile.html'

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


from django.http import JsonResponse
import json
from student_registration.students.models import Nationality

def child_duplication_check(request):
    body_unicode = request.body.decode('utf-8')
    if body_unicode:
        body = json.loads(body_unicode)

        birthday_year = body.get('birthday_year')
        birthday_month = body.get('birthday_month')
        birthday_day = body.get('birthday_day')
        first_name = body.get('first_name')
        father_name = body.get('father_name')
        last_name = body.get('last_name')
        mother_fullname = body.get('mother_fullname')
        sex = body.get('sex')
        nationality_id = body.get('nationality')
        registration_id = body.get('registration_id')

        try:
            nationality = Nationality.objects.get(id=nationality_id).name_en
        except Nationality.DoesNotExist:
            nationality = ''

        birthdate = '{0}-{1}-{2}'.format(birthday_year, birthday_month, birthday_day)
        from student_registration.students.utils import generate_one_unique_id
        unicef_id = generate_one_unique_id(
            '0',
            first_name,
            father_name,
            last_name,
            mother_fullname,
            birthdate,
            nationality,
            sex
        )

        if unicef_id:
            qs = ALPRegistration.objects.filter(
                child__unicef_id=unicef_id,
                deleted=False
            )
            if registration_id:
                try:
                    current_reg = ALPRegistration.objects.get(pk=registration_id)
                    qs = qs.exclude(child_id=current_reg.child_id)
                except ALPRegistration.DoesNotExist:
                    qs = qs.exclude(pk=registration_id)
            qs = qs.values(
                'id',
                'school__name',
                'child__first_name',
                'child__father_name',
                'child__last_name',
                'child__mother_fullname',
                'child__birthday_day',
                'child__birthday_month',
                'child__birthday_year',
                'child__gender',
                'child__nationality__name'
            )
            results = list(qs)
            for row in results:
                row['center__name'] = row.pop('school__name')
            return JsonResponse({'result': results})

    return JsonResponse({'result': []})
