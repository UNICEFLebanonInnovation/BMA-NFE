from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin
from django_tables2.export.views import ExportMixin

from .models import ALPAttendance, ALPTeacherAttendance
from .views import ALPUserRequiredMixin, ALPEditPermissionMixin
from .tables import ALPAttendanceTable, ALPTeacherAttendanceTable
from .filters import ALPAttendanceFilter, ALPTeacherAttendanceFilter
from .utils import filter_by_school

class AttendanceListView(LoginRequiredMixin, ALPUserRequiredMixin, ExportMixin, SingleTableMixin, FilterView):
    model = ALPAttendance
    table_class = ALPAttendanceTable
    filterset_class = ALPAttendanceFilter
    template_name = 'alp/attendance_list.html'

    def get_queryset(self):
        qs = super().get_queryset()
        return filter_by_school(qs, self.request.user)

class TeacherAttendanceListView(LoginRequiredMixin, ALPUserRequiredMixin, ExportMixin, SingleTableMixin, FilterView):
    model = ALPTeacherAttendance
    table_class = ALPTeacherAttendanceTable
    filterset_class = ALPTeacherAttendanceFilter
    template_name = 'alp/teacher_attendance_list.html'

    def get_queryset(self):
        qs = super().get_queryset()
        return filter_by_school(qs, self.request.user)

from django.views.generic import CreateView, UpdateView
from django.urls import reverse_lazy
from django import forms

from .mixins import ALPSchoolFilterMixin

class ALPAttendanceForm(ALPSchoolFilterMixin, forms.ModelForm):
    class Meta:
        model = ALPAttendance
        fields = ['registration', 'date', 'status', 'shift']

class TeacherAttendanceForm(ALPSchoolFilterMixin, forms.ModelForm):
    class Meta:
        model = ALPTeacherAttendance
        fields = ['teacher', 'date', 'status']

class AttendanceAddView(LoginRequiredMixin, ALPUserRequiredMixin, ALPEditPermissionMixin, CreateView):
    model = ALPAttendance
    form_class = ALPAttendanceForm
    template_name = 'alp/attendance_form.html'
    success_url = reverse_lazy('alp:attendance_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

class AttendanceEditView(LoginRequiredMixin, ALPUserRequiredMixin, ALPEditPermissionMixin, UpdateView):
    model = ALPAttendance
    form_class = ALPAttendanceForm
    template_name = 'alp/attendance_form.html'
    success_url = reverse_lazy('alp:attendance_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get_queryset(self):
        qs = super().get_queryset()
        return filter_by_school(qs, self.request.user)

class TeacherAttendanceAddView(LoginRequiredMixin, ALPUserRequiredMixin, ALPEditPermissionMixin, CreateView):
    model = ALPTeacherAttendance
    form_class = TeacherAttendanceForm
    template_name = 'alp/attendance_form.html'
    success_url = reverse_lazy('alp:teacher_attendance_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

class TeacherAttendanceEditView(LoginRequiredMixin, ALPUserRequiredMixin, ALPEditPermissionMixin, UpdateView):
    model = ALPTeacherAttendance
    form_class = TeacherAttendanceForm
    template_name = 'alp/attendance_form.html'
    success_url = reverse_lazy('alp:teacher_attendance_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get_queryset(self):
        qs = super().get_queryset()
        return filter_by_school(qs, self.request.user)
