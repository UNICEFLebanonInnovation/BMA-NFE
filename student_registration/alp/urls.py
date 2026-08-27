from __future__ import absolute_import, unicode_literals

from django.urls import re_path

from . import views, attendance_views

app_name = 'alp'

urlpatterns = [
    re_path(r'^registrations/$', view=views.RegistrationListView.as_view(), name='registration_list'),
    re_path(r'^registrations/add/$', view=views.RegistrationAddView.as_view(), name='registration_add'),
    re_path(r'^registrations/edit/(?P<pk>[\w.@+-]+)/$', view=views.RegistrationEditView.as_view(), name='registration_edit'),
    re_path(r'^registrations/delete/(?P<pk>[\w.@+-]+)/$', view=views.RegistrationDeleteView.as_view(), name='registration_delete'),
    re_path(r'^child-profile/(?P<pk>[\w.@+-]+)/$', view=views.ChildProfileView.as_view(), name='child_profile'),

    re_path(r'^teachers/$', view=views.TeacherListView.as_view(), name='teacher_list'),
    re_path(r'^teachers/add/$', view=views.TeacherAddView.as_view(), name='teacher_add'),
    re_path(r'^teachers/edit/(?P<pk>[\w.@+-]+)/$', view=views.TeacherEditView.as_view(), name='teacher_edit'),
    re_path(r'^teachers/delete/(?P<pk>[\w.@+-]+)/$', view=views.TeacherDeleteView.as_view(), name='teacher_delete'),

    re_path(r'^attendance/$', view=attendance_views.AttendanceListView.as_view(), name='attendance_list'),
    re_path(r'^attendance/add/$', view=attendance_views.AttendanceAddView.as_view(), name='attendance_add'),
    re_path(r'^attendance/edit/(?P<pk>[\w.@+-]+)/$', view=attendance_views.AttendanceEditView.as_view(), name='attendance_edit'),

    re_path(r'^teacher-attendance/$', view=attendance_views.TeacherAttendanceListView.as_view(), name='teacher_attendance_list'),
    re_path(r'^teacher-attendance/add/$', view=attendance_views.TeacherAttendanceAddView.as_view(), name='teacher_attendance_add'),
    re_path(r'^teacher-attendance/edit/(?P<pk>[\w.@+-]+)/$', view=attendance_views.TeacherAttendanceEditView.as_view(), name='teacher_attendance_edit'),

    re_path(r'^grading/add/$', view=views.GradingAddView.as_view(), name='grading_add'),
    re_path(r'^grading/edit/(?P<pk>[\w.@+-]+)/$', view=views.GradingEditView.as_view(), name='grading_edit'),

    re_path(r'^school-profile/$', view=views.SchoolProfileView.as_view(), name='school_profile'),
]
