# -*- coding: utf-8 -*-
"""Generate realistic bootstrap/pull fixtures for the mobile app screenshots.

Run against any database (the local test one is fine):

    DJANGO_SETTINGS_MODULE=config.settings.test python manage.py shell -c \\
        "from student_registration.mobile_api.tests.make_fixtures import run; run('/tmp/out')"

The script seeds reference data and a handful of registrations through the
mobile push engine, then dumps the JSON responses of ``/bootstrap/`` and
``/pull/`` (plus a sample push report) so the app can be rendered offline.
"""
from __future__ import unicode_literals

import datetime
import json
import os
import uuid
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework.test import APIClient

from student_registration.alp.models import ALPProgram, ALPRound
from student_registration.clm.models import Disability
from student_registration.locations.models import Center, Location, LocationType
from student_registration.mscc.models import Packages, Round
from student_registration.schools.models import CLMRound, EducationalLevel, PartnerOrganization, School
from student_registration.students.models import AttachmentType, IDType, Nationality, Training

User = get_user_model()


def _get_or_create(model, **kwargs):
    defaults = kwargs.pop('defaults', {})
    obj, _ = model.objects.get_or_create(defaults=defaults, **kwargs)
    return obj


def seed():
    for pk, name, name_en, code in ((1, 'سوري', 'Syrian', 'SY'), (2, 'لبناني', 'Lebanese', 'LB'),
                                    (3, 'فلسطيني', 'Palestinian', 'PS'), (6, 'أخرى', 'Other', 'OT')):
        Nationality.objects.get_or_create(id=pk, defaults={'name': name, 'name_en': name_en, 'code': code})
    for pk, name in ((1, 'UNHCR Registered'), (2, 'UNHCR Recorded'), (3, 'Syrian national ID'),
                     (4, 'Palestinian national ID'), (5, 'Lebanese national ID'),
                     (6, 'Other nationality'), (7, 'Caregiver has no ID'), (9, 'Lebanese Extract of Record')):
        IDType.objects.get_or_create(id=pk, defaults={'name': name, 'active': True})
    for name, name_en in (('لا', 'No'), ('صعوبة في الرؤية', 'Seeing'), ('صعوبة في السمع', 'Hearing'),
                          ('صعوبة في المشي', 'Walking'), ('غير ذلك', 'Other')):
        Disability.objects.get_or_create(name=name, defaults={'name_en': name_en, 'active': True})
    for name in ('Illiterate', 'Primary', 'Intermediate', 'Secondary', 'University'):
        EducationalLevel.objects.get_or_create(name=name)
    for name in ('Child protection', 'Classroom management', 'Inclusive education', 'PSS'):
        Training.objects.get_or_create(name=name)
    for name in ('Certificate', 'ID copy', 'Contract'):
        AttachmentType.objects.get_or_create(name=name)

    gov_type = _get_or_create(LocationType, name='Governorate', defaults={'name_en': 'Governorate'})
    dist_type = _get_or_create(LocationType, name='District', defaults={'name_en': 'District'})
    cad_type = _get_or_create(LocationType, name='Cadaster', defaults={'name_en': 'Cadaster'})
    bekaa = _get_or_create(Location, name='البقاع', type=gov_type,
                           defaults={'name_en': 'Bekaa', 'p_code': 'LB3'})
    zahle = _get_or_create(Location, name='زحلة', type=dist_type,
                           defaults={'name_en': 'Zahle', 'parent': bekaa, 'p_code': 'LB31'})
    bar_elias = _get_or_create(Location, name='بر الياس', type=cad_type,
                               defaults={'name_en': 'Bar Elias', 'parent': zahle, 'p_code': 'LB3101'})
    mount = _get_or_create(Location, name='جبل لبنان', type=gov_type,
                           defaults={'name_en': 'Mount Lebanon', 'p_code': 'LB2'})
    baabda = _get_or_create(Location, name='بعبدا', type=dist_type,
                            defaults={'name_en': 'Baabda', 'parent': mount, 'p_code': 'LB21'})

    partner = _get_or_create(PartnerOrganization, name='Partner NGO Lebanon',
                             defaults={'short_name': 'PNL', 'active': True})
    center = _get_or_create(Center, name='Makani Centre – Bar Elias', defaults={
        'partner': partner, 'governorate': bekaa, 'caza': zahle, 'cadaster': bar_elias, 'type': 'Community Hub',
        'programs': ['BLN', 'CBECE', 'YBLN'], 'is_active': True})
    _get_or_create(Center, name='Makani Centre – Baabda', defaults={
        'partner': partner, 'governorate': mount, 'caza': baabda, 'type': 'Municipality', 'programs': ['BLN', 'RS'],
        'is_active': True})
    school = _get_or_create(School, number='1234', defaults={
        'name': 'Bar Elias Public School', 'is_bma': True, 'type': 'Public School',
        'governorate': bekaa, 'district': zahle, 'cadaster': bar_elias})
    partner.schools.add(school)
    Round.objects.filter(current_year=True).exclude(name='2025-2026').update(current_year=False)
    _get_or_create(Round, name='2025-2026', defaults={'current_year': True, 'year': 2025})
    _get_or_create(Round, name='2024-2025', defaults={'current_year': False, 'year': 2024})
    _get_or_create(ALPRound, name='2025-2026', defaults={'current_year': True})
    for name in ('ALP', 'ALP Level 1', 'ALP Level 2'):
        _get_or_create(ALPProgram, name=name)
    _get_or_create(CLMRound, name='Bridging 2025-2026', defaults={'current_year': True, 'current_round_bridging': True})
    for category, ptype, names in (
        ('Education', 'BLN', ('BLN Level 1', 'BLN Level 2', 'BLN Level 3')),
        ('Education', 'CBECE', ('CBECE Level 1', 'CBECE Level 2', 'CBECE Level 3')),
        ('Education', 'YBLN', ('YBLN Level 1', 'YBLN Level 2')),
        ('Education', 'RS', ('RS Grade 1', 'RS Grade 2', 'RS Grade 3')),
    ):
        for name in names:
            _get_or_create(Packages, name=name,
                           defaults={'type': ptype, 'category': category, 'min_age': 6, 'max_age': 14})

    for name in ('MSCC', 'MSCC_CENTER', 'MSCC_PARTNER', 'MSCC_UNICEF', 'ALP_SCHOOL', 'CLM_Bridging', 'CLM_ATTENDANCE'):
        Group.objects.get_or_create(name=name)
    user, created = User.objects.get_or_create(username='rima.center', defaults={
        'first_name': 'Rima', 'last_name': 'Haddad', 'email': 'rima@example.org', 'partner': partner, 'center': center})
    if created:
        user.set_password('demo-pass-123')
        user.save()
    user.groups.add(Group.objects.get(name='MSCC'), Group.objects.get(name='MSCC_CENTER'))
    return user, center, partner


