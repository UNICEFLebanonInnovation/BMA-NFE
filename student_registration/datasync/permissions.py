# -*- coding: utf-8 -*-
"""Access control for the replication endpoint."""

from __future__ import unicode_literals, absolute_import, division

from django.conf import settings
from rest_framework.permissions import BasePermission


def sync_client_group():
    """Return the group name a service account must belong to."""
    return getattr(settings, 'DATASYNC_CLIENT_GROUP', 'DataSync')


class IsSyncClient(BasePermission):
    """Allow only the dedicated replication service account.

    The Compiler authenticates with a DRF token belonging to a user in the
    ``DATASYNC_CLIENT_GROUP`` group. Superusers are allowed as well so an
    administrator can replay a batch by hand while debugging.
    """

    message = 'This account is not allowed to push replication data.'

    def has_permission(self, request, view):
        user = getattr(request, 'user', None)
        if not user or not user.is_authenticated or not user.is_active:
            return False
        if user.is_superuser:
            return True
        return user.groups.filter(name=sync_client_group()).exists()
