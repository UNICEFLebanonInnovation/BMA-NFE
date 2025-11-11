# -- coding: utf-8 --
from itertools import chain
import logging

from datetime import datetime, date
from django.core.exceptions import ValidationError
from django.db.models import Exists, OuterRef, Subquery
from django import forms
from import_export import resources, fields
from django.db import transaction

from student_registration.students.models import Student
from student_registration.clm.models import (
    Bridging,
)
from student_registration.attendances.models import MSCCAttendance, MSCCAttendanceChild
from student_registration.mscc.models import Registration, EducationService, Referral

logger = logging.getLogger(__name__)



def to_array(fields, obj):
    data = {}
    for field_name in fields:
        if hasattr(obj, field_name):
            value = getattr(obj, field_name)
            if hasattr(value, 'id'):
                value = getattr(value, 'id')
            data[field_name] = value

    return data


def generate_services(child_age, registry, user=None):
    try:
        from .models import ProvidedServices, Packages
        from student_registration.users.templatetags.custom_tags import has_group

        packages = Packages.objects.filter(type=registry.type, age=child_age)
        if user and has_group(user, 'MSCC_YOUTH'):
            packages = packages.filter(category="Youth")

        for package in packages.all():
            instance, created = ProvidedServices.objects.get_or_create(name=package.name,
                                                                       registration=registry,
                                                                       type=package.type,
                                                                       category=package.category)
            instance.save()
    except Exception as ex:
        return False


def regenerate_services(child_age, registry, user=None):
    from .templatetags.simple_tags import service_data
    from .models import ProvidedServices

    ProvidedServices.objects.filter(registration=registry).delete()
    generate_services(child_age, registry, user)
    service = service_data('EducationService', registry)
    if service:
        service.education_program = ""
        service.save()


def update_service(service_name, registry_id, service_id):
    from .models import ProvidedServices
    ProvidedServices.objects.filter(registration_id=registry_id,
                                    name=service_name).update(service_id=service_id,
                                                              completed=True,
                                                              completion_date=datetime.now())


def generate_education_history(registration_id, child_id, student_old_id):
    from .models import EducationHistory

    # 'BLN'
    bln_old_registrations = BLN.objects.filter(student_id=student_old_id).values_list('id', flat=True)
    bln_old_registrations = list(bln_old_registrations)

    for reg_id in bln_old_registrations:
        instance, created = EducationHistory.objects.get_or_create(registration_id=registration_id,
                                                                   child=child_id,
                                                                   student_old=student_old_id,
                                                                   programme_type = 'BLN',
                                                                   programme_id = reg_id)
        instance.save()

    # 'ABLN'
    abln_old_registrations = ABLN.objects.filter(student_id=student_old_id).values_list('id', flat=True)
    abln_old_registrations = list(abln_old_registrations)

    for reg_id in abln_old_registrations:
        instance, created = EducationHistory.objects.get_or_create(registration_id=registration_id,
                                                                   child=child_id,
                                                                   student_old=student_old_id,
                                                                   programme_type='ABLN',
                                                                   programme_id=reg_id)
        instance.save()

    # 'Bridging'
    bridging_old_registrations = Bridging.objects.filter(student_id=student_old_id).values_list('id', flat=True)
    bridging_old_registrations = list(bridging_old_registrations)

    for reg_id in bridging_old_registrations:
        instance, created = EducationHistory.objects.get_or_create(registration_id=registration_id,
                                                                   child=child_id,
                                                                   student_old=student_old_id,
                                                                   programme_type='Bridging',
                                                                   programme_id=reg_id)
        instance.save()


    # 'RS'
    rs_old_registrations = RS.objects.filter(student_id=student_old_id).values_list('id', flat=True)
    rs_old_registrations = list(rs_old_registrations)

    for reg_id in rs_old_registrations:
        instance, created = EducationHistory.objects.get_or_create(registration_id=registration_id,
                                                                   child=child_id,
                                                                   student_old=student_old_id,
                                                                   programme_type='RS',
                                                                   programme_id=reg_id)
        instance.save()

    # 'CBECE'
    cbece_old_registrations = CBECE.objects.filter(student_id=student_old_id).values_list('id', flat=True)
    cbece_old_registrations = list(cbece_old_registrations)

    for reg_id in cbece_old_registrations:
        instance, created = EducationHistory.objects.get_or_create(registration_id=registration_id,
                                                                   child=child_id,
                                                                   student_old=student_old_id,
                                                                   programme_type='CBECE',
                                                                   programme_id=reg_id)
        instance.save()

    # 'Inclusion'
    inclusion_old_registrations = Inclusion.objects.filter(student_id=student_old_id).values_list('id', flat=True)
    inclusion_old_registrations = list(inclusion_old_registrations)

    for reg_id in inclusion_old_registrations:
        instance, created = EducationHistory.objects.get_or_create(registration_id=registration_id,
                                                                   child=child_id,
                                                                   student_old=student_old_id,
                                                                   programme_type='Inclusion',
                                                                   programme_id=reg_id)
        instance.save()


