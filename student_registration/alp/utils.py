import logging
from datetime import datetime

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from student_registration.users.templatetags.custom_tags import has_group

from .models import (
    ALPAttendance,
    ALPAttendanceChild,
    ALPRegistration,
    ALPTeacher,
    ALPTeacherAttendance,
)

logger = logging.getLogger(__name__)


def user_has_alp_permission(user):
    return has_group(user, 'ALP_SCHOOL')


def filter_by_school(queryset, user):
    """
    Filter the queryset to only include records related to the user's school.

    ALP records are school-owned data, so the connected user's school remains
    the boundary even when that user has elevated Django permissions. Views
    that intentionally provide cross-school reporting must opt in explicitly
    instead of relying on a privilege-based exception here.
    """
    school_id = getattr(user, 'school_id', None)
    if school_id is None:
        return queryset.none()

    # Most ALP models have a school field directly. Related attendance models
    # must be filtered through their owning teacher or registration instead.
    model_name = queryset.model.__name__

    if model_name in ('ALPRegistration', 'ALPTeacher', 'ALPAttendance'):
        return queryset.filter(school_id=school_id)
    elif model_name == 'ALPTeacherAttendance':
        return queryset.filter(teacher__school_id=school_id)
    elif model_name in ('ALPGrading', 'ALPAttendanceChild'):
        return queryset.filter(registration__school_id=school_id)

    return queryset


def parse_int(value):
    """Return ``value`` as an int, or ``None`` when it is not a whole number."""
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    value = str(value).strip()
    if not value.isdigit():
        return None
    return int(value)


def parse_int_list(values):
    """Return the numeric entries of ``values`` as ints, dropping the rest."""
    result = []
    for value in values or []:
        number = parse_int(value)
        if number is not None:
            result.append(number)
    return result


def parse_date_flexible(date_str):
    if not date_str:
        return None
    if not isinstance(date_str, str):
        return None
    for fmt in ('%m/%d/%Y', '%Y-%m-%d'):
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except ValueError:
            continue
    return None


def _as_date(value):
    return value.date() if hasattr(value, 'date') else value


def _today():
    """Today's date; ``localdate`` cannot be used when USE_TZ is off."""
    if settings.USE_TZ:
        return timezone.localdate()
    return timezone.now().date()


def _choice_or_none(value, choices):
    """Return ``value`` when it is a valid (non-empty) key of ``choices``."""
    if value in (None, ''):
        return None
    valid = {key for key, _label in choices if key}
    return value if value in valid else None


def _child_record(registration, child, attended='Yes', absence_reason='', absence_reason_other=''):
    return {
        'registration_id': registration.id,
        'child_id': child.id,
        'child_fullname': child.full_name,
        'child_mother_fullname': child.mother_fullname,
        'child_birthday': child.birthday,
        'child_nationality': child.nationality.name if child.nationality else '',
        'attended': attended or '',
        'absence_reason': absence_reason or '',
        'absence_reason_other': absence_reason_other or '',
    }


def load_child_attendance(school_id, round_id, attendance_date_str, programme_id):
    """
    Return the children to display on the daily attendance sheet.

    ``instances`` holds the rows that already have an attendance record for the
    day (or every registration when the day has not been saved yet) and
    ``new_instances`` the registrations added since the day was first saved.
    Rows whose registration or child no longer exists are skipped instead of
    hiding the whole sheet.
    """
    empty = {'instances': [], 'new_instances': []}
    round_id = parse_int(round_id)
    programme_id = parse_int(programme_id)
    attendance_date = _as_date(parse_date_flexible(attendance_date_str))
    if school_id is None or round_id is None or programme_id is None or attendance_date is None:
        return empty

    attendance = ALPAttendance.objects.filter(
        school_id=school_id,
        attendance_date=attendance_date,
        programme_id=programme_id,
        round_id=round_id,
    ).last()

    registrations = ALPRegistration.objects.filter(
        school_id=school_id,
        deleted=False,
        round_id=round_id,
        programme_id=programme_id,
        child__isnull=False,
    ).select_related('child', 'child__nationality').order_by('id')

    existing_children = []
    new_children = []

    if attendance:
        existing_ids = []
        attendances = ALPAttendanceChild.objects.filter(
            attendance_day=attendance,
            registration__isnull=False,
            registration__deleted=False,
            child__isnull=False,
        ).select_related('registration', 'child', 'child__nationality').order_by('id')
        for attendance_child in attendances:
            existing_ids.append(attendance_child.registration_id)
            existing_children.append(_child_record(
                attendance_child.registration,
                attendance_child.child,
                attendance_child.attended,
                attendance_child.absence_reason,
                attendance_child.absence_reason_other,
            ))

        for registration in registrations.exclude(id__in=existing_ids):
            new_children.append(_child_record(registration, registration.child))
    else:
        for registration in registrations:
            existing_children.append(_child_record(registration, registration.child))

    return {'instances': existing_children, 'new_instances': new_children}


