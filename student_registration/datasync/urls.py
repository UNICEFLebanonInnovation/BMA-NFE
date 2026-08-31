# -*- coding: utf-8 -*-
"""URLs for the replication endpoint."""

from __future__ import unicode_literals

from django.urls import re_path

from .api_views import SyncIngestView

app_name = 'datasync'

urlpatterns = [
    re_path(r'^events/$', SyncIngestView.as_view(), name='ingest'),
]
