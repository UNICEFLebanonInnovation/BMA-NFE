"""Authenticated photo uploads into the storage already used by Child.photo."""

import hashlib
import hmac
import io
import re
import uuid
import warnings

from django.conf import settings
from django.db import DatabaseError
from django.core.files.base import ContentFile
from PIL import Image

from student_registration.child.models import Child
from .identity import source_timestamp
from .models import SyncedChildPhoto, SyncedRecord, SyncConflict


class PhotoUploadRequired(Exception):
    """The receiver needs bytes before it can commit this complete event."""


def stored_photo_digest(child, validate=False):
    if not child.photo:
        return None
    try:
        with child.photo.open('rb') as stream:
            data = stream.read(max_photo_bytes() + 1)
    except FileNotFoundError:
        return None
    if not data or len(data) > max_photo_bytes():
        return None
    digest = hashlib.sha256(data).hexdigest()
    if validate:
        try:
            verified_image(ContentFile(data), digest)
        except ValueError:
            return None
    return digest


def max_photo_bytes():
    return getattr(settings, 'DATASYNC_PHOTO_MAX_BYTES', 5 * 1024 * 1024)


def verified_image(upload, expected_hash):
    """Check actual bytes rather than the sender's MIME type or filename."""
    if upload is None or upload.size > max_photo_bytes():
        raise ValueError('A photo within DATASYNC_PHOTO_MAX_BYTES is required')
    data = upload.read(max_photo_bytes() + 1)
    if not data or len(data) > max_photo_bytes():
        raise ValueError('Photo is empty or too large')
    digest = hashlib.sha256(data).hexdigest()
    if not hmac.compare_digest(digest, str(expected_hash or '')):
        raise ValueError('Photo SHA-256 does not match')
    try:
        with warnings.catch_warnings():
            warnings.simplefilter('error', Image.DecompressionBombWarning)
            with Image.open(io.BytesIO(data)) as image:
                formats = {'JPEG': 'jpg', 'PNG': 'png', 'WEBP': 'webp'}
                extension = formats.get(image.format)
                if extension is None:
                    raise ValueError('Only JPEG, PNG and WebP photos are accepted')
                if image.width * image.height > getattr(settings, 'DATASYNC_PHOTO_MAX_PIXELS', 20000000):
                    raise ValueError('Photo dimensions are too large')
                image.verify()
    except (OSError, Image.DecompressionBombError, Image.DecompressionBombWarning) as error:
        raise ValueError('Invalid image') from error
    return data, digest, extension


def apply_registration_photo(event, source_system, uploads, saved_files):
    """Part of the registration transaction; no independent photo request."""
    from .constants import RESOURCE_REGISTRATION, OPERATION_DELETE
    from .identity import UnresolvedDependency, reference_bma_id
    if event['resource'] != RESOURCE_REGISTRATION or event['operation'] == OPERATION_DELETE:
        return ''
    child_ref = (event.get('payload') or {}).get('child')
    descriptor = child_ref.get('photo_sync') if isinstance(child_ref, dict) else None
    if descriptor is None:
        return ''
    if not isinstance(descriptor, dict):
        raise ValueError('child.photo_sync must be an object')
    if not getattr(settings, 'DATASYNC_INGEST_ENABLED', True):
        raise UnresolvedDependency('Sync is disabled')
    action = descriptor.get('action')
    if action == 'unavailable':
        return 'Source child has no verified Student photo link; existing photo retained'
    if action not in ('put', 'remove', 'verify'):
        raise ValueError('photo_sync.action must be put, remove, verify or unavailable')
    source_id = reference_bma_id(child_ref)
    event_id = uuid.UUID(str(event['event_id']))
    timestamp = source_timestamp(descriptor.get('source_modified', event.get('source_modified')))
    if timestamp is None:
        raise ValueError('Photo source_modified is required')
    data, digest, extension = None, '', ''
    if action == 'verify':
        digest = str(descriptor.get('sha256') or '')
        if not re.fullmatch('[0-9a-f]{64}', digest):
            raise ValueError('A valid photo SHA-256 is required')
    if action == 'put':
        key = descriptor.get('file_key')
        if key != 'photo_' + event_id.hex:
            raise ValueError('Photo file_key must belong to this event')
        data, digest, extension = verified_image((uploads or {}).get(key), descriptor.get('sha256'))
    SyncedChildPhoto.objects.get_or_create(source_system=source_system, source_id=source_id)
    state = SyncedChildPhoto.objects.select_for_update().get(
        source_system=source_system, source_id=source_id)
    if state.last_event_id == event_id or (state.source_modified and timestamp <= state.source_modified):
        return 'Photo already synchronized or older; record applied'
    child = Child.objects.select_for_update().filter(bma_id=source_id).first()
    if child is None:
        raise UnresolvedDependency('Child must exist before its photo can be saved')
    storage = Child._meta.get_field('photo').storage
    note = 'Child profile photo synchronized'
    try:
        previous = state.storage_name
        current = child.photo.name or ''
        current_digest = stored_photo_digest(child, validate=action == 'verify') if action in ('put', 'verify') else None
        if action == 'verify':
            if current_digest != digest:
                raise PhotoUploadRequired('Receiver photo is missing or changed; upload required')
            state.storage_name = current
            note = 'Existing child photo verified; no image transfer needed'
        if action == 'put':
            if current_digest != digest:
                prefix = hashlib.sha256((source_system + ':' + source_id).encode()).hexdigest()[:24]
                name = storage.save('child_photos/sync/{}/{}.{}'.format(prefix, event_id.hex, extension),
                                    ContentFile(data))
                saved_files.append((storage, name))
                child.photo = name
                child.save(update_fields=['photo'])
                state.storage_name = name
                if current:
                    note += ' (existing photo replaced)'
                if current != previous or (current and current_digest != state.sha256):
                    from .constants import RESOURCE_CHILD
                    record = SyncedRecord.objects.get(
                        source_system=source_system, resource=RESOURCE_CHILD,
                        source_id=source_id, source_scope='',
                    )
                    audit, _ = SyncConflict.objects.get_or_create(
                        synced_record=record, event_id=event_id,
                        resource=RESOURCE_CHILD, source_id=source_id,
                        defaults={'diverged_fields': {}},
                    )
                    changes = dict(audit.diverged_fields or {})
                    changes['photo'] = {'synced': previous, 'local': current}
                    audit.diverged_fields = changes
                    audit.save(update_fields=['diverged_fields'])
                    note += '; local NFE photo edit overwritten'
            state.storage_name = child.photo.name or ''
        elif action == 'remove' and previous:
            if child.photo.name == previous:
                child.photo = ''
                child.save(update_fields=['photo'])
            state.storage_name = ''
    except DatabaseError:
        raise
    except PhotoUploadRequired:
        raise
    except Exception as error:
        raise UnresolvedDependency('Photo storage unavailable; the whole event will retry') from error
    state.child = child
    state.last_event_id = event_id
    state.source_modified = timestamp
    state.sha256 = digest
    state.save()
    return note