def create_attendance(data, school_id):
    """
    Persist the daily attendance sheet posted by the school focal point.

    Every child row is checked against the school, round and programme of the
    attendance day so a client cannot attach attendance to another school's
    registrations. Returns ``False`` when the payload is not usable.
    """
    if not isinstance(data, dict) or school_id is None:
        return False

    round_id = parse_int(data.get('round_id'))
    programme_id = parse_int(data.get('programme'))
    attendance_date = _as_date(parse_date_flexible(data.get('attendance_date')))
    if round_id is None or programme_id is None or attendance_date is None:
        logger.error('Invalid attendance header: %s', {
            'round_id': data.get('round_id'), 'programme': data.get('programme'),
            'attendance_date': data.get('attendance_date'),
        })
        return False
    if attendance_date > _today():
        logger.error('Refusing to save attendance for a future date: %s', attendance_date)
        return False

    day_off = 'Yes' if data.get('attendance_day_off') == 'Yes' else 'No'
    close_reason = _choice_or_none(data.get('close_reason'), ALPAttendance.CLOSE_REASON) if day_off == 'Yes' else None

    children = data.get('children_attendance') or []
    if not isinstance(children, list):
        return False

    allowed = dict(
        ALPRegistration.objects.filter(
            school_id=school_id,
            deleted=False,
            round_id=round_id,
            programme_id=programme_id,
        ).values_list('id', 'child_id')
    )
    valid_absence_reasons = ALPAttendanceChild.ABSENCE_REASON

    try:
        with transaction.atomic():
            attendance, _created = ALPAttendance.objects.get_or_create(
                round_id=round_id,
                school_id=school_id,
                attendance_date=attendance_date,
                programme_id=programme_id,
            )
            attendance.day_off = day_off
            attendance.close_reason = close_reason
            attendance.save()

            if day_off == 'Yes':
                # A closed day has no child attendance: drop rows that were
                # recorded before the day was marked as a day off.
                ALPAttendanceChild.objects.filter(attendance_day=attendance).delete()
                return True

            for child in children:
                if not isinstance(child, dict):
                    continue
                child_id = parse_int(child.get('child_id'))
                registration_id = parse_int(child.get('registration_id'))
                if child_id is None or registration_id is None:
                    logger.warning('Missing child_id or registration_id for child: %s', child)
                    continue
                if allowed.get(registration_id) != child_id:
                    logger.warning(
                        'Skipping attendance for registration %s / child %s outside school %s',
                        registration_id, child_id, school_id,
                    )
                    continue

                attended = 'No' if child.get('attended') == 'No' else 'Yes'
                if attended == 'No':
                    absence_reason = _choice_or_none(child.get('absence_reason'), valid_absence_reasons)
                    absence_reason_other = (child.get('absence_reason_other') or '')[:500]
                else:
                    absence_reason = None
                    absence_reason_other = ''

                attendance_child, _child_created = ALPAttendanceChild.objects.get_or_create(
                    attendance_day=attendance,
                    child_id=child_id,
                    registration_id=registration_id,
                )
                attendance_child.attended = attended
                attendance_child.absence_reason = absence_reason
                attendance_child.absence_reason_other = absence_reason_other
                attendance_child.save()

        return True
    except Exception as ex:
        logger.exception('create_attendance failed: %s', ex)
        return False


def _teacher_fullname(teacher):
    return ' '.join(part for part in (teacher.first_name, teacher.last_name) if part)


def load_teacher_attendance(school_id, attendance_date_str):
    empty = {'instances': [], 'new_instances': []}
    attendance_date = _as_date(parse_date_flexible(attendance_date_str))
    if school_id is None or attendance_date is None:
        return empty

    teachers = ALPTeacher.objects.filter(school_id=school_id).order_by('id')
    existing_attendances = ALPTeacherAttendance.objects.filter(
        teacher__in=teachers,
        date=attendance_date,
    ).select_related('teacher').order_by('id')

    existing_teachers = []
    existing_ids = []
    for att in existing_attendances:
        if att.teacher is None:
            continue
        existing_ids.append(att.teacher_id)
        existing_teachers.append({
            'teacher_id': att.teacher_id,
            'teacher_fullname': _teacher_fullname(att.teacher),
            'status': att.status or '',
        })

    new_teachers = [{
        'teacher_id': teacher.id,
        'teacher_fullname': _teacher_fullname(teacher),
        'status': 'Present',
    } for teacher in teachers.exclude(id__in=existing_ids)]

    return {'instances': existing_teachers, 'new_instances': new_teachers}


def create_teacher_attendance(data, school_id, user):
    """Persist teacher attendance for the teachers of ``school_id`` only."""
    if not isinstance(data, dict) or school_id is None:
        return False

    attendance_date = _as_date(parse_date_flexible(data.get('attendance_date')))
    if attendance_date is None:
        logger.error('Invalid date format: %s', data.get('attendance_date'))
        return False
    if attendance_date > _today():
        logger.error('Refusing to save teacher attendance for a future date: %s', attendance_date)
        return False

    rows = data.get('teachers_attendance') or []
    if not isinstance(rows, list):
        return False

    school_teacher_ids = set(
        ALPTeacher.objects.filter(school_id=school_id).values_list('id', flat=True)
    )
    status_choices = ALPTeacherAttendance._meta.get_field('status').choices

    try:
        with transaction.atomic():
            for teacher_data in rows:
                if not isinstance(teacher_data, dict):
                    continue
                teacher_id = parse_int(teacher_data.get('teacher_id'))
                if teacher_id is None:
                    logger.warning('Missing teacher_id for teacher: %s', teacher_data)
                    continue
                if teacher_id not in school_teacher_ids:
                    logger.warning('Skipping attendance for teacher %s outside school %s', teacher_id, school_id)
                    continue

                status = _choice_or_none(teacher_data.get('status'), status_choices) or 'Present'
                teacher_attendance, _created = ALPTeacherAttendance.objects.get_or_create(
                    teacher_id=teacher_id,
                    date=attendance_date,
                )
                teacher_attendance.status = status
                teacher_attendance.owner = user
                teacher_attendance.save()

        return True
    except Exception as ex:
        logger.exception('create_teacher_attendance failed: %s', ex)
        return False
