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
