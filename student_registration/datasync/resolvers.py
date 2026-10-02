# -*- coding: utf-8 -*-
"""Turn the natural keys sent by the Compiler into local objects.

The two databases do not share primary keys, so every relation crossing the
wire travels as a small dictionary of natural keys, for example::

    "center": {"source_id": 12, "p_code": "LB-030201", "name": "Makani Tyre"}

The helpers below resolve such a dictionary against the local database. They
try, in order: an existing sync mapping, then the natural key columns, and --
only for the lookups listed in :data:`AUTO_CREATE_LOOKUPS` -- creation of a
placeholder row.

Every resolver appends a human readable note to the :class:`ResolutionLog`
handed to it, and those notes end up in the response the Compiler stores
against the event, so an operator can see exactly why a field came out empty.
"""

from __future__ import unicode_literals, absolute_import, division

import logging

from django.conf import settings

from student_registration.child.models import Child
from student_registration.clm.models import Disability
from student_registration.locations.models import Center, Location
from student_registration.mscc.models import Round
from student_registration.schools.models import (
    EducationalLevel,
    PartnerOrganization,
    School,
)
from student_registration.students.models import (
    AttachmentType,
    IDType,
    Nationality,
    Training,
)

from .constants import (
    RESOURCE_CENTER,
    RESOURCE_CHILD,
    RESOURCE_REGISTRATION,
    RESOURCE_ROUND,
)
from .models import SyncedRecord

logger = logging.getLogger(__name__)

#: Lookup tables that partners extend freely. A value arriving from the
#: Compiler that does not exist locally is created rather than dropped.
AUTO_CREATE_LOOKUPS = ('Training', 'AttachmentType', 'PartnerOrganization')


class ResolutionLog(object):
    """Collects the notes produced while resolving one payload."""

    def __init__(self):
        self.notes = []

    def add(self, message):
        """Record ``message`` unless it was already noted."""
        if message not in self.notes:
            self.notes.append(message)

    def as_text(self):
        """Return the notes joined into a single line, or an empty string."""
        return '; '.join(self.notes)


def _clean(value):
    """Return ``value`` stripped, or ``None`` when it is empty."""
    if value is None:
        return None
    value = str(value).strip()
    return value or None


def _create_missing_allowed():
    """Return whether placeholder reference rows may be created."""
    return getattr(settings, 'DATASYNC_CREATE_MISSING_REFERENCES', True)


def mapped_object(resource, source_id, source_system=None):
    """Return the local object previously synced for ``source_id``.

    Args:
        resource (str): One of the ``RESOURCE_*`` constants.
        source_id: Primary key of the record in the Compiler.
        source_system (str): Producer identifier; defaults to the Compiler.

    Returns:
        The mapped model instance, or ``None`` when nothing is mapped yet.
    """
    if source_id in (None, ''):
        return None
    lookup = {'resource': resource, 'source_id': str(source_id)}
    if source_system:
        lookup['source_system'] = source_system
    record = SyncedRecord.objects.filter(**lookup).first()
    if not record:
        return None
    return record.local_object


def resolve_lookup(model, key, log, create=False, extra_fields=None):
    """Resolve a simple ``{"name": ...}`` style lookup value.

    Args:
        model: The Django model to search.
        key (dict | str | None): Natural key sent by the Compiler. A bare
            string is treated as ``{"name": value}``.
        log (ResolutionLog): Collector for explanatory notes.
        create (bool): Create the row when it is missing and creation is
            enabled by ``DATASYNC_CREATE_MISSING_REFERENCES``.
        extra_fields (dict): Additional values used only on creation.

    Returns:
        The model instance, or ``None`` when it could not be resolved.
    """
    if not key:
        return None
    if not isinstance(key, dict):
        key = {'name': key}

    name = _clean(key.get('name'))
    name_en = _clean(key.get('name_en'))

    queryset = model.objects.all()
    instance = None
    if name:
        instance = queryset.filter(name__iexact=name).first()
    if instance is None and name_en and hasattr(model, 'name_en'):
        instance = queryset.filter(name_en__iexact=name_en).first()

    if instance is not None:
        return instance
    if not name:
        return None

    if create and model.__name__ in AUTO_CREATE_LOOKUPS and _create_missing_allowed():
        values = {'name': name}
        values.update(extra_fields or {})
        instance = model.objects.create(**values)
        log.add('created {} "{}"'.format(model.__name__, name))
        return instance

    log.add('unknown {} "{}" ignored'.format(model.__name__, name))
    return None


def resolve_nationality(key, log):
    """Resolve a nationality natural key."""
    return resolve_lookup(Nationality, key, log)


def resolve_id_type(key, log):
    """Resolve an ID type natural key."""
    return resolve_lookup(IDType, key, log)


def resolve_disability(key, log):
    """Resolve a disability natural key."""
    return resolve_lookup(Disability, key, log)


def resolve_educational_level(key, log):
    """Resolve an educational level natural key."""
    return resolve_lookup(EducationalLevel, key, log)


def resolve_training(key, log):
    """Resolve a teacher training topic, creating it when unknown."""
    return resolve_lookup(Training, key, log, create=True)


def resolve_attachment_type(key, log):
    """Resolve an attachment type, creating it when unknown."""
    return resolve_lookup(AttachmentType, key, log, create=True)


def resolve_partner(key, log):
    """Resolve a partner organization by its unique name."""
    return resolve_lookup(PartnerOrganization, key, log, create=True)


