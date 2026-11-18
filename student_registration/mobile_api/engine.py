# -*- coding: utf-8 -*-
"""Push engine: applies a batch of offline records through the web forms.

Every item is processed in its own savepoint so one failure never blocks the
rest of the batch. Identity entities go through duplicate verification and
support the ``merge`` / ``link`` / ``create`` / ``discard`` resolutions
described in ``docs/mobile_sync_protocol.md``.
"""
from __future__ import unicode_literals

import datetime
import inspect
import logging

from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import transaction
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from . import dedup, serialization
from .models import MobileSyncBatch, MobileSyncItem
from .registry import (
    KIND_ATTENDANCE, KIND_BRIDGING_SUBFORM, KIND_FORM, KIND_IDENTITY, KIND_MODELFORM, KIND_NEW_ROUND,
    KIND_SCHOOL_ACTIVITY, KIND_TEACHER, KIND_TEACHER_ATTENDANCE, get_registry,
)
from .request_factory import build_request

logger = logging.getLogger(__name__)

MAX_ITEMS = 500


class ItemError(Exception):
    """Validation failure with structured field errors."""

    def __init__(self, message, errors=None, status=MobileSyncItem.STATUS_ERROR):
        super(ItemError, self).__init__(message)
        self.message = message
        self.errors = errors or {}
        self.status = status


class ItemOutcome(object):
    def __init__(self, status, server_id=None, message='', result=None, duplicates=None,
                 person_id=None, duplicate_override=False, errors=None):
        self.status = status
        self.server_id = server_id
        self.message = message
        self.result = result or {}
        self.duplicates = duplicates or []
        self.person_id = person_id
        self.duplicate_override = duplicate_override
        self.errors = errors or {}


def _form_errors(form):
    errors = {}
    for name, messages in form.errors.items():
        errors[name] = [str(m) for m in messages]
    return errors


def _parse_date(value):
    if not value:
        return None
    if isinstance(value, datetime.date):
        return value
    text = str(value)
    for fmt in ('%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y'):
        try:
            return datetime.datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    return None


def _supported_kwargs(func, kwargs):
    """Keep only the keyword arguments ``func`` accepts (forms differ)."""
    try:
        params = inspect.signature(func).parameters
    except (TypeError, ValueError):  # pragma: no cover
        return kwargs
    if any(p.kind == inspect.Parameter.VAR_KEYWORD for p in params.values()):
        return kwargs
    return {k: v for k, v in kwargs.items() if k in params}


def kwargs_for_save(form, init_kwargs):
    """Extra constructor kwargs (programme_type, pre_post, …) that save() also wants."""
    extra = {}
    for key in ('programme_type', 'pre_post', 'number', 'age'):
        if key in init_kwargs:
            extra[key] = init_kwargs[key]
    return extra


class BatchContext(object):
    """Maps client uuids of the current batch to the server ids they became."""

    def __init__(self, user, device):
        self.user = user
        self.device = device
        self.uuid_map = {}

    def remember(self, client_uuid, entity, server_id, person_id=None):
        self.uuid_map[client_uuid] = {'entity': entity, 'server_id': server_id, 'person_id': person_id}

    def resolve(self, client_uuid):
        return self.uuid_map.get(client_uuid)


