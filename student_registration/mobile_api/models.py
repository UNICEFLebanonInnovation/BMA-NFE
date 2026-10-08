# -*- coding: utf-8 -*-
"""Audit-trail models for the mobile synchronisation API.

Every push from a device is stored as a ``MobileSyncBatch`` with one
``MobileSyncItem`` per record, so supervisors can review what was uploaded,
what was rejected as a duplicate and how the field worker resolved it.
"""
from __future__ import unicode_literals

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from model_utils.models import TimeStampedModel


class MobileDevice(TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='mobile_devices',
        on_delete=models.CASCADE,
        verbose_name=_('User'),
    )
    device_id = models.CharField(_('Device id'), max_length=128, db_index=True)
    name = models.CharField(_('Device name'), max_length=255, blank=True, default='')
    app_version = models.CharField(_('App version'), max_length=64, blank=True, default='')
    last_login = models.DateTimeField(_('Last login'), null=True, blank=True)
    last_pull = models.DateTimeField(_('Last pull'), null=True, blank=True)
    last_push = models.DateTimeField(_('Last push'), null=True, blank=True)

    class Meta:
        verbose_name = _('Mobile device')
        verbose_name_plural = _('Mobile devices')
        unique_together = ('user', 'device_id')
        ordering = ['-modified']

    def __str__(self):
        return '{} ({})'.format(self.name or self.device_id, self.user)


class MobileSyncBatch(TimeStampedModel):
    STATUS_PROCESSING = 'processing'
    STATUS_COMPLETED = 'completed'
    STATUS_FAILED = 'failed'
    STATUS = (
        (STATUS_PROCESSING, _('Processing')),
        (STATUS_COMPLETED, _('Completed')),
        (STATUS_FAILED, _('Failed')),
    )

    uuid = models.CharField(_('Batch uuid'), max_length=64, unique=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='mobile_sync_batches',
        on_delete=models.CASCADE,
        verbose_name=_('User'),
    )
    device = models.ForeignKey(
        MobileDevice,
        related_name='sync_batches',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        verbose_name=_('Device'),
    )
    app_version = models.CharField(_('App version'), max_length=64, blank=True, default='')
    status = models.CharField(_('Status'), max_length=16, choices=STATUS, default=STATUS_PROCESSING)
    item_count = models.PositiveIntegerField(_('Items'), default=0)
    summary = models.JSONField(_('Summary'), default=dict, blank=True)

    class Meta:
        verbose_name = _('Mobile sync batch')
        verbose_name_plural = _('Mobile sync batches')
        ordering = ['-created']

    def __str__(self):
        return 'Batch {} by {}'.format(self.pk, self.user)


class MobileSyncItem(TimeStampedModel):
    STATUS_PENDING = 'pending'
    STATUS_CREATED = 'created'
    STATUS_UPDATED = 'updated'
    STATUS_MERGED = 'merged'
    STATUS_LINKED = 'linked'
    STATUS_DUPLICATE = 'duplicate'
    STATUS_CONFLICT = 'conflict'
    STATUS_ERROR = 'error'
    STATUS_DISCARDED = 'discarded'
    STATUS_SKIPPED = 'skipped'
    STATUS_DELETED = 'deleted'
    STATUS = (
        (STATUS_PENDING, _('Pending')),
        (STATUS_CREATED, _('Created')),
        (STATUS_UPDATED, _('Updated')),
        (STATUS_MERGED, _('Merged')),
        (STATUS_LINKED, _('Linked')),
        (STATUS_DUPLICATE, _('Duplicate')),
        (STATUS_CONFLICT, _('Conflict')),
        (STATUS_ERROR, _('Error')),
        (STATUS_DISCARDED, _('Discarded')),
        (STATUS_SKIPPED, _('Skipped')),
        (STATUS_DELETED, _('Deleted')),
    )

    batch = models.ForeignKey(
        MobileSyncBatch,
        related_name='items',
        on_delete=models.CASCADE,
        verbose_name=_('Batch'),
    )
    position = models.PositiveIntegerField(_('Position'), default=0)
    client_uuid = models.CharField(_('Client uuid'), max_length=64, db_index=True)
    entity = models.CharField(_('Entity'), max_length=64, db_index=True)
    op = models.CharField(_('Operation'), max_length=16, default='create')
    server_id = models.IntegerField(_('Server id'), null=True, blank=True)
    parent_uuid = models.CharField(_('Parent uuid'), max_length=64, blank=True, default='')
    parent_id = models.IntegerField(_('Parent id'), null=True, blank=True)
    payload = models.JSONField(_('Payload'), default=dict, blank=True)
    resolution = models.JSONField(_('Resolution'), null=True, blank=True)
    status = models.CharField(_('Status'), max_length=16, choices=STATUS, default=STATUS_PENDING)
    message = models.TextField(_('Message'), blank=True, default='')
    errors = models.JSONField(_('Errors'), default=dict, blank=True)
    duplicates = models.JSONField(_('Duplicates'), default=list, blank=True)
    result = models.JSONField(_('Result'), null=True, blank=True)
    duplicate_override = models.BooleanField(_('Duplicate override'), default=False)

    class Meta:
        verbose_name = _('Mobile sync item')
        verbose_name_plural = _('Mobile sync items')
        unique_together = ('batch', 'client_uuid')
        ordering = ['batch', 'position']

    def __str__(self):
        return '{} {} ({})'.format(self.entity, self.client_uuid, self.status)

    def to_report(self):
        data = {
            'client_uuid': self.client_uuid,
            'entity': self.entity,
            'op': self.op,
            'status': self.status,
            'server_id': self.server_id,
            'parent_id': self.parent_id,
            'message': self.message,
            'errors': self.errors or {},
            'duplicates': self.duplicates or [],
        }
        if self.result:
            data.update(self.result)
        return data