def create_attendance(data, center_id):
    from datetime import datetime
    round_id = data["round_id"]
    education_program = data["education_program"]
    class_section = data["class_section"]
    try:
        attendance, created = MSCCAttendance.objects.get_or_create(round_id=round_id, center_id=center_id,
                                                                   attendance_date=datetime.strptime(data["attendance_date"], '%m/%d/%Y'),
                                                                   education_program=education_program,
                                                                   class_section=class_section
                                                                   )
        attendance.day_off = data["attendance_day_off"]
        attendance.close_reason = data["close_reason"]
        attendance.save()

        for child in data.get('children_attendance', []):
            child_id = child.get('child_id')
            registration_id = child.get('registration_id')

            if not child_id or not registration_id:
                logger.warning(f"Missing child_id or registration_id for child: {child}")
                continue

            attendance_child, created = MSCCAttendanceChild.objects.get_or_create(
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
        logger.exception("Error in create_attendance: %s", ex)
        return False


def load_child_attendance(center_id, round_id, attendance_date, education_program, class_section):
    from datetime import datetime

    attendance = None

    if attendance_date is not None:
        attendance_date = datetime.strptime(attendance_date, '%m/%d/%Y')

        attendance = MSCCAttendance.objects.filter(
            center_id=center_id,
            attendance_date=attendance_date,
            education_program=education_program,
            class_section=class_section,
            round_id=round_id,
        ).last()

    existing_children = []
    new_children = []

    try:
        if attendance:
            attendances = MSCCAttendanceChild.objects.filter(attendance_day=attendance)

            existing_ids = []
            for attendance in attendances:
                existing_ids.append(attendance.registration.id)
                attendance_record = {
                    'registration_id': attendance.registration.id,
                    'child_id': attendance.child.id,
                    'child_fullname': attendance.child.full_name,
                    'child_mother_fullname': attendance.child.mother_fullname,
                    'child_birthday': attendance.child.birthday,
                    'child_nationality': attendance.child.nationality.name,
                    'attended': attendance.attended,
                    'absence_reason': attendance.absence_reason,
                    'absence_reason_other': attendance.absence_reason_other,
                }

                existing_children.append(attendance_record)

            registrations = (
                Registration.objects.filter(
                    center_id=center_id,
                    type='Core-Package',
                    deleted=False,
                    round_id=round_id,
                )
                .annotate(
                    has_education_service=Exists(
                        EducationService.objects.filter(
                            registration_id=OuterRef('pk'),
                            education_program=education_program,
                            class_section=class_section,
                        )
                    )
                )
                .filter(has_education_service=True)
                .exclude(
                    id__in=Subquery(
                        Referral.objects.filter(
                            registration_id=OuterRef('pk'),
                            recommended_learning_path='Drop out',
                            dropout_date__lte=attendance_date,
                        ).values('registration_id')
                    )
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
                Registration.objects.filter(
                    center_id=center_id,
                    type='Core-Package',
                    deleted=False,
                    round_id=round_id,
                )
                .annotate(
                    has_education_service=Exists(
                        EducationService.objects.filter(
                            registration_id=OuterRef('pk'),
                            education_program=education_program,
                            class_section=class_section,
                        )
                    )
                )
                .filter(has_education_service=True)
                .exclude(
                    id__in=Subquery(
                        Referral.objects.filter(
                            registration_id=OuterRef('pk'),
                            recommended_learning_path='Drop out',
                            dropout_date__lte=attendance_date,
                        ).values('registration_id')
                    )
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


def update_child_attendance(registration_id, education_program, old_class_section, new_class_section):
    try:
        with transaction.atomic():
            children = list(
                MSCCAttendanceChild.objects.filter(
                    registration_id=registration_id,
                    attendance_day__education_program=education_program,
                    attendance_day__class_section=old_class_section,
                ).select_related('attendance_day__center')
            )

            for ca in children:
                old_attendance = ca.attendance_day
                old_attendance_id = old_attendance.id
                center_id = old_attendance.center_id
                attendance_date = old_attendance.attendance_date

                new_attendance = (
                    MSCCAttendance.objects
                    .filter(
                        center_id=center_id,
                        attendance_date=attendance_date,
                        education_program=education_program,
                        class_section=new_class_section,
                    )
                    .order_by('id')
                    .last()
                )

                others_count = (
                    MSCCAttendanceChild.objects
                    .filter(attendance_day=old_attendance)
                    .exclude(pk=ca.pk)
                    .count()
                )

                if new_attendance:
                    ca.attendance_day = new_attendance
                    ca.save(update_fields=['attendance_day'])
                else:
                    MSCCAttendanceChild.objects.filter(pk=ca.pk).delete()

                if others_count == 0:
                    # delete old attendance if now empty
                    MSCCAttendance.objects.filter(pk=old_attendance_id).delete()

        return []
    except Exception as ex:
        logger.exception("update_child_attendance failed: %s", ex)
        return []


class RegistrationResource(resources.ModelResource):
    class Meta:
        model = Registration
        fields = (
            'id',
            'child__id',
            'student_old',
            'partner__name',
            'type',
            'center__name',
            'center__governorate__name',
            'center__caza__name',
            'center__cadaster__name',
            'child__id',
            'child__number',
            'child__first_name',
            'child__father_name',
            'child__last_name',
            'child__mother_fullname',
            'child__gender',
            'child__nationality__name',
            'child__nationality_other',
            'child__birthday_year',
            'child__birthday_month',
            'child__birthday_day',
            'child__p_code',
            'child__address',
            'child__disability',
            'child__marital_status',
            'child__have_children',
            'child__children_number',
            'source_of_identification',
            'source_of_identification_specify',
            'cash_support_programmes',
            'child__father_educational_level',
            'child__mother_educational_level',
            'child__first_phone_owner',
            'child__first_phone_number',
            'child__first_phone_number_confirm',
            'child__second_phone_owner',
            'child__second_phone_number',
            'child__second_phone_number_confirm',
            'child__main_caregiver',
            'child__main_caregiver_other',
            'child__caregiver_first_name',
            'child__caregiver_middle_name',
            'child__caregiver_last_name',
            'child__caregiver_mother_name',
            'child__main_caregiver_nationality__name',
            'child__main_caregiver_nationality_other',
            'have_labour',
            'labour_type',
            'labour_type_specify',
            'labour_hours',
            'labour_weekly_income',
            'child__id_type',
            'child__case_number',
            'child__case_number_confirm',
            'child__parent_individual_case_number',
            'child__parent_individual_case_number_confirm',
            'child__individual_case_number',
            'child__individual_case_number_confirm',
            'child__recorded_number',
            'child__recorded_number_confirm',
            'child__parent_national_number',
            'child__parent_national_number_confirm',
            'child__national_number',
            'child__national_number_confirm',
            'child__parent_syrian_national_number',
            'child__parent_syrian_national_number_confirm',
            'child__syrian_national_number',
            'child__syrian_national_number_confirm',
            'child__parent_sop_national_number',
            'child__parent_sop_national_number_confirm',
            'child__sop_national_number',
            'child__sop_national_number_confirm',
            'child__parent_other_number',
            'child__parent_other_number_confirm',
            'child__other_number',
            'child__other_number_confirm',
            'registration_date',
            'owner__username',
            'modified_by__username',
            'created',
            'modified',
        )
        export_order = fields


def load_dashboard_data(param, grouping):
    from django.db import connection

    cursor = connection.cursor()
    cursor.execute(
        "SELECT count(mr.id), "+grouping+" "
        "FROM public.mscc_registration mr, public.child_child cc "
        "WHERE mr.child_id = cc.id "+param+" "
        "GROUP By "+grouping
    )

    rows = cursor.fetchall()
    return rows


class TrimmedDateField(forms.DateField):
    """DateField that strips whitespace before parsing."""

    def to_python(self, value):
        if hasattr(value, 'strip'):
            value = value.strip()
        return super().to_python(value)


def validate_date(date_str):

    if not date_str:
        return None

    # If the value is already a date object, return it as is
    if isinstance(date_str, date):
        return date_str

    # Trim white spaces from the provided value
    if hasattr(date_str, 'strip'):
        date_str = date_str.strip()

    # Supported date format
    formats = ['%Y-%m-%d']
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue

    raise ValidationError("Date is not valid. Please use the format YYYY-MM-DD.")


