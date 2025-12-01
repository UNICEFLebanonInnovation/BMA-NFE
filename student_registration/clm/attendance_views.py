# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import json
from django.views.generic import ListView, TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from student_registration.users.templatetags.custom_tags import has_group
from braces.views import GroupRequiredMixin
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest, HttpResponseForbidden

from student_registration.attendances.models import CLMAttendance, CLMAttendanceStudent, CLMStudentAbsences, CLMStudentTotalAttendance
from student_registration.schools.models import (
    School,
    PartnerOrganization,
    CLMRound
)
from student_registration.clm.models import Bridging
from .utils import load_child_attendance, create_attendance


class AttendanceView(LoginRequiredMixin,
                     GroupRequiredMixin,
                     TemplateView):

    group_required = [u"CLM_ATTENDANCE"]
    template_name = 'clm/attendance.html'

    def get_context_data(self, **kwargs):
        """Build the context for the attendance landing page.

        Args:
            **kwargs: Optional template context overrides.

        Returns:
            dict: Context containing dates, school options, registration levels, and defaults for the attendance form.
        """
        from datetime import datetime
        from collections import OrderedDict
        clm_bridging_all = has_group(self.request.user, 'CLM_BRIDGING_ALL')
        is_staff = self.request.user.is_staff

        attendance_date = datetime.now().strftime('%m/%d/%Y')
        day_off = 'No'
        close_reason = ''
        rounds = CLMRound.objects.filter(current_year=True)

        school = School.objects.filter(is_closed=False).all()
        if clm_bridging_all or is_staff:
            school = School.objects.filter(is_closed=False).order_by('name')
        else:
            school_id = 0
            partner_id = 0

            if self.request.user.school:
                school_id = self.request.user.school.id
            if self.request.user.partner_id:
                partner_id = self.request.user.partner_id

            if school_id and school_id > 0:
                school = School.objects.filter(id=school_id).order_by('name')

            elif partner_id > 0:
                school = School.objects.filter(is_closed=False,
                                                 id__in=PartnerOrganization
                                                 .objects
                                                 .filter(id=partner_id)
                                                 .values_list('schools', flat=True)).order_by('name')
            else:
                school = school.none()

        # sorted_education_programs = sorted(education_programs, key=lambda x: x[1])
        # education_program_dict = OrderedDict(sorted_education_programs)

        registration_level_dict = OrderedDict((display, value) for value, display in Bridging.REGISTRATION_LEVEL if value)

        instance = CLMAttendance.objects.filter(id=1).last()
        #
        # instance = CLMAttendance.objects.filter(id=1,
        #                                          attendance_date=datetime.now()).last()

        if instance:
            day_off = instance.day_off
            close_reason = instance.close_reason

        return {
            'instance': instance,
            'attendance_date': attendance_date,
            'day_off': day_off,
            'close_reason': close_reason,
            'school': school,
            'registration_level': registration_level_dict,
            'round': rounds
        }


def save_attendance_children(request):
    """Persist attendance submissions coming from the client UI.

    Args:
        request (HttpRequest): Request carrying a JSON body with attendance payload.

    Returns:
        JsonResponse: Success flag or error details when validation fails.
    """

    body_unicode = request.body.decode('utf-8')

    if body_unicode.strip():
        try:
            data = json.loads(body_unicode)
            result = create_attendance(data)
            return JsonResponse({'result': result})
        except Exception as e:
            return JsonResponse({'error': 'Failed to save attendance.'}, status=500)
            # return JsonResponse({'error': 'Error processing attendance', 'details': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Empty request body'}, status=400)



class LoadAttendanceChildren(LoginRequiredMixin, TemplateView):
    template_name = 'clm/attendance_children.html'

    def get_context_data(self, **kwargs):
        """Load attendance records for the provided date and filters.

        Args:
            **kwargs: Additional template context values passed by Django.

        Returns:
            dict: Context including attendance instances or validation error messages.
        """
        from datetime import datetime
        current_date = datetime.today().date()

        attendance_date_str = self.request.GET.get("attendance_date")
        round_id = self.request.GET.get("round_id")
        school_id = self.request.GET.get("school_id")
        registration_level = self.request.GET.get("registration_level")

        if attendance_date_str is None:
            return {'instances': [], 'error_message': 'Attendance date is required.'}

        try:
            attendance_date = datetime.strptime(attendance_date_str, '%m/%d/%Y').date()

            working_day_names = School.objects.filter(id=school_id).values_list('working_days', flat=True).first()
            working_days_set = set(working_day_names)

            if attendance_date > current_date:
                return {'instances': [], 'error_message': 'Attendance date cannot be in the future.'}

            elif attendance_date.strftime('%A') not in working_days_set:
                return {'instances': [], 'error_message': 'Attendance date is not a working day.'}

            else:
                instances = load_child_attendance(round_id, attendance_date_str, school_id, registration_level)
                return {'instances': instances, 'error_message': None}

        except ValueError:
            return {'instances': [], 'error_message': 'Invalid date format. Please use MM/DD/YYYY.'}

        return context


class LoadAttendanceChild(LoginRequiredMixin,
                          TemplateView):

    template_name = 'mscc/child_attendance_month.html'

    def get_context_data(self, **kwargs):
        """Return monthly attendance totals for a single child.

        Args:
            **kwargs: Expected to include ``child`` path parameter representing the child ID.

        Returns:
            dict: Attendance records along with counts of attended and absent days for the month.
        """
        import calendar

        child_id = kwargs["child"]
        month = int(self.request.GET.get("month"))

        instances = CLMAttendanceStudent.objects.filter(child_id=child_id,
                                                       attendance_day__attendance_date__month=month)\
            .order_by('attendance_day__attendance_date')

        return {
            'instances': instances,
            'nbr_attended': instances.filter(attended='Yes').count(),
            'nbr_absent': instances.filter(attended='No').count(),
            'attendance_month': calendar.month_name[month]
        }
