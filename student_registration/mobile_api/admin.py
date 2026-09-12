# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from prettyjson import PrettyJSONWidget
from django.db import models as db_models

from .models import MobileDevice, MobileSyncBatch, MobileSyncItem


class MobileSyncItemInline(admin.TabularInline):
    model = MobileSyncItem
    extra = 0
    can_delete = False
    fields = ('position', 'client_uuid', 'entity', 'op', 'status', 'server_id', 'message',
              'duplicate_override')
    readonly_fields = fields
    show_change_link = True


@admin.register(MobileDevice)
class MobileDeviceAdmin(admin.ModelAdmin):
    list_display = ('device_id', 'name', 'user', 'app_version', 'last_login', 'last_pull', 'last_push')
    search_fields = ('device_id', 'name', 'user__username')
    list_filter = ('app_version',)
    readonly_fields = ('created', 'modified')


@admin.register(MobileSyncBatch)
class MobileSyncBatchAdmin(admin.ModelAdmin):
    list_display = ('id', 'uuid', 'user', 'device', 'status', 'item_count', 'created')
    search_fields = ('uuid', 'user__username')
    list_filter = ('status', 'created')
    readonly_fields = ('uuid', 'user', 'device', 'app_version', 'status', 'item_count', 'summary',
                       'created', 'modified')
    inlines = [MobileSyncItemInline]
    formfield_overrides = {db_models.JSONField: {'widget': PrettyJSONWidget}}


@admin.register(MobileSyncItem)
class MobileSyncItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'batch', 'entity', 'op', 'status', 'server_id', 'client_uuid',
                    'duplicate_override', 'created')
    search_fields = ('client_uuid', 'entity', 'batch__uuid', 'batch__user__username')
    list_filter = ('status', 'entity', 'duplicate_override')
    readonly_fields = ('batch', 'position', 'client_uuid', 'entity', 'op', 'server_id', 'parent_uuid',
                       'parent_id', 'payload', 'resolution', 'status', 'message', 'errors', 'duplicates',
                       'result', 'duplicate_override', 'created', 'modified')
    formfield_overrides = {db_models.JSONField: {'widget': PrettyJSONWidget}}
