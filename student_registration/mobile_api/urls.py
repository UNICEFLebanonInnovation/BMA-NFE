# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.urls import re_path

from . import views

app_name = 'mobile_api'

urlpatterns = [
    re_path(r'^auth/login/$', views.LoginView.as_view(), name='login'),
    re_path(r'^auth/logout/$', views.LogoutView.as_view(), name='logout'),
    re_path(r'^me/$', views.MeView.as_view(), name='me'),
    re_path(r'^bootstrap/$', views.BootstrapView.as_view(), name='bootstrap'),
    re_path(r'^pull/$', views.PullView.as_view(), name='pull'),
    re_path(r'^push/$', views.PushView.as_view(), name='push'),
    re_path(r'^push/history/$', views.PushHistoryView.as_view(), name='push_history'),
    re_path(r'^push/(?P<batch_id>\d+)/$', views.PushBatchView.as_view(), name='push_batch'),
    re_path(r'^duplicates/check/$', views.DuplicateCheckView.as_view(), name='duplicate_check'),
]
