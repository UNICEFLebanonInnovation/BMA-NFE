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
    EducationHistory,
    EducationService,
    HealthNutritionReferral,
    HealthNutritionService,
    Packages,
    ProvidedServices,
    PSSService,
    Referral,
    Registration,
    Round,
    YouthAssessment,
)

from ..constants import (
    RESOURCE_ATTENDANCE,
    RESOURCE_EDUCATION_SERVICE,
    RESOURCE_HEALTH_NUTRITION_REFERRAL,
    RESOURCE_HEALTH_NUTRITION_SERVICE,
    RESOURCE_ORDER,
    RESOURCE_PACKAGE,
    RESOURCE_PSS_SERVICE,
    RESOURCE_REFERRAL,
    RESOURCE_REGISTRATION,
    RESOURCE_YOUTH_ASSESSMENT,
    SOURCE_SYSTEM_COMPILER,
)
from ..appliers import HANDLERS
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


def checklist_row(source_id, name, service=None, completed=False):
    """Return one ``provided_services`` row as the Compiler sends it."""
    return {
        'source_id': source_id,
        'fields': {
            'name': name,
            'type': 'Core-Package',
            'category': 'Child Protection',
            'service_id': 999999,  # the Compiler's local id: must never be copied
            'completed': completed,
            'required': True,
            'completion_date': '2026-03-05' if completed else None,
        },
        'service': service,
    }


