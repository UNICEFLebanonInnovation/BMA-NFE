from __future__ import absolute_import, unicode_literals

from django.urls import re_path

from . import views

app_name = 'locations'

urlpatterns = [
    re_path(
        r'^center-add/$',
        view=views.CenterFormView.as_view(),
        name='center_add'
    ),
    re_path(
        r'^center-edit/(?P<pk>[\w.@+-]+)/$',
        view=views.CenterFormView.as_view(),
        name='center_edit'
    ),
    re_path(
        r'^center-list/$',
        view=views.CenterListView.as_view(),
        name='center_list'
    ),
    re_path(
        r'^export/$',
        view=views.export_data,
        name='export'
    ),
    re_path(
        r'^export-center-background/$',
        view=views.export_center_background,
        name='export_center_background'
    ),
    re_path(
        r'^center-profile/(?P<pk>[\w.@+-]+)/$',
        view=views.ProfileView.as_view(),
        name='center_profile'
    ),
    re_path(
        r'^program-staff-add/(?P<center_id>[\w.@+-]+)/$',
        view=views.ProgramStaffFormView.as_view(),
        name='program_staff_add'
    ),
    re_path(
        r'^program-staff-edit/(?P<center_id>[\w.@+-]+)/(?P<pk>[\w.@+-]+)/$',
        view=views.ProgramStaffFormView.as_view(),
        name='program_staff_edit'
    ),
    re_path(
        r'^program-staff-delete/(?P<pk>[\w.@+-]+)/$',
        view=views.program_staff_delete,
        name='program_staff_delete'
    ),
]
