import json
from django.views.generic import TemplateView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin
from django_tables2.export.views import ExportMixin
from django.http import JsonResponse, HttpResponseBadRequest
from django.urls import reverse_lazy
from django import forms
from django.views.decorators.http import require_POST
from student_registration.users.mixins import GroupRequiredMixin, group_required
from datetime import datetime

from .models import ALPAttendance, ALPTeacherAttendance, ALPRound, ALPProgram
from .views import ALPUserRequiredMixin, ALPEditPermissionMixin
from .tables import ALPTeacherAttendanceTable
from .filters import ALPTeacherAttendanceFilter
from .utils import filter_by_school, load_child_attendance, create_attendance, load_teacher_attendance, create_teacher_attendance
from .mixins import ALPSchoolFilterMixin

class AttendanceView(LoginRequiredMixin, ALPUserRequiredMixin, TemplateView):
    template_name = 'alp/attendance.html'

    def get_context_data(self, **kwargs):
        school_id = self.request.user.school_id
        now = datetime.now()
        attendance_date = now.strftime('%m/%d/%Y')
        attendance_date_iso = now.strftime('%Y-%m-%d')
        day_off = 'No'
        close_reason = ''
        rounds = ALPRound.objects.filter(current_year=True)
        programmes = ALPProgram.objects.all()

        instance = None

        if school_id:
            instance = ALPAttendance.objects.filter(school_id=school_id,
                                                 attendance_date=now.date()).last()

        if instance:
            day_off = instance.day_off
            close_reason = instance.close_reason

        return {
            'instance': instance,
            'attendance_date': attendance_date,
            'attendance_date_iso': attendance_date_iso,
            'day_off': day_off,
            'close_reason': close_reason,
            'rounds': rounds,
            'programmes': programmes,
        }

class LoadAttendanceChildren(LoginRequiredMixin, ALPUserRequiredMixin, TemplateView):
    template_name = 'alp/attendance_children.html'

    def get_context_data(self, **kwargs):
        current_date = datetime.today().date()
        attendance_date_str = self.request.GET.get("attendance_date")
        school_id = self.request.user.school_id
        programme_id = self.request.GET.get("programme")
        round_id = self.request.GET.get("round_id")

        if attendance_date_str is None:
            return {'instances': [], 'new_instances': []}

        try:
            if '-' in attendance_date_str:
                attendance_date = datetime.strptime(attendance_date_str, '%Y-%m-%d').date()
            else:
                attendance_date = datetime.strptime(attendance_date_str, '%m/%d/%Y').date()

            if attendance_date <= current_date and school_id:
                data = load_child_attendance(
                    school_id,
                    round_id,
                    attendance_date_str,
                    programme_id,
                )
            else:
                data = {'instances': [], 'new_instances': []}
        except ValueError:
            data = {'instances': [], 'new_instances': []}

        return data

@require_POST
@group_required("ALP_SCHOOL")
def save_attendance_children(request):
    if request.user.school_id is None:
        return HttpResponseBadRequest("No school assigned")

    body_unicode = request.body.decode("utf-8")

    if not body_unicode.strip():
        return HttpResponseBadRequest("Empty request body")

    try:
        data = json.loads(body_unicode)
    except ValueError:
        return HttpResponseBadRequest("Invalid JSON payload")

    try:
        result = create_attendance(data, request.user.school_id)
    except Exception:
        return HttpResponseBadRequest("Failed to save attendance")

    return JsonResponse({"result": result})


class TeacherAttendanceView(LoginRequiredMixin, ALPUserRequiredMixin, TemplateView):
    template_name = 'alp/teacher_attendance.html'

    def get_context_data(self, **kwargs):
        school_id = self.request.user.school_id
        now = datetime.now()
        attendance_date = now.strftime('%m/%d/%Y')
        attendance_date_iso = now.strftime('%Y-%m-%d')

        return {
            'attendance_date': attendance_date,
            'attendance_date_iso': attendance_date_iso,
        }

class LoadAttendanceTeachers(LoginRequiredMixin, ALPUserRequiredMixin, TemplateView):
    template_name = 'alp/teacher_attendance_list_partial.html'

    def get_context_data(self, **kwargs):
        current_date = datetime.today().date()
        attendance_date_str = self.request.GET.get("attendance_date")
        school_id = self.request.user.school_id

        if attendance_date_str is None:
            return {'instances': [], 'new_instances': []}

        try:
            if '-' in attendance_date_str:
                attendance_date = datetime.strptime(attendance_date_str, '%Y-%m-%d').date()
            else:
                attendance_date = datetime.strptime(attendance_date_str, '%m/%d/%Y').date()

            if attendance_date <= current_date and school_id:
                data = load_teacher_attendance(
                    school_id,
                    attendance_date_str,
                )
            else:
                data = {'instances': [], 'new_instances': []}
        except ValueError:
            data = {'instances': [], 'new_instances': []}

        return data

@require_POST
@group_required("ALP_SCHOOL")
def save_attendance_teachers(request):
    if request.user.school_id is None:
        return HttpResponseBadRequest("No school assigned")

    body_unicode = request.body.decode("utf-8")

    if not body_unicode.strip():
        return HttpResponseBadRequest("Empty request body")

    try:
        data = json.loads(body_unicode)
    except ValueError:
        return HttpResponseBadRequest("Invalid JSON payload")

    try:
        result = create_teacher_attendance(data, request.user.school_id, request.user)
    except Exception:
        return HttpResponseBadRequest("Failed to save teacher attendance")

    return JsonResponse({"result": result})
