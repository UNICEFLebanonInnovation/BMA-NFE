# -*- coding: utf-8 -*-
"""Write incoming Compiler events into the local BMA-NFE tables.

Each replicated resource has a handler that knows which local model it writes
and how to turn a payload into column values. Rows are identified by their
BMA IDs, or by BMA Teacher ID plus centre for teachers.

The generic :func:`apply_event` then does the parts that are the same for
every resource -- adopting or creating the row, detecting that a BMA-NFE user
had edited it since the last sync, writing the new values, and refreshing the
:class:`~student_registration.datasync.models.SyncedRecord` mapping.

The Compiler is the system of record: an incoming update always wins. When it
overwrites locally modified values a
:class:`~student_registration.datasync.models.SyncConflict` row is written so
the change is not lost silently.
"""

from __future__ import unicode_literals, absolute_import, division

import datetime
import decimal
import hashlib
import json
import logging
import uuid

from django.contrib.contenttypes.models import ContentType
from django.db import models as django_models

from student_registration.attendances.models import (
    MSCCAttendance,
    MSCCAttendanceChild,
)
from student_registration.child.models import Child
from student_registration.locations.models import Center
from student_registration.mscc.models import (
    EducationProgrammeAssessment,
    EducationService,
    Referral,
    Registration,
    Round,
    Teacher,
)

from . import resolvers
from .constants import (
    OPERATION_DELETE,
    RESOURCE_ATTENDANCE,
    RESOURCE_CENTER,
    RESOURCE_CHILD,
    RESOURCE_EDUCATION_SERVICE,
    RESOURCE_GRADING,
    RESOURCE_REFERRAL,
    RESOURCE_REGISTRATION,
    RESOURCE_ROUND,
    RESOURCE_TEACHER,
)
from .models import SyncConflict, SyncedRecord
from .identity import UnresolvedDependency, normalize_bma_id, reference_bma_id

logger = logging.getLogger(__name__)

#: Columns that must never be copied across: local primary keys, audit
#: timestamps maintained by ``TimeStampedModel``, and user foreign keys whose
#: ids mean nothing in the other database.
NEVER_COPIED = frozenset({
    'id', 'pk', 'bma_id', 'created', 'modified',
    'owner', 'owner_id',
    'modified_by', 'modified_by_id',
    'deleted_by', 'deleted_by_id',
})


def jsonable(value):
    """Return a JSON-serialisable version of a model attribute value."""
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, decimal.Decimal):
        return float(value)
    if isinstance(value, (datetime.datetime, datetime.date, datetime.time)):
        return value.isoformat()
    if isinstance(value, uuid.UUID):
        return str(value)
    if isinstance(value, (list, tuple)):
        return [jsonable(item) for item in value]
    if isinstance(value, dict):
        return {str(key): jsonable(item) for key, item in value.items()}
    return str(value)


def fingerprint(snapshot):
    """Return a stable hash of a snapshot dictionary."""
    payload = json.dumps(snapshot, sort_keys=True, default=str)
    return hashlib.sha256(payload.encode('utf-8')).hexdigest()


def plain_field_names(model):
    """Return the concrete, non-relational column names of ``model``.

    Relations are excluded because they travel as reference dictionaries and are
    resolved explicitly by the handlers.
    """
    names = set()
    for field in model._meta.get_fields():
        if not getattr(field, 'concrete', False):
            continue
        if field.is_relation or field.auto_created:
            continue
        if field.name in NEVER_COPIED:
            continue
        names.add(field.name)
    return names


def split_fields(model, fields):
    """Split incoming plain fields into ones this model has and ones it lacks.

    BMA-NFE runs a subset of the Compiler's schema, so extra columns are
    expected. They are reported rather than treated as an error.

    Args:
        model: The local Django model.
        fields (dict): ``{column: value}`` sent by the Compiler.

    Returns:
        tuple[dict, list]: Accepted values, and the sorted names of the
        columns this model does not have.
    """
    known = plain_field_names(model)
    accepted = {}
    ignored = []
    for name, value in (fields or {}).items():
        if name in known:
            accepted[name] = value
        else:
            ignored.append(name)
    return accepted, sorted(ignored)


