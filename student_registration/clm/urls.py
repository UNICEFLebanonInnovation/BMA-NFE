from __future__ import absolute_import, unicode_literals

from django.urls import re_path

from . import views, attendance_views, bridging_views

app_name = 'clm'

urlpatterns = [

    re_path(
        r'^search-clm-child/$',
        bridging_views.search_clm_child,
        name='search_clm_child'
    ),
    re_path(
        r'^bridging-add/$',
        view=bridging_views.BridgingAddView.as_view(),
        name='bridging_add'
    ),
    re_path(
        r'^bridging-edit/(?P<pk>[\w.@+-]+)/$',
        view=bridging_views.BridgingEditView.as_view(),
        name='bridging_edit'
    ),
    re_path(
        r'^bridging-post-assessment/(?P<pk>[\w.@+-]+)/$',
        view=bridging_views.BridgingPostAssessmentView.as_view(),
        name='bridging_post_assessment'
    ),
    re_path(
        r'^bridging-mid-assessment/(?P<pk>[\w.@+-]+)/(?P<number>[\w.@+-]+)/$',
        view=bridging_views.BridgingMidAssessmentView.as_view(),
        name='bridging_mid_assessment'
    ),
    re_path(
        r'^bridging-followup/(?P<pk>[\w.@+-]+)/$',
        view=bridging_views.BridgingFollowupView.as_view(),
        name='bridging_followup'
    ),
    re_path(
        r'^bridging-service/(?P<pk>[\w.@+-]+)/$',
        view=bridging_views.BridgingServiceView.as_view(),
        name='bridging_service'
    ),
    re_path(
        r'^bridging-export/(?P<round>[\w.@+-]+)/$',
        view=bridging_views.bridging_export_data,
        name='bridging_export'
    ),
    re_path(
        r'^bridging-export-all/$',
        view=bridging_views.bridging_export_all,
        name='bridging_export_all'
    ),
    re_path(
        r'^bridging-school-export-data/(?P<school_id>[\w.@+-]+)/$',
        view=bridging_views.bridging_school_export,
        name='bridging_school_export_data'
    ),
    re_path(
        r'^bridging-list/$',
        view=bridging_views.BridgingListView.as_view(),
        name='bridging_list'
    ),
    re_path(
        r'^bridging-page/$',
        view=bridging_views.BridgingPage.as_view(),
        name='bridging_page'
    ),
    re_path(
        r'^bridging-attendance-report/$',
        bridging_views.BridgingAttendanceReport.as_view(),
        name='bridging_attendance_report'
    ),
    re_path(
        r'^bridging-delete/(?P<pk>[\w.@+-]+)/$',
        view=bridging_views.bridging_mark_delete_view,
        name='bridging_delete'
    ),
    re_path(
        r'^attendance/$',
        view=attendance_views.AttendanceView.as_view(),
        name='attendance'
    ),
    re_path(
        r'^load-attendance-children/$',
        view=attendance_views.LoadAttendanceChildren.as_view(),
        name='load_attendance_children'
    ),
    re_path(
        r'^save-attendance-children/$',
        view=attendance_views.save_attendance_children,
        name='save_attendance_children'
    ),
    re_path(
        r'^attendance-child/(?P<child>[\w.@+-]+)/$',
        view=attendance_views.LoadAttendanceChild.as_view(),
        name='attendance_child'
    ),
    re_path(
        r'^dashboard/$',
        view=views.DashboardView.as_view(),
        name='dashboard'
    ),
]
