# -- coding: utf-8 --
from itertools import chain
import logging

from datetime import datetime, date
from django.core.exceptions import ValidationError
from django.db.models import Exists, OuterRef, Subquery
from django import forms
from import_export import resources, fields
from django.db import transaction

from student_registration.outreach.models import OutreachChild
from student_registration.students.models import Student
from student_registration.clm.models import (
    BLN,
    ABLN,
    Bridging,
    RS,
    CBECE,
    Inclusion
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


def get_outreach_child(outreach_id):
    initial = {}
    instance = OutreachChild.objects.get(id=outreach_id)

    initial['child_outreach'] = instance.id
    initial['child_first_name'] = instance.first_name
    initial['child_father_name'] = instance.outreach_caregiver.father_name
    initial['child_last_name'] = instance.outreach_caregiver.last_name
    initial['child_mother_fullname'] = instance.outreach_caregiver.mother_full_name
    initial['child_birthday_year'] = instance.birthday_year
    initial['child_birthday_month'] = instance.birthday_month
    initial['child_birthday_day'] = instance.birthday_day
    initial['child_gender'] = (instance.gender or '').strip()
    initial['child_address'] = instance.outreach_caregiver.address

    nationality_raw = instance.nationality or ''
    nationality = nationality_raw.strip().lower()
    nationality_map = {
        'syrian': 1,
        'سورية': 1,
        'lebanese': 5,
        'لبنانية': 5,
        'palestinian from syria': 3,
        'فلسطينية  - من سوريا': 3,
        'palestinian from lebanon': 4,
        'فلسطينية - من لبنان': 4,
        'iraqi': 2,
        'عراقية': 2,
        'stateless': 7,
        'other': 6,
        'اخرى': 6
    }
    initial['child_nationality'] = nationality_map.get(nationality, None)
    initial['child_nationality_other'] = instance.nationality_other

    disability_raw = (instance.disability or '').strip()
    if not disability_raw:
        initial['child_disability'] = 1
    else:
        disability_key = disability_raw.lower()
        disability_map = {
            'no': 1, 'كلا': 1,
            'other': 2, 'other difficulties': 2, 'غير ذالك': 2,
            'difficulty hearing': 3, 'difficulty_hearing': 3, 'صعوبة في السمع': 3,
            'difficulty walking or moving hands': 4, 'difficulty_walking_or_moving_hands': 4, 'صعوبة في الحركة': 4,
            'difficulty speaking': 5, 'difficulty_speaking': 5, 'صعوبة في التحدث': 5,
            'difficulty seeing': 6, 'difficulty_seeing': 6, 'صعوبة في الرؤية': 6,
            'difficulty with self-care': 7, 'صعوبة في الرعاية الذاتية - الأكل، خلع الملابس': 7,
            'learning difficulties': 8, 'learning_difficulties': 8, 'صعوبة في التعلم': 8,
            'difficulty interacting with others': 9, 'difficulty_interacting_with_others': 9,
            'صعوبة التفاعل مع الآخرين': 9,
            'intellectual disability': 10, 'intellectual_disability': 10, 'الإعاقة الذهنية': 10
        }
        initial['child_disability'] = disability_map.get(disability_key, None)

    initial['disability_other'] = instance.disability_other

    family_status_raw = instance.family_status or ''
    family_status_key = family_status_raw.strip().lower()
    status_map = {
        'widow': 'Widowed',
        'widowed': 'Widowed',
        'widower': 'Widowed',
        'separated': 'Divorced',
        'divorced': 'Divorced',
        'married': 'Married',
        'engaged': 'Engaged',
        'single': 'Single'
    }
    initial['child_marital_status'] = status_map.get(family_status_key, family_status_raw)

    initial['child_have_children'] = (instance.have_children or '').strip().capitalize()

    living_arrangement_raw = instance.living_arrangement or ''
    living_arrangement_key = living_arrangement_raw.strip()
    living_arrangement_map = {
        'Unaccompanied': 'Unaccompanied',
        'Separated': 'Separated',
        'Living with one caregivers': 'Living with one caregivers',
        'Living with caregivers': 'Living with caregivers',
        'Child headed household': 'Child headed household',
        'Married and living with extended family': 'Married and living with extended family',
    }
    initial['child_living_arrangement'] = living_arrangement_map.get(living_arrangement_key, living_arrangement_raw)

    initial['child_have_sibling'] = (instance.have_sibling or '').strip().capitalize()
    initial['child_siblings_have_disability'] = (instance.siblings_have_disability or '').strip().capitalize()
    initial['child_mother_pregnant_expecting'] = (instance.mother_pregnant_expecting or '').strip().capitalize()

    source_of_identification_raw = instance.source_of_identification or ''
    source_of_identification_key = source_of_identification_raw.strip()
    source_of_identification_map = {
        'Dirassa': 'Dirassa',
        'Awareness Session': 'Awareness Session',
        'Child\'s parents': 'Child\'s parents',
        'From Hosted Community': 'From Hosted Community',
        'From Host Community': 'From Hosted Community',
        'Sector Partners referral (CP, Education, Health, Wash, Youth, Palestenian program...)': 'Sector Partners referral (CP, Education, Health, Wash, Youth, Palestenian program...) ',
        'From Profiling Database': 'From Profiling Database',
        'From Other NGO': 'From Other NGO',
        'From Displaced Community': 'From Displaced Community',
        'Referred by the municipality/Other formal sources': 'Referred by the municipality/Other formal sources',
        'Other Sources': 'Other Sources',
    }
    initial['source_of_identification'] = source_of_identification_map.get(source_of_identification_key, source_of_identification_raw)

    initial['children_number_under18'] = instance.children_number_under18

    main_care_nat_raw = instance.outreach_caregiver.caregiver_nationality or ''
    main_care_nat = main_care_nat_raw.strip().lower()
    initial['main_caregiver_nationality'] = nationality_map.get(main_care_nat, None)
    initial['main_caregiver_nationality_other'] = instance.outreach_caregiver.caregiver_nationality_other

    working_status_raw = (instance.working_status or '').strip()
    working_status_map = {
        'yes - morning': 'Yes - Morning',
        'Yes -Morning': 'Yes - Morning',
        'yes - afternoon': 'Yes - Afternoon',
        'Yes-Afternoon': 'Yes - Afternoon',
        'no': 'No',
        'yes': 'Yes - Full day',
        'Yes - Night Shift': 'Yes - Night Shift',
        'Yes - Morning & Night Shift': 'Yes - Morning & Night Shift',
        'Yes - Afternoon & Night Shift': 'Yes - Afternoon & Night Shift',
        'Yes - Full Day & Night Shift': 'Yes - Full Day & Night Shift',
    }
    if not working_status_raw:
        initial['have_labour'] = 'No'
    else:
        initial['have_labour'] = working_status_map.get(working_status_raw)

    labour_type_raw = instance.work_type or ''
    labour_type_key = labour_type_raw.strip().lower()
    labour_type_map = {
        'manufacturing_producing': 'manufacturing',
        'manufacturing': 'manufacturing',
        'garage_mechanics_workshop': '',
        'construction_site': 'building',
        'building': 'building',
        'shop_restaurant_bakery_barber': 'retail_store',
        'retail_store': 'retail_store',
        'street_connected_work__begging__vending_': 'begging',
        'begging': 'begging',
        'agriculture_animal_herding': 'agriculture',
        'agriculture': 'agriculture',
        'others': 'other_many_other',
        'other_many_other': 'other_many_other',
        'other': 'other_many_other'
    }
    initial['labour_type'] = labour_type_map.get(labour_type_key, '')
    initial['labour_type_specify'] = instance.work_type_other

    initial['first_phone_number'] = instance.outreach_caregiver.primary_phone
    initial['first_phone_number_confirm'] = instance.outreach_caregiver.primary_phone

    first_phone_owner_raw = instance.outreach_caregiver.first_phone_owner or ''
    first_phone_owner_key = first_phone_owner_raw.strip()
    phone_owner_map = {
        'Phone Main Caregiver': 'Phone Main Caregiver',
        'Family Member': 'Family Member',
        'Father': 'Phone Main Caregiver',
        'Mother': 'Phone Main Caregiver',
        'Neighbors': 'Neighbors',
        'Shawish': 'Shawish',
    }
    initial['first_phone_owner'] = phone_owner_map.get(first_phone_owner_key, '')

    initial['second_phone_number'] = instance.outreach_caregiver.secondary_phone
    initial['second_phone_number_confirm'] = instance.outreach_caregiver.secondary_phone

    main_caregiver = (instance.outreach_caregiver.main_caregiver or '').strip()
    if main_caregiver == u'الاب':
        initial['main_caregiver'] = 'Father'   # match *_correct option value
        initial['caregiver_first_name'] = instance.outreach_caregiver.father_name
        initial['caregiver_last_name'] = instance.outreach_caregiver.last_name
    else:
        if main_caregiver == u'الام':
            initial['main_caregiver'] = 'Mother'
        elif main_caregiver == u'اخر':
            initial['main_caregiver'] = 'Other'
        else:
            initial['main_caregiver'] = (main_caregiver or '').lower() or None
        initial['caregiver_first_name'] = instance.outreach_caregiver.caregiver_first_name
        initial['caregiver_last_name'] = instance.outreach_caregiver.caregiver_last_name

    initial['caregiver_middle_name'] = instance.outreach_caregiver.caregiver_father_name
    initial['caregiver_mother_name'] = instance.outreach_caregiver.caregiver_mother_name

    id_type = instance.outreach_caregiver.id_type
    if id_type == 'unhcr_registered' or id_type == 'UNHCR registered':
        initial['id_type'] = 1
        initial['case_number'] = instance.outreach_caregiver.unhcr_case_number
        initial['case_number_confirm'] = instance.outreach_caregiver.unhcr_case_number
        initial['parent_individual_case_number'] = instance.outreach_caregiver.caregiver_unhcr_id
        initial['parent_individual_case_number_confirm'] = instance.outreach_caregiver.caregiver_unhcr_id
        initial['individual_case_number'] = instance.child_unhcr_number
        initial['individual_case_number_confirm'] = instance.child_unhcr_number
    elif id_type == 'unhcr_recorded' or id_type == 'UNHCR recorded':
        initial['id_type'] = 2
        initial['recorded_number'] = instance.outreach_caregiver.unhcr_barcode
        initial['recorded_number_confirm'] = instance.outreach_caregiver.unhcr_barcode
    elif id_type == 'syrian_id' or id_type == 'Syrian ID':
        initial['id_type'] = 3
        initial['parent_syrian_national_number'] = instance.outreach_caregiver.caregiver_personal_id
        initial['parent_syrian_national_number_confirm'] = instance.outreach_caregiver.caregiver_personal_id
        initial['syrian_national_number'] = instance.child_personal_id
        initial['syrian_national_number_confirm'] = instance.child_personal_id
    elif id_type == 'palestinian_id' or id_type == 'Palestinian ID':
        initial['id_type'] = 4
        initial['parent_sop_national_number'] = instance.outreach_caregiver.caregiver_personal_id
        initial['parent_sop_national_number_confirm'] = instance.outreach_caregiver.caregiver_personal_id
        initial['sop_national_number'] = instance.child_personal_id
        initial['sop_national_number_confirm'] = instance.child_personal_id
    elif id_type == 'lebanese_id' or id_type == 'Lebanese ID':
        initial['id_type'] = 5
        initial['parent_national_number'] = instance.outreach_caregiver.caregiver_personal_id
        initial['parent_national_number_confirm'] = instance.outreach_caregiver.caregiver_personal_id
        initial['national_number'] = instance.child_personal_id
        initial['national_number_confirm'] = instance.child_personal_id
    elif id_type == 'other_nationality_id' or id_type == 'Other Nationality ID':
        initial['id_type'] = 6
        initial['parent_national_number'] = instance.outreach_caregiver.caregiver_personal_id
        initial['parent_national_number_confirm'] = instance.outreach_caregiver.caregiver_personal_id
        initial['national_number'] = instance.child_personal_id
        initial['national_number_confirm'] = instance.child_personal_id
    elif id_type == 'No_papers' or id_type == 'No papers':
        initial['id_type'] = 7

    education_map = {
        'لا تعليم رسمي': 1,
        'غير متعلم لكنه يجيد القراءة والكتابة / غير متعلمة لكنها تجيد القرأة و الكتابة': 2,
        'بعض التعليم الإبتدائي-إكمال صف 1 إلى صف 5': 4,
        'تعليم إبتدائي': 4,
        'مرحلة متوسطة': 5,
        'مرحلة ثانوي': 6,
        'جامعي أو دراسات عليا': 7,
        'N/A': 8
    }
    mother_education_raw = instance.outreach_caregiver.mother_education_level
    mother_education = (mother_education_raw or '').strip()
    initial['mother_educational_level'] = education_map.get(mother_education, '')

    father_education_raw = instance.outreach_caregiver.father_education_level
    father_education = (father_education_raw or '').strip()

    initial['father_educational_level'] = education_map.get(father_education, '')

    return initial


def get_old_child(student_id):
    initial = {}
    instance = Student.objects.get(id=student_id)
    initial['student_old'] = instance.id
    initial['child_first_name'] = instance.first_name
    initial['child_father_name'] = instance.father_name
    initial['child_last_name'] = instance.last_name
    initial['child_mother_fullname'] = instance.mother_fullname
    initial['child_birthday_year'] = instance.birthday_year
    initial['child_birthday_month'] = instance.birthday_month
    initial['child_birthday_day'] = instance.birthday_day
    initial['child_gender'] = instance.sex
    initial['child_nationality'] = instance.nationality.id if instance.nationality else 0
    initial['child_marital_status'] = instance.family_status

    # initial['id_type'] = instance.outreach_caregiver.id_type
    # initial['case_number'] = instance.outreach_caregiver.unhcr_case_number
    # initial['case_number_confirm'] = instance.outreach_caregiver.unhcr_case_number
    # initial['parent_individual_case_number'] = instance.outreach_caregiver.caregiver_unhcr_id
    # initial['parent_individual_case_number_confirm'] = instance.outreach_caregiver.caregiver_unhcr_id
    # initial['individual_case_number'] = instance.child_unhcr_number
    # initial['individual_case_number_confirm'] = instance.child_unhcr_number
    # initial['recorded_number'] = instance.outreach_caregiver.unhcr_barcode
    # initial['recorded_number_confirm'] = instance.outreach_caregiver.unhcr_barcode
    # initial['parent_syrian_national_number'] = instance.outreach_caregiver.caregiver_personal_id
    # initial['parent_syrian_national_number_confirm'] = instance.outreach_caregiver.caregiver_personal_id
    # initial['syrian_national_number'] = instance.child_personal_id
    # initial['syrian_national_number_confirm'] = instance.child_personal_id
    # initial['parent_sop_national_number'] = instance.outreach_caregiver.caregiver_personal_id
    # initial['parent_sop_national_number_confirm'] = instance.outreach_caregiver.caregiver_personal_id
    # initial['sop_national_number'] = instance.child_personal_id
    # initial['sop_national_number_confirm'] = instance.child_personal_id
    # initial['parent_national_number'] = instance.outreach_caregiver.caregiver_personal_id
    # initial['parent_national_number_confirm'] = instance.outreach_caregiver.caregiver_personal_id
    # initial['national_number'] = instance.child_personal_id
    # initial['national_number_confirm'] = instance.child_personal_id

    return initial


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
            'child_outreach',
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


