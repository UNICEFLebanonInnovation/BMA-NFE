# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig


class DataSyncConfig(AppConfig):
    """Inbound replication of MSCC data from the Compiler."""

    name = 'student_registration.datasync'
    verbose_name = 'Data replication'
