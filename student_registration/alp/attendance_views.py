import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseBadRequest, JsonResponse
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView

from .models import ALPAttendance, ALPProgram, ALPRound
from .utils import (
    create_attendance,
    create_teacher_attendance,
    load_child_attendance,
    load_teacher_attendance,
    parse_date_flexible,
    user_has_alp_permission,
)
from .views import ALPUserRequiredMixin, _current_date

EMPTY_ATTENDANCE = {'instances': [], 'new_instances': []}


def _attendance_dates():
    today = _current_date()
    return today, today.strftime('%m/%d/%Y'), today.strftime('%Y-%m-%d')


def _requested_date(request):
    """Return the requested attendance day, or None when missing, invalid or in the future."""
    attendance_date = parse_date_flexible(request.GET.get('attendance_date'))
    if attendance_date is None:
        return None
    attendance_date = attendance_date.date()
    if attendance_date > _current_date():
        return None
    return attendance_date


class AttendanceView(LoginRequiredMixin, ALPUserRequiredMixin, TemplateView):
    template_name = 'alp/attendance.html'

    def get_context_data(self, **kwargs):
        school_id = self.request.user.school_id
        today, attendance_date, attendance_date_iso = _attendance_dates()
        day_off = 'No'
        close_reason = ''
        rounds = ALPRound.objects.filter(current_year=True)
        programmes = ALPProgram.objects.all()

        instance = None

        if school_id:
            instance = ALPAttendance.objects.filter(school_id=school_id,
                                                    attendance_date=today).last()

        if instance:
            day_off = instance.day_off or 'No'
            close_reason = instance.close_reason or ''

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
        school_id = self.request.user.school_id
        if _requested_date(self.request) is None or school_id is None:
            return dict(EMPTY_ATTENDANCE)

        return load_child_attendance(
            school_id,
            self.request.GET.get('round_id'),
            self.request.GET.get('attendance_date'),
            self.request.GET.get('programme'),
        )


def _attendance_write_guard(request):
    """Shared access checks for the JSON attendance endpoints."""
    if not request.user.is_authenticated:
        return redirect_to_login(request.get_full_path())
    if request.user.is_superuser or not user_has_alp_permission(request.user):
        raise PermissionDenied("Only ALP school users can record attendance.")
    if request.user.school_id is None:
        return HttpResponseBadRequest("No school assigned")
    return None


def _json_body(request):
    body_unicode = request.body.decode("utf-8")

    if not body_unicode.strip():
        return None, HttpResponseBadRequest("Empty request body")

    try:
        data = json.loads(body_unicode)
    except ValueError:
        return None, HttpResponseBadRequest("Invalid JSON payload")

    if not isinstance(data, dict):
        return None, HttpResponseBadRequest("Invalid JSON payload")

    return data, None


@require_POST
def save_attendance_children(request):
    denied = _attendance_write_guard(request)
    if denied is not None:
        return denied

    data, error = _json_body(request)
    if error is not None:
        return error

    if not create_attendance(data, request.user.school_id):
        return JsonResponse(
            {'result': False,
             'error': 'Attendance could not be saved. Check the date, programme and round.'},
            status=400,
        )

    return JsonResponse({"result": True})


class TeacherAttendanceView(LoginRequiredMixin, ALPUserRequiredMixin, TemplateView):
    template_name = 'alp/teacher_attendance.html'

    def get_context_data(self, **kwargs):
        today, attendance_date, attendance_date_iso = _attendance_dates()

        return {
            'attendance_date': attendance_date,
            'attendance_date_iso': attendance_date_iso,
        }


class LoadAttendanceTeachers(LoginRequiredMixin, ALPUserRequiredMixin, TemplateView):
    template_name = 'alp/teacher_attendance_list_partial.html'

    def get_context_data(self, **kwargs):
        school_id = self.request.user.school_id
        if _requested_date(self.request) is None or school_id is None:
            return dict(EMPTY_ATTENDANCE)

        return load_teacher_attendance(
            school_id,
            self.request.GET.get('attendance_date'),
        )


@require_POST
def save_attendance_teachers(request):
    denied = _attendance_write_guard(request)
    if denied is not None:
        return denied

    data, error = _json_body(request)
    if error is not None:
        return error

    if not create_teacher_attendance(data, request.user.school_id, request.user):
        return JsonResponse(
            {'result': False, 'error': 'Teacher attendance could not be saved. Check the date.'},
            status=400,
        )

    return JsonResponse({"result": True})
