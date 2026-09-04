# -*- coding: utf-8 -*-
"""Bookkeeping models for data replicated in from the Compiler.

Three concerns are stored here:

``SyncedRecord``
    Maps a Compiler primary key to the local object it produced, and keeps a
    snapshot of the values that were last written by the sync. That snapshot
    is what lets us notice a BMA-NFE user edited a replicated record.

``SyncEventLog``
    An append-only log of every event received, keyed by the producer's
    ``event_id`` so a redelivered event is recognised and skipped.

``SyncConflict``
    Raised whenever an incoming update overwrites a record that had been
    edited locally since the previous sync. The Compiler always wins, but the
    overwrite is recorded here for review.
"""

from __future__ import unicode_literals, absolute_import, division

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import JSONField
from django.utils.translation import gettext as _

from model_utils.models import TimeStampedModel

from .constants import (
    OPERATIONS,
    RESOURCE_LABELS,
    SOURCE_SYSTEM_COMPILER,
)

EVENT_STATUS = (
    ('applied', _('Applied')),
    ('skipped', _('Skipped')),
    ('failed', _('Failed')),
)


class SyncedRecord(TimeStampedModel):
    """Link between a Compiler record and the local object replicating it."""

    source_system = models.CharField(
        max_length=50,
        default=SOURCE_SYSTEM_COMPILER,
        db_index=True,
        verbose_name=_('Source system')
    )
    resource = models.CharField(
        max_length=100,
        choices=RESOURCE_LABELS,
        db_index=True,
        verbose_name=_('Resource')
    )
    source_id = models.CharField(
        max_length=64,
        db_index=True,
        verbose_name=_('Source primary key')
    )
    content_type = models.ForeignKey(
        ContentType,
        blank=True, null=True,
        on_delete=models.CASCADE,
        verbose_name=_('Local model')
    )
    object_id = models.PositiveIntegerField(
        blank=True, null=True,
        verbose_name=_('Local primary key')
    )
    local_object = GenericForeignKey('content_type', 'object_id')

    last_event_id = models.UUIDField(
        blank=True, null=True,
        verbose_name=_('Last event applied')
    )
    last_source_modified = models.DateTimeField(
        blank=True, null=True,
        verbose_name=_('Source modified at')
    )
    last_applied_snapshot = JSONField(
        default=dict, blank=True,
        verbose_name=_('Values written by the last sync')
    )
    local_fingerprint = models.CharField(
        max_length=64,
        blank=True, null=True,
        verbose_name=_('Fingerprint of the last sync write')
    )
    deleted = models.BooleanField(
        default=False,
        verbose_name=_('Deleted upstream')
    )

    class Meta:
        ordering = ['-modified']
        unique_together = ('source_system', 'resource', 'source_id')
        indexes = [
            models.Index(fields=['resource', 'source_id']),
            models.Index(fields=['content_type', 'object_id']),
        ]
        verbose_name = _('Synced record')
        verbose_name_plural = _('Synced records')

    def __str__(self):
        return '{}#{} -> {}'.format(self.resource, self.source_id, self.object_id)


class SyncEventLog(models.Model):
    """One row per event received, kept for idempotency and audit."""

    event_id = models.UUIDField(
        unique=True,
        verbose_name=_('Event id')
    )
    source_system = models.CharField(
        max_length=50,
        default=SOURCE_SYSTEM_COMPILER,
        db_index=True,
        verbose_name=_('Source system')
    )
    resource = models.CharField(
        max_length=100,
        choices=RESOURCE_LABELS,
        db_index=True,
        verbose_name=_('Resource')
    )
    source_id = models.CharField(
        max_length=64,
        db_index=True,
        verbose_name=_('Source primary key')
    )
    operation = models.CharField(
        max_length=20,
        choices=OPERATIONS,
        verbose_name=_('Operation')
    )
    status = models.CharField(
        max_length=20,
        choices=EVENT_STATUS,
        db_index=True,
        verbose_name=_('Status')
    )
    detail = models.TextField(
        blank=True, null=True,
        verbose_name=_('Detail')
    )
    ignored_fields = JSONField(
        default=list, blank=True,
        verbose_name=_('Fields the local model does not have')
    )
    payload = JSONField(
        default=dict, blank=True,
        verbose_name=_('Payload')
    )
    received = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name=_('Received at')
    )

    class Meta:
        ordering = ['-received']
        verbose_name = _('Sync event')
        verbose_name_plural = _('Sync events')

    def __str__(self):
        return '{} {}#{} ({})'.format(
            self.operation, self.resource, self.source_id, self.status
        )


class SyncConflict(models.Model):
    """An incoming update that overwrote locally modified values.

    The Compiler is the system of record, so the overwrite always goes
    through. This row records what was lost so the change can be re-applied
    upstream if it mattered.
    """

    synced_record = models.ForeignKey(
        SyncedRecord,
        related_name='conflicts',
        on_delete=models.CASCADE,
        verbose_name=_('Synced record')
    )
    event_id = models.UUIDField(
        blank=True, null=True,
        verbose_name=_('Event id')
    )
    resource = models.CharField(
        max_length=100,
        choices=RESOURCE_LABELS,
        db_index=True,
        verbose_name=_('Resource')
    )
    source_id = models.CharField(
        max_length=64,
        db_index=True,
        verbose_name=_('Source primary key')
    )
    diverged_fields = JSONField(
        default=dict, blank=True,
        verbose_name=_('Overwritten values')
    )
    acknowledged = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name=_('Reviewed')
    )
    detected = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name=_('Detected at')
    )

    class Meta:
        ordering = ['-detected']
        verbose_name = _('Sync conflict')
        verbose_name_plural = _('Sync conflicts')

    def __str__(self):
        return '{}#{} ({} field(s))'.format(
            self.resource, self.source_id, len(self.diverged_fields or {})
        )
