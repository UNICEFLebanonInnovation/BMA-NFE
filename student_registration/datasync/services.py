# -*- coding: utf-8 -*-
"""Orchestration for a batch of events pushed by the Compiler.

:func:`ingest_events` is the single entry point used by the API view and by
the tests. It sorts the batch into dependency order, applies each event in its
own transaction, and returns a per-event result the producer stores against
its outbox rows.

Each event is independent: one bad record never blocks the rest of the batch,
and an event whose parent has not arrived yet comes back marked retryable so
the producer sends it again instead of dropping it.
"""

from __future__ import unicode_literals, absolute_import, division

import logging
import uuid

from django.db import OperationalError, transaction

from .appliers import UnresolvedDependency, apply_event
from .constants import (
    OPERATION_DELETE,
    OPERATION_UPSERT,
    RESOURCE_ORDER,
    STATUS_APPLIED,
    STATUS_FAILED,
    STATUS_SKIPPED,
    resource_sort_key,
)
from .models import SyncEventLog
from .identity import StaleEvent, normalize_bma_id, source_timestamp
from .photos import PhotoUploadRequired

logger = logging.getLogger(__name__)

REQUIRED_EVENT_KEYS = ('event_id', 'resource', 'operation', 'source_id')


class EnvelopeError(Exception):
    """The batch itself is malformed and cannot be processed at all."""


def _validate_event(event):
    """Return an error string for ``event``, or ``None`` when it is usable."""
    if not isinstance(event, dict):
        return 'event must be an object'
    missing = [key for key in REQUIRED_EVENT_KEYS if not event.get(key)]
    if missing:
        return 'missing required key(s): {}'.format(', '.join(missing))
    if event['resource'] not in RESOURCE_ORDER:
        return 'unknown resource "{}"'.format(event['resource'])
    if event['operation'] not in (OPERATION_UPSERT, OPERATION_DELETE):
        return 'unknown operation "{}"'.format(event['operation'])
    try:
        normalize_bma_id(event['source_id'])
        uuid.UUID(str(event['event_id']))
        source_timestamp(event.get('source_modified'))
        if not isinstance(event.get('payload', {}), dict):
            return 'payload must be an object'
    except ValueError as error:
        return str(error)
    return None


def _result(event, status, detail='', local_id=None, conflict=False,
            retryable=False, ignored_fields=None):
    """Build one entry of the response ``results`` list."""
    return {
        'event_id': str(event.get('event_id') or ''),
        'resource': event.get('resource'),
        'source_id': event.get('source_id'),
        'status': status,
        'detail': detail,
        'local_id': local_id,
        'conflict': conflict,
        'retryable': retryable,
        'ignored_fields': ignored_fields or [],
    }


def _already_applied(event_id):
    """Return the previous log row for ``event_id``, if the event was seen."""
    return SyncEventLog.objects.filter(event_id=event_id).first()


def _log_event(event, source_system, status, detail, ignored_fields, applied_result=None):
    """Record the outcome of an event, tolerating a duplicate event id."""
    # A late failed attempt must not replace another delivery's committed result.
    with transaction.atomic():
        SyncEventLog.objects.get_or_create(
            event_id=event['event_id'],
            defaults={'source_system': source_system, 'resource': event['resource'],
                      'source_id': str(event['source_id']),
                      'operation': event['operation'], 'status': STATUS_FAILED},
        )
        previous = SyncEventLog.objects.select_for_update().get(event_id=event['event_id'])
        if previous.status in (STATUS_APPLIED, STATUS_SKIPPED):
            return
        _write_event_log(event, source_system, status, detail, ignored_fields, applied_result)


def _write_event_log(event, source_system, status, detail, ignored_fields, applied_result=None):
    SyncEventLog.objects.update_or_create(
        event_id=event['event_id'],
        defaults={
            'source_system': source_system,
            'resource': event.get('resource') or '',
            'source_id': str(event.get('source_id') or ''),
            'operation': event.get('operation') or '',
            'status': status,
            'detail': detail or '',
            'ignored_fields': ignored_fields or [],
            'payload': event.get('payload') or {},
            'applied_result': applied_result or {},
        },
    )


def _replayed_result(event, previous):
    """Retries retain the original local ID, conflict flag and event notes."""
    from .models import SyncConflict, SyncedRecord
    cached = previous.applied_result or {}
    local_id = cached.get('local_id')
    if not cached:
        # Older logs have no receipt; recover only what their audit can prove.
        local_id = SyncedRecord.objects.filter(
            source_system=previous.source_system, resource=previous.resource,
            source_id=previous.source_id, last_event_id=previous.event_id,
        ).values_list('object_id', flat=True).first()
    conflict = bool(cached.get('conflict')) or SyncConflict.objects.filter(
        event_id=previous.event_id,
        synced_record__source_system=previous.source_system,
    ).exists()
    prefix = 'already applied' if previous.status == STATUS_APPLIED else 'already processed'
    detail = '; '.join(part for part in (prefix, cached.get('detail', previous.detail)) if part)
    return _result(event, STATUS_SKIPPED, detail=detail, local_id=local_id,
                   conflict=conflict,
                   ignored_fields=cached.get('ignored_fields', previous.ignored_fields))


