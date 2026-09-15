# -*- coding: utf-8 -*-
"""End-to-end tests for the mobile synchronisation API."""
from __future__ import unicode_literals

import datetime
import uuid
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework.test import APIClient

from student_registration.attendances.models import MSCCAttendance, MSCCAttendanceChild
from student_registration.child.models import Child
from student_registration.clm.models import Disability
from student_registration.locations.models import Center
from student_registration.mscc.models import EducationService, Packages, Registration, Round
from student_registration.schools.models import EducationalLevel, PartnerOrganization
from student_registration.students.models import IDType, Nationality

from ..models import MobileSyncBatch, MobileSyncItem

User = get_user_model()

LOGIN = '/api/mobile/v1/auth/login/'
BOOTSTRAP = '/api/mobile/v1/bootstrap/'
PULL = '/api/mobile/v1/pull/'
PUSH = '/api/mobile/v1/push/'


def child_payload(**overrides):
    data = {
        'child_first_name': 'Mohamad',
        'child_father_name': 'Ahmad',
        'child_last_name': 'Sayed',
        'child_mother_fullname': 'Fatima Ali',
        'child_gender': 'Male',
        'child_nationality': None,          # set by the test
        'child_birthday_year': '2015',
        'child_birthday_month': '3',
        'child_birthday_day': '5',
        'child_address': 'Bar Elias',
        'child_disability': None,           # set by the test
        'child_marital_status': 'Single',
        'child_have_children': 'No',
        'child_have_sibling': 'No',
        'child_siblings_have_disability': 'No',
        'child_mother_pregnant_expecting': 'No',
        'child_living_arrangement': 'Living with caregivers',
        'source_of_identification': 'Dirassa',
        'cash_support_programmes': ['None'],
        'father_educational_level': None,
        'mother_educational_level': None,
        'first_phone_owner': 'Phone Main Caregiver',
        'first_phone_number': '03-123456',
        'first_phone_number_confirm': '03-123456',
        'main_caregiver': 'Mother',
        'children_number_under18': '2',
        'caregiver_first_name': 'Fatima',
        'caregiver_middle_name': 'Hassan',
        'caregiver_last_name': 'Ali',
        'caregiver_mother_name': 'Mariam',
        'main_caregiver_nationality': None,
        'have_labour': 'No',
        'id_type': None,
        'parent_national_number': '123456789012',
        'parent_national_number_confirm': '123456789012',
        'national_number': '123456789012',
        'national_number_confirm': '123456789012',
    }
    data.update(overrides)
    return data


PSS_PAYLOAD = {
    'child_registered': 'Yes',
    'child_living_arrangement': 'Living with single parent/caregiver',
    'child_vulnerability': 'Clear signs of neglect',
    'child_out_school_reasons': 'N/A',
    'caregivers_distress': 'No',
    'caregivers_additional_parenting': 'No',
    'child_distress': 'No',
    'child_additional_parenting': 'No',
    'child_know_seek_help': 'Yes',
    'child_protection_concern': 'Nightmares',
}


