"""Phase 1 identity, dependency, ordering and authenticated HTTP regressions."""

from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db import connections
from django.test import TestCase, TransactionTestCase
from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from student_registration.child.models import Child
from student_registration.locations.models import Center
from student_registration.mscc.models import EducationAssessment, Registration, Round
from student_registration.schools.models import PartnerOrganization
from student_registration.students.models import Nationality

from ..constants import (RESOURCE_EDUCATION_ASSESSMENT, RESOURCE_PARTNER,
                         RESOURCE_REGISTRATION, RESOURCE_ROUND, SOURCE_SYSTEM_COMPILER)
from ..models import SyncedRecord, SyncEventLog
from ..services import ingest_events
from .test_ingest import event, registration_payload


def push(wire):
    return ingest_events([wire], SOURCE_SYSTEM_COMPILER)


def dated_event(resource, source_id, payload=None, day=1, operation='upsert'):
    wire = event(resource, source_id, payload, operation=operation)
    wire['source_modified'] = '2026-03-{:02d}T10:00:00Z'.format(day)
    return wire


class Phase1SyncTests(TestCase):
    def registration(self, day=1, source_id=1234, payload=None):
        result = push(dated_event(RESOURCE_REGISTRATION, source_id,
                                 payload or registration_payload(), day=day))
        self.assertEqual(result['applied'], 1, result)
        return Registration.objects.get(bma_id=str(source_id))

    def test_empty_receiver_creates_identified_references_and_local_relationships(self):
        reg = self.registration()
        self.assertEqual(reg.partner.bma_id, '7')
        self.assertEqual(reg.center.partner_id, reg.partner_id)
        self.assertEqual(reg.center.bma_id, '41')
        self.assertEqual(reg.round.bma_id, '3')
        self.assertEqual(reg.child.bma_id, '900')
        self.assertNotEqual(reg.partner.pk, 7)

    def test_partner_rename_keeps_identity_and_relationships(self):
        reg = self.registration()
        payload = registration_payload()
        payload['partner']['name'] = 'Renamed partner'
        payload['center']['partner']['name'] = 'Renamed partner'
        self.registration(day=2, payload=payload)
        reg.partner.refresh_from_db()
        self.assertEqual(reg.partner.name, 'Renamed partner')
        self.assertEqual(PartnerOrganization.objects.count(), 1)

    def test_standalone_partner_event_and_older_reference_do_not_undo_rename(self):
        reg = self.registration()
        result = push(dated_event(RESOURCE_PARTNER, 7,
                                 {'fields': {'name': 'Latest partner'}}, day=3))
        self.assertEqual(result['applied'], 1, result)
        self.registration(day=2, source_id=1235)
        reg.partner.refresh_from_db()
        self.assertEqual(reg.partner.name, 'Latest partner')

    def test_unidentified_partner_is_rejected_atomically(self):
        payload = registration_payload()
        payload['partner'] = {'name': 'Partner One'}
        result = push(dated_event(RESOURCE_REGISTRATION, 1234, payload))
        self.assertEqual(result['failed'], 1, result)
        self.assertFalse(result['results'][0]['retryable'])
        self.assertEqual(Child.objects.count(), 0)
        self.assertEqual(Center.objects.count(), 0)
        self.assertEqual(SyncedRecord.objects.count(), 0)

    def test_same_partner_name_with_different_ids_is_not_silently_merged(self):
        self.registration()
        result = push(dated_event(RESOURCE_PARTNER, 8, {'fields': {'name': 'Partner One'}}))
        self.assertEqual(result['failed'], 1, result)
        self.assertFalse(PartnerOrganization.objects.filter(bma_id='8').exists())

    def test_missing_nationality_rolls_back_and_same_event_can_retry(self):
        payload = registration_payload()
        payload['child']['nationality'] = {'source_id': 1, 'name': 'Lebanese'}
        wire = dated_event(RESOURCE_REGISTRATION, 1234, payload)
        result = push(wire)
        self.assertTrue(result['results'][0]['retryable'], result)
        for model in (Child, Registration, Center, Round, PartnerOrganization, SyncedRecord):
            self.assertEqual(model.objects.count(), 0)
        nationality = Nationality.objects.create(name='Lebanese')
        result = push(wire)
        self.assertEqual(result['applied'], 1, result)
        self.assertEqual(Child.objects.get().nationality_id, nationality.pk)

    def test_missing_caregiver_nationality_also_blocks_the_record(self):
        payload = registration_payload()
        payload['child']['main_caregiver_nationality'] = {'name': 'Missing'}
        result = push(dated_event(RESOURCE_REGISTRATION, 1234, payload))
        self.assertTrue(result['results'][0]['retryable'], result)
        self.assertFalse(Child.objects.exists())

    def test_older_registration_does_not_mutate_embedded_child_or_partner(self):
        reg = self.registration(day=3)
        payload = registration_payload()
        payload['fields']['have_labour'] = 'Yes - Morning'
        payload['child']['fields']['first_name'] = 'Older child'
        payload['partner']['name'] = 'Older partner'
        wire = dated_event(RESOURCE_REGISTRATION, 1234, payload, day=2)
        result = push(wire)
        self.assertEqual(result['skipped'], 1, result)
        reg.refresh_from_db()
        self.assertEqual(reg.have_labour, 'No')
        self.assertEqual(reg.child.first_name, 'Lina')
        self.assertEqual(reg.partner.name, 'Partner One')
        self.assertEqual(SyncEventLog.objects.get(event_id=wire['event_id']).status, 'skipped')
        self.assertEqual(push(wire)['skipped'], 1)

    def test_older_child_in_another_registration_preserves_latest_child(self):
        self.registration(day=3)
        payload = registration_payload()
        payload['child']['fields']['first_name'] = 'Older child'
        self.registration(day=2, source_id=1235, payload=payload)
        self.assertEqual(Child.objects.get().first_name, 'Lina')
        self.assertEqual(Registration.objects.count(), 2)

    def test_explicit_child_timestamp_is_used(self):
        payload = registration_payload()
        payload['child']['source_modified'] = '2026-03-03T10:00:00Z'
        self.registration(day=3, payload=payload)
        payload['child']['source_modified'] = '2026-03-02T10:00:00Z'
        payload['child']['fields']['first_name'] = 'Stale child'
        self.registration(day=4, payload=payload)
        self.assertEqual(Child.objects.get().first_name, 'Lina')

    def test_stale_delete_is_skipped_and_tombstone_blocks_old_recreation(self):
        self.registration(day=3)
        result = push(dated_event(RESOURCE_REGISTRATION, 1234, day=2, operation='delete'))
        self.assertEqual(result['skipped'], 1, result)
        self.assertTrue(Registration.objects.exists())
        result = push(dated_event(RESOURCE_REGISTRATION, 1234, day=4, operation='delete'))
        self.assertEqual(result['applied'], 1, result)
        result = push(dated_event(RESOURCE_REGISTRATION, 1234, registration_payload(), day=3))
        self.assertEqual(result['skipped'], 1, result)
        self.assertFalse(Registration.objects.exists())

    def test_assessment_waits_for_registration_then_creates_and_updates_same_record(self):
        wire = dated_event(RESOURCE_EDUCATION_ASSESSMENT, 50, {
            'registration': {'source_id': 1234},
            'fields': {'pre_arabic_grade': 10},
        })
        result = push(wire)
        self.assertTrue(result['results'][0]['retryable'], result)
        reg = self.registration()
        self.assertEqual(push(wire)['applied'], 1)
        assessment = EducationAssessment.objects.get(bma_id='50')
        self.assertEqual(assessment.registration_id, reg.pk)
        self.assertEqual(push(wire)['skipped'], 1)
        wire = dated_event(RESOURCE_EDUCATION_ASSESSMENT, 50, {
            'registration': {'source_id': 1234},
            'fields': {'pre_arabic_grade': 20},
        }, day=2)
        self.assertEqual(push(wire)['applied'], 1)
        assessment.refresh_from_db()
        self.assertEqual(assessment.pre_arabic_grade, 20)
        self.assertEqual(EducationAssessment.objects.count(), 1)

    def test_missing_timestamp_cannot_overwrite_a_versioned_record(self):
        self.registration()
        wire = dated_event(RESOURCE_REGISTRATION, 1234, registration_payload())
        del wire['source_modified']
        result = push(wire)
        self.assertEqual(result['failed'], 1, result)

    def test_bad_event_id_and_naive_timestamp_are_reported_without_writes(self):
        for field, value in [('event_id', 'bad-uuid'),
                             ('source_modified', '2026-03-01T10:00:00')]:
            wire = dated_event(RESOURCE_REGISTRATION, 1234, registration_payload())
            wire[field] = value
            self.assertEqual(push(wire)['failed'], 1)
        self.assertFalse(Registration.objects.exists())


