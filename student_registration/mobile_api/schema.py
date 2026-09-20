# -*- coding: utf-8 -*-
"""Generate form schemas for the mobile app from the web platform's forms.

The app renders every registration/service form from these descriptions, so
labels, choices, required flags and lengths always match the website.
"""
from __future__ import unicode_literals

import logging

from django import forms
from django.core import validators as core_validators
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


# Validators whose regex is an implementation detail rather than a rule worth
# shipping: the app has a field TYPE for each of these, and their patterns are
# enormous and not portable to Dart's RegExp.
_OPAQUE_REGEX_VALIDATORS = (
    core_validators.URLValidator,
    core_validators.EmailValidator,
)


def _bound(data, key, value):
    """Record a bound only when there is one.

    Writing `None` would look like an answer to `setdefault`, and the same
    bound expressed as MinValueValidator(1) rather than min_value=1 would then
    be dropped -- which is how `validators=[...]` came to be invisible.
    """
    if value is not None:
        data[key] = value


def _rules_from_validators(field, data):
    """Copy what `validators=[...]` says into the schema.

    A Django field carries rules in three places: its own arguments
    (max_length, min_value), its class (EmailField), and its `validators`
    list. Only the first two were exported, so a RegexValidator attached to a
    form field reached the app as nothing at all -- the thirteen name fields on
    the child registration are letters-only on the website and were
    unconstrained in the app, which turns a typo into a push error the worker
    cannot fix once they are back offline.

    Patterns are emitted as a LIST, because a field may legitimately carry
    several, and also as a single `pattern` for the app already installed in
    the field: an older APK reads `pattern` and must keep working against a
    newer server.
    """
    patterns = []

    def add_pattern(regex, message):
        try:
            source = regex.pattern
        except AttributeError:
            source = str(regex)
        if not source or any(p['pattern'] == source for p in patterns):
            return
        item = {'pattern': source}
        if message:
            item['message'] = str(message)
        patterns.append(item)

    # A RegexField's own regex is also present in field.validators, so this is
    # deduplicated by add_pattern rather than guarded by an isinstance check.
    own = getattr(field, 'regex', None)
    if own is not None:
        add_pattern(own, None)

    for validator in getattr(field, 'validators', None) or []:
        if isinstance(validator, _OPAQUE_REGEX_VALIDATORS):
            continue
        if isinstance(validator, core_validators.RegexValidator):
            add_pattern(validator.regex, getattr(validator, 'message', None))
        elif isinstance(validator, core_validators.MinLengthValidator):
            data.setdefault('min_length', validator.limit_value)
        elif isinstance(validator, core_validators.MaxLengthValidator):
            data.setdefault('max_length', validator.limit_value)
        elif isinstance(validator, core_validators.MinValueValidator):
            data.setdefault('min_value', validator.limit_value)
        elif isinstance(validator, core_validators.MaxValueValidator):
            data.setdefault('max_value', validator.limit_value)
        elif isinstance(validator, core_validators.DecimalValidator):
            data.setdefault('max_digits', validator.max_digits)
            data.setdefault('decimal_places', validator.decimal_places)

    if patterns:
        data['patterns'] = patterns
        data.setdefault('pattern', patterns[0]['pattern'])
        if patterns[0].get('message'):
            data.setdefault('pattern_message', patterns[0]['message'])
    return data


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
    # DecimalField SUBCLASSES IntegerField in Django, so it has to be tested
    # first: the other order typed every decimal as a number, and the app then
    # parsed it with int.tryParse and rejected "31.25" as not a number.
    elif isinstance(field, (forms.DecimalField, forms.FloatField)):
        data['type'] = 'decimal'
        _bound(data, 'min_value', field.min_value)
        _bound(data, 'max_value', field.max_value)
        # Only DecimalField has these; FloatField does not.
        _bound(data, 'max_digits', getattr(field, 'max_digits', None))
        _bound(data, 'decimal_places', getattr(field, 'decimal_places', None))
    elif isinstance(field, forms.IntegerField):
        data['type'] = 'number'
        _bound(data, 'min_value', field.min_value)
        _bound(data, 'max_value', field.max_value)
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
    if isinstance(field, forms.CharField) and getattr(field, 'min_length', None):
        data['min_length'] = field.min_length
    if isinstance(widget, forms.DateInput) and data['type'] == 'text':
        data['type'] = 'date'
    # Last, so an explicit field argument above wins over the same rule
    # restated as a validator (setdefault in the helper).
    _rules_from_validators(field, data)
    return data


