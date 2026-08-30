from student_registration.users.templatetags.custom_tags import has_group

def user_has_alp_permission(user):
    return has_group(user, 'ALP_SCHOOL')

def filter_by_school(queryset, user):
    """
    Filter the queryset to only include records related to the user's school.
    Superusers can see all records.
    """
    if user.is_superuser:
        return queryset

    # Most ALP models have a school field directly. Related attendance models
    # must be filtered through their owning teacher or registration instead.
    model_name = queryset.model.__name__

    if model_name in ['ALPRegistration', 'ALPTeacher']:
        return queryset.filter(school=user.school)
    elif model_name == 'ALPAttendance':
        return queryset.filter(school=user.school)
    elif model_name == 'ALPTeacherAttendance':
        return queryset.filter(teacher__school=user.school)
    elif model_name == 'ALPGrading':
        return queryset.filter(registration__school=user.school)

    return queryset
from datetime import datetime
import logging

from django.db import transaction
from django.db.models import Subquery, OuterRef, Exists
from .models import ALPAttendance, ALPAttendanceChild, ALPRegistration

logger = logging.getLogger(__name__)

def parse_date_flexible(date_str):
    if not date_str:
        return None
    for fmt in ('%m/%d/%Y', '%Y-%m-%d'):
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    return None

def load_child_attendance(school_id, round_id, attendance_date_str, programme_id):

    attendance = None

    if attendance_date_str is not None:
        attendance_date = parse_date_flexible(attendance_date_str)
        attendance_day = attendance_date.date() if hasattr(attendance_date, "date") else attendance_date

        attendance = ALPAttendance.objects.filter(
            school_id=school_id,
            attendance_date=attendance_date,
            programme_id=programme_id,
            round_id=round_id,
        ).last()

    existing_children = []
    new_children = []

    try:
        if attendance:
            attendances = ALPAttendanceChild.objects.filter(attendance_day=attendance)

            existing_ids = []
            for attendance_child in attendances:
                existing_ids.append(attendance_child.registration.id)

                attendance_record = {
                    'registration_id': attendance_child.registration.id,
                    'child_id': attendance_child.child.id,
                    'child_fullname': attendance_child.child.full_name,
                    'child_mother_fullname': attendance_child.child.mother_fullname,
                    'child_birthday': attendance_child.child.birthday,
                    'child_nationality': attendance_child.child.nationality.name,
                    'attended': attendance_child.attended,
                    'absence_reason': attendance_child.absence_reason,
                    'absence_reason_other': attendance_child.absence_reason_other,
                }

                existing_children.append(attendance_record)

            registrations = (
                ALPRegistration.objects.filter(
                    school_id=school_id,
                    deleted=False,
                    round_id=round_id,
                    programme_id=programme_id,
                )
                .exclude(id__in=existing_ids)
            )

            for registration_child in registrations:
                registration_record = {
                    'registration_id': registration_child.id,
                    'child_id': registration_child.child.id,
                    'child_fullname': registration_child.child.full_name,
                    'child_mother_fullname': registration_child.child.mother_fullname,
                    'child_birthday': registration_child.child.birthday,
                    'child_nationality': registration_child.child.nationality.name,
                    'attended': 'Yes',
                    'absence_reason': '',
                    'absence_reason_other': '',
                }
                new_children.append(registration_record)

        else:
            registrations = (
                ALPRegistration.objects.filter(
                    school_id=school_id,
                    deleted=False,
                    round_id=round_id,
                    programme_id=programme_id,
                )
            )

            for registration_child in registrations:
                registration_record = {
                    'registration_id': registration_child.id,
                    'child_id': registration_child.child.id,
                    'child_fullname': registration_child.child.full_name,
                    'child_mother_fullname': registration_child.child.mother_fullname,
                    'child_birthday': registration_child.child.birthday,
                    'child_nationality': registration_child.child.nationality.name,
                    'attended': 'Yes',
                    'absence_reason': '',
                    'absence_reason_other': '',
                }
                existing_children.append(registration_record)

        return {'instances': existing_children, 'new_instances': new_children}

    except Exception as ex:
        logger.exception(ex)
        return {'instances': [], 'new_instances': []}

