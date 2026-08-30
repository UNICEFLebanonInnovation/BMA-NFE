# -*- coding: utf-8 -*-
"""Write incoming Compiler events into the local BMA-NFE tables.

Each replicated resource has a handler that knows three things: which local
model it writes, how to turn a payload into a dictionary of column values, and
how to find an already existing local row for it.

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
from django.utils import timezone

from student_registration.attendances.models import (
    MSCCAttendance,
    MSCCAttendanceChild,
)
from student_registration.child.models import Child
from student_registration.locations.models import Center
from student_registration.mscc.models import (
    DigitalService,
    EducationAssessment,
    EducationHistory,
    EducationProgrammeAssessment,
    EducationRSService,
    EducationService,
    FollowUpService,
    HealthNutritionReferral,
    HealthNutritionService,
    InclusionService,
    LegoService,
    Packages,
    ProvidedServices,
    PSSService,
    Recreational,
    Referral,
    Registration,
    Round,
    Teacher,
    YouthAssessment,
    YouthKitService,
    YouthReferral,
    YouthService,
)

from . import resolvers
from .constants import (
    OPERATION_DELETE,
    RESOURCE_ATTENDANCE,
    RESOURCE_CENTER,
    RESOURCE_CHILD,
    RESOURCE_DIGITAL_SERVICE,
    RESOURCE_EDUCATION_ASSESSMENT,
    RESOURCE_EDUCATION_RS_SERVICE,
    RESOURCE_EDUCATION_SERVICE,
    RESOURCE_FOLLOW_UP_SERVICE,
    RESOURCE_GRADING,
    RESOURCE_HEALTH_NUTRITION_REFERRAL,
    RESOURCE_HEALTH_NUTRITION_SERVICE,
    RESOURCE_INCLUSION_SERVICE,
    RESOURCE_LEGO_SERVICE,
    RESOURCE_PACKAGE,
    RESOURCE_PSS_SERVICE,
    RESOURCE_RECREATIONAL,
    RESOURCE_REFERRAL,
    RESOURCE_REGISTRATION,
    RESOURCE_ROUND,
    RESOURCE_TEACHER,
    RESOURCE_YOUTH_ASSESSMENT,
    RESOURCE_YOUTH_KIT_SERVICE,
    RESOURCE_YOUTH_REFERRAL,
    RESOURCE_YOUTH_SERVICE,
)
from .models import SyncConflict, SyncedRecord

logger = logging.getLogger(__name__)

#: Columns that must never be copied across: local primary keys, audit
#: timestamps maintained by ``TimeStampedModel``, and user foreign keys whose
#: ids mean nothing in the other database.
NEVER_COPIED = frozenset({
    'id', 'pk', 'created', 'modified',
    'owner', 'owner_id',
    'modified_by', 'modified_by_id',
    'deleted_by', 'deleted_by_id',
})


class UnresolvedDependency(Exception):
    """Raised when a parent record has not been replicated yet.

    The producer retries these events rather than discarding them, because the
    parent usually arrives moments later.
    """


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

    Relations are excluded because they always travel as natural keys and are
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

    def find_existing(self, payload, log):
        """Return an existing local row to adopt, or ``None`` to create one.

        Adoption matters on first run: BMA-NFE already holds rounds, centres
        and children that the Compiler also knows about, and they must be
        linked rather than duplicated.
        """
        return None

    def after_save(self, instance, payload, log, ctx, record):
        """Hook for related rows (many-to-many links, child tables).

        Args:
            instance: The local row that was just written.
            payload (dict): The event payload.
            log (resolvers.ResolutionLog): Collector for explanatory notes.
            ctx (ApplyContext): Producer identity and event id.
            record (SyncedRecord): The mapping row for ``instance``, already
                saved. A handler that needs to remember something for a later
                event writes it to ``record.pending_links`` and saves.
        """
        return None


def _plain(model, payload, extra=None):
    """Build the value dictionary for a resource with no special handling."""
    values, ignored = split_fields(model, payload.get('fields'))
    values.update(extra or {})
    return values, ignored


class RoundHandler(BaseHandler):
    """Programme rounds. Matched on their unique name."""

    resource = RESOURCE_ROUND
    model = Round

    def build(self, payload, log, ctx):
        return _plain(Round, payload)

    def find_existing(self, payload, log):
        name = (payload.get('fields') or {}).get('name')
        if not name:
            return None
        return Round.objects.filter(name__iexact=str(name).strip()).first()


class PackageHandler(BaseHandler):
    """Package definitions, matched on name and type.

    BMA-NFE's own ``min_age``/``max_age`` columns have no source in the
    Compiler and are left as they are.
    """

    resource = RESOURCE_PACKAGE
    model = Packages

    def build(self, payload, log, ctx):
        return _plain(Packages, payload)

    def find_existing(self, payload, log):
        fields = payload.get('fields') or {}
        name = (fields.get('name') or '').strip()
        if not name:
            return None
        return Packages.objects.filter(
            name__iexact=name, type=fields.get('type') or None
        ).first()


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

    def find_existing(self, payload, log):
        fields = payload.get('fields') or {}
        p_code = (fields.get('p_code') or '').strip()
        if p_code:
            existing = Center.objects.filter(p_code__iexact=p_code).first()
            if existing is not None:
                return existing
        name = (fields.get('name') or '').strip()
        if not name:
            return None
        queryset = Center.objects.filter(name__iexact=name)
        partner = resolvers.resolve_partner(payload.get('partner'), log)
        if partner is not None:
            queryset = queryset.filter(partner=partner)
        return queryset.first()


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
        return _plain(Teacher, payload, extra)

    def find_existing(self, payload, log):
        unicef_id = ((payload.get('fields') or {}).get('unicef_id') or '').strip()
        if not unicef_id:
            return None
        return Teacher.objects.filter(unicef_id=unicef_id).first()

    def after_save(self, instance, payload, log, ctx, record):
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
        return _plain(Child, payload, extra)

    def find_existing(self, payload, log):
        unicef_id = ((payload.get('fields') or {}).get('unicef_id') or '').strip()
        if not unicef_id:
            return None
        return Child.objects.filter(unicef_id=unicef_id).first()


class RegistrationHandler(BaseHandler):
    """MSCC registrations, carrying their child record inline."""

    resource = RESOURCE_REGISTRATION
    model = Registration

    def build(self, payload, log, ctx):
        child_payload = payload.get('child')
        child = None
        if child_payload:
            child_result = apply_resource(
                RESOURCE_CHILD,
                child_payload.get('source_id'),
                child_payload,
                log,
                ctx,
            )
            child = child_result.instance
        extra = {
            'child': child,
            'center': resolvers.resolve_center(payload.get('center'), log),
            'round': resolvers.resolve_round(payload.get('round'), log),
            'partner': resolvers.resolve_partner(payload.get('partner'), log),
        }
        return _plain(Registration, payload, extra)

    def after_save(self, instance, payload, log, ctx, record):
        """Bring the services checklist and education history in line.

        Neither table is generated on this side -- the Compiler creates and
        regenerates both -- so they travel inside the registration and are
        replaced as a set, which mirrors ``regenerate_services`` exactly.
        """
        if payload.get('provided_services') is not None:
            links = self._sync_checklist(instance, payload['provided_services'], log, ctx)
            record.pending_links = dict(record.pending_links or {}, checklist=links)
            record.save(update_fields=['pending_links', 'modified'])
        if payload.get('education_history') is not None:
            self._sync_history(instance, payload['education_history'])
        return None

    def _sync_checklist(self, registration, rows, log, ctx):
        """Upsert the ``ProvidedServices`` rows, remapping ``service_id``.

        Returns:
            dict: ``{name: reference | None}`` -- what each row is meant to
            point at, in the Compiler's terms. Stored on the registration's
            mapping row so a service that lands *after* the registration can
            tell whether it is the intended target (see
            :class:`ChecklistServiceHandler`).
        """
        seen = []
        links = {}
        for row in rows:
            values, _ignored = split_fields(ProvidedServices, row.get('fields'))
            values.pop('service_id', None)
            name = values.get('name')
            if not name:
                continue
            item, _created = ProvidedServices.objects.get_or_create(
                registration=registration,
                name=name,
                type=values.get('type'),
                category=values.get('category'),
            )
            for field, value in values.items():
                setattr(item, field, value)

            # ``service_id`` is a local primary key in both databases. Resolve
            # the Compiler's reference through the mapping; when the service
            # has not arrived yet, keep whatever is there -- the service's own
            # handler completes the link when it lands.
            reference = row.get('service') or None
            links[name] = reference
            if reference:
                service = resolvers.mapped_object(
                    reference.get('resource'), reference.get('source_id'),
                    source_system=ctx.source_system,
                )
                if service is not None:
                    item.service_id = service.pk
                else:
                    log.add('checklist "{}" waits for {}#{}'.format(
                        name, reference.get('resource'), reference.get('source_id')
                    ))
            else:
                item.service_id = None
            item.save()
            seen.append(item.pk)

        ProvidedServices.objects.filter(registration=registration).exclude(pk__in=seen).delete()
        return links

    def _sync_history(self, registration, lines):
        """Upsert the ``EducationHistory`` lines with local ids filled in."""
        seen = []
        for line in lines:
            values, _ignored = split_fields(EducationHistory, line.get('fields'))
            values.pop('child', None)
            values.pop('registration_id', None)
            item, _created = EducationHistory.objects.get_or_create(
                registration_id=registration.pk,
                programme_type=values.get('programme_type'),
                programme_id=values.get('programme_id'),
            )
            for field, value in values.items():
                setattr(item, field, value)
            item.child = registration.child_id
            item.save()
            seen.append(item.pk)

        EducationHistory.objects.filter(registration_id=registration.pk).exclude(pk__in=seen).delete()


class RegistrationChildHandler(BaseHandler):
    """Base for the tables hanging off a registration."""

    def registration_of(self, payload, log):
        """Return the local registration, or raise when it is missing."""
        registration = resolvers.resolve_registration(payload.get('registration'), log)
        if registration is None:
            raise UnresolvedDependency(
                'registration #{} has not been replicated yet'.format(
                    (payload.get('registration') or {}).get('source_id')
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


class SimpleRegistrationChildHandler(RegistrationChildHandler):
    """A table whose only relation is its registration.

    Subclasses set ``resource`` and ``model``; every column is copied as-is.
    """

    def build(self, payload, log, ctx):
        extra = {'registration': self.registration_of(payload, log)}
        return _plain(self.model, payload, extra)


class ChecklistServiceHandler(SimpleRegistrationChildHandler):
    """A service that completes a row of the registration's checklist.

    In the Compiler, saving one of these makes ``update_service`` point the
    matching ``ProvidedServices`` row at the new record. The registration
    payload carries that pointer as a natural key, but the service itself may
    land after the registration did -- in which case the pointer could not be
    resolved then, and the registration's mapping row remembers it under
    ``pending_links``. On arrival, a service checks whether it is the record
    that row was meant to point at, and completes the link only if so. That
    matters for "Health and Nutrition", which two different tables can
    complete: the first to arrive must not claim a row meant for the other.
    """

    service_name = None

    def after_save(self, instance, payload, log, ctx, record):
        if not self.service_name or not instance.registration_id:
            return None

        registration_map = SyncedRecord.objects.filter(
            source_system=ctx.source_system,
            resource=RESOURCE_REGISTRATION,
            content_type=ContentType.objects.get_for_model(Registration),
            object_id=instance.registration_id,
        ).first()
        links = (registration_map.pending_links or {}).get('checklist') if registration_map else None

        rows = ProvidedServices.objects.filter(
            registration_id=instance.registration_id, name=self.service_name,
        )

        if links is None or self.service_name not in links:
            # No registration push has described this row yet (or it predates
            # the checklist travelling with the registration): fill an empty
            # pointer, and let the next registration push confirm it.
            rows.filter(service_id__isnull=True).update(service_id=instance.pk)
            return None

        wanted = links.get(self.service_name)
        if (
            wanted
            and wanted.get('resource') == self.resource
            and str(wanted.get('source_id')) == record.source_id
        ):
            rows.update(service_id=instance.pk)
            log.add('completed checklist "{}"'.format(self.service_name))
        return None


class EducationRSServiceHandler(ChecklistServiceHandler):
    """Retention-support education service, with its school."""

    resource = RESOURCE_EDUCATION_RS_SERVICE
    model = EducationRSService
    service_name = 'RS'

    def build(self, payload, log, ctx):
        extra = {
            'registration': self.registration_of(payload, log),
            'school': resolvers.resolve_school(payload.get('school'), log),
        }
        return _plain(EducationRSService, payload, extra)


class EducationAssessmentHandler(SimpleRegistrationChildHandler):
    resource = RESOURCE_EDUCATION_ASSESSMENT
    model = EducationAssessment


class PSSServiceHandler(ChecklistServiceHandler):
    resource = RESOURCE_PSS_SERVICE
    model = PSSService
    service_name = 'PSS'


class InclusionServiceHandler(ChecklistServiceHandler):
    resource = RESOURCE_INCLUSION_SERVICE
    model = InclusionService
    service_name = 'Inclusion'


class DigitalServiceHandler(ChecklistServiceHandler):
    resource = RESOURCE_DIGITAL_SERVICE
    model = DigitalService
    service_name = 'Digital component'


class HealthNutritionServiceHandler(ChecklistServiceHandler):
    resource = RESOURCE_HEALTH_NUTRITION_SERVICE
    model = HealthNutritionService
    service_name = 'Health and Nutrition'


class HealthNutritionReferralHandler(ChecklistServiceHandler):
    resource = RESOURCE_HEALTH_NUTRITION_REFERRAL
    model = HealthNutritionReferral
    service_name = 'Health and Nutrition'


class YouthKitServiceHandler(ChecklistServiceHandler):
    resource = RESOURCE_YOUTH_KIT_SERVICE
    model = YouthKitService
    service_name = 'Adolescents kit'


class YouthServiceHandler(SimpleRegistrationChildHandler):
    resource = RESOURCE_YOUTH_SERVICE
    model = YouthService


class YouthAssessmentHandler(SimpleRegistrationChildHandler):
    resource = RESOURCE_YOUTH_ASSESSMENT
    model = YouthAssessment


class YouthReferralHandler(SimpleRegistrationChildHandler):
    resource = RESOURCE_YOUTH_REFERRAL
    model = YouthReferral


class FollowUpServiceHandler(ChecklistServiceHandler):
    resource = RESOURCE_FOLLOW_UP_SERVICE
    model = FollowUpService
    service_name = 'Caregivers Package'


class RecreationalHandler(SimpleRegistrationChildHandler):
    resource = RESOURCE_RECREATIONAL
    model = Recreational


class LegoServiceHandler(ChecklistServiceHandler):
    resource = RESOURCE_LEGO_SERVICE
    model = LegoService
    service_name = 'LEGO'


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
        extra = {'center': resolvers.resolve_center(payload.get('center'), log)}
        values, ignored = _plain(MSCCAttendance, payload, extra)
        # ``round_id`` is a bare integer column on this model rather than a
        # foreign key, so the local round's primary key has to be written into
        # it explicitly -- the Compiler's own id would point at the wrong row.
        values.pop('round_id', None)
        round_object = resolvers.resolve_round(payload.get('round'), log)
        values['round_id'] = round_object.id if round_object else None
        return values, ignored

    def after_save(self, instance, payload, log, ctx, record):
        """Bring the day's child rows in line with the incoming list."""
        children = payload.get('children')
        if children is None:
            return None

        seen = []
        for row in children:
            registration = resolvers.resolve_registration(row.get('registration'), log)
            if registration is None:
                log.add(
                    'attendance row for registration #{} skipped, not replicated yet'.format(
                        (row.get('registration') or {}).get('source_id')
                    )
                )
                continue
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
        PackageHandler,
        CenterHandler,
        TeacherHandler,
        ChildHandler,
        RegistrationHandler,
        EducationServiceHandler,
        EducationRSServiceHandler,
        EducationAssessmentHandler,
        GradingHandler,
        ReferralHandler,
        PSSServiceHandler,
        InclusionServiceHandler,
        DigitalServiceHandler,
        HealthNutritionServiceHandler,
        HealthNutritionReferralHandler,
        YouthKitServiceHandler,
        YouthServiceHandler,
        YouthAssessmentHandler,
        YouthReferralHandler,
        FollowUpServiceHandler,
        RecreationalHandler,
        LegoServiceHandler,
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
        payload (dict): Natural-keyed representation of the record.
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
    values, ignored = handler.build(payload, log, ctx)

    mapping_lookup = {
        'source_system': ctx.source_system,
        'resource': resource,
        'source_id': str(source_id),
    }
    record = SyncedRecord.objects.filter(**mapping_lookup).first()

    instance = record.local_object if record else None
    if instance is None:
        instance = handler.find_existing(payload, log)
        if instance is not None:
            log.add('adopted existing {} #{}'.format(handler.model.__name__, instance.pk))
    created = instance is None
    if created:
        instance = handler.model()

    attnames = _attnames_for(handler.model, sorted(values.keys()))

    conflict_fields = {}
    if not created and record is not None and record.last_applied_snapshot:
        conflict_fields = _diverged(
            record.last_applied_snapshot, snapshot_of(instance, attnames)
        )

    for name, value in values.items():
        setattr(instance, name, value)
    instance.save()

    # The mapping row is written before the related-row hook runs, so the
    # hook can both look other mappings up and leave notes on this one.
    applied_snapshot = snapshot_of(instance, attnames)
    defaults = {
        'content_type': ContentType.objects.get_for_model(handler.model),
        'object_id': instance.pk,
        'last_event_id': ctx.event_id,
        'last_applied_snapshot': applied_snapshot,
        'local_fingerprint': fingerprint(applied_snapshot),
        'deleted': False,
    }
    if record is None:
        record = SyncedRecord.objects.create(**dict(mapping_lookup, **defaults))
    else:
        for name, value in defaults.items():
            setattr(record, name, value)
        record.save()

    handler.after_save(instance, payload, log, ctx, record)

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


