# -*- coding: utf-8 -*-
"""Tests for the inbound replication endpoint."""

from __future__ import unicode_literals, absolute_import, division

import uuid

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from student_registration.attendances.models import (
    MSCCAttendance,
    MSCCAttendanceChild,
)
from student_registration.child.models import Child
from student_registration.locations.models import Center
from student_registration.mscc.models import (
    EducationService,
    Referral,
    Registration,
    Round,
)

from ..constants import (
    RESOURCE_ATTENDANCE,
    RESOURCE_EDUCATION_SERVICE,
    RESOURCE_REFERRAL,
    RESOURCE_REGISTRATION,
    SOURCE_SYSTEM_COMPILER,
)
from ..models import SyncConflict, SyncedRecord, SyncEventLog
from ..services import ingest_events


def registration_payload(**overrides):
    """Return a minimal registration payload as the Compiler would send it."""
    payload = {
        'fields': {
            'have_labour': 'No',
            'type': 'Core-Package',
            'registration_date': '2026-03-01',
            'deleted': False,
        },
        'center': {
            'source_id': 41,
            'p_code': 'LB-0301',
            'name': 'Makani Tripoli',
            'partner': {'source_id': 7, 'name': 'Partner One'},
        },
        'round': {'source_id': 3, 'name': '2026 Round A', 'year': 2026,
                  'current_year': True},
        'partner': {'source_id': 7, 'name': 'Partner One'},
        'child': {
            'source_id': 900,
            'fields': {
                'first_name': 'Lina',
                'father_name': 'Omar',
                'last_name': 'Haddad',
                'mother_fullname': 'Nour Haddad',
                'gender': 'Female',
                'birthday_year': '2015',
                'birthday_month': '4',
                'birthday_day': '12',
                'unicef_id': 'UNI-900',
            },
        },
    }
    payload.update(overrides)
    return payload


def event(resource, source_id, payload=None, operation='upsert', event_id=None):
    """Return one wire event."""
    return {
        'event_id': event_id or str(uuid.uuid4()),
        'resource': resource,
        'operation': operation,
        'source_id': source_id,
        'source_modified': '2026-03-01T10:00:00Z',
        'payload': payload or {},
    }


