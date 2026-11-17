"""An event receipt belongs to one immutable producer/record/operation."""
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from unittest.mock import patch
import uuid

from django.db import connections
from django.test import TestCase, TransactionTestCase

from student_registration.locations.models import Center
from student_registration.mscc.models import Round
from ..constants import RESOURCE_CENTER, RESOURCE_ROUND, SOURCE_SYSTEM_COMPILER
from ..models import SyncEventLog
from ..services import _log_event, ingest_events
from .test_ingest import event


class EventIdentityTests(TestCase):
    def setUp(self):
        self.wire = event(RESOURCE_ROUND, 70, {'fields': {'name': 'Original QA round'}})
        self.original = self.push(self.wire)['results'][0]
        self.receipt = dict(SyncEventLog.objects.get().applied_result)

    def push(self, wire, source=SOURCE_SYSTEM_COMPILER):
        return ingest_events([wire], source)

    def assert_rejected(self, wire, source=SOURCE_SYSTEM_COMPILER):
        result = self.push(wire, source)
        self.assertEqual(result['failed'], 1, result)
        self.assertEqual(result['skipped'], 0)
        self.assertFalse(result['results'][0]['retryable'])
        self.assertIsNone(result['results'][0]['local_id'])
        self.assertIn('event_id', result['results'][0]['detail'])
        self.assertEqual(Round.objects.count(), 1)
        self.assertEqual(Round.objects.get().name, 'Original QA round')
        log = SyncEventLog.objects.get()
        self.assertEqual(log.source_id, '70')
        self.assertEqual(log.resource, RESOURCE_ROUND)
        self.assertEqual(log.operation, 'upsert')
        self.assertEqual(log.source_system, SOURCE_SYSTEM_COMPILER)
        self.assertEqual(log.applied_result, self.receipt)

    def test_applied_event_id_cannot_be_reused_for_another_record(self):
        self.assert_rejected(dict(self.wire, source_id=71))

    def test_applied_event_id_cannot_be_reused_for_another_resource(self):
        self.assert_rejected(dict(self.wire, resource=RESOURCE_CENTER))
        self.assertFalse(Center.objects.exists())

    def test_applied_event_id_cannot_be_reused_for_delete(self):
        self.assert_rejected(dict(self.wire, operation='delete'))

    def test_applied_event_id_cannot_be_reused_by_another_producer(self):
        self.assert_rejected(self.wire, source='another-producer')

    def test_normalized_record_id_is_still_a_valid_replay(self):
        result = self.push(dict(self.wire, source_id=' 70 '))
        self.assertEqual(result['skipped'], 1, result)
        self.assertEqual(result['results'][0]['local_id'], self.original['local_id'])

    def test_rebuilt_payload_does_not_change_a_committed_receipt(self):
        result = self.push(dict(self.wire, payload={'fields': {'name': 'Latest payload'}}))
        self.assertEqual(result['skipped'], 1, result)
        self.assertEqual(result['results'][0]['local_id'], self.original['local_id'])
        self.assertEqual(Round.objects.get().name, 'Original QA round')

    def test_a_stale_skipped_receipt_cannot_acknowledge_another_record(self):
        old = dict(self.wire, event_id=str(uuid.uuid4()), source_modified='2000-01-01T00:00:00Z')
        self.assertEqual(self.push(old)['skipped'], 1)
        result = self.push(dict(old, source_id=71))
        self.assertEqual(result['failed'], 1, result)
        self.assertFalse(Round.objects.filter(bma_id='71').exists())

    def test_failed_event_identity_is_reserved_and_its_log_is_preserved(self):
        wire = event(RESOURCE_ROUND, 72)
        SyncEventLog.objects.create(event_id=wire['event_id'], source_system=SOURCE_SYSTEM_COMPILER,
            resource=RESOURCE_ROUND, source_id='72', operation='upsert', status='failed', detail='Pending repair')
        result = self.push(dict(wire, source_id=73))
        self.assertEqual(result['failed'], 1, result)
        self.assertFalse(Round.objects.filter(bma_id__in=['72','73']).exists())
        log = SyncEventLog.objects.get(event_id=wire['event_id'])
        self.assertEqual((log.source_id,log.status,log.detail), ('72','failed','Pending repair'))

    def test_failed_event_can_retry_the_same_identity_with_a_repaired_payload(self):
        wire = event(RESOURCE_ROUND, 72, {'fields': {'name': 'Repaired'}})
        SyncEventLog.objects.create(event_id=wire['event_id'], source_system=SOURCE_SYSTEM_COMPILER,
            resource=RESOURCE_ROUND, source_id='72', operation='upsert', status='failed')
        result = self.push(wire)
        self.assertEqual(result['applied'], 1, result)
        self.assertEqual(Round.objects.get(bma_id='72').name, 'Repaired')

    def test_collision_is_rechecked_under_the_database_lock(self):
        # Simulate a receipt committed after the first unlocked read.
        with patch('student_registration.datasync.services._already_applied', return_value=None):
            self.assert_rejected(dict(self.wire, source_id=71))

    def test_late_failed_attempt_cannot_reassign_an_existing_failed_log(self):
        wire = event(RESOURCE_ROUND, 72)
        SyncEventLog.objects.create(event_id=wire['event_id'], source_system=SOURCE_SYSTEM_COMPILER,
            resource=RESOURCE_ROUND, source_id='72', operation='upsert', status='failed', detail='Original failure')
        _log_event(dict(wire, source_id=73), SOURCE_SYSTEM_COMPILER, 'failed', 'Wrong identity', [])
        log = SyncEventLog.objects.get(event_id=wire['event_id'])
        self.assertEqual((log.source_id,log.detail), ('72','Original failure'))

    def test_collision_does_not_block_an_unrelated_valid_event_in_the_batch(self):
        fresh = event(RESOURCE_ROUND, 74, {'fields': {'name': 'Unrelated valid round'}})
        result = ingest_events([dict(self.wire,source_id=71),fresh], SOURCE_SYSTEM_COMPILER)
        self.assertEqual((result['applied'],result['failed'],result['skipped']), (1,1,0), result)
        self.assertFalse(Round.objects.filter(bma_id='71').exists())
        self.assertTrue(Round.objects.filter(bma_id='74').exists())


class ConcurrentEventIdentityTests(TransactionTestCase):
    def test_two_records_racing_with_one_event_id_produce_one_winner(self):
        event_id = str(uuid.uuid4())
        wires = [event(RESOURCE_ROUND,source_id,{'fields':{'name':'QA '+str(source_id)}},event_id=event_id)
                 for source_id in (80,81)]
        barrier = Barrier(2)
        def push(wire):
            try:
                barrier.wait(timeout=10)
                return ingest_events([wire],SOURCE_SYSTEM_COMPILER)
            finally:
                connections.close_all()
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(push,wires))
        self.assertEqual(sum(row['applied'] for row in results),1,results)
        self.assertEqual(sum(row['failed'] for row in results),1,results)
        self.assertEqual(sum(row['skipped'] for row in results),0,results)
        self.assertEqual(Round.objects.count(),1)
        log = SyncEventLog.objects.get()
        self.assertEqual(log.source_id,Round.objects.get().bma_id)
        self.assertEqual(log.status,'applied')
