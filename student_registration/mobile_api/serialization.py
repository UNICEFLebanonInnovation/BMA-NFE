# -*- coding: utf-8 -*-
"""Model → JSON helpers shared by pull responses and push result reports."""
from __future__ import unicode_literals

import datetime
import decimal

from django.db import models


def _value(field, value):
    if value is None:
        return None
    if isinstance(field, models.FileField):
        return value.name if hasattr(value, 'name') else str(value)
    if isinstance(value, (datetime.datetime, datetime.date)):
        return value.isoformat()
    if isinstance(value, decimal.Decimal):
        return str(value)
    return value


def serialize_instance(obj, exclude=(), labels=True):
    """Serialize concrete fields; FKs as ``<name>`` id + ``<name>_label``."""
    data = {}
    for field in obj._meta.concrete_fields:
        if field.name in exclude:
            continue
        if isinstance(field, models.ForeignKey):
            data[field.name] = getattr(obj, field.attname)
            if labels and data[field.name] is not None:
                try:
                    related = getattr(obj, field.name)
                    data[field.name + '_label'] = str(related) if related is not None else None
                except Exception:  # pragma: no cover - dangling FK
                    data[field.name + '_label'] = None
        else:
            data[field.name] = _value(field, getattr(obj, field.name))
    for field in obj._meta.many_to_many:
        if field.name in exclude:
            continue
        try:
            data[field.name] = list(getattr(obj, field.name).values_list('pk', flat=True))
        except Exception:  # pragma: no cover
            data[field.name] = []
    data['id'] = obj.pk
    return data


PERSON_EXTRA = ('full_name', 'birthday', 'birthdate', 'age', 'number', 'unicef_id')


def serialize_person(person):
    if person is None:
        return None
    data = serialize_instance(person, exclude=('photo',))
    for attr in PERSON_EXTRA:
        try:
            data[attr] = getattr(person, attr)
        except Exception:
            data[attr] = None
    return data


def serialize_registration(obj, spec):
    """Registration/bridging row with the nested person and a display label."""
    data = serialize_instance(obj)
    person = getattr(obj, spec.person_field, None) if spec.person_field else None
    data[spec.person_field or 'child'] = serialize_person(person)
    data['label'] = str(person) if person is not None else str(obj)
    if spec.key == 'mscc.registration':
        data['education_summary'] = [
            {
                'id': s.id, 'round': s.round_id, 'education_program': s.education_program,
                'class_section': s.class_section,
                'registration_date': s.registration_date.isoformat() if s.registration_date else None,
                'education_status': s.education_status,
            }
            for s in obj.education_service.all().order_by('id')
        ]
        from student_registration.mscc.models import Referral
        dropout = (Referral.objects.filter(registration_id=obj.id, recommended_learning_path='Drop out')
                   .order_by('-id').values_list('dropout_date', flat=True).first())
        data['dropout_date'] = dropout.isoformat() if dropout else None
    return data


def serialize_mscc_attendance(day):
    return {
        'id': day.id,
        'round_id': day.round_id,
        'center_id': day.center_id,
        'attendance_date': day.attendance_date.isoformat() if day.attendance_date else None,
        'education_program': day.education_program,
        'class_section': day.class_section,
        'attendance_day_off': day.day_off,
        'close_reason': day.close_reason,
        'children_attendance': [
            {
                'id': row.id, 'registration_id': row.registration_id, 'child_id': row.child_id,
                'attended': row.attended, 'absence_reason': row.absence_reason,
                'absence_reason_other': row.absence_reason_other,
            }
            for row in day.attendance_child.all().order_by('id')
        ],
    }


def serialize_alp_attendance(day):
    return {
        'id': day.id,
        'round_id': day.round_id,
        'school_id': day.school_id,
        'programme': day.programme_id,
        'attendance_date': day.attendance_date.isoformat() if day.attendance_date else None,
        'attendance_day_off': day.day_off,
        'close_reason': day.close_reason,
        'children_attendance': [
            {
                'id': row.id, 'registration_id': row.registration_id, 'child_id': row.child_id,
                'attended': row.attended, 'absence_reason': row.absence_reason,
                'absence_reason_other': row.absence_reason_other,
            }
            for row in day.attendance_child.all().order_by('id')
        ],
    }


def serialize_clm_attendance(day):
    return {
        'id': day.id,
        'round_id': day.round_id,
        'school_id': day.school_id,
        'registration_level': day.registration_level,
        'attendance_date': day.attendance_date.isoformat() if day.attendance_date else None,
        'attendance_day_off': day.day_off,
        'close_reason': day.close_reason,
        'children_attendance': [
            {
                'id': row.id, 'registration_id': row.registration_id, 'child_id': row.student_id,
                'attended': row.attended, 'absence_reason': row.absence_reason,
                'absence_reason_other': row.absence_reason_other,
            }
            for row in day.attendance_student.all().order_by('id')
        ],
    }


def serialize_alp_teacher_attendance(date, rows):
    return {
        'attendance_date': date.isoformat() if date else None,
        'teachers_attendance': [
            {'id': r.id, 'teacher_id': r.teacher_id, 'status': r.status} for r in rows
        ],
    }