def delete_resource(resource, source_id, log, ctx):
    """Remove the local row for a record deleted in the Compiler.

    Args:
        resource (str): One of the ``RESOURCE_*`` constants.
        source_id: The record's primary key in the Compiler.
        log (resolvers.ResolutionLog): Collector for explanatory notes.
        ctx (ApplyContext): Producer identity for this event.

    Returns:
        bool: ``True`` when a row was removed, ``False`` when there was
        nothing mapped to remove.
    """
    record = SyncedRecord.objects.filter(
        source_system=ctx.source_system,
        resource=resource,
        source_id=str(source_id),
    ).first()
    if record is None:
        log.add('nothing mapped for {}#{}'.format(resource, source_id))
        return False

    instance = record.local_object
    if instance is not None:
        instance.delete()

    # Written through the queryset rather than ``record.save()``: the generic
    # relation still caches the object we just deleted, and saving the model
    # would refuse to write a reference to a row that no longer exists. The
    # content type is kept so the admin still shows what the mapping was for.
    SyncedRecord.objects.filter(pk=record.pk).update(
        object_id=None,
        deleted=True,
        last_applied_snapshot={},
        local_fingerprint='',
        modified=timezone.now(),
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
        removed = delete_resource(resource, source_id, log, ctx)
        return resource, removed, log.as_text()

    result = apply_resource(resource, source_id, event.get('payload') or {}, log, ctx)
    return resource, result, log.as_text()
