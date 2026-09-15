# -*- coding: utf-8 -*-
"""Generate form schemas for the mobile app from the web platform's forms.

The app renders every registration/service form from these descriptions, so
labels, choices, required flags and lengths always match the website.
"""
from __future__ import unicode_literals

import logging

from django import forms
from django.db import models as db_models
from django.utils import translation

from .registry import (
    KIND_ATTENDANCE, KIND_BRIDGING_SUBFORM, KIND_FORM, KIND_IDENTITY, KIND_MODELFORM, KIND_NEW_ROUND,
    KIND_SCHOOL_ACTIVITY, KIND_TEACHER, KIND_TEACHER_ATTENDANCE, specs_for_user,
)
from .request_factory import build_request

logger = logging.getLogger(__name__)

REF_BY_MODEL = {
    'students.Nationality': 'nationalities',
    'students.IDType': 'id_types',
    'students.Training': 'trainings',
    'students.AttachmentType': 'attachment_types',
    'clm.Disability': 'disabilities',
    'schools.EducationalLevel': 'education_levels',
    'schools.School': 'schools',
    'schools.PartnerOrganization': 'partners',
    'schools.CLMRound': 'rounds.clm',
    'schools.ClubType': 'club_types',
    'locations.Center': 'centers',
    'locations.Location': 'locations',
    'mscc.Round': 'rounds.mscc',
    'mscc.Registration': 'parent',
    'alp.ALPRound': 'rounds.alp',
    'alp.ALPProgram': 'alp_programs',
    'alp.ALPRegistration': 'parent',
    'alp.ALPTeacher': 'alp_teachers',
    'clm.Bridging': 'parent',
}

# Fields the app never renders (server-managed or browser-only).
ALWAYS_HIDDEN = {'csrfmiddlewaretoken', 'save', 'registration_id', 'is_cbece', 'child_photo'}


def _instantiate(spec, user):
    """Try to build an unbound form the way the view does, else use base_fields."""
    request = build_request(user, {}, method='GET')
    kwargs = {'request': request}
    if spec.kind in (KIND_FORM, KIND_NEW_ROUND):
        kwargs['registry'] = None
        if spec.kind == KIND_FORM:
            kwargs[spec.instance_kw] = None
        if spec.extra_kwargs:
            kwargs.update(spec.extra_kwargs(user, spec, {}, None, None))
    elif spec.kind == KIND_BRIDGING_SUBFORM:
        kwargs['instance'] = None
        if spec.extra_kwargs:
            kwargs.update(spec.extra_kwargs(user, spec, {}, None, None))
    elif spec.kind == KIND_SCHOOL_ACTIVITY:
        kwargs.update({'school_id': user.school_id, 'pk': None})
    elif spec.kind in (KIND_IDENTITY, KIND_TEACHER, KIND_MODELFORM):
        kwargs['instance'] = None
    try:
        return spec.form_class(**kwargs)
    except Exception as ex:  # pragma: no cover - defensive: fall back to declared fields
        logger.warning('Could not instantiate %s for schema: %s', spec.form_class.__name__, ex)
        return None


def _model_label(model):
    return '{}.{}'.format(model._meta.app_label, model.__name__)


def _choices(field):
    result = []
    for value, label in field.choices:
        if isinstance(label, (list, tuple)):
            for v2, l2 in label:
                result.append({'value': '' if v2 is None else str(v2), 'label': str(l2)})
        else:
            result.append({'value': '' if value is None else str(value), 'label': str(label)})
    return result


