from __future__ import absolute_import, unicode_literals
from django.urls import re_path
from . import export_views

app_name = 'attendances'

urlpatterns = [
    re_path(
        r'^mscc-attendance-export/(?P<month>[\w.@+-]+)/(?P<year>[\w.@+-]+)/(?P<education_program>[\w\s.@+-]*)/(?P<class_section>[\w\s.@+-]*)/(?P<partner>[\w\s.@+-]*)/(?P<center>[\w\s.@+-]*)/?$',
        view=export_views.mscc_attendance_export,
        name='mscc_attendance_export'
    ),
    re_path(
        r'^mscc-total-attendance-export/(?P<month>[\w.@+-]+)/(?P<year>[\w.@+-]+)/(?P<education_program>[\w\s.@+-]*)/(?P<class_section>[\w\s.@+-]*)/(?P<partner>[\w\s.@+-]*)/(?P<center>[\w\s.@+-]*)/?$',
        view=export_views.mscc_total_attendance_export,
        name='mscc_total_attendance_export'
    ),
]