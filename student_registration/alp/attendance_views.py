from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import ALPAttendance, ALPTeacherAttendance
from .views import ALPUserRequiredMixin

from .utils import filter_by_school

class AttendanceListView(LoginRequiredMixin, ALPUserRequiredMixin, ListView):
    model = ALPAttendance
    template_name = 'alp/attendance_list.html'
    context_object_name = 'attendances'

    def get_queryset(self):
        qs = super().get_queryset()
        return filter_by_school(qs, self.request.user)

class TeacherAttendanceListView(LoginRequiredMixin, ALPUserRequiredMixin, ListView):
    model = ALPTeacherAttendance
    template_name = 'alp/teacher_attendance_list.html'
    context_object_name = 'attendances'

    def get_queryset(self):
        qs = super().get_queryset()
        return filter_by_school(qs, self.request.user)

from django.views.generic import CreateView, UpdateView
from django.urls import reverse_lazy
from django import forms

class ALPAttendanceForm(forms.ModelForm):
    class Meta:
        model = ALPAttendance
        fields = ['registration', 'date', 'status', 'shift']

class TeacherAttendanceForm(forms.ModelForm):
    class Meta:
        model = ALPTeacherAttendance
        fields = ['teacher', 'date', 'status']

class AttendanceAddView(LoginRequiredMixin, ALPUserRequiredMixin, CreateView):
    model = ALPAttendance
    form_class = ALPAttendanceForm
    template_name = 'alp/attendance_form.html'
    success_url = reverse_lazy('alp:attendance_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

class AttendanceEditView(LoginRequiredMixin, ALPUserRequiredMixin, UpdateView):
    model = ALPAttendance
    form_class = ALPAttendanceForm
    template_name = 'alp/attendance_form.html'
    success_url = reverse_lazy('alp:attendance_list')

    def get_queryset(self):
        qs = super().get_queryset()
        return filter_by_school(qs, self.request.user)

class TeacherAttendanceAddView(LoginRequiredMixin, ALPUserRequiredMixin, CreateView):
    model = ALPTeacherAttendance
    form_class = TeacherAttendanceForm
    template_name = 'alp/attendance_form.html'
    success_url = reverse_lazy('alp:teacher_attendance_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

class TeacherAttendanceEditView(LoginRequiredMixin, ALPUserRequiredMixin, UpdateView):
    model = ALPTeacherAttendance
    form_class = TeacherAttendanceForm
    template_name = 'alp/attendance_form.html'
    success_url = reverse_lazy('alp:teacher_attendance_list')

    def get_queryset(self):
        qs = super().get_queryset()
        return filter_by_school(qs, self.request.user)
