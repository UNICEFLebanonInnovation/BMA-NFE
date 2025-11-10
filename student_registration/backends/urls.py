from __future__ import absolute_import, unicode_literals

from django.urls import re_path

from . import views

app_name = 'backends'

urlpatterns = [

    re_path(
        r'^files-list/$',
        view=views.ExporterListView.as_view(),
        name='files_list'
    ),
    re_path(
        r'^export-history-list/$',
        view=views.export_history_list,
        name='export_history_list'
    ),
]