CHILDREN = [
    ('محمد', 'أحمد', 'السيد', 'فاطمة علي', 'Male', '2015', '3', '5', 1, '03-123456'),
    ('سارة', 'خالد', 'حسن', 'مريم يوسف', 'Female', '2014', '11', '20', 1, '70-234567'),
    ('علي', 'حسين', 'ناصر', 'زينب محمود', 'Male', '2016', '6', '1', 2, '71-345678'),
    ('لين', 'سمير', 'عبدالله', 'هدى كامل', 'Female', '2013', '1', '15', 3, '76-456789'),
    ('Omar', 'Bilal', 'Kassem', 'Nour Ahmad', 'Male', '2017', '9', '9', 1, '78-567890'),
    ('Maya', 'Jad', 'Saab', 'Rana Khoury', 'Female', '2012', '4', '30', 2, '79-678901'),
]


def registration_payload(first, father, last, mother, gender, y, m, d, nationality, phone, index=0):
    number = '12345678{:04d}'.format(index * 7 + nationality)
    return {
        'child_first_name': first, 'child_father_name': father, 'child_last_name': last,
        'child_mother_fullname': mother, 'child_gender': gender, 'child_nationality': nationality,
        'child_birthday_year': y, 'child_birthday_month': m, 'child_birthday_day': d,
        'child_address': 'Bar Elias main road', 'child_disability': Disability.objects.get(name='لا').id,
        'child_marital_status': 'Single', 'child_have_children': 'No', 'child_have_sibling': 'Yes',
        'child_siblings_have_disability': 'No', 'child_mother_pregnant_expecting': 'No',
        'child_living_arrangement': 'Living with caregivers', 'source_of_identification': 'Dirassa',
        'cash_support_programmes': ['None'],
        'father_educational_level': EducationalLevel.objects.get(name='Primary').id,
        'mother_educational_level': EducationalLevel.objects.get(name='Intermediate').id,
        'first_phone_owner': 'Phone Main Caregiver', 'first_phone_number': phone, 'first_phone_number_confirm': phone,
        'main_caregiver': 'Mother', 'children_number_under18': '3', 'caregiver_first_name': mother.split()[0],
        'caregiver_middle_name': 'Hassan', 'caregiver_last_name': mother.split()[-1], 'caregiver_mother_name': 'Amal',
        'main_caregiver_nationality': nationality, 'have_labour': 'No', 'id_type': 5,
        'parent_national_number': number, 'parent_national_number_confirm': number,
        'national_number': '9' + number[1:], 'national_number_confirm': '9' + number[1:],
    }