@override_settings(MOBILE_API_USE_UNIQUE_ID_SERVICE=False)
class MobileApiBase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.partner = PartnerOrganization.objects.create(name='Partner NGO', active=True)
        cls.center = Center.objects.create(name='Makani Bar Elias', partner=cls.partner)
        cls.round = Round.objects.create(name='2025-2026', current_year=True, year=2025)
        Packages.objects.create(name='BLN Level 1', type='BLN', category='Education', min_age=6, max_age=14)
        cls.nationality = Nationality.objects.create(name='سوري', name_en='Syrian', code='SY')
        cls.other_nationality = Nationality.objects.create(name='آخر', name_en='Other', code='OT')
        cls.disability = Disability.objects.create(name='لا', name_en='No', active=True)
        cls.level = EducationalLevel.objects.create(name='Primary')
        # MainForm.clean keys the ID-number rules on the real IDType ids (5 = Lebanese).
        for pk, name in ((1, 'UNHCR Registered'), (2, 'UNHCR Recorded'), (3, 'Syrian national ID'),
                         (4, 'Palestinian national ID'), (5, 'Lebanese national ID'),
                         (6, 'Other nationality'), (7, 'Caregiver has no ID')):
            IDType.objects.create(id=pk, name=name, active=True)
        cls.id_type = IDType.objects.get(pk=5)
        for name in ('MSCC', 'MSCC_CENTER', 'MSCC_PARTNER', 'MSCC_UNICEF', 'ALP_SCHOOL', 'CLM_Bridging'):
            Group.objects.get_or_create(name=name)
        cls.user = User.objects.create_user(
            username='center_user', password='secret-pass', partner=cls.partner, center=cls.center)
        cls.user.groups.add(Group.objects.get(name='MSCC_CENTER'))
        cls.user.groups.add(Group.objects.get(name='MSCC'))

    def setUp(self):
        self.client = APIClient()
        self.token = self.login()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        # MainForm.save calls the external Unique-ID service: never hit the network.
        patcher = patch('student_registration.students.utils.get_api_token', return_value=None)
        patcher.start()
        self.addCleanup(patcher.stop)

    def login(self, username='center_user', password='secret-pass'):
        response = APIClient().post(LOGIN, {
            'username': username, 'password': password,
            'device_id': 'device-1', 'device_name': 'Test tablet', 'app_version': '1.0.0',
        }, format='json')
        self.assertEqual(response.status_code, 200, response.content)
        return response.data['token']

    def payload(self, **overrides):
        data = child_payload(
            child_nationality=self.nationality.id,
            child_disability=self.disability.id,
            father_educational_level=self.level.id,
            mother_educational_level=self.level.id,
            main_caregiver_nationality=self.nationality.id,
            id_type=self.id_type.id,
        )
        data.update(overrides)
        return data

    def push(self, items, batch_uuid=None):
        response = self.client.post(PUSH, {
            'batch_uuid': batch_uuid or str(uuid.uuid4()),
            'device_id': 'device-1', 'app_version': '1.0.0', 'items': items,
        }, format='json')
        self.assertEqual(response.status_code, 200, response.content)
        return response.data


class AuthAndBootstrapTests(MobileApiBase):

    def test_login_returns_profile_and_modules(self):
        response = APIClient().post(LOGIN, {'username': 'center_user', 'password': 'secret-pass'},
                                    format='json')
        self.assertEqual(response.status_code, 200)
        user = response.data['user']
        self.assertEqual(user['center']['id'], self.center.id)
        self.assertTrue(user['modules']['mscc']['enabled'])
        self.assertTrue(user['modules']['mscc']['can_register'])
        self.assertFalse(user['modules']['alp']['enabled'])

    def test_login_rejects_bad_password(self):
        response = APIClient().post(LOGIN, {'username': 'center_user', 'password': 'nope'}, format='json')
        self.assertEqual(response.status_code, 401)

    def test_endpoints_require_token(self):
        self.assertEqual(APIClient().get(BOOTSTRAP).status_code, 401)

    def test_bootstrap_contains_reference_data_and_schemas(self):
        response = self.client.get(BOOTSTRAP)
        self.assertEqual(response.status_code, 200, response.content)
        data = response.data
        self.assertEqual([n['name_en'] for n in data['reference']['nationalities']][0], 'Syrian')
        self.assertEqual(data['reference']['centers'][0]['id'], self.center.id)
        self.assertEqual(data['reference']['rounds']['mscc'][0]['name'], '2025-2026')
        schema = data['schemas']['mscc.registration']
        names = {f['name'] for f in schema['fields']}
        self.assertIn('child_first_name', names)
        self.assertIn('cash_support_programmes', names)
        by_name = {f['name']: f for f in schema['fields']}
        self.assertEqual(by_name['child_gender']['type'], 'select')
        self.assertEqual(by_name['child_nationality']['type'], 'ref')
        self.assertEqual(by_name['child_nationality']['ref'], 'nationalities')
        self.assertEqual(by_name['cash_support_programmes']['type'], 'multiselect')
        self.assertTrue(by_name['child_first_name']['required'])
        self.assertIn('label_ar', by_name['child_first_name'])
        self.assertTrue(schema['wizard'])
        self.assertEqual(schema['sections'][0]['key'], 'identity')
        self.assertIn('mscc.pss', data['schemas'])
        self.assertIn('mscc.attendance_day', data['schemas'])
        self.assertNotIn('alp.registration', data['schemas'])
        self.assertIn('mscc.attendance.education_program', data['choices'])