def field_spec(name, field, spec=None):
    widget = field.widget
    data = {
        'name': name,
        'label': str(field.label) if field.label else name.replace('_', ' ').capitalize(),
        'required': bool(field.required),
        'help_text': str(field.help_text) if field.help_text else '',
        'placeholder': widget.attrs.get('placeholder', '') if hasattr(widget, 'attrs') else '',
        'type': 'text',
    }
    if isinstance(widget, forms.HiddenInput) or name in ALWAYS_HIDDEN \
            or (spec and name in spec.hidden_fields):
        data['type'] = 'hidden'
    elif isinstance(field, forms.ModelMultipleChoiceField):
        data['type'] = 'multiref'
        data['ref'] = REF_BY_MODEL.get(_model_label(field.queryset.model), _model_label(field.queryset.model))
    elif isinstance(field, forms.ModelChoiceField):
        data['type'] = 'ref'
        data['ref'] = REF_BY_MODEL.get(_model_label(field.queryset.model), _model_label(field.queryset.model))
    elif isinstance(field, forms.MultipleChoiceField):
        data['type'] = 'multiselect'
        data['choices'] = _choices(field)
    elif isinstance(field, forms.ChoiceField):
        data['type'] = 'select'
        data['choices'] = _choices(field)
    elif isinstance(field, forms.BooleanField):
        data['type'] = 'boolean'
    elif isinstance(field, forms.IntegerField):
        data['type'] = 'number'
        data['min_value'] = field.min_value
        data['max_value'] = field.max_value
    elif isinstance(field, (forms.DecimalField, forms.FloatField)):
        data['type'] = 'decimal'
    elif isinstance(field, forms.DateField):
        data['type'] = 'date'
    elif isinstance(field, forms.DateTimeField):
        data['type'] = 'datetime'
    elif isinstance(field, forms.EmailField):
        data['type'] = 'email'
    elif isinstance(field, (forms.FileField, forms.ImageField)):
        data['type'] = 'file'
    elif isinstance(field, forms.RegexField):
        data['type'] = 'text'
        try:
            data['pattern'] = field.regex.pattern
        except AttributeError:  # pragma: no cover
            pass
    elif isinstance(widget, forms.Textarea):
        data['type'] = 'textarea'
    if isinstance(field, forms.CharField) and field.max_length:
        data['max_length'] = field.max_length
    if isinstance(widget, forms.DateInput) and data['type'] == 'text':
        data['type'] = 'date'
    return data


def _with_arabic_labels(fields, spec, user):
    """Second pass under the Arabic locale to capture translated labels."""
    with translation.override('ar'):
        form = _instantiate(spec, user)
        source = form.fields if form is not None else spec.form_class.base_fields
        for item in fields:
            f = source.get(item['name'])
            if f is not None and f.label:
                item['label_ar'] = str(f.label)
                if f.help_text:
                    item['help_text_ar'] = str(f.help_text)
                if hasattr(f.widget, 'attrs') and f.widget.attrs.get('placeholder'):
                    item['placeholder_ar'] = str(f.widget.attrs.get('placeholder'))
                if 'choices' in item and isinstance(f, forms.ChoiceField):
                    ar = _choices(f)
                    if len(ar) == len(item['choices']):
                        for orig, translated in zip(item['choices'], ar):
                            orig['label_ar'] = translated['label']


def entity_schema(spec, user):
    fields = []
    if spec.form_class is not None:
        with translation.override('en'):
            form = _instantiate(spec, user)
            source = form.fields if form is not None else spec.form_class.base_fields
            for name, field in source.items():
                fields.append(field_spec(name, field, spec))
        _with_arabic_labels(fields, spec, user)
        present = {f['name'] for f in fields}
        for extra in spec.extra_fields:
            if extra['name'] in present:
                continue
            item = {'help_text': '', 'placeholder': '', 'required': False}
            item.update(extra)
            fields.append(item)
    layout = spec.layout or {}
    sections = _sections(layout.get('sections'), fields)
    return {
        'key': spec.key,
        'module': spec.module,
        'label': spec.label,
        'kind': spec.kind,
        'parent': spec.parent,
        'identity': spec.identity,
        'multiple': spec.multiple,
        'pullable': spec.pullable,
        'description': spec.description,
        'fields': fields,
        'sections': sections,
        'reveals': layout.get('reveals', []),
        'wizard': layout.get('wizard', False),
        'confirm_fields': layout.get('confirm_fields', []),
    }


def _sections(declared, fields):
    names = [f['name'] for f in fields if f['type'] != 'hidden']
    if not declared:
        return [{'key': 'main', 'label': 'Details', 'label_ar': 'التفاصيل', 'fields': names}]
    used = set()
    result = []
    for section in declared:
        present = [n for n in section['fields'] if n in names]
        used.update(present)
        result.append({**section, 'fields': present})
    leftovers = [n for n in names if n not in used]
    if leftovers:
        if result and result[-1]['key'] in ('pre_test', 'other'):
            result[-1]['fields'].extend(leftovers)
        else:
            result.append({'key': 'other', 'label': 'Other', 'label_ar': 'أخرى', 'fields': leftovers})
    return [s for s in result if s['fields']]


def build_schemas(user):
    schemas = {}
    for spec in specs_for_user(user):
        if spec.kind in (KIND_ATTENDANCE, KIND_TEACHER_ATTENDANCE):
            schemas[spec.key] = {
                'key': spec.key, 'module': spec.module, 'label': spec.label, 'kind': spec.kind,
                'parent': None, 'identity': False, 'multiple': True, 'pullable': True,
                'description': spec.description, 'fields': [], 'sections': [], 'reveals': [],
                'wizard': False, 'confirm_fields': [],
            }
            continue
        if spec.form_class is None:
            continue
        schemas[spec.key] = entity_schema(spec, user)
    return schemas
