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
        r'^ajax/load-districts/$',
        view=views.load_districts,
        name='load_districts'
    ),
    re_path(
        r'^ajax/load-cadasters/$',
        view=views.load_cadasters,
        name='load_cadasters'
    ),
]