class IngestServiceTests(TestCase):
    """The applier layer, exercised without going through HTTP."""

    def test_registration_creates_child_center_and_round(self):
        result = ingest_events(
            [event(RESOURCE_REGISTRATION, 1234, registration_payload())],
            SOURCE_SYSTEM_COMPILER,
        )

        self.assertEqual(result['applied'], 1, result['results'])
        registration = Registration.objects.get()
        self.assertEqual(registration.child.first_name, 'Lina')
        self.assertEqual(registration.center.p_code, 'LB-0301')
        self.assertEqual(registration.round.name, '2026 Round A')
        self.assertEqual(registration.partner.name, 'Partner One')
        self.assertTrue(
            SyncedRecord.objects.filter(
                resource=RESOURCE_REGISTRATION, source_id='1234'
            ).exists()
        )

    def test_second_push_updates_rather_than_duplicates(self):
        ingest_events(
            [event(RESOURCE_REGISTRATION, 1234, registration_payload())],
            SOURCE_SYSTEM_COMPILER,
        )
        payload = registration_payload()
        payload['fields']['have_labour'] = 'Yes - Morning'
        ingest_events(
            [event(RESOURCE_REGISTRATION, 1234, payload)],
            SOURCE_SYSTEM_COMPILER,
        )

        self.assertEqual(Registration.objects.count(), 1)
        self.assertEqual(Child.objects.count(), 1)
        self.assertEqual(Registration.objects.get().have_labour, 'Yes - Morning')

    def test_replaying_the_same_event_is_a_no_op(self):
        wire = event(RESOURCE_REGISTRATION, 1234, registration_payload())

        first = ingest_events([wire], SOURCE_SYSTEM_COMPILER)
        second = ingest_events([wire], SOURCE_SYSTEM_COMPILER)

        self.assertEqual(first['applied'], 1)
        self.assertEqual(second['skipped'], 1)
        self.assertEqual(Registration.objects.count(), 1)

    def test_compiler_only_columns_are_reported_not_fatal(self):
        payload = registration_payload()
        # These three exist in the Compiler's Registration but not here.
        payload['fields'].update({
            'child_is_idp': 'No',
            'consent': 'Yes',
            'child_outreach': 12,
        })

        result = ingest_events(
            [event(RESOURCE_REGISTRATION, 1234, payload)], SOURCE_SYSTEM_COMPILER
        )

        self.assertEqual(result['applied'], 1, result['results'])
        self.assertEqual(
            sorted(result['results'][0]['ignored_fields']),
            ['child_is_idp', 'child_outreach', 'consent'],
        )

    def test_local_edit_is_overwritten_and_recorded(self):
        ingest_events(
            [event(RESOURCE_REGISTRATION, 1234, registration_payload())],
            SOURCE_SYSTEM_COMPILER,
        )

        registration = Registration.objects.get()
        registration.have_labour = 'Yes - Night Shift'
        registration.save()

        payload = registration_payload()
        payload['fields']['have_labour'] = 'Yes - Full Day'
        result = ingest_events(
            [event(RESOURCE_REGISTRATION, 1234, payload)], SOURCE_SYSTEM_COMPILER
        )

        registration.refresh_from_db()
        self.assertEqual(registration.have_labour, 'Yes - Full Day')
        self.assertTrue(result['results'][0]['conflict'])

        conflict = SyncConflict.objects.get()
        self.assertIn('have_labour', conflict.diverged_fields)
        self.assertEqual(
            conflict.diverged_fields['have_labour'],
            {'synced': 'No', 'local': 'Yes - Night Shift'},
        )

    def test_untouched_replica_records_no_conflict(self):
        ingest_events(
            [event(RESOURCE_REGISTRATION, 1234, registration_payload())],
            SOURCE_SYSTEM_COMPILER,
        )
        payload = registration_payload()
        payload['fields']['have_labour'] = 'Yes - Full Day'
        ingest_events(
            [event(RESOURCE_REGISTRATION, 1234, payload)], SOURCE_SYSTEM_COMPILER
        )

        self.assertEqual(SyncConflict.objects.count(), 0)

    def test_child_table_without_its_registration_is_retryable(self):
        result = ingest_events(
            [event(RESOURCE_EDUCATION_SERVICE, 55, {
                'fields': {'education_status': 'No'},
                'registration': {'source_id': 1234},
            })],
            SOURCE_SYSTEM_COMPILER,
        )

        self.assertEqual(result['failed'], 1)
        self.assertTrue(result['results'][0]['retryable'])
        self.assertEqual(EducationService.objects.count(), 0)

    def test_batch_is_applied_in_dependency_order(self):
        # The education service is listed first on purpose: the receiver has
        # to reorder it behind the registration it belongs to.
        result = ingest_events(
            [
                event(RESOURCE_EDUCATION_SERVICE, 55, {
                    'fields': {'education_status': 'No'},
                    'registration': {'source_id': 1234},
                }),
                event(RESOURCE_REGISTRATION, 1234, registration_payload()),
            ],
            SOURCE_SYSTEM_COMPILER,
        )

        self.assertEqual(result['applied'], 2, result['results'])
        self.assertEqual(
            EducationService.objects.get().registration,
            Registration.objects.get(),
        )

    def test_referral_resolves_registration_and_survives_unknown_school(self):
        ingest_events(
            [event(RESOURCE_REGISTRATION, 1234, registration_payload())],
            SOURCE_SYSTEM_COMPILER,
        )
        result = ingest_events(
            [event(RESOURCE_REFERRAL, 77, {
                'fields': {'referred_formal_education': 'Yes'},
                'registration': {'source_id': 1234},
                'referred_school': {'source_id': 9, 'number': '99999',
                                    'name': 'Not In BMA'},
            })],
            SOURCE_SYSTEM_COMPILER,
        )

        self.assertEqual(result['applied'], 1, result['results'])
        referral = Referral.objects.get()
        self.assertEqual(referral.registration, Registration.objects.get())
        self.assertIsNone(referral.referred_school)
        self.assertIn('unknown School', result['results'][0]['detail'])

    def test_attendance_day_replaces_its_child_rows(self):
        ingest_events(
            [event(RESOURCE_REGISTRATION, 1234, registration_payload())],
            SOURCE_SYSTEM_COMPILER,
        )
        attendance = {
            'fields': {'attendance_date': '2026-03-02', 'day_off': 'no',
                       'education_program': 'BLN Level 1'},
            'center': {'source_id': 41, 'p_code': 'LB-0301',
                       'name': 'Makani Tripoli'},
            'round': {'source_id': 3, 'name': '2026 Round A'},
            'children': [{
                'source_id': 1,
                'fields': {'attended': 'Yes'},
                'registration': {'source_id': 1234},
            }],
        }
        ingest_events(
            [event(RESOURCE_ATTENDANCE, 500, attendance)], SOURCE_SYSTEM_COMPILER
        )

        self.assertEqual(MSCCAttendanceChild.objects.count(), 1)
        day = MSCCAttendance.objects.get()
        self.assertEqual(day.round_id, Round.objects.get().id)
        self.assertEqual(MSCCAttendanceChild.objects.get().attended, 'Yes')

        attendance['children'] = []
        ingest_events(
            [event(RESOURCE_ATTENDANCE, 500, attendance)], SOURCE_SYSTEM_COMPILER
        )
        self.assertEqual(MSCCAttendanceChild.objects.count(), 0)

    def test_delete_removes_the_local_row(self):
        ingest_events(
            [event(RESOURCE_REGISTRATION, 1234, registration_payload())],
            SOURCE_SYSTEM_COMPILER,
        )
        result = ingest_events(
            [event(RESOURCE_REGISTRATION, 1234, operation='delete')],
            SOURCE_SYSTEM_COMPILER,
        )

        self.assertEqual(result['applied'], 1, result['results'])
        self.assertEqual(Registration.objects.count(), 0)
        self.assertTrue(
            SyncedRecord.objects.get(
                resource=RESOURCE_REGISTRATION, source_id='1234'
            ).deleted
        )

    def test_existing_center_is_adopted_not_duplicated(self):
        Center.objects.create(name='Makani Tripoli', p_code='LB-0301')

        ingest_events(
            [event(RESOURCE_REGISTRATION, 1234, registration_payload())],
            SOURCE_SYSTEM_COMPILER,
        )

        self.assertEqual(Center.objects.count(), 1)

    def test_one_bad_event_does_not_stop_the_batch(self):
        result = ingest_events(
            [
                {'event_id': str(uuid.uuid4()), 'resource': 'nope',
                 'operation': 'upsert', 'source_id': 1},
                event(RESOURCE_REGISTRATION, 1234, registration_payload()),
            ],
            SOURCE_SYSTEM_COMPILER,
        )

        self.assertEqual(result['applied'], 1)
        self.assertEqual(result['failed'], 1)
        self.assertEqual(Registration.objects.count(), 1)

    def test_every_event_is_logged(self):
        ingest_events(
            [event(RESOURCE_REGISTRATION, 1234, registration_payload())],
            SOURCE_SYSTEM_COMPILER,
        )
        log = SyncEventLog.objects.get()
        self.assertEqual(log.status, 'applied')
        self.assertEqual(log.resource, RESOURCE_REGISTRATION)