def snapshot_of(instance, attnames):
    """Return the current values of ``attnames`` on ``instance``."""
    return {
        name: jsonable(getattr(instance, name, None))
        for name in sorted(attnames)
    }


class ApplyContext(object):
    """Per-event context threaded through the handlers."""

    def __init__(self, source_system, event_id=None):
        self.source_system = source_system
        self.event_id = event_id


class BaseHandler(object):
    """Common behaviour for every replicated resource."""

    resource = None
    model = None

    def build(self, payload, log, ctx):
        """Return ``{attname: value}`` to write for this payload.

        Args:
            payload (dict): The ``payload`` block of the incoming event.
            log (resolvers.ResolutionLog): Collector for explanatory notes.
            ctx (ApplyContext): Producer identity for this event.

        Returns:
            tuple[dict, list]: Values to write, and the payload columns the
            local model does not have.

        Raises:
            UnresolvedDependency: When a required parent is not replicated.
        """
        raise NotImplementedError

    def after_save(self, instance, payload, log):
        """Hook for related rows (many-to-many links, child tables)."""
        return None


def _plain(model, payload, extra=None):
    """Build the value dictionary for a resource with no special handling."""
    values, ignored = split_fields(model, payload.get('fields'))
    values.update(extra or {})
    return values, ignored


class RoundHandler(BaseHandler):
    """Programme rounds identified by BMA ID, regardless of their name."""

    resource = RESOURCE_ROUND
    model = Round

    def build(self, payload, log, ctx):
        return _plain(Round, payload)


class CenterHandler(BaseHandler):
    """Makani / NFE centres, including their partner and geography."""

    resource = RESOURCE_CENTER
    model = Center

    def build(self, payload, log, ctx):
        extra = {
            'partner': resolvers.resolve_partner(payload.get('partner'), log),
            'governorate': resolvers.resolve_location(payload.get('governorate'), log),
            'caza': resolvers.resolve_location(payload.get('caza'), log),
            'cadaster': resolvers.resolve_location(payload.get('cadaster'), log),
        }
        return _plain(Center, payload, extra)


class TeacherHandler(BaseHandler):
    """Teachers.

    The Compiler stores teachers as ``students.Teacher`` (school based) while
    BMA-NFE stores them as ``mscc.Teacher`` (centre based). The producer does
    the field translation; everything that arrives here is already expressed
    in BMA-NFE's own vocabulary.
    """

    resource = RESOURCE_TEACHER
    model = Teacher

    def build(self, payload, log, ctx):
        extra = {
            'round': resolvers.resolve_round(payload.get('round'), log),
            'center': resolvers.resolve_center(payload.get('center'), log),
            'id_type': resolvers.resolve_id_type(payload.get('id_type'), log),
            'nationality': resolvers.resolve_nationality(payload.get('nationality'), log),
        }
        for index in range(1, 6):
            key = 'attach_type_{}'.format(index)
            extra[key] = resolvers.resolve_attachment_type(payload.get(key), log)
        if extra['center'] is None:
            raise ValueError('A teacher requires a center identified by BMA ID')
        return _plain(Teacher, payload, extra)

    def after_save(self, instance, payload, log):
        """Replace the teacher's training topics with the incoming set."""
        trainings = payload.get('trainings')
        if trainings is None:
            return None
        resolved = []
        for key in trainings:
            training = resolvers.resolve_training(key, log)
            if training is not None:
                resolved.append(training)
        instance.trainings.set(resolved)
        return None


class ChildHandler(BaseHandler):
    """Children. Always applied as part of their registration."""

    resource = RESOURCE_CHILD
    model = Child

    def build(self, payload, log, ctx):
        extra = {
            'nationality': resolvers.resolve_nationality(payload.get('nationality'), log),
            'main_caregiver_nationality': resolvers.resolve_nationality(
                payload.get('main_caregiver_nationality'), log
            ),
            'id_type': resolvers.resolve_id_type(payload.get('id_type'), log),
            'disability': resolvers.resolve_disability(payload.get('disability'), log),
            'father_educational_level': resolvers.resolve_educational_level(
                payload.get('father_educational_level'), log
            ),
            'mother_educational_level': resolvers.resolve_educational_level(
                payload.get('mother_educational_level'), log
            ),
        }
        values, ignored = _plain(Child, payload, extra)
        if isinstance(values.get('unicef_id'), str):
            values['unicef_id'] = values['unicef_id'].strip()
        return values, ignored