def resolve_round(key, log):
    """Resolve a round by sync mapping or by its unique name.

    Rounds are cheap and fully described by the payload, so a missing round is
    created rather than left dangling -- otherwise every registration in a new
    round would land without one.
    """
    if not key:
        return None
    if not isinstance(key, dict):
        key = {'name': key}

    instance = mapped_object(RESOURCE_ROUND, key.get('source_id'))
    if instance is not None:
        return instance

    name = _clean(key.get('name'))
    if not name:
        return None

    instance = Round.objects.filter(name__iexact=name).first()
    if instance is not None:
        return instance

    if not _create_missing_allowed():
        log.add('unknown Round "{}" ignored'.format(name))
        return None

    instance = Round.objects.create(
        name=name,
        year=key.get('year') or None,
        current_year=bool(key.get('current_year')),
    )
    log.add('created Round "{}"'.format(name))
    return instance


def resolve_center(key, log):
    """Resolve a centre by sync mapping, P-code, or name plus partner.

    A centre is itself a replicated resource, so in normal operation the
    mapping already exists. When a registration arrives before its centre --
    possible on a first run -- a stub is created from the natural key and the
    later centre event fills in the remaining columns.
    """
    if not key:
        return None
    if not isinstance(key, dict):
        key = {'name': key}

    instance = mapped_object(RESOURCE_CENTER, key.get('source_id'))
    if instance is not None:
        return instance

    p_code = _clean(key.get('p_code'))
    name = _clean(key.get('name'))
    partner = resolve_partner(key.get('partner'), log)

    if p_code:
        instance = Center.objects.filter(p_code__iexact=p_code).first()
        if instance is not None:
            return instance

    if name:
        queryset = Center.objects.filter(name__iexact=name)
        if partner is not None:
            queryset = queryset.filter(partner=partner)
        instance = queryset.first()
        if instance is not None:
            return instance

    if not name or not _create_missing_allowed():
        if name:
            log.add('unknown Center "{}" ignored'.format(name))
        return None

    instance = Center.objects.create(name=name, p_code=p_code, partner=partner)
    log.add('created placeholder Center "{}"'.format(name))
    return instance


def resolve_location(key, log):
    """Resolve an administrative location by P-code, then by name.

    Lebanese administrative geography is master data shared by both systems
    and is never created here.
    """
    if not key:
        return None
    if not isinstance(key, dict):
        key = {'name': key}

    p_code = _clean(key.get('p_code'))
    name = _clean(key.get('name'))
    name_en = _clean(key.get('name_en'))

    if p_code:
        instance = Location.objects.filter(p_code=p_code).first()
        if instance is not None:
            return instance
    if name:
        instance = Location.objects.filter(name__iexact=name).first()
        if instance is not None:
            return instance
    if name_en:
        instance = Location.objects.filter(name_en__iexact=name_en).first()
        if instance is not None:
            return instance

    if p_code or name:
        log.add('unknown Location "{}" ignored'.format(p_code or name))
    return None


def resolve_school(key, log):
    """Resolve a school by its unique CERD number, then by name.

    Schools are ministry master data and are never created here; an unmatched
    school is reported and the field is left empty.
    """
    if not key:
        return None
    if not isinstance(key, dict):
        key = {'name': key}

    number = _clean(key.get('number'))
    name = _clean(key.get('name'))

    if number:
        instance = School.objects.filter(number=number).first()
        if instance is not None:
            return instance
    if name:
        instance = School.objects.filter(name__iexact=name).first()
        if instance is not None:
            return instance

    if number or name:
        log.add('unknown School "{}" ignored'.format(number or name))
    return None


def resolve_registration(key, log):
    """Resolve a registration through its sync mapping.

    Registrations have no natural key of their own, so an unmapped one means
    the parent event has not been applied yet and the caller should retry.
    """
    if not key:
        return None
    source_id = key.get('source_id') if isinstance(key, dict) else key
    instance = mapped_object(RESOURCE_REGISTRATION, source_id)
    if instance is None:
        log.add('registration #{} not replicated yet'.format(source_id))
    return instance


def resolve_child(key, log):
    """Resolve a child by sync mapping, then by UNICEF unique id."""
    if not key:
        return None
    if not isinstance(key, dict):
        key = {'source_id': key}

    instance = mapped_object(RESOURCE_CHILD, key.get('source_id'))
    if instance is not None:
        return instance

    unicef_id = _clean(key.get('unicef_id'))
    if unicef_id:
        instance = Child.objects.filter(unicef_id=unicef_id).first()
        if instance is not None:
            return instance

    log.add('child #{} not replicated yet'.format(key.get('source_id')))
    return None


#: Maps the ``__relation`` suffix used in payloads to the resolver above.
RELATION_RESOLVERS = {
    'nationality': resolve_nationality,
    'id_type': resolve_id_type,
    'disability': resolve_disability,
    'educational_level': resolve_educational_level,
    'training': resolve_training,
    'attachment_type': resolve_attachment_type,
    'partner': resolve_partner,
    'round': resolve_round,
    'center': resolve_center,
    'location': resolve_location,
    'school': resolve_school,
    'registration': resolve_registration,
    'child': resolve_child,
}


def resolve_relation(kind, key, log):
    """Resolve ``key`` using the resolver registered for ``kind``.

    Args:
        kind (str): A key of :data:`RELATION_RESOLVERS`.
        key: The natural key dictionary sent by the Compiler.
        log (ResolutionLog): Collector for explanatory notes.

    Returns:
        The resolved instance, or ``None``.

    Raises:
        KeyError: If ``kind`` is not a known relation type.
    """
    return RELATION_RESOLVERS[kind](key, log)


__all__ = [
    'ResolutionLog',
    'RELATION_RESOLVERS',
    'mapped_object',
    'resolve_relation',
    'resolve_center',
    'resolve_child',
    'resolve_location',
    'resolve_registration',
    'resolve_round',
    'resolve_school',
]
