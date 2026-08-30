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

    re_path(r'^attendance/$', view=attendance_views.AttendanceView.as_view(), name='attendance_list'),
    re_path(r'^load-attendance-children/$', view=attendance_views.LoadAttendanceChildren.as_view(), name='load_attendance_children'),
    re_path(r'^save-attendance-children/$', view=attendance_views.save_attendance_children, name='save_attendance_children'),

    re_path(r'^teacher-attendance/$', view=attendance_views.TeacherAttendanceView.as_view(), name='teacher_attendance_list'),
    re_path(r'^load-attendance-teachers/$', view=attendance_views.LoadAttendanceTeachers.as_view(), name='load_attendance_teachers'),
    re_path(r'^save-attendance-teachers/$', view=attendance_views.save_attendance_teachers, name='save_attendance_teachers'),

    re_path(r'^grading/add/$', view=views.GradingAddView.as_view(), name='grading_add'),
    re_path(r'^grading/edit/(?P<pk>[\w.@+-]+)/$', view=views.GradingEditView.as_view(), name='grading_edit'),

    re_path(r'^school-profile/$', view=views.SchoolProfileView.as_view(), name='school_profile'),


    re_path(r'^dashboard/registration/$', view=views.ALPRegistrationDashboardView.as_view(), name='dashboard_registration'),
    re_path(r'^dashboard/teacher/$', view=views.ALPTeacherDashboardView.as_view(), name='dashboard_teacher'),
    re_path(r'^dashboard/attendance/$', view=views.ALPAttendanceDashboardView.as_view(), name='dashboard_attendance'),
    re_path(r'^dashboard/school/$', view=views.ALPSchoolDashboardView.as_view(), name='dashboard_school'),

    re_path(r'^alp_dashboard_data/$', view=views.ALPDashboardDataView.as_view(), name='alp_dashboard_data'),

    re_path(r'^landing-page/$', view=views.ALPLandingPage.as_view(), name='landing_page'),
]