class RegistrationHandler(BaseHandler):
    """Registrations and embedded children have independent BMA IDs."""

    resource = RESOURCE_REGISTRATION
    model = Registration

    def build(self, payload, log, ctx):
        child_payload = payload.get('child')
        if not child_payload or not payload.get('round') or not payload.get('center'):
            raise ValueError('A registration requires child, round and center BMA IDs')
        child_id = reference_bma_id(child_payload)
        if isinstance(child_payload, dict) and 'fields' in child_payload:
            child_result = apply_resource(
                RESOURCE_CHILD,
                child_id,
                child_payload,
                log,
                ctx,
            )
            child = child_result.instance
        else:
            child = resolvers.resolve_child(child_payload, log)
            if child is None:
                raise UnresolvedDependency('BMA child #{} has not arrived yet'.format(child_id))
        extra = {
            'child': child,
            'center': resolvers.resolve_center(payload.get('center'), log),
            'round': resolvers.resolve_round(payload.get('round'), log),
            'partner': resolvers.resolve_partner(payload.get('partner'), log),
        }
        return _plain(Registration, payload, extra)


class RegistrationChildHandler(BaseHandler):
    """Base for the tables hanging off a registration."""

    def registration_of(self, payload, log):
        """Return the local registration, or raise when it is missing."""
        if payload.get('registration') is None:
            raise ValueError('A service, grading or referral requires a registration BMA ID')
        registration = resolvers.resolve_registration(payload.get('registration'), log)
        if registration is None:
            raise UnresolvedDependency(
                'registration #{} has not been replicated yet'.format(
                    reference_bma_id(payload['registration'])
                )
            )
        return registration


class EducationServiceHandler(RegistrationChildHandler):
    """The child's education situation."""

    resource = RESOURCE_EDUCATION_SERVICE
    model = EducationService

    def build(self, payload, log, ctx):
        extra = {
            'registration': self.registration_of(payload, log),
            'round': resolvers.resolve_round(payload.get('round'), log),
        }
        return _plain(EducationService, payload, extra)


class GradingHandler(RegistrationChildHandler):
    """Programme grading (pre / post / school test score sheets)."""

    resource = RESOURCE_GRADING
    model = EducationProgrammeAssessment

    def build(self, payload, log, ctx):
        extra = {'registration': self.registration_of(payload, log)}
        return _plain(EducationProgrammeAssessment, payload, extra)


class ReferralHandler(RegistrationChildHandler):
    """Referrals out of the NFE programme."""

    resource = RESOURCE_REFERRAL
    model = Referral

    def build(self, payload, log, ctx):
        extra = {
            'registration': self.registration_of(payload, log),
            'referred_school': resolvers.resolve_school(payload.get('referred_school'), log),
        }
        return _plain(Referral, payload, extra)


class AttendanceHandler(BaseHandler):
    """A centre's attendance day, together with its per-child rows."""

    resource = RESOURCE_ATTENDANCE
    model = MSCCAttendance

    def build(self, payload, log, ctx):
        if payload.get('center') is None or payload.get('round') is None:
            raise ValueError('Attendance requires center and round BMA IDs')
        extra = {
            'center': resolvers.resolve_center(payload['center'], log),
            'round': resolvers.resolve_round(payload['round'], log),
        }
        values, ignored = _plain(MSCCAttendance, payload, extra)
        return values, ignored

    def after_save(self, instance, payload, log):
        """Bring the day's child rows in line with the incoming list."""
        children = payload.get('children')
        if children is None:
            return None

        seen = []
        for row in children:
            registration = resolvers.resolve_registration(row.get('registration'), log)
            if registration is None:
                raise UnresolvedDependency(
                    'attendance registration #{} has not arrived yet'.format(
                        reference_bma_id(row.get('registration'))
                    )
                )
            values, _ignored = split_fields(MSCCAttendanceChild, row.get('fields'))
            child_row, _created = MSCCAttendanceChild.objects.get_or_create(
                attendance_day=instance,
                registration=registration,
                defaults={'child': registration.child},
            )
            child_row.child = registration.child
            for name, value in values.items():
                setattr(child_row, name, value)
            child_row.save()
            seen.append(child_row.pk)

        instance.attendance_child.exclude(pk__in=seen).delete()
        return None