class IngestEndpointTests(TestCase):
    """Authentication and request handling on the HTTP endpoint."""

    def setUp(self):
        self.url = reverse('datasync:ingest')
        self.client = APIClient()

        user_model = get_user_model()
        self.service_account = user_model.objects.create(username='compiler-sync')
        group, _ = Group.objects.get_or_create(name='DataSync')
        self.service_account.groups.add(group)
        self.token = Token.objects.create(user=self.service_account)

        self.outsider = user_model.objects.create(username='someone-else')
        self.outsider_token = Token.objects.create(user=self.outsider)

    def authenticate(self, token=None):
        self.client.credentials(
            HTTP_AUTHORIZATION='Token {}'.format(token or self.token.key)
        )

    def test_anonymous_is_rejected(self):
        response = self.client.post(self.url, {'events': []}, format='json')
        self.assertIn(response.status_code, (401, 403))

    def test_account_outside_the_group_is_rejected(self):
        self.authenticate(self.outsider_token.key)
        response = self.client.post(self.url, {'events': []}, format='json')
        self.assertEqual(response.status_code, 403)

    def test_service_account_can_push(self):
        self.authenticate()
        response = self.client.post(
            self.url,
            {'source_system': SOURCE_SYSTEM_COMPILER,
             'events': [event(RESOURCE_REGISTRATION, 1234, registration_payload())]},
            format='json',
        )

        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(response.data['applied'], 1)
        self.assertEqual(Registration.objects.count(), 1)

    def test_unknown_source_system_is_rejected(self):
        self.authenticate()
        response = self.client.post(
            self.url, {'source_system': 'somewhere-else', 'events': []}, format='json'
        )
        self.assertEqual(response.status_code, 403)

    def test_events_must_be_a_list(self):
        self.authenticate()
        response = self.client.post(self.url, {'events': {}}, format='json')
        self.assertEqual(response.status_code, 400)

    def test_oversized_batch_is_rejected(self):
        self.authenticate()
        with self.settings(DATASYNC_MAX_BATCH_SIZE=1):
            response = self.client.post(
                self.url,
                {'events': [
                    event(RESOURCE_REGISTRATION, 1, registration_payload()),
                    event(RESOURCE_REGISTRATION, 2, registration_payload()),
                ]},
                format='json',
            )
        self.assertEqual(response.status_code, 413)

    def test_disabled_ingest_answers_service_unavailable(self):
        self.authenticate()
        with self.settings(DATASYNC_INGEST_ENABLED=False):
            response = self.client.post(self.url, {'events': []}, format='json')
        self.assertEqual(response.status_code, 503)

    def test_capability_document_is_served(self):
        self.authenticate()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIn(RESOURCE_REGISTRATION, response.data['resources'])
