# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.urls import re_path, include

from . import views

app_name = 'users'

urlpatterns = [
    # Before the username pattern, which would otherwise swallow it.
    # users/user_detail.html and users/user_form.html both link to
    # `users:update`, but the route was never added, so opening a user's profile
    # raised NoReverseMatch and returned 500.
    re_path(
        r'^~update/$',
        view=views.UserUpdateView.as_view(),
        name='update'
    ),
    re_path(
        r'^~redirect/$',
        view=views.UserRedirectView.as_view(),
        name='redirect'
    ),
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
