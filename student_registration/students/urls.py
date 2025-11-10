from __future__ import absolute_import, unicode_literals

from django.urls import re_path

from . import views

app_name = 'students'

urlpatterns = [
    re_path(
        r'^teacher-list/$',
        view=views.TeacherListView.as_view(),
        name='teacher_list'
    ),
    re_path(
        r'^teacher-add/$',
        view=views.TeacherAddView.as_view(),
        name='teacher_add'
    ),
    re_path(
        r'^teacher-edit/(?P<pk>[\w.@+-]+)/$',
        view=views.TeacherEditView.as_view(),
        name='teacher_edit'
    ),
    re_path(
        r'^teacher-export/$',
        view=views.teacher_export_data,
        name='teacher_export'
    ),
    re_path(
        r'^teacher-delete/(?P<pk>[\w.@+-]+)/$',
        view=views.TeacherDeleteView.as_view(),
        name='teacher_delete'
    ),
]