class PushEngine(object):

    def __init__(self, user, device=None):
        self.user = user
        self.device = device
        self.registry = get_registry()

    # ------------------------------------------------------------------ batch
    def process(self, batch_uuid, items, app_version=''):
        existing = MobileSyncBatch.objects.filter(uuid=batch_uuid, user=self.user).first()
        if existing is not None and existing.status == MobileSyncBatch.STATUS_COMPLETED:
            return existing
        if existing is not None:
            existing.items.all().delete()
            batch = existing
            batch.status = MobileSyncBatch.STATUS_PROCESSING
            batch.app_version = app_version or batch.app_version
            batch.save()
        else:
            batch = MobileSyncBatch.objects.create(
                uuid=batch_uuid, user=self.user, device=self.device, app_version=app_version or '',
                item_count=len(items),
            )
        records = []
        for position, raw in enumerate(items):
            records.append(MobileSyncItem.objects.create(
                batch=batch, position=position,
                client_uuid=str(raw.get('client_uuid') or 'item-{}'.format(position)),
                entity=str(raw.get('entity') or ''),
                op=str(raw.get('op') or 'create'),
                server_id=raw.get('server_id'),
                parent_uuid=str(raw.get('parent_uuid') or ''),
                parent_id=raw.get('parent_id'),
                payload=raw.get('data') or {},
                resolution=raw.get('resolution'),
                result={'client_modified': raw.get('client_modified'),
                        'base_modified': raw.get('base_modified')},
            ))
        ctx = BatchContext(self.user, self.device)
        ordered = sorted(records, key=lambda r: (self._order(r.entity), r.position))
        for record in ordered:
            self._run_item(record, ctx)
        batch.summary = self.summarise(batch)
        batch.status = MobileSyncBatch.STATUS_COMPLETED
        batch.item_count = len(records)
        batch.save()
        if self.device is not None:
            self.device.last_push = timezone.now()
            self.device.save(update_fields=['last_push', 'modified'])
        return batch

    def _order(self, entity):
        spec = self.registry.get(entity)
        return spec.order if spec else 99

    @staticmethod
    def summarise(batch):
        summary = {'total': 0}
        for item in batch.items.all():
            summary['total'] += 1
            summary[item.status] = summary.get(item.status, 0) + 1
        return summary

    # ------------------------------------------------------------------- item
    def _run_item(self, record, ctx):
        meta = record.result or {}
        try:
            with transaction.atomic():
                outcome = self.apply(record, ctx, meta)
        except ItemError as ex:
            outcome = ItemOutcome(ex.status, message=ex.message, errors=ex.errors)
        except ValidationError as ex:
            outcome = ItemOutcome(MobileSyncItem.STATUS_ERROR, message='; '.join(ex.messages),
                                  errors={'__all__': ex.messages})
        except ObjectDoesNotExist as ex:
            outcome = ItemOutcome(MobileSyncItem.STATUS_ERROR, message=str(ex) or 'Record not found.',
                                  errors={'__all__': [str(ex) or 'Record not found.']})
        except Exception as ex:  # pragma: no cover - never let one item kill the batch
            logger.exception('Mobile push item %s failed', record.client_uuid)
            outcome = ItemOutcome(MobileSyncItem.STATUS_ERROR, message=str(ex) or ex.__class__.__name__,
                                  errors={'__all__': [str(ex) or ex.__class__.__name__]})
        record.status = outcome.status
        record.server_id = outcome.server_id if outcome.server_id is not None else record.server_id
        record.message = outcome.message or ''
        record.errors = outcome.errors
        record.duplicates = outcome.duplicates
        record.duplicate_override = outcome.duplicate_override
        result = dict(meta)
        result.update(outcome.result)
        record.result = result
        record.save()
        if outcome.status in (MobileSyncItem.STATUS_CREATED, MobileSyncItem.STATUS_UPDATED,
                              MobileSyncItem.STATUS_MERGED, MobileSyncItem.STATUS_LINKED):
            ctx.remember(record.client_uuid, record.entity, record.server_id, outcome.person_id)
        elif outcome.status == MobileSyncItem.STATUS_DISCARDED and (record.resolution or {}).get('target_id'):
            ctx.remember(record.client_uuid, record.entity, record.resolution.get('target_id'))

    def apply(self, record, ctx, meta):
        spec = self.registry.get(record.entity)
        if spec is None:
            raise ItemError('Unknown entity "{}".'.format(record.entity))
        if not spec.can_write or not spec.can_write(self.user):
            raise ItemError('You are not allowed to write {}.'.format(spec.label))
        payload = dict(record.payload or {})
        resolution = record.resolution or {}
        parent_obj, parent_id = self._resolve_parent(spec, record, ctx)
        record.parent_id = parent_id

        if record.op == 'delete':
            return self._delete(spec, record)

        if spec.kind == KIND_IDENTITY:
            return self._apply_identity(spec, record, payload, resolution, meta, ctx)
        if spec.kind == KIND_NEW_ROUND:
            return self._apply_new_round(spec, record, payload, parent_obj)
        if spec.kind == KIND_FORM:
            return self._apply_form(spec, record, payload, parent_obj, meta, resolution)
        if spec.kind == KIND_MODELFORM:
            return self._apply_modelform(spec, record, payload, parent_obj, meta, resolution)
        if spec.kind == KIND_TEACHER:
            return self._apply_teacher(spec, record, payload, meta, resolution)
        if spec.kind == KIND_BRIDGING_SUBFORM:
            return self._apply_bridging_subform(spec, record, payload, parent_obj)
        if spec.kind == KIND_SCHOOL_ACTIVITY:
            return self._apply_school_activity(spec, record, payload)
        if spec.kind == KIND_ATTENDANCE:
            return self._apply_attendance(spec, record, payload, ctx)
        if spec.kind == KIND_TEACHER_ATTENDANCE:
            return self._apply_teacher_attendance(spec, record, payload, ctx)
        raise ItemError('Entity kind {} is not supported.'.format(spec.kind))

    # --------------------------------------------------------------- helpers
    def _resolve_parent(self, spec, record, ctx):
        if not spec.parent:
            return None, None
        parent_spec = self.registry[spec.parent]
        parent_id = record.parent_id
        if not parent_id and record.parent_uuid:
            resolved = ctx.resolve(record.parent_uuid)
            if resolved is None:
                raise ItemError('Parent record was not saved in this batch.',
                                status=MobileSyncItem.STATUS_SKIPPED)
            parent_id = resolved['server_id']
        if not parent_id:
            raise ItemError('Parent {} is required.'.format(parent_spec.label))
        parent_qs = parent_spec.scope(self.user) if parent_spec.scope else parent_spec.model.objects.all()
        parent_obj = parent_qs.filter(pk=parent_id).first()
        if parent_obj is None:
            raise ItemError('Parent {} #{} is not accessible.'.format(parent_spec.label, parent_id))
        return parent_obj, parent_obj.pk

    def _instance_for_update(self, spec, record):
        if not record.server_id:
            raise ItemError('server_id is required for updates.')
        qs = spec.scope(self.user) if spec.scope else spec.model.objects.all()
        instance = qs.filter(pk=record.server_id).first()
        if instance is None:
            raise ItemError('{} #{} is not accessible.'.format(spec.label, record.server_id))
        return instance

    def _check_conflict(self, instance, meta, resolution):
        base = meta.get('base_modified')
        modified = getattr(instance, 'modified', None)
        if not base or modified is None:
            return
        base_dt = parse_datetime(str(base))
        if base_dt is None:
            return
        if timezone.is_aware(base_dt) and not timezone.is_aware(modified):
            base_dt = timezone.make_naive(base_dt, timezone.get_default_timezone())
        elif not timezone.is_aware(base_dt) and timezone.is_aware(modified):
            base_dt = timezone.make_aware(base_dt, timezone.get_default_timezone())
        action = resolution.get('action')
        if modified > base_dt + datetime.timedelta(seconds=1):
            if action == 'overwrite':
                return
            if action == 'keep_server':
                raise ItemError('Server version kept.', status=MobileSyncItem.STATUS_SKIPPED)
            raise ItemError('Record changed on the server since it was downloaded.',
                            status=MobileSyncItem.STATUS_CONFLICT,
                            errors={'server_data': serialization.serialize_instance(instance)})

    def _delete(self, spec, record):
        instance = self._instance_for_update(spec, record)
        if hasattr(instance, 'deleted'):
            instance.deleted = True
            if hasattr(instance, 'deleted_by'):
                instance.deleted_by = self.user
            instance.save()
        else:
            instance.delete()
        return ItemOutcome(MobileSyncItem.STATUS_DELETED, server_id=record.server_id)

    def _saved_instance(self, spec, request, form_result, parent_id=None, instance_id=None):
        """Find the row a form saved (forms return it or store its id in the session)."""
        if isinstance(form_result, spec.model):
            return form_result
        if instance_id:
            return spec.model.objects.get(pk=instance_id)
        session_id = request.session.get('instance_id')
        if session_id:
            return spec.model.objects.get(pk=session_id)
        if parent_id and spec.parent_field:
            return (spec.model.objects.filter(**{spec.parent_field + '_id': parent_id})
                    .order_by('-id').first())
        return None

    # ------------------------------------------------------------- identity
    def _apply_identity(self, spec, record, payload, resolution, meta, ctx):
        action = resolution.get('action')
        target_id = resolution.get('target_id')
        person_fk = spec.person_field
        is_update = record.op == 'update' and record.server_id

        if action == 'discard':
            return ItemOutcome(MobileSyncItem.STATUS_DISCARDED, message='Discarded by the field worker.')

        instance = None
        status = MobileSyncItem.STATUS_CREATED
        duplicate_override = False
        if is_update:
            instance = self._instance_for_update(spec, record)
            self._check_conflict(instance, meta, resolution)
            status = MobileSyncItem.STATUS_UPDATED
        elif action == 'merge':
            if not target_id:
                raise ItemError('merge requires target_id (registration id).')
            instance = self._instance_for_update(spec, MobileSyncItem(server_id=target_id))
            payload = self._merge_payload(spec, instance, payload, resolution.get('overwrite', False))
            status = MobileSyncItem.STATUS_MERGED
        elif action == 'link':
            if not target_id:
                raise ItemError('link requires target_id (child id).')
            payload[person_fk + '_id'] = target_id
            status = MobileSyncItem.STATUS_LINKED
        elif action == 'create':
            duplicate_override = True
        else:
            identity = dedup.identity_from_payload(spec, payload)
            if identity.complete:
                duplicates = dedup.find_duplicates(spec, identity)
                blocking = [d for d in duplicates if d['match']['reason'] != 'near']
                if blocking:
                    return ItemOutcome(
                        MobileSyncItem.STATUS_DUPLICATE, duplicates=duplicates,
                        message='A child with the same identity already exists ({}).'.format(
                            ', '.join(sorted({d['match']['reason'] for d in blocking}))),
                    )
                if duplicates:
                    meta['near_matches'] = duplicates

        payload = self._scope_payload(spec, payload)
        request = build_request(self.user, payload)
        form = spec.form_class(request.POST, request.FILES, instance=instance, request=request)
        if not form.is_valid():
            raise ItemError('Validation failed.', errors=_form_errors(form))
        result = form.save(request=request, instance=instance)
        saved = self._saved_instance(spec, request, result, instance_id=instance.pk if instance else None)
        if saved is None:
            warnings = request._messages.warnings()
            raise ItemError('The server could not save the record.',
                            errors={'__all__': warnings or ['Unknown error']})
        person = getattr(saved, person_fk, None)
        data_after = serialization.serialize_registration(saved, spec)
        return ItemOutcome(status, server_id=saved.pk, result={'data_after': data_after},
                           person_id=person.pk if person else None,
                           duplicate_override=duplicate_override,
                           duplicates=meta.get('near_matches') or [])

    def _scope_payload(self, spec, payload):
        """Force scope fields to the user's own centre/school (as the web views do)."""
        user = self.user
        if spec.key == 'alp.registration' and not user.is_superuser and user.school_id:
            payload['school'] = user.school_id
        if spec.key == 'clm.bridging':
            if user.partner_id and not payload.get('partner'):
                payload['partner'] = user.partner_id
            if user.school_id and not payload.get('school'):
                payload['school'] = user.school_id
        return payload

    def _merge_payload(self, spec, instance, incoming, overwrite):
        """Existing values as the web edit form would post them, overlaid with incoming."""
        from student_registration.mscc.serializers import MainSerializer
        if spec.key == 'clm.bridging':
            from student_registration.clm.serializers import BridgingSerializer
            data = dict(BridgingSerializer(instance).data)
            if 'student_nationality_id' in data:
                data['student_nationality'] = data['student_nationality_id']
        else:
            serializer_class = MainSerializer
            if spec.key == 'alp.registration':
                from student_registration.alp.serializers import ALPRegistrationSerializer
                serializer_class = ALPRegistrationSerializer
            data = dict(serializer_class(instance).data)
            for key in ('child_nationality', 'child_disability', 'main_caregiver_nationality',
                        'father_educational_level', 'mother_educational_level', 'id_type'):
                data[key] = data.get(key + '_id') or ''
        # Only post what the browser form would post: the form's own fields plus the
        # hidden person id used by the web edit/re-enrol flows.
        allowed = set(spec.form_class.base_fields) | {'child_id', 'student_id', 'student_old'}
        merged = {}
        for key, value in data.items():
            if value is None or key not in allowed:
                continue
            merged[key] = value
        for key, value in incoming.items():
            if value in (None, '', [], {}):
                continue
            if overwrite or merged.get(key) in (None, '', [], {}):
                merged[key] = value
        return merged

    # ------------------------------------------------------------ new round
    def _apply_new_round(self, spec, record, payload, parent_obj):
        request = build_request(self.user, payload)
        form = spec.form_class(request.POST, registry=parent_obj.pk, request=request)
        if not form.is_valid():
            raise ItemError('Validation failed.', errors=_form_errors(form))
        form.save(request=request, registry=parent_obj.pk, instance=None)
        new_registration = getattr(form, 'new_registration', None)
        if new_registration is None:
            raise ItemError('The server could not create the new round.',
                            errors={'__all__': request._messages.warnings() or ['Unknown error']})
        reg_spec = self.registry['mscc.registration']
        data_after = serialization.serialize_registration(new_registration, reg_spec)
        service = new_registration.education_service.order_by('-id').first()
        return ItemOutcome(
            MobileSyncItem.STATUS_CREATED, server_id=new_registration.pk,
            person_id=new_registration.child_id,
            result={'data_after': data_after, 'created_entity': 'mscc.registration',
                    'education_service': serialization.serialize_instance(service) if service else None},
        )

    # ----------------------------------------------------------------- form
    def _apply_form(self, spec, record, payload, parent_obj, meta, resolution):
        instance_id = None
        if record.op == 'update':
            instance = self._instance_for_update(spec, record)
            self._check_conflict(instance, meta, resolution)
            instance_id = instance.pk
        elif not spec.multiple:
            existing = spec.model.objects.filter(**{spec.parent_field + '_id': parent_obj.pk}).order_by('-id').first()
            if existing is not None:
                instance_id = existing.pk
        payload['registration_id'] = parent_obj.pk
        request = build_request(self.user, payload)
        kwargs = {'request': request, 'registry': parent_obj.pk, spec.instance_kw: instance_id}
        if spec.extra_kwargs:
            kwargs.update(spec.extra_kwargs(self.user, spec, payload, parent_obj, instance_id))
        form = spec.form_class(request.POST, **kwargs)
        if not form.is_valid():
            raise ItemError('Validation failed.', errors=_form_errors(form))
        save_kwargs = {'request': request, 'registry': parent_obj.pk, 'instance': instance_id}
        save_kwargs.update(kwargs_for_save(form, kwargs))
        result = form.save(**_supported_kwargs(form.save, save_kwargs))
        saved = self._saved_instance(spec, request, result, parent_id=parent_obj.pk, instance_id=instance_id)
        if saved is None:
            raise ItemError('The server could not save the record.',
                            errors={'__all__': request._messages.warnings() or ['Unknown error']})
        status = MobileSyncItem.STATUS_UPDATED if instance_id else MobileSyncItem.STATUS_CREATED
        return ItemOutcome(status, server_id=saved.pk,
                           result={'data_after': serialization.serialize_instance(saved)})

    # ------------------------------------------------------------ modelform
    def _apply_modelform(self, spec, record, payload, parent_obj, meta, resolution):
        instance = None
        if record.op == 'update':
            instance = self._instance_for_update(spec, record)
            self._check_conflict(instance, meta, resolution)
        elif spec.key == 'alp.school_profile':
            instance = self._instance_for_update(spec, MobileSyncItem(server_id=self.user.school_id))
        if parent_obj is not None:
            payload['registration'] = parent_obj.pk
        if spec.form_class is None:
            return self._apply_generic_modelform(spec, record, payload, instance)
        request = build_request(self.user, payload)
        form = spec.form_class(request.POST, request.FILES, instance=instance, request=request)
        if not form.is_valid():
            raise ItemError('Validation failed.', errors=_form_errors(form))
        obj = form.save(commit=False)
        if hasattr(obj, 'owner') and not getattr(obj, 'owner_id', None):
            obj.owner = self.user
        if hasattr(obj, 'modified_by'):
            obj.modified_by = self.user
        if spec.key == 'alp.teacher':
            obj.school = self.user.school
        obj.save()
        form.save_m2m()
        status = MobileSyncItem.STATUS_UPDATED if instance is not None else MobileSyncItem.STATUS_CREATED
        return ItemOutcome(status, server_id=obj.pk,
                           result={'data_after': serialization.serialize_instance(obj)})

    def _apply_generic_modelform(self, spec, record, payload, instance):
        """Entities without a dedicated web form (CLM teachers): plain ModelForm."""
        from django.forms import modelform_factory
        from student_registration.students.serializers import TeacherSerializer
        fields = [f for f in TeacherSerializer.Meta.fields if f != 'id']
        form_class = modelform_factory(spec.model, fields=fields)
        request = build_request(self.user, payload)
        form = form_class(request.POST, request.FILES, instance=instance)
        if not form.is_valid():
            raise ItemError('Validation failed.', errors=_form_errors(form))
        obj = form.save(commit=False)
        if hasattr(obj, 'owner') and not getattr(obj, 'owner_id', None):
            obj.owner = self.user
        if hasattr(obj, 'modified_by'):
            obj.modified_by = self.user
        if not obj.school_id and self.user.school_id:
            obj.school_id = self.user.school_id
        obj.save()
        form.save_m2m()
        status = MobileSyncItem.STATUS_UPDATED if instance is not None else MobileSyncItem.STATUS_CREATED
        return ItemOutcome(status, server_id=obj.pk,
                           result={'data_after': serialization.serialize_instance(obj)})

    # -------------------------------------------------------------- teacher
    def _apply_teacher(self, spec, record, payload, meta, resolution):
        instance = None
        if record.op == 'update':
            instance = self._instance_for_update(spec, record)
            self._check_conflict(instance, meta, resolution)
        if self.user.center_id and not payload.get('center'):
            payload['center'] = self.user.center_id
        request = build_request(self.user, payload)
        form = spec.form_class(request.POST, request.FILES, instance=instance, request=request)
        if not form.is_valid():
            raise ItemError('Validation failed.', errors=_form_errors(form))
        result = form.save(request, instance=instance)
        saved = self._saved_instance(spec, request, result, instance_id=instance.pk if instance else None)
        if saved is None:
            saved = spec.model.objects.filter(owner=self.user).order_by('-id').first()
        if saved is None:
            raise ItemError('The server could not save the teacher.',
                            errors={'__all__': request._messages.warnings() or ['Unknown error']})
        status = MobileSyncItem.STATUS_UPDATED if instance is not None else MobileSyncItem.STATUS_CREATED
        return ItemOutcome(status, server_id=saved.pk,
                           result={'data_after': serialization.serialize_instance(saved)})

    # ----------------------------------------------------- bridging subform
    def _apply_bridging_subform(self, spec, record, payload, parent_obj):
        request = build_request(self.user, payload)
        kwargs = {'request': request, 'instance': parent_obj}
        extra = spec.extra_kwargs(self.user, spec, payload, parent_obj, None) if spec.extra_kwargs else {}
        kwargs.update(extra)
        form = spec.form_class(request.POST, **kwargs)
        if not form.is_valid():
            raise ItemError('Validation failed.', errors=_form_errors(form))
        save_kwargs = {'request': request, 'instance': parent_obj}
        save_kwargs.update(extra)
        form.save(**save_kwargs)
        parent_obj.refresh_from_db()
        reg_spec = self.registry['clm.bridging']
        return ItemOutcome(MobileSyncItem.STATUS_UPDATED, server_id=parent_obj.pk,
                           result={'data_after': serialization.serialize_registration(parent_obj, reg_spec),
                                   'updated_entity': 'clm.bridging'})

    # ------------------------------------------------------ school activity
    def _apply_school_activity(self, spec, record, payload):
        from .registry import clm_school_ids
        school_id = payload.get('school') or self.user.school_id
        if not school_id or int(school_id) not in set(clm_school_ids(self.user)):
            raise ItemError('School is not accessible.')
        pk = None
        if record.op == 'update':
            pk = self._instance_for_update(spec, record).pk
        request = build_request(self.user, payload)
        form = spec.form_class(request.POST, pk=pk, school_id=school_id, request=request)
        if not form.is_valid():
            raise ItemError('Validation failed.', errors=_form_errors(form))
        result = form.save(request=request, school_id=school_id, instance=pk)
        saved = self._saved_instance(spec, request, result, instance_id=pk)
        if saved is None:
            saved = spec.model.objects.filter(school_id=school_id).order_by('-id').first()
        status = MobileSyncItem.STATUS_UPDATED if pk else MobileSyncItem.STATUS_CREATED
        return ItemOutcome(status, server_id=saved.pk if saved else None,
                           result={'data_after': serialization.serialize_instance(saved) if saved else None})

    # ----------------------------------------------------------- attendance
    def _resolve_rows(self, rows, ctx):
        """Map registration_uuid / child_uuid references to server ids."""
        resolved = []
        dropped = 0
        for row in rows or []:
            row = dict(row)
            if not row.get('registration_id') and row.get('registration_uuid'):
                ref = ctx.resolve(row['registration_uuid'])
                if ref is None:
                    dropped += 1
                    continue
                row['registration_id'] = ref['server_id']
                if not row.get('child_id') and ref.get('person_id'):
                    row['child_id'] = ref['person_id']
            if not row.get('registration_id'):
                dropped += 1
                continue
            resolved.append(row)
        return resolved, dropped

    def _validate_attendance_common(self, payload, rows):
        errors = {}
        date = _parse_date(payload.get('attendance_date'))
        if date is None:
            errors['attendance_date'] = ['Enter a valid date (YYYY-MM-DD).']
        elif date > datetime.date.today():
            errors['attendance_date'] = ['Attendance date cannot be in the future.']
        day_off = str(payload.get('attendance_day_off') or 'No')
        if day_off.lower() == 'yes' and not payload.get('close_reason'):
            errors['close_reason'] = ['Close reason is required on a day off.']
        for index, row in enumerate(rows):
            attended = str(row.get('attended') or 'Yes')
            if attended == 'No':
                if not row.get('absence_reason'):
                    errors['children_attendance[{}].absence_reason'.format(index)] = ['Absence reason is required.']
                elif row.get('absence_reason') == 'Other' and not (row.get('absence_reason_other') or '').strip():
                    errors['children_attendance[{}].absence_reason_other'.format(index)] = ['Please specify.']
        if errors:
            raise ItemError('Validation failed.', errors=errors)
        return date

    def _apply_attendance(self, spec, record, payload, ctx):
        rows, dropped = self._resolve_rows(payload.get('children_attendance'), ctx)
        date = self._validate_attendance_common(payload, rows)
        payload = dict(payload)
        payload['children_attendance'] = rows
        payload['attendance_date'] = date.isoformat()
        if spec.key == 'mscc.attendance_day':
            saved = self._save_mscc_attendance(payload, date)
            data_after = serialization.serialize_mscc_attendance(saved)
        elif spec.key == 'alp.attendance_day':
            saved = self._save_alp_attendance(payload, date)
            data_after = serialization.serialize_alp_attendance(saved)
        elif spec.key == 'clm.attendance_day':
            saved = self._save_clm_attendance(payload, date)
            data_after = serialization.serialize_clm_attendance(saved)
        else:  # pragma: no cover
            raise ItemError('Unsupported attendance entity.')
        message = ''
        if dropped:
            message = '{} child row(s) ignored (registration not found).'.format(dropped)
        status = MobileSyncItem.STATUS_UPDATED if record.server_id else MobileSyncItem.STATUS_CREATED
        return ItemOutcome(status, server_id=saved.pk, message=message, result={'data_after': data_after})

    def _save_mscc_attendance(self, payload, date):
        from student_registration.attendances.models import MSCCAttendance
        from student_registration.mscc.utils import create_attendance
        from .registry import mscc_center_ids
        center_id = payload.get('center_id') or self.user.center_id
        if not center_id or int(center_id) not in set(mscc_center_ids(self.user)):
            raise ItemError('Centre is not accessible.', errors={'center_id': ['Centre is not accessible.']})
        for key in ('round_id', 'education_program', 'class_section'):
            if not payload.get(key):
                raise ItemError('Validation failed.', errors={key: ['This field is required.']})
        payload.setdefault('close_reason', '')
        payload['attendance_day_off'] = str(payload.get('attendance_day_off') or 'no').lower()
        ok = create_attendance(payload, center_id)
        if not ok:
            raise ItemError('The server rejected the attendance sheet.')
        saved = MSCCAttendance.objects.filter(
            round_id=payload['round_id'], center_id=center_id, attendance_date=date,
            education_program=payload['education_program'], class_section=payload['class_section'],
        ).order_by('-id').first()
        if saved is None:
            raise ItemError('The attendance sheet could not be found after saving.')
        return saved

    def _save_alp_attendance(self, payload, date):
        from student_registration.alp.models import ALPAttendance
        from student_registration.alp.utils import create_attendance
        if not self.user.school_id:
            raise ItemError('No school assigned.')
        for key in ('round_id', 'programme'):
            if not payload.get(key):
                raise ItemError('Validation failed.', errors={key: ['This field is required.']})
        payload.setdefault('close_reason', '')
        payload['attendance_day_off'] = 'Yes' if str(payload.get('attendance_day_off') or 'No').lower() == 'yes' else 'No'
        ok = create_attendance(payload, self.user.school_id)
        if not ok:
            raise ItemError('The server rejected the attendance sheet.')
        saved = ALPAttendance.objects.filter(
            round_id=payload['round_id'], school_id=self.user.school_id, attendance_date=date,
            programme_id=payload['programme'],
        ).order_by('-id').first()
        if saved is None:
            raise ItemError('The attendance sheet could not be found after saving.')
        return saved

    def _save_clm_attendance(self, payload, date):
        from student_registration.attendances.models import CLMAttendance
        from student_registration.clm.utils import create_attendance
        from .registry import clm_school_ids
        school_id = payload.get('school_id') or self.user.school_id
        if not school_id or int(school_id) not in set(clm_school_ids(self.user)):
            raise ItemError('School is not accessible.', errors={'school_id': ['School is not accessible.']})
        for key in ('round_id', 'registration_level'):
            if not payload.get(key):
                raise ItemError('Validation failed.', errors={key: ['This field is required.']})
        payload['school_id'] = school_id
        payload.setdefault('close_reason', '')
        payload['attendance_day_off'] = 'Yes' if str(payload.get('attendance_day_off') or 'No').lower() == 'yes' else 'No'
        payload['attendance_date'] = date.strftime('%m/%d/%Y')
        ok = create_attendance(payload)
        if not ok:
            raise ItemError('The server rejected the attendance sheet.')
        saved = CLMAttendance.objects.filter(
            round_id=payload['round_id'], school_id=school_id, attendance_date=date,
            registration_level=payload['registration_level'],
        ).order_by('-id').first()
        if saved is None:
            raise ItemError('The attendance sheet could not be found after saving.')
        return saved

    def _apply_teacher_attendance(self, spec, record, payload, ctx):
        from student_registration.alp.models import ALPTeacherAttendance
        from student_registration.alp.utils import create_teacher_attendance
        if not self.user.school_id:
            raise ItemError('No school assigned.')
        date = _parse_date(payload.get('attendance_date'))
        if date is None:
            raise ItemError('Validation failed.', errors={'attendance_date': ['Enter a valid date.']})
        if date > datetime.date.today():
            raise ItemError('Validation failed.', errors={'attendance_date': ['Date cannot be in the future.']})
        rows = []
        for row in payload.get('teachers_attendance') or []:
            row = dict(row)
            if not row.get('teacher_id') and row.get('teacher_uuid'):
                ref = ctx.resolve(row['teacher_uuid'])
                if ref is None:
                    continue
                row['teacher_id'] = ref['server_id']
            if row.get('teacher_id'):
                rows.append(row)
        data = {'attendance_date': date.isoformat(), 'teachers_attendance': rows}
        ok = create_teacher_attendance(data, self.user.school_id, self.user)
        if not ok:
            raise ItemError('The server rejected the teacher attendance.')
        saved_rows = ALPTeacherAttendance.objects.filter(
            date=date, teacher__school_id=self.user.school_id).order_by('teacher_id')
        data_after = serialization.serialize_alp_teacher_attendance(date, saved_rows)
        return ItemOutcome(MobileSyncItem.STATUS_UPDATED if record.server_id else MobileSyncItem.STATUS_CREATED,
                           server_id=None, result={'data_after': data_after, 'key': date.isoformat()})


def batch_report(batch):
    return {
        'batch_id': batch.pk,
        'batch_uuid': batch.uuid,
        'status': batch.status,
        'received_at': batch.created.isoformat() if batch.created else None,
        'completed_at': batch.modified.isoformat() if batch.modified else None,
        'summary': batch.summary,
        'results': [item.to_report() for item in batch.items.all().order_by('position')],
    }


def validate_batch_payload(payload):
    if not isinstance(payload, dict):
        raise ValidationError('Body must be a JSON object.')
    if not payload.get('batch_uuid'):
        raise ValidationError('batch_uuid is required.')
    items = payload.get('items')
    if not isinstance(items, list) or not items:
        raise ValidationError('items must be a non-empty list.')
    if len(items) > MAX_ITEMS:
        raise ValidationError('A batch may contain at most {} items.'.format(MAX_ITEMS))
    for item in items:
        if not isinstance(item, dict) or not item.get('entity'):
            raise ValidationError('Every item needs an entity.')
    return items