class PushRegistrationTests(MobileApiBase):

    def test_create_registration_then_service_in_same_batch(self):
        reg_uuid = str(uuid.uuid4())
        report = self.push([
            {'client_uuid': reg_uuid, 'entity': 'mscc.registration', 'op': 'create', 'data': self.payload()},
            {'client_uuid': 'svc-1', 'entity': 'mscc.education_service', 'op': 'create',
             'parent_uuid': reg_uuid,
             'data': {'education_status': 'No', 'education_program': 'BLN Level 1', 'class_section': 'A',
                      'round': self.round.id, 'registration_date': datetime.date.today().isoformat()}},
        ])
        self.assertEqual(report['summary']['created'], 2, report)
        reg_result, svc_result = report['results']
        self.assertEqual(reg_result['status'], 'created')
        registration = Registration.objects.get(pk=reg_result['server_id'])
        self.assertEqual(registration.center_id, self.center.id)
        self.assertEqual(registration.partner_id, self.partner.id)
        self.assertEqual(registration.owner_id, self.user.id)
        self.assertEqual(registration.child.first_name, 'Mohamad')
        self.assertEqual(registration.child.number, Child.objects.get(pk=registration.child_id).number)
        self.assertEqual(reg_result['data_after']['child']['full_name'], 'Mohamad Ahmad Sayed')
        self.assertEqual(svc_result['status'], 'created')
        service = EducationService.objects.get(pk=svc_result['server_id'])
        self.assertEqual(service.registration_id, registration.id)
        self.assertEqual(service.class_section, 'A')
        batch = MobileSyncBatch.objects.get(pk=report['batch_id'])
        self.assertEqual(batch.status, MobileSyncBatch.STATUS_COMPLETED)
        self.assertEqual(batch.items.count(), 2)

    def test_validation_errors_are_reported_per_field(self):
        report = self.push([
            {'client_uuid': 'bad-1', 'entity': 'mscc.registration', 'op': 'create',
             'data': self.payload(child_first_name='', cash_support_programmes=[])},
        ])
        result = report['results'][0]
        self.assertEqual(result['status'], 'error')
        self.assertIn('child_first_name', result['errors'])
        self.assertIn('cash_support_programmes', result['errors'])
        self.assertEqual(Registration.objects.count(), 0)

    def test_duplicate_is_detected_and_can_be_merged(self):
        first = self.push([{'client_uuid': 'r1', 'entity': 'mscc.registration', 'op': 'create',
                            'data': self.payload()}])
        existing_id = first['results'][0]['server_id']
        # Same child typed slightly differently offline (case + extra spaces).
        second = self.push([
            {'client_uuid': 'r2', 'entity': 'mscc.registration', 'op': 'create',
             'data': self.payload(child_first_name='mohamad ', child_last_name='SAYED',
                                  child_address='New address', national_number='', national_number_confirm='',
                                  parent_national_number='', parent_national_number_confirm='')},
            {'client_uuid': 'svc-2', 'entity': 'mscc.pss', 'op': 'create', 'parent_uuid': 'r2',
             'data': PSS_PAYLOAD},
        ])
        dup, svc = second['results']
        self.assertEqual(dup['status'], 'duplicate', dup)
        self.assertEqual(dup['duplicates'][0]['registration_id'], existing_id)
        self.assertEqual(dup['duplicates'][0]['match']['reason'], 'identity')
        self.assertEqual(svc['status'], 'skipped')
        self.assertEqual(Registration.objects.count(), 1)

        merged = self.push([
            {'client_uuid': 'r2', 'entity': 'mscc.registration', 'op': 'create',
             'data': self.payload(child_first_name='mohamad ', child_address='New address'),
             'resolution': {'action': 'merge', 'target_id': existing_id, 'overwrite': True}},
            {'client_uuid': 'svc-2', 'entity': 'mscc.pss', 'op': 'create', 'parent_uuid': 'r2',
             'data': PSS_PAYLOAD},
        ])
        merged_reg, merged_svc = merged['results']
        self.assertEqual(merged_reg['status'], 'merged', merged_reg)
        self.assertEqual(merged_reg['server_id'], existing_id)
        self.assertEqual(Registration.objects.count(), 1)
        self.assertEqual(Child.objects.get().address, 'New address')
        self.assertEqual(merged_svc['status'], 'created')
        self.assertEqual(merged_svc['parent_id'], existing_id)

    def test_duplicate_by_id_number_and_create_anyway(self):
        self.push([{'client_uuid': 'r1', 'entity': 'mscc.registration', 'op': 'create',
                    'data': self.payload()}])
        report = self.push([{'client_uuid': 'r2', 'entity': 'mscc.registration', 'op': 'create',
                             'data': self.payload(child_first_name='Ali', child_birthday_year='2012')}])
        result = report['results'][0]
        self.assertEqual(result['status'], 'duplicate')
        self.assertEqual(result['duplicates'][0]['match']['reason'], 'id_number')
        forced = self.push([{'client_uuid': 'r2', 'entity': 'mscc.registration', 'op': 'create',
                             'data': self.payload(child_first_name='Ali', child_birthday_year='2012'),
                             'resolution': {'action': 'create'}}])
        self.assertEqual(forced['results'][0]['status'], 'created')
        self.assertEqual(Registration.objects.count(), 2)
        item = MobileSyncItem.objects.get(batch_id=forced['batch_id'])
        self.assertTrue(item.duplicate_override)

    def test_link_creates_registration_for_existing_child(self):
        first = self.push([{'client_uuid': 'r1', 'entity': 'mscc.registration', 'op': 'create',
                            'data': self.payload()}])
        child_id = first['results'][0]['data_after']['child']['id']
        Registration.objects.update(round=None)
        report = self.push([{'client_uuid': 'r2', 'entity': 'mscc.registration', 'op': 'create',
                             'data': self.payload(),
                             'resolution': {'action': 'link', 'target_id': child_id}}])
        self.assertEqual(report['results'][0]['status'], 'linked', report)
        self.assertEqual(Child.objects.count(), 1)
        self.assertEqual(Registration.objects.filter(child_id=child_id).count(), 2)

    def test_discard_writes_nothing(self):
        report = self.push([{'client_uuid': 'r1', 'entity': 'mscc.registration', 'op': 'create',
                             'data': self.payload(), 'resolution': {'action': 'discard'}}])
        self.assertEqual(report['results'][0]['status'], 'discarded')
        self.assertEqual(Registration.objects.count(), 0)

    def test_update_detects_conflicts(self):
        first = self.push([{'client_uuid': 'r1', 'entity': 'mscc.registration', 'op': 'create',
                            'data': self.payload()}])
        server_id = first['results'][0]['server_id']
        stale = (datetime.datetime.now() - datetime.timedelta(days=1)).isoformat()
        report = self.push([{'client_uuid': 'r1', 'entity': 'mscc.registration', 'op': 'update',
                             'server_id': server_id, 'base_modified': stale,
                             'data': self.payload(child_address='Changed')}])
        self.assertEqual(report['results'][0]['status'], 'conflict')
        self.assertIn('server_data', report['results'][0]['errors'])
        report = self.push([{'client_uuid': 'r1', 'entity': 'mscc.registration', 'op': 'update',
                             'server_id': server_id, 'base_modified': stale,
                             'data': self.payload(child_address='Changed'),
                             'resolution': {'action': 'overwrite'}}])
        self.assertEqual(report['results'][0]['status'], 'updated', report)
        self.assertEqual(Child.objects.get().address, 'Changed')

    def test_batch_is_idempotent(self):
        batch_uuid = str(uuid.uuid4())
        items = [{'client_uuid': 'r1', 'entity': 'mscc.registration', 'op': 'create', 'data': self.payload()}]
        first = self.push(items, batch_uuid=batch_uuid)
        second = self.push(items, batch_uuid=batch_uuid)
        self.assertEqual(first['batch_id'], second['batch_id'])
        self.assertEqual(Registration.objects.count(), 1)

    def test_unknown_entity_and_permissions(self):
        report = self.push([{'client_uuid': 'x', 'entity': 'nope.thing', 'op': 'create', 'data': {}}])
        self.assertEqual(report['results'][0]['status'], 'error')
        report = self.push([{'client_uuid': 'y', 'entity': 'alp.registration', 'op': 'create',
                             'data': self.payload()}])
        self.assertEqual(report['results'][0]['status'], 'error')
        self.assertIn('not allowed', report['results'][0]['message'])

    def test_history_endpoints(self):
        report = self.push([{'client_uuid': 'r1', 'entity': 'mscc.registration', 'op': 'create',
                             'data': self.payload()}])
        history = self.client.get('/api/mobile/v1/push/history/')
        self.assertEqual(history.status_code, 200)
        self.assertEqual(history.data['batches'][0]['batch_id'], report['batch_id'])
        detail = self.client.get('/api/mobile/v1/push/{}/'.format(report['batch_id']))
        self.assertEqual(detail.status_code, 200)
        self.assertEqual(detail.data['results'][0]['status'], 'created')


