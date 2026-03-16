# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from django.contrib import admin

from .models import (
    MSCCAttendance,
    MSCCAttendanceChild,
    CLMStudentTotalAttendance,
    CLMAttendance,
    CLMAttendanceStudent,
    CLMStudentAbsences
)
from .forms import CLMAttendanceAdminForm


class CLMAttendanceAdmin(admin.ModelAdmin):
    form = CLMAttendanceAdminForm
    list_display = (
        'school',
        'registration_level',
        'attendance_date',
        'day_off',
        'close_reason'
    )
    list_filter = (
        'school',
        'registration_level',
        'attendance_date',
        'day_off'
    )
    search_fields = (
        'school__name',
        'school__number',
        'registration_level',
        'attendance_date'
    )


class CLMAttendanceStudentAdmin(admin.ModelAdmin):
    list_display = (
        'student',
        'attendance_day',
        'attended',
        'absence_reason',
        'absence_reason_other'
    )
    list_filter = (
        'attended',
    )
    search_fields = (
        'student__first_name',
        'student__father_name',
        'student__last_name',
    )


class CLMStudentTotalAttendanceAdmin(admin.ModelAdmin):
    list_display = (
        'student_id',
        'registration_id',
        'round_id',
        'student_first_name',
        'student_father_name',
        'student_last_name',
        'school_name',
        'registation_level',
        'total_attendance_days',
        'total_absence_days'
    )
    list_filter = (
        'student_id',
        'registration_id',
        'round_id',
        'school_name',
        'registation_level'
    )
    search_fields = (
        'student_first_name',
        'student_father_name',
        'student_last_name',
    )


class CLMStudentAbsencesAdmin(admin.ModelAdmin):
    list_display = (
        'student_id',
        'registration_id',
        'round_id',
        'student_first_name',
        'student_father_name',
        'student_last_name',
        'school_name',
        'registation_level',
        'absence_starting_date',
        'absence_ending_date',
        'absence_dates',
        'consecutive_absence_days',
    )
    list_filter = (
        'student_id',
        'registration_id',
        'round_id',
        'school_name',
        'registation_level'
    )
    search_fields = (
        'student_first_name',
        'student_father_name',
        'student_last_name',
    )


class MSCCAttendanceAdmin(admin.ModelAdmin):
    list_display = (
        'center',
        'attendance_date',
        'day_off',
        'close_reason',
        'education_program',
        'class_section'
    )
    list_filter = (
        'center',
        'attendance_date',
        'day_off',
        'education_program',
        'class_section'
    )


class MSCCAttendanceChildAdmin(admin.ModelAdmin):
    list_display = (
        'child',
        'attendance_day',
        'attended',
        'absence_reason',
        'absence_reason_other'
    )
    list_filter = (
        'attended',
    )
    search_fields = (
        'child__first_name',
        'child__father_name',
        'child__last_name',
    )


# admin.site.register(CLMAttendance, CLMAttendanceAdmin)
# admin.site.register(CLMAttendanceStudent, CLMAttendanceStudentAdmin)
# admin.site.register(CLMStudentTotalAttendance, CLMStudentTotalAttendanceAdmin)
# admin.site.register(CLMStudentAbsences, CLMStudentAbsencesAdmin)
admin.site.register(MSCCAttendance, MSCCAttendanceAdmin)
admin.site.register(MSCCAttendanceChild, MSCCAttendanceChildAdmin)


