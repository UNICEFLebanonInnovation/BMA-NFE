from __future__ import absolute_import, unicode_literals

from django.urls import re_path

from . import views

app_name = 'dashboard'

urlpatterns = [
    re_path(
        r'^chart-builder/$',
        view=views.ChartBuilderView.as_view(),
        name='chart_builder'
    ),
    re_path(
        r'^pivot-dashboard/$',
        view=views.PivotDashboardView.as_view(),
        name='pivot_dashboard'
    ),
    re_path(
        r'^pivot-data/$',
        view=views.pivot_data,
        name='pivot_data'
    ),
]