HANDLERS = {
    handler.resource: handler()
    for handler in (
        RoundHandler,
        CenterHandler,
        TeacherHandler,
        ChildHandler,
        RegistrationHandler,
        EducationServiceHandler,
        GradingHandler,
        ReferralHandler,
        AttendanceHandler,
    )
}


class ApplyResult(object):
    """Outcome of applying a single event."""

    def __init__(self, instance=None, created=False, conflict=False, ignored_fields=None):
        self.instance = instance
        self.created = created
        self.conflict = conflict
        self.ignored_fields = ignored_fields or []


def _diverged(previous, current):
    """Return the values a local user changed since the last sync write.

    Args:
        previous (dict): Snapshot taken right after the previous sync write.
        current (dict): The row's values as they are now.

    Returns:
        dict: ``{field: {"synced": ..., "local": ...}}`` for each field whose
        value no longer matches what the sync last wrote.
    """
    changed = {}
    for name, was in (previous or {}).items():
        if name not in current:
            continue
        now = current[name]
        if was != now:
            changed[name] = {'synced': was, 'local': now}
    return changed


def apply_resource(resource, source_id, payload, log, ctx):
    """Create or update the local row for one replicated record.

    Args:
        resource (str): One of the ``RESOURCE_*`` constants.
        source_id: The record's primary key in the Compiler.
        payload (dict): Fields and BMA-ID references for the record.
        log (resolvers.ResolutionLog): Collector for explanatory notes.
        ctx (ApplyContext): Producer identity and current event id.

    Returns:
        ApplyResult: The written instance and what happened to it.

    Raises:
        UnresolvedDependency: When a parent record is not replicated yet.
        KeyError: When ``resource`` is unknown.
    """
    handler = HANDLERS[resource]
    payload = payload or {}
    source_id = normalize_bma_id(source_id)
    for supplied_id in (payload.get('bma_id'), (payload.get('fields') or {}).get('bma_id')):
        if supplied_id is not None and normalize_bma_id(supplied_id) != source_id:
            raise ValueError('Payload bma_id must equal the event source_id')
    values, ignored = handler.build(payload, log, ctx)
    values['bma_id'] = source_id
    identity = {'bma_id': source_id}
    source_scope = ''
    if resource == RESOURCE_TEACHER:
        identity['center'] = values['center']
        source_scope = values['center'].bma_id

    mapping_lookup = {
        'source_system': ctx.source_system,
        'resource': resource,
        'source_id': source_id,
        'source_scope': source_scope,
    }
    instance = handler.model.objects.select_for_update().filter(**identity).first()
    created = False
    if instance is None:
        # The unique BMA identity also protects concurrent first deliveries.
        instance, created = handler.model.objects.get_or_create(**identity, defaults=values)
        if not created:
            instance = handler.model.objects.select_for_update().get(pk=instance.pk)
    record = SyncedRecord.objects.select_for_update().filter(**mapping_lookup).first()
    if record is not None and record.local_object is not None:
        if record.object_id != instance.pk:
            raise ValueError('Sync mapping disagrees with the model BMA ID; review the mapping')
    if not created and record is None:
        log.add('adopted existing {} #{} by BMA ID'.format(handler.model.__name__, instance.pk))

    attnames = _attnames_for(handler.model, sorted(values.keys()))

    conflict_fields = {}
    if not created and record is not None and record.last_applied_snapshot:
        conflict_fields = _diverged(
            record.last_applied_snapshot, snapshot_of(instance, attnames)
        )

    for name, value in values.items():
        setattr(instance, name, value)
    instance.save()

    handler.after_save(instance, payload, log)

    applied_snapshot = snapshot_of(instance, attnames)
    defaults = {
        'content_type': ContentType.objects.get_for_model(handler.model),
        'object_id': instance.pk,
        'last_event_id': ctx.event_id,
        'last_applied_snapshot': applied_snapshot,
        'local_fingerprint': fingerprint(applied_snapshot),
        'deleted': False,
    }
    record, _ = SyncedRecord.objects.update_or_create(**mapping_lookup, defaults=defaults)

    if conflict_fields:
        SyncConflict.objects.create(
            synced_record=record,
            event_id=ctx.event_id,
            resource=resource,
            source_id=str(source_id),
            diverged_fields=conflict_fields,
        )
        log.add(
            '{} locally modified field(s) overwritten: {}'.format(
                len(conflict_fields), ', '.join(sorted(conflict_fields))
            )
        )

    return ApplyResult(
        instance=instance,
        created=created,
        conflict=bool(conflict_fields),
        ignored_fields=ignored,
    )


