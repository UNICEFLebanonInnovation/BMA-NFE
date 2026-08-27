from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView, DetailView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin
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

class RegistrationListView(LoginRequiredMixin, ALPUserRequiredMixin, SingleTableMixin, FilterView):
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

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

class RegistrationEditView(LoginRequiredMixin, ALPUserRequiredMixin, ALPEditPermissionMixin, UpdateView):
    model = ALPRegistration
    form_class = ALPRegistrationForm
    template_name = 'alp/registration_form.html'
    success_url = reverse_lazy('alp:registration_list')

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

class TeacherListView(LoginRequiredMixin, ALPUserRequiredMixin, SingleTableMixin, FilterView):
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

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

class TeacherEditView(LoginRequiredMixin, ALPUserRequiredMixin, ALPEditPermissionMixin, UpdateView):
    model = ALPTeacher
    form_class = ALPTeacherForm
    template_name = 'alp/teacher_form.html'
    success_url = reverse_lazy('alp:teacher_list')

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
from .forms import ALPGradingForm

class GradingAddView(LoginRequiredMixin, ALPUserRequiredMixin, ALPEditPermissionMixin, CreateView):
    model = ALPGrading
    form_class = ALPGradingForm
    template_name = 'alp/grading_form.html'
    success_url = reverse_lazy('alp:registration_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

class GradingEditView(LoginRequiredMixin, ALPUserRequiredMixin, ALPEditPermissionMixin, UpdateView):
    model = ALPGrading
    form_class = ALPGradingForm
    template_name = 'alp/grading_form.html'
    success_url = reverse_lazy('alp:registration_list')

    def get_queryset(self):
        qs = super().get_queryset()
        return filter_by_school(qs, self.request.user)
