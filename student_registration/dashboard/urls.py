from __future__ import absolute_import, unicode_literals

from django.urls import re_path

from . import views

app_name = 'dashboard'

urlpatterns = [
    re_path(r'^chart-builder/$', view=views.ChartBuilderView.as_view(), name='chart_builder'),
    re_path(r'^pivot-dashboard/$', view=views.PivotDashboardView.as_view(), name='pivot_dashboard'),
    re_path(r'^pivot-data/$', view=views.pivot_data, name='pivot_data'),

    re_path(r'^advanced-analytics/$', view=views.AdvancedAnalyticsDashboardView.as_view(), name='advanced_analytics'),
    re_path(r'^api/analytics/summary/$', view=views.analytics_summary, name='analytics_summary'),
    re_path(r'^api/analytics/trend/$', view=views.analytics_trend, name='analytics_trend'),
    re_path(r'^api/analytics/breakdown/$', view=views.analytics_breakdown, name='analytics_breakdown'),
    re_path(r'^api/analytics/crosstab/$', view=views.analytics_crosstab, name='analytics_crosstab'),
    re_path(r'^api/analytics/export.csv$', view=views.analytics_export_csv, name='analytics_export_csv'),

    re_path(r'^centers-map/$', view=views.CentersMapView.as_view(), name='centers_map'),
    re_path(r'^api/centers-geo-data/$', view=views.centers_geo_data, name='centers_geo_data'),
]

# Added for Advanced Exporter
from .advanced_exporter_views import AdvancedExporterDashboardView, queue_advanced_export
urlpatterns += [
    re_path(r'^advanced-exporter/$', view=AdvancedExporterDashboardView.as_view(), name='advanced_exporter'),
    re_path(r'^api/queue-advanced-export/$', view=queue_advanced_export, name='queue_advanced_export'),
]

urlpatterns += [
    re_path(r'^wiki/(?P<page_name>[\w\-]+)/$', view=views.WikiPageView.as_view(), name='wiki_page'),
    re_path(r'^wiki/$', views.WikiPageView.as_view(), {'page_name': 'index'}, name='wiki_index'),
]