def _with_arabic_labels(fields, spec, user):
    """Second pass under the Arabic locale to capture translated labels."""
    with translation.override('ar'):
        form = _instantiate(spec, user)
        source = form.fields if form is not None else spec.form_class.base_fields
        for item in fields:
            f = source.get(item['name'])
            if f is None:
                continue
            # A validator message is translated like any other string, and a
            # rule the worker cannot read is a rule they cannot act on.
            if item.get('patterns'):
                ar = _rules_from_validators(f, {}).get('patterns') or []
                by_pattern = {p['pattern']: p.get('message') for p in ar}
                for rule in item['patterns']:
                    translated = by_pattern.get(rule['pattern'])
                    if translated:
                        rule['message_ar'] = translated
                if item['patterns'][0].get('message_ar'):
                    item['pattern_message_ar'] = item['patterns'][0]['message_ar']
            if f.label:
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


def _field(name, label, label_ar, ftype, **extra):
    item = {'name': name, 'label': label, 'label_ar': label_ar, 'type': ftype,
            'required': False, 'help_text': '', 'placeholder': ''}
    item.update(extra)
    return item


def attendance_schema(spec):
    """Describe an attendance sheet the way every other entity is described.

    Attendance used to ship `fields: []`, which meant the one thing the app
    could not do with an attendance sheet was validate it: the rules lived
    only in `engine._validate_attendance_common`, on the far side of a sync.
    A worker filling a sheet in a centre with no signal learned that a reason
    was missing hours later, in a push report, by which time the children had
    gone home.

    These are exactly the rules the engine enforces, in the schema language
    the app already applies to the other twenty-four entities, so attendance
    stops being a special case. The choice lists are named rather than inlined
    because the roster's own pickers already read those reference lists: the
    validator then checks membership against the very list the worker chose
    from, and the two can never drift apart.
    """
    module = spec.module
    header = [
        _field('attendance_date', 'Date', 'التاريخ', 'date', required=True, max_date='today'),
    ]
    rows = []
    if spec.kind == KIND_ATTENDANCE:
        header += [
            _field('attendance_day_off', 'Day off', 'يوم عطلة', 'boolean'),
            _field('close_reason', 'Reason for closing', 'سبب الإغلاق', 'select',
                   choices_ref='{}.attendance.close_reason'.format(module)),
        ]
        rows = [
            _field('attended', 'Attendance', 'الحضور', 'select', required=True,
                   choices=[{'value': 'Yes', 'label': 'Present', 'label_ar': 'حاضر'},
                            {'value': 'No', 'label': 'Absent', 'label_ar': 'غائب'}]),
            _field('absence_reason', 'Reason for absence', 'سبب الغياب', 'select',
                   choices_ref='{}.attendance.absence_reason'.format(module)),
            _field('absence_reason_other', 'Please specify', 'يرجى التحديد', 'text'),
        ]
    else:
        # A teacher row carries `status`, not `attended`, and the only rule the
        # server applies to it is the model's own choice list -- there is no
        # required check in create_teacher_attendance, so there is none here.
        rows = [
            _field('status', 'Status', 'الحالة', 'select',
                   choices=[{'value': 'Present', 'label': 'Present', 'label_ar': 'حاضر'},
                            {'value': 'Absent', 'label': 'Absent', 'label_ar': 'غائب'}]),
        ]
    return {
        'key': spec.key, 'module': module, 'label': spec.label, 'kind': spec.kind,
        'parent': None, 'identity': False, 'multiple': True, 'pullable': True,
        'description': spec.description,
        'fields': header,
        'sections': [{'key': 'main', 'label': 'Details', 'label_ar': 'التفاصيل',
                      'fields': [f['name'] for f in header]}],
        # close_reason is required only on a day off, and a reason for absence
        # only for a child marked absent -- the same two conditions the engine
        # checks, expressed as reveals so the app both hides and requires.
        'reveals': ([{'when': {'field': 'attendance_day_off', 'in': ['true', 'Yes', 'yes']},
                      'show': ['close_reason'], 'require': True}]
                    if spec.kind == KIND_ATTENDANCE else []),
        'row_fields': rows,
        'row_reveals': ([{'when': {'field': 'attended', 'in': ['No']},
                          'show': ['absence_reason'], 'require': True},
                         {'when': {'field': 'absence_reason', 'in': ['Other']},
                          'show': ['absence_reason_other'], 'require': True}]
                        if spec.kind == KIND_ATTENDANCE else []),
        'row_key': 'children_attendance' if spec.kind == KIND_ATTENDANCE else 'teachers_attendance',
        'wizard': False, 'confirm_fields': [],
    }


def build_schemas(user):
    schemas = {}
    for spec in specs_for_user(user):
        if spec.kind in (KIND_ATTENDANCE, KIND_TEACHER_ATTENDANCE):
            schemas[spec.key] = attendance_schema(spec)
            continue
        if spec.form_class is None:
            continue
        schemas[spec.key] = entity_schema(spec, user)
    return schemas
