# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.urls import re_path, include

from . import views

app_name = 'users'

urlpatterns = [
    # URL pattern for the UserDetailView
    re_path(
        r'^(?P<username>[\w.@+-]+)/$',
        view=views.UserDetailView.as_view(),
        name='detail'
    ),
    re_path(
        r'^set-language/(?P<language>[\w.@+-]+)/$',
        view=views.UserChangeLanguageRedirectView.as_view(),
        name='set_language'
    ),
    re_path(
        r'^partner',
        view=views.user_overview,
        name='profile'
    ),
]