def create_attendance(data, school_id):
    round_id = data.get("round_id")
    programme_id = data.get("programme")

    attendance_date = parse_date_flexible(data["attendance_date"])
    if not attendance_date:
        logger.error(f"Invalid date format: {data['attendance_date']}")
        return False

    try:
        attendance, created = ALPAttendance.objects.get_or_create(
            round_id=round_id,
            school_id=school_id,
            attendance_date=attendance_date,
            programme_id=programme_id,
        )
        attendance.day_off = data.get("attendance_day_off")
        attendance.close_reason = data.get("close_reason")
        attendance.save()

        for child in data.get('children_attendance', []):
            child_id = child.get('child_id')
            registration_id = child.get('registration_id')

            if not child_id or not registration_id:
                logger.warning(f"Missing child_id or registration_id for child: {child}")
                continue

            attendance_child, child_created = ALPAttendanceChild.objects.get_or_create(
                attendance_day=attendance,
                child_id=child_id,
                registration_id=registration_id
            )

            attendance_child.attended = child.get('attended')
            attendance_child.absence_reason = child.get('absence_reason')
            attendance_child.absence_reason_other = child.get('absence_reason_other')
            attendance_child.save()

        return True
    except Exception as ex:
        logger.exception("create_attendance failed: %s", ex)
        return False

from .models import ALPTeacher, ALPTeacherAttendance

def load_teacher_attendance(school_id, attendance_date_str):
    if not attendance_date_str:
        return {'instances': [], 'new_instances': []}

    attendance_date = parse_date_flexible(attendance_date_str)
    if not attendance_date:
        return {'instances': [], 'new_instances': []}

    attendance_date = attendance_date.date() if hasattr(attendance_date, "date") else attendance_date

    existing_teachers = []
    new_teachers = []

    try:
        teachers = ALPTeacher.objects.filter(school_id=school_id)
        existing_attendances = ALPTeacherAttendance.objects.filter(
            teacher__in=teachers,
            date=attendance_date
        ).select_related('teacher')

        existing_ids = [att.teacher.id for att in existing_attendances]

        for att in existing_attendances:
            teacher_record = {
                'teacher_id': att.teacher.id,
                'teacher_fullname': att.teacher.first_name + ' ' + (att.teacher.last_name or ''),
                'status': att.status,
            }
            existing_teachers.append(teacher_record)

        for teacher in teachers.exclude(id__in=existing_ids):
            teacher_record = {
                'teacher_id': teacher.id,
                'teacher_fullname': teacher.first_name + ' ' + (teacher.last_name or ''),
                'status': 'Present',
            }
            new_teachers.append(teacher_record)

        return {'instances': existing_teachers, 'new_instances': new_teachers}

    except Exception as ex:
        logger.exception(ex)
        return {'instances': [], 'new_instances': []}


def create_teacher_attendance(data, school_id, user):
    attendance_date = parse_date_flexible(data.get("attendance_date"))
    if not attendance_date:
        logger.error(f"Invalid date format: {data.get('attendance_date')}")
        return False

    attendance_date = attendance_date.date() if hasattr(attendance_date, "date") else attendance_date

    try:
        for teacher_data in data.get('teachers_attendance', []):
            teacher_id = teacher_data.get('teacher_id')
            if not teacher_id:
                logger.warning(f"Missing teacher_id for teacher: {teacher_data}")
                continue

            teacher_attendance, created = ALPTeacherAttendance.objects.get_or_create(
                teacher_id=teacher_id,
                date=attendance_date,
            )

            teacher_attendance.status = teacher_data.get('status')
            teacher_attendance.owner = user
            teacher_attendance.save()

        return True
    except Exception as ex:
        logger.exception("create_teacher_attendance failed: %s", ex)
        return False