class CoverageTests(TestCase):
    """Every shared MSCC table replicates, and the derived tables come along."""

    def test_every_resource_in_the_contract_has_a_handler(self):
        missing = [r for r in RESOURCE_ORDER if r not in HANDLERS]
        self.assertEqual(missing, [])

    def test_a_simple_service_table_replicates(self):
        ingest_events(
            [event(RESOURCE_REGISTRATION, 1234, registration_payload())],
            SOURCE_SYSTEM_COMPILER,
        )
        result = ingest_events(
            [event(RESOURCE_YOUTH_ASSESSMENT, 31, {
                'fields': {},
                'registration': {'source_id': 1234},
            })],
            SOURCE_SYSTEM_COMPILER,
        )

        self.assertEqual(result['applied'], 1, result['results'])
        self.assertEqual(
            YouthAssessment.objects.get().registration, Registration.objects.get()
        )

    def test_package_is_matched_on_name_and_type(self):
        existing = Packages.objects.create(
            name='PSS', type='Core-Package', category='Child Protection',
            min_age=3, max_age=17,
        )
        ingest_events(
            [event(RESOURCE_PACKAGE, 7, {'fields': {
                'name': 'PSS', 'type': 'Core-Package',
                'category': 'Child Protection', 'required': True, 'age': 9,
            }})],
            SOURCE_SYSTEM_COMPILER,
        )

        self.assertEqual(Packages.objects.count(), 1)
        existing.refresh_from_db()
        self.assertTrue(existing.required)
        self.assertEqual(existing.age, 9)
        # BMA-NFE's own age bounds have no source in the Compiler: untouched.
        self.assertEqual((existing.min_age, existing.max_age), (3, 17))

    def test_checklist_arrives_with_the_registration(self):
        payload = registration_payload(provided_services=[
            checklist_row(1, 'PSS'),
            checklist_row(2, 'Inclusion'),
        ])
        ingest_events(
            [event(RESOURCE_REGISTRATION, 1234, payload)], SOURCE_SYSTEM_COMPILER
        )

        rows = ProvidedServices.objects.filter(registration=Registration.objects.get())
        self.assertEqual(sorted(rows.values_list('name', flat=True)), ['Inclusion', 'PSS'])
        # The Compiler's local service id is never copied across.
        self.assertEqual(set(rows.values_list('service_id', flat=True)), {None})

    def test_checklist_is_replaced_as_a_set(self):
        ingest_events(
            [event(RESOURCE_REGISTRATION, 1234, registration_payload(
                provided_services=[checklist_row(1, 'PSS'), checklist_row(2, 'LEGO')],
            ))],
            SOURCE_SYSTEM_COMPILER,
        )
        ingest_events(
            [event(RESOURCE_REGISTRATION, 1234, registration_payload(
                provided_services=[checklist_row(1, 'PSS')],
            ))],
            SOURCE_SYSTEM_COMPILER,
        )

        self.assertEqual(
            list(ProvidedServices.objects.values_list('name', flat=True)), ['PSS']
        )

    def test_service_id_is_remapped_when_the_service_arrived_first(self):
        ingest_events(
            [event(RESOURCE_REGISTRATION, 1234, registration_payload())],
            SOURCE_SYSTEM_COMPILER,
        )
        ingest_events(
            [event(RESOURCE_PSS_SERVICE, 55, {
                'fields': {}, 'registration': {'source_id': 1234},
            })],
            SOURCE_SYSTEM_COMPILER,
        )
        local_pss = PSSService.objects.get()

        ingest_events(
            [event(RESOURCE_REGISTRATION, 1234, registration_payload(
                provided_services=[checklist_row(
                    1, 'PSS', completed=True,
                    service={'resource': RESOURCE_PSS_SERVICE, 'source_id': 55},
                )],
            ))],
            SOURCE_SYSTEM_COMPILER,
        )

        row = ProvidedServices.objects.get(name='PSS')
        self.assertEqual(row.service_id, local_pss.pk)
        self.assertTrue(row.completed)
        self.assertEqual(str(row.completion_date), '2026-03-05')

    def test_service_id_is_filled_in_when_the_service_arrives_later(self):
        """Live pushes can land the registration before the service it names."""
        result = ingest_events(
            [event(RESOURCE_REGISTRATION, 1234, registration_payload(
                provided_services=[checklist_row(
                    1, 'PSS', completed=True,
                    service={'resource': RESOURCE_PSS_SERVICE, 'source_id': 55},
                )],
            ))],
            SOURCE_SYSTEM_COMPILER,
        )
        self.assertIsNone(ProvidedServices.objects.get(name='PSS').service_id)
        self.assertIn('waits for mscc.pss_service#55', result['results'][0]['detail'])

        ingest_events(
            [event(RESOURCE_PSS_SERVICE, 55, {
                'fields': {}, 'registration': {'source_id': 1234},
            })],
            SOURCE_SYSTEM_COMPILER,
        )

        self.assertEqual(
            ProvidedServices.objects.get(name='PSS').service_id,
            PSSService.objects.get().pk,
        )

    def test_shared_checklist_name_follows_the_compilers_reference(self):
        """Two models complete "Health and Nutrition"; the reference decides."""
        # The two tables have independent id sequences and would otherwise
        # both land on the same id here, which would make the check below
        # pass for the wrong reason.
        HealthNutritionReferral.objects.create()

        ingest_events([
            event(RESOURCE_REGISTRATION, 1234, registration_payload()),
            event(RESOURCE_HEALTH_NUTRITION_SERVICE, 70, {
                'fields': {}, 'registration': {'source_id': 1234},
            }),
            event(RESOURCE_HEALTH_NUTRITION_REFERRAL, 71, {
                'fields': {}, 'registration': {'source_id': 1234},
            }),
        ], SOURCE_SYSTEM_COMPILER)

        ingest_events(
            [event(RESOURCE_REGISTRATION, 1234, registration_payload(
                provided_services=[checklist_row(
                    1, 'Health and Nutrition', completed=True,
                    service={'resource': RESOURCE_HEALTH_NUTRITION_REFERRAL,
                             'source_id': 71},
                )],
            ))],
            SOURCE_SYSTEM_COMPILER,
        )

        registration = Registration.objects.get()
        row = ProvidedServices.objects.get(name='Health and Nutrition')
        self.assertEqual(
            row.service_id,
            HealthNutritionReferral.objects.get(registration=registration).pk,
        )
        self.assertNotEqual(
            row.service_id,
            HealthNutritionService.objects.get(registration=registration).pk,
        )

    def test_shared_name_is_not_claimed_by_the_wrong_table_arriving_first(self):
        """Registration first, then the *other* table, then the intended one.

        This is the live order when a partner saves the referral form: the
        registration push carries the reference, and the two services can land
        in any order behind it. The service that is not the intended target
        must leave the row alone.
        """
        HealthNutritionReferral.objects.create()  # desynchronise the id sequences
        ingest_events(
            [event(RESOURCE_REGISTRATION, 1234, registration_payload(
                provided_services=[checklist_row(
                    1, 'Health and Nutrition', completed=True,
                    service={'resource': RESOURCE_HEALTH_NUTRITION_REFERRAL,
                             'source_id': 71},
                )],
            ))],
            SOURCE_SYSTEM_COMPILER,
        )
        self.assertIsNone(ProvidedServices.objects.get().service_id)

        ingest_events(
            [event(RESOURCE_HEALTH_NUTRITION_SERVICE, 70, {
                'fields': {}, 'registration': {'source_id': 1234},
            })],
            SOURCE_SYSTEM_COMPILER,
        )
        self.assertIsNone(ProvidedServices.objects.get().service_id,
                          'the service claimed a row meant for the referral')

        ingest_events(
            [event(RESOURCE_HEALTH_NUTRITION_REFERRAL, 71, {
                'fields': {}, 'registration': {'source_id': 1234},
            })],
            SOURCE_SYSTEM_COMPILER,
        )
        registration = Registration.objects.get()
        self.assertEqual(
            ProvidedServices.objects.get().service_id,
            HealthNutritionReferral.objects.get(registration=registration).pk,
        )

    def test_a_checklist_row_with_no_service_is_not_claimed(self):
        """The Compiler says "not completed"; an unrelated service must not change that."""
        ingest_events(
            [event(RESOURCE_REGISTRATION, 1234, registration_payload(
                provided_services=[checklist_row(1, 'PSS')],
            ))],
            SOURCE_SYSTEM_COMPILER,
        )
        ingest_events(
            [event(RESOURCE_PSS_SERVICE, 55, {
                'fields': {}, 'registration': {'source_id': 1234},
            })],
            SOURCE_SYSTEM_COMPILER,
        )

        self.assertIsNone(ProvidedServices.objects.get(name='PSS').service_id)

    def test_education_history_gets_local_ids(self):
        ingest_events(
            [event(RESOURCE_REGISTRATION, 1234, registration_payload(
                education_history=[{
                    'source_id': 5,
                    'fields': {'student_old': 4242, 'programme_type': 'BLN',
                               'programme_id': 88},
                }],
            ))],
            SOURCE_SYSTEM_COMPILER,
        )

        registration = Registration.objects.get()
        line = EducationHistory.objects.get()
        self.assertEqual(line.registration_id, registration.pk)
        self.assertEqual(line.child, registration.child_id)
        self.assertEqual(line.programme_type, 'BLN')
        self.assertEqual(line.programme_id, 88)
        self.assertEqual(line.student_old, 4242)


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