def reset():
    """Remove records from previous runs (scratch databases only)."""
    from student_registration.attendances.models import MSCCAttendance, MSCCAttendanceChild
    from student_registration.child.models import Child
    from student_registration.mscc.models import Registration, Teacher
    from student_registration.mobile_api.models import MobileSyncBatch
    MSCCAttendanceChild.objects.all().delete()
    MSCCAttendance.objects.all().delete()
    Registration.objects.all().delete()
    Child.objects.all().delete()
    Teacher.objects.all().delete()
    MobileSyncBatch.objects.all().delete()


def run(out_dir, wipe=True):
    from django.conf import settings
    settings.ALLOWED_HOSTS = ['*']  # the test client host is not in ALLOWED_HOSTS outside the test runner
    os.makedirs(out_dir, exist_ok=True)
    if wipe:
        reset()
    user, center, partner = seed()
    client = APIClient()
    with patch('student_registration.students.utils.get_api_token', return_value=None):
        login = client.post('/api/mobile/v1/auth/login/', {
            'username': 'rima.center', 'password': 'demo-pass-123', 'device_id': 'fixture-device',
            'device_name': 'Fixture tablet', 'app_version': '1.0.0'}, format='json')
        assert login.status_code == 200, login.content
        client.credentials(HTTP_AUTHORIZATION='Token ' + login.data['token'])

        round_id = Round.objects.get(name='2025-2026').id
        today = datetime.date.today()
        items = []
        for index, child in enumerate(CHILDREN):
            reg_uuid = 'fixture-reg-{}'.format(index)
            items.append({'client_uuid': reg_uuid, 'entity': 'mscc.registration', 'op': 'create',
                          'data': registration_payload(*child, index=index)})
            programme = ['BLN Level 1', 'BLN Level 1', 'CBECE Level 2',
                         'BLN Level 2', 'CBECE Level 1', 'BLN Level 1'][index]
            items.append({'client_uuid': 'fixture-svc-{}'.format(index), 'entity': 'mscc.education_service',
                          'op': 'create', 'parent_uuid': reg_uuid,
                          'data': {'education_status': 'Never registered in any formal school before',
                                   'education_program': programme, 'class_section': 'A', 'round': round_id,
                                   'registration_date': (today - datetime.timedelta(days=40)).isoformat()}})
        items.append({'client_uuid': 'fixture-pss', 'entity': 'mscc.pss', 'op': 'create',
                      'parent_uuid': 'fixture-reg-0',
                      'data': {'child_registered': 'Yes',
                               'child_living_arrangement': 'Living with single parent/caregiver',
                               'child_vulnerability': 'Clear signs of neglect', 'child_out_school_reasons': 'N/A',
                               'caregivers_distress': 'No', 'caregivers_additional_parenting': 'No',
                               'child_distress': 'No', 'child_additional_parenting': 'No',
                               'child_know_seek_help': 'Yes', 'child_protection_concern': 'Nightmares'}})
        for day_offset in (1, 2, 3):
            date = today - datetime.timedelta(days=day_offset)
            items.append({'client_uuid': 'fixture-att-{}'.format(day_offset), 'entity': 'mscc.attendance_day',
                          'op': 'upsert',
                          'data': {'round_id': round_id, 'education_program': 'BLN Level 1', 'class_section': 'A',
                                   'attendance_date': date.isoformat(), 'attendance_day_off': 'No', 'close_reason': '',
                                   'children_attendance': [
                                       {'registration_uuid': 'fixture-reg-0', 'attended': 'Yes'},
                                       {'registration_uuid': 'fixture-reg-1',
                                        'attended': 'No' if day_offset == 2 else 'Yes',
                                        'absence_reason': 'Sick' if day_offset == 2 else ''},
                                       {'registration_uuid': 'fixture-reg-5', 'attended': 'Yes'},
                                   ]}})
        items.append({'client_uuid': 'fixture-teacher', 'entity': 'mscc.teacher', 'op': 'create',
                      'data': {'first_name': 'Hala', 'father_name': 'Nabil', 'last_name': 'Sleiman',
                               'mother_fullname': 'Rita Sleiman', 'sex': 'Female', 'birthdate': '1990-05-12',
                               'nationality': 2, 'round': round_id, 'center': center.id,
                               'primary_phone_number': '03-999888', 'email': 'hala@example.org',
                               'subjects_provided': ['arabic', 'math'], 'registration_level': ['Level one'],
                               'teacher_assignment': 'Makani only', 'teaching_hours_mscc': 20,
                               'years_of_experience': 5, 'training_sessions_attended': 3, 'extra_coaching': 'no',
                               'trainings': list(Training.objects.values_list('id', flat=True)[:2])}})
        push = client.post('/api/mobile/v1/push/', {'batch_uuid': str(uuid.uuid4()), 'device_id': 'fixture-device',
                                                    'app_version': '1.0.0', 'items': items}, format='json')
        assert push.status_code == 200, push.content
        report = push.data
        # A second push with a duplicate of child 0 gives a realistic duplicate report.
        dup = client.post('/api/mobile/v1/push/', {'batch_uuid': str(uuid.uuid4()), 'device_id': 'fixture-device',
                                                   'app_version': '1.0.0', 'items': [
                                                       {'client_uuid': 'fixture-dup', 'entity': 'mscc.registration',
                                                        'op': 'create', 'data': registration_payload(*CHILDREN[0])},
                                                   ]}, format='json')
        assert dup.status_code == 200, dup.content

        bootstrap = client.get('/api/mobile/v1/bootstrap/')
        assert bootstrap.status_code == 200, bootstrap.content
        pull = client.get('/api/mobile/v1/pull/')
        assert pull.status_code == 200, pull.content

    def dump(name, data):
        with open(os.path.join(out_dir, name), 'w', encoding='utf-8') as handle:
            json.dump(data, handle, ensure_ascii=False, indent=1, default=str)

    dump('bootstrap.json', bootstrap.data)
    dump('pull.json', pull.data)
    dump('push_report.json', report)
    dump('duplicate_report.json', dup.data)
    print('fixtures written to', out_dir, '| statuses:', report['summary'], dup.data['summary'])