def ingest_events(events, source_system, uploads=None):
    """Apply a batch of events and report what happened to each one.

    Args:
        events (list): Decoded event dictionaries from the request body.
        source_system (str): Producer identifier, already authorised.

    Returns:
        dict: ``{"applied": n, "skipped": n, "failed": n, "results": [...]}``.

    Raises:
        EnvelopeError: When ``events`` is not a list.
    """
    if not isinstance(events, list):
        raise EnvelopeError('"events" must be a list')

    ordered = sorted(
        enumerate(events),
        key=lambda pair: (
            resource_sort_key(pair[1].get('resource'))
            if isinstance(pair[1], dict) else len(RESOURCE_ORDER),
            pair[0],
        ),
    )

    results = []
    counts = {STATUS_APPLIED: 0, STATUS_SKIPPED: 0, STATUS_FAILED: 0}

    for _position, event in ordered:
        error = _validate_event(event)
        if error:
            results.append(_result(event if isinstance(event, dict) else {},
                                   STATUS_FAILED, detail=error))
            counts[STATUS_FAILED] += 1
            continue

        previous = _already_applied(event['event_id'])
        if previous is not None and previous.status in (STATUS_APPLIED, STATUS_SKIPPED):
            results.append(_replayed_result(event, previous))
            counts[STATUS_SKIPPED] += 1
            continue

        results.append(_apply_one(event, source_system, counts, uploads))

    return {
        'applied': counts[STATUS_APPLIED],
        'skipped': counts[STATUS_SKIPPED],
        'failed': counts[STATUS_FAILED],
        'results': results,
    }


def _apply_one(event, source_system, counts, uploads=None):
    """Apply a single validated event inside its own transaction."""
    saved_files = []
    committed = False
    try:
        with transaction.atomic():
            # Serialize repeated deliveries before either can mutate business rows.
            SyncEventLog.objects.get_or_create(
                event_id=event['event_id'],
                defaults={'source_system': source_system, 'resource': event['resource'],
                          'source_id': str(event['source_id']),
                          'operation': event['operation'], 'status': STATUS_FAILED},
            )
            previous = SyncEventLog.objects.select_for_update().get(event_id=event['event_id'])
            if previous.status in (STATUS_APPLIED, STATUS_SKIPPED):
                counts[STATUS_SKIPPED] += 1
                return _replayed_result(event, previous)
            _resource, outcome, notes = apply_event(event, source_system)
            from .photos import apply_registration_photo
            photo_note = apply_registration_photo(event, source_system, uploads, saved_files)
            notes = '; '.join(note for note in (notes, photo_note) if note)
            local_id = None
            conflict = False
            ignored = []
            if event['operation'] == OPERATION_DELETE:
                detail = notes or ('deleted' if outcome else 'nothing to delete')
            else:
                local_id = outcome.instance.pk if outcome.instance else None
                from .models import SyncConflict
                conflict = outcome.conflict or SyncConflict.objects.filter(
                    event_id=event['event_id'],
                    synced_record__source_system=source_system,
                ).exists()
                ignored = outcome.ignored_fields
                action = 'Created record in BMA-NFE' if outcome.created else 'Updated existing record in BMA-NFE'
                detail = '; '.join(part for part in (action, notes) if part)
            receipt = _result(event, STATUS_APPLIED, detail=detail, local_id=local_id,
                              conflict=conflict, ignored_fields=ignored)
            _log_event(event, source_system, STATUS_APPLIED, detail, ignored, receipt)
        committed = True
    except StaleEvent as error:
        detail = str(error)
        _log_event(event, source_system, STATUS_SKIPPED, detail, [])
        counts[STATUS_SKIPPED] += 1
        return _result(event, STATUS_SKIPPED, detail=detail)
    except PhotoUploadRequired as error:
        # Negotiation rolls back all metadata; the same event continues with
        # its image attached. This is not an applied event or a failed attempt.
        counts[STATUS_FAILED] += 1
        result = _result(event, STATUS_FAILED, detail=str(error), retryable=True)
        result['photo_upload_required'] = True
        return result
    except UnresolvedDependency as error:
        detail = str(error)
        _log_event(event, source_system, STATUS_FAILED, detail, [])
        counts[STATUS_FAILED] += 1
        logger.info('datasync: deferring %s#%s (%s)',
                    event.get('resource'), event.get('source_id'), detail)
        return _result(event, STATUS_FAILED, detail=detail, retryable=True)
    except OperationalError as error:
        detail = 'Temporary database failure: {}'.format(error)
        _log_event(event, source_system, STATUS_FAILED, detail, [])
        counts[STATUS_FAILED] += 1
        return _result(event, STATUS_FAILED, detail=detail, retryable=True)
    except Exception as error:  # noqa: BLE001 - one bad row must not stop the batch
        detail = '{}: {}'.format(error.__class__.__name__, error)
        _log_event(event, source_system, STATUS_FAILED, detail, [])
        counts[STATUS_FAILED] += 1
        logger.exception('datasync: failed to apply %s#%s',
                         event.get('resource'), event.get('source_id'))
        return _result(event, STATUS_FAILED, detail=detail, retryable=False)

    finally:
        if not committed:
            for storage, name in saved_files:
                try:
                    storage.delete(name)
                except Exception:
                    logger.warning('datasync: orphan photo requires storage cleanup')

    counts[STATUS_APPLIED] += 1
    return _result(
        event,
        STATUS_APPLIED,
        detail=detail,
        local_id=local_id,
        conflict=conflict,
        ignored_fields=ignored,
    )
