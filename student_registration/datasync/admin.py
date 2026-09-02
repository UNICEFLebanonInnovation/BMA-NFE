# -*- coding: utf-8 -*-
"""Admin screens for monitoring the replication feed.

Everything here is read-only apart from acknowledging a conflict: these tables
describe what the Compiler sent, and editing them by hand would only make the
two databases disagree about what has already been applied.
"""

from __future__ import unicode_literals, absolute_import, division

from django.contrib import admin

from .models import SyncConflict, SyncedRecord, SyncEventLog


class ReadOnlyAdmin(admin.ModelAdmin):
    """Base admin that allows viewing and deleting but not editing."""

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(SyncedRecord)
class SyncedRecordAdmin(ReadOnlyAdmin):
    list_display = (
        'resource', 'source_id', 'object_id', 'source_system',
        'deleted', 'modified',
    )
    list_filter = ('resource', 'source_system', 'deleted')
    search_fields = ('source_id', 'object_id')
    date_hierarchy = 'modified'


@admin.register(SyncEventLog)
class SyncEventLogAdmin(ReadOnlyAdmin):
    list_display = (
        'received', 'resource', 'source_id', 'operation', 'status', 'short_detail',
    )
    list_filter = ('status', 'resource', 'operation', 'source_system')
    search_fields = ('event_id', 'source_id', 'detail')
    date_hierarchy = 'received'

    @admin.display(description='Detail')
    def short_detail(self, obj):
        """Return the first line of the detail, trimmed for the changelist."""
        detail = (obj.detail or '').strip()
        return detail[:120] + ('...' if len(detail) > 120 else '')


@admin.register(SyncConflict)
class SyncConflictAdmin(admin.ModelAdmin):
    """Local edits that an incoming Compiler update overwrote."""

    list_display = ('detected', 'resource', 'source_id', 'field_count', 'acknowledged')
    list_filter = ('acknowledged', 'resource')
    search_fields = ('source_id', 'event_id')
    date_hierarchy = 'detected'
    actions = ('mark_acknowledged',)
    readonly_fields = (
        'synced_record', 'event_id', 'resource', 'source_id',
        'diverged_fields', 'detected',
    )

    def has_add_permission(self, request):
        return False

    @admin.display(description='Overwritten fields')
    def field_count(self, obj):
        """Return how many fields the incoming update overwrote."""
        return len(obj.diverged_fields or {})

    @admin.action(description='Mark selected conflicts as reviewed')
    def mark_acknowledged(self, request, queryset):
        """Flag the selected conflicts as reviewed by an operator."""
        updated = queryset.update(acknowledged=True)
        self.message_user(request, '{} conflict(s) marked as reviewed.'.format(updated))
