from __future__ import absolute_import, unicode_literals

from django.urls import re_path

from . import export_views

app_name = 'attendances'

urlpatterns = [
    # re_path(
    #     r'^attendance-absence/$',
    #     view=views.AttendanceAbsenceView.as_view(),
    #     name='attendance_absence'
    # ),
    # re_path(
    #     r'^absence-export/(?P<number_of_absences>[\w.@+-]+)/(?P<total_days>[\w.@+-]+)/$',
    #     view=views.absence_export,
    #     name='absence_export'
    # ),
    # re_path(
    #     r'^attendance-export/(?P<month>[\w.@+-]+)/(?P<year>[\w.@+-]+)/$',
    #     view=views.attendance_export,
    #     name='attendance_export'
    # ),
    # re_path(
    #     r'^total-attendance-export/(?P<round>[\w.@+-]+)/$',
    #     view=views.total_attendance_export,
    #     name='total_attendance_export'
    # ),
    # re_path(
    #     r'^consecutive-attendance-export/(?P<round>[\w.@+-]+)/$',
    #     view=views.consecutive_absence_export,
    #     name='consecutive_attendance_export'
    # ),
    # re_path(
    #     r'^mscc-attendance-export/(?P<month>[\w.@+-]+)/(?P<year>[\w.@+-]+)/(?P<education_program>[\w\s.@+-]*)/(?P<class_section>[\w\s.@+-]*)/(?P<partner>[\w\s.@+-]*)/(?P<center>[\w\s.@+-]*)/?$',
    #     view=views.mscc_attendance_export,
    #     name='mscc_attendance_export'
    # ),
    re_path(
        r'^mscc-attendance-export/(?P<month>[\w.@+-]+)/(?P<year>[\w.@+-]+)/(?P<education_program>[\w\s.@+-]*)/(?P<class_section>[\w\s.@+-]*)/(?P<partner>[\w\s.@+-]*)/(?P<center>[\w\s.@+-]*)/?$',
        view=export_views.mscc_attendance_export,
        name='mscc_attendance_export'
    ),

]