class AttendanceAndPullTests(MobileApiBase):

    def _register(self):
        report = self.push([
            {'client_uuid': 'r1', 'entity': 'mscc.registration', 'op': 'create', 'data': self.payload()},
            {'client_uuid': 's1', 'entity': 'mscc.education_service', 'op': 'create', 'parent_uuid': 'r1',
             'data': {'education_status': 'No', 'education_program': 'BLN Level 1', 'class_section': 'A',
                      'round': self.round.id,
                      'registration_date': (datetime.date.today() - datetime.timedelta(days=3)).isoformat()}},
        ])
        return report['results'][0]

    def test_attendance_upsert_is_idempotent(self):
        reg = self._register()
        today = datetime.date.today().isoformat()
        day = {'round_id': self.round.id, 'education_program': 'BLN Level 1', 'class_section': 'A',
               'attendance_date': today, 'attendance_day_off': 'No', 'close_reason': '',
               'children_attendance': [{'registration_id': reg['server_id'],
                                        'child_id': reg['data_after']['child']['id'],
                                        'attended': 'No', 'absence_reason': 'Sick',
                                        'absence_reason_other': ''}]}
        first = self.push([{'client_uuid': 'a1', 'entity': 'mscc.attendance_day', 'op': 'upsert', 'data': day}])
        self.assertEqual(first['results'][0]['status'], 'created', first)
        self.assertEqual(MSCCAttendance.objects.count(), 1)
        self.assertEqual(MSCCAttendanceChild.objects.get().attended, 'No')
        day['children_attendance'][0]['attended'] = 'Yes'
        day['children_attendance'][0]['absence_reason'] = ''
        second = self.push([{'client_uuid': 'a2', 'entity': 'mscc.attendance_day', 'op': 'upsert', 'data': day}])
        self.assertEqual(second['results'][0]['status'], 'created')
        self.assertEqual(MSCCAttendance.objects.count(), 1)
        self.assertEqual(MSCCAttendanceChild.objects.count(), 1)
        self.assertEqual(MSCCAttendanceChild.objects.get().attended, 'Yes')

    def test_attendance_rejects_future_and_missing_reason(self):
        reg = self._register()
        tomorrow = (datetime.date.today() + datetime.timedelta(days=1)).isoformat()
        report = self.push([{'client_uuid': 'a1', 'entity': 'mscc.attendance_day', 'op': 'upsert',
                             'data': {'round_id': self.round.id, 'education_program': 'BLN Level 1',
                                      'class_section': 'A', 'attendance_date': tomorrow,
                                      'attendance_day_off': 'No',
                                      'children_attendance': [{'registration_id': reg['server_id'],
                                                               'child_id': reg['data_after']['child']['id'],
                                                               'attended': 'No', 'absence_reason': ''}]}}])
        result = report['results'][0]
        self.assertEqual(result['status'], 'error')
        self.assertIn('attendance_date', result['errors'])
        self.assertIn('children_attendance[0].absence_reason', result['errors'])

    def test_attendance_can_reference_registration_created_in_batch(self):
        today = datetime.date.today().isoformat()
        report = self.push([
            {'client_uuid': 'r1', 'entity': 'mscc.registration', 'op': 'create', 'data': self.payload()},
            {'client_uuid': 's1', 'entity': 'mscc.education_service', 'op': 'create', 'parent_uuid': 'r1',
             'data': {'education_status': 'No', 'education_program': 'BLN Level 1', 'class_section': 'A',
                      'round': self.round.id, 'registration_date': today}},
            {'client_uuid': 'a1', 'entity': 'mscc.attendance_day', 'op': 'upsert',
             'data': {'round_id': self.round.id, 'education_program': 'BLN Level 1', 'class_section': 'A',
                      'attendance_date': today, 'attendance_day_off': 'No',
                      'children_attendance': [{'registration_uuid': 'r1', 'attended': 'Yes'}]}},
        ])
        statuses = [r['status'] for r in report['results']]
        self.assertEqual(statuses, ['created', 'created', 'created'], report)
        row = MSCCAttendanceChild.objects.get()
        self.assertEqual(row.registration_id, report['results'][0]['server_id'])
        self.assertEqual(row.child_id, report['results'][0]['data_after']['child']['id'])

    def test_pull_returns_scoped_changes_and_incremental_since(self):
        reg = self._register()
        response = self.client.get(PULL)
        self.assertEqual(response.status_code, 200, response.content)
        entities = {c['entity'] for c in response.data['changes']}
        self.assertIn('mscc.registration', entities)
        self.assertIn('mscc.education_service', entities)
        registration_change = next(c for c in response.data['changes'] if c['entity'] == 'mscc.registration')
        self.assertEqual(registration_change['server_id'], reg['server_id'])
        self.assertEqual(registration_change['data']['child']['first_name'], 'Mohamad')
        self.assertEqual(registration_change['data']['education_summary'][0]['class_section'], 'A')

        # Another centre's registration must not leak.
        other_center = Center.objects.create(name='Other', partner=self.partner)
        other_child = Child.objects.create(first_name='X', father_name='Y', last_name='Z', gender='Female',
                                           birthday_year='2014', birthday_month='1', birthday_day='1')
        Registration.objects.create(child=other_child, center=other_center, partner=self.partner,
                                    round=self.round)
        response = self.client.get(PULL)
        ids = [c['server_id'] for c in response.data['changes'] if c['entity'] == 'mscc.registration']
        self.assertEqual(ids, [reg['server_id']])

        future = (datetime.datetime.now() + datetime.timedelta(minutes=5)).isoformat()
        response = self.client.get(PULL, {'since': future})
        self.assertEqual(response.data['changes'], [])

        response = self.client.get(PULL, {'limit': 1})
        self.assertEqual(len(response.data['changes']), 1)
        self.assertTrue(response.data['has_more'])
        response = self.client.get(PULL, {'limit': 1, 'cursor': response.data['next_cursor']})
        self.assertEqual(len(response.data['changes']), 1)

    def test_duplicate_check_endpoint(self):
        self._register()
        response = self.client.post('/api/mobile/v1/duplicates/check/', {
            'entity': 'mscc.registration', 'data': self.payload(),
        }, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['result']), 1)
        self.assertEqual(response.data['result'][0]['match']['reason'], 'identity')