def _attnames_for(model, field_names):
    """Return the attribute names used to read ``field_names`` off ``model``.

    Foreign keys are tracked through their ``_id`` attribute so a snapshot
    compares primary keys rather than model instances.
    """
    attnames = []
    for name in field_names:
        try:
            field = model._meta.get_field(name)
        except Exception:  # pragma: no cover - defensive, name came from us
            attnames.append(name)
            continue
        if isinstance(field, django_models.ForeignKey):
            attnames.append(field.attname)
        else:
            attnames.append(field.name)
    return attnames


def delete_resource(resource, source_id, log, ctx, payload=None):
    """Remove the local row for a record deleted in the Compiler.

    Args:
        resource (str): One of the ``RESOURCE_*`` constants.
        source_id: The record's primary key in the Compiler.
        log (resolvers.ResolutionLog): Collector for explanatory notes.
        ctx (ApplyContext): Producer identity for this event.

    Returns:
        bool: ``True`` when a row was removed, ``False`` when there was
        no BMA-identified local row to remove.
    """
    source_id = normalize_bma_id(source_id)
    identity = {'bma_id': source_id}
    source_scope = ''
    if resource == RESOURCE_TEACHER:
        center_id = reference_bma_id((payload or {}).get('center'))
        center = Center.objects.filter(bma_id=center_id).first()
        if center is None:
            raise UnresolvedDependency('BMA center #{} has not arrived yet'.format(center_id))
        identity['center'] = center
        source_scope = center_id
    record = SyncedRecord.objects.select_for_update().filter(
        source_system=ctx.source_system,
        resource=resource,
        source_id=source_id,
        source_scope=source_scope,
    ).first()
    handler = HANDLERS[resource]
    instance = handler.model.objects.select_for_update().filter(**identity).first()
    if record is not None and record.local_object is not None:
        if instance is None or record.object_id != instance.pk:
            raise ValueError('Sync mapping disagrees with the model BMA ID; review the mapping')
    if instance is not None:
        instance.delete()

    # Clear the local reference while preserving the identity as a tombstone.
    SyncedRecord.objects.update_or_create(
        source_system=ctx.source_system, resource=resource,
        source_id=source_id, source_scope=source_scope,
        defaults={
            'content_type': ContentType.objects.get_for_model(handler.model),
            'object_id': None, 'deleted': True, 'last_event_id': ctx.event_id,
            'last_applied_snapshot': {}, 'local_fingerprint': '',
        },
    )
    return instance is not None


def apply_event(event, source_system):
    """Apply one decoded event.

    Args:
        event (dict): ``resource``, ``operation``, ``source_id``, ``payload``
            and ``event_id`` as sent by the producer.
        source_system (str): Producer identifier.

    Returns:
        tuple[str, ApplyResult | bool, str]: The notes-bearing log text is the
        third element; the second is the apply result (upsert) or whether a
        row was removed (delete).

    Raises:
        UnresolvedDependency: When a parent record is not replicated yet.
        KeyError: When the resource is unknown.
    """
    log = resolvers.ResolutionLog()
    resource = event['resource']
    source_id = event['source_id']
    ctx = ApplyContext(source_system, event_id=event.get('event_id'))

    if event.get('operation') == OPERATION_DELETE:
        removed = delete_resource(resource, source_id, log, ctx, event.get('payload'))
        return resource, removed, log.as_text()

    result = apply_resource(resource, source_id, event.get('payload') or {}, log, ctx)
    return resource, result, log.as_text()