class Phase1HttpTests(TestCase):
    def setUp(self):
        user = get_user_model().objects.create(username='phase1-sync')
        group, _ = Group.objects.get_or_create(name='DataSync')
        user.groups.add(group)
        token = Token.objects.create(user=user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Token {}'.format(token.key))
        self.url = reverse('datasync:ingest')

    def test_unsupported_contract_rejected_before_writes(self):
        response = self.client.post(self.url, {
            'contract_version': '99.0',
            'events': [dated_event(RESOURCE_REGISTRATION, 1234, registration_payload())],
        }, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertFalse(Registration.objects.exists())

    def test_out_of_order_http_batch_resolves_dependencies(self):
        response = self.client.post(self.url, {
            'contract_version': '1.0', 'source_system': SOURCE_SYSTEM_COMPILER,
            'events': [
                dated_event(RESOURCE_EDUCATION_ASSESSMENT, 50,
                            {'registration': {'source_id': 1234},
                             'fields': {'pre_arabic_grade': 10}}),
                dated_event(RESOURCE_REGISTRATION, 1234, registration_payload()),
            ],
        }, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['applied'], 2, response.data)
        self.assertEqual(EducationAssessment.objects.get().registration_id,
                         Registration.objects.get().pk)


class ConcurrentSyncTests(TransactionTestCase):
    def concurrent_push(self, wires):
        barrier = Barrier(len(wires))

        def worker(wire):
            try:
                barrier.wait(timeout=10)
                return push(wire)
            finally:
                connections.close_all()

        with ThreadPoolExecutor(max_workers=len(wires)) as executor:
            return list(executor.map(worker, wires))

    def test_concurrent_same_event_is_applied_once(self):
        wire = dated_event(RESOURCE_REGISTRATION, 1234, registration_payload())
        results = self.concurrent_push([wire, wire])
        self.assertEqual(sum(result['applied'] for result in results), 1, results)
        self.assertEqual(sum(result['skipped'] for result in results), 1, results)
        self.assertEqual(Registration.objects.count(), 1)
        self.assertEqual(SyncEventLog.objects.count(), 1)

    def test_concurrent_first_updates_finish_with_newest_source_version(self):
        results = self.concurrent_push([
            dated_event(RESOURCE_ROUND, 3, {'fields': {'name': 'Older'}}, day=1),
            dated_event(RESOURCE_ROUND, 3, {'fields': {'name': 'Newest'}}, day=2),
        ])
        self.assertEqual(sum(result['failed'] for result in results), 0, results)
        self.assertEqual(Round.objects.get().name, 'Newest')
        self.assertEqual(SyncedRecord.objects.count(), 1)
