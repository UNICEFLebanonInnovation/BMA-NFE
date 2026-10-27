"""ProgramStaff IDs must not collide with old school-teacher IDs."""
from django.db import IntegrityError, transaction
from django.test import TestCase

from student_registration.locations.models import Center
from student_registration.mscc.models import Teacher, Registration
from ..constants import RESOURCE_PROGRAM_STAFF, RESOURCE_REGISTRATION, SOURCE_SYSTEM_COMPILER
from ..models import SyncedRecord
from ..services import ingest_events
from .test_ingest import event, registration_payload


class ProgramStaffTests(TestCase):
    def setUp(self):
        self.center = Center.objects.create(name='Existing Makani centre', bma_id='center-1')
        self.payload = {
            'source_model': 'locations.programstaff',
            'center': {'source_id': 'center-1'},
            'fields': {
                'facilitator_name': 'Full facilitator name ' * 8,
                'sex': 'Female', 'primary_phone_number': '70-123456',
                'email': 'facilitator@example.test', 'teaching_hours_mscc': 14,
                'program_staff_details': {'programs': ['BLN', 'RS'],
                    'subject': ['Education'], 'training_topics': ['PSEA'],
                    'attendance_training': 'Yes', 'is_active_current_round': 'Yes'},
            },
        }

    def push(self, operation='upsert', payload=None):
        return ingest_events([event(RESOURCE_PROGRAM_STAFF, '17',
            self.payload if payload is None else payload, operation=operation)], SOURCE_SYSTEM_COMPILER)

    def current(self):
        return Teacher.objects.get(bma_id='17', bma_source=RESOURCE_PROGRAM_STAFF)

    def test_program_staff_arrives_in_existing_teacher_table(self):
        result = self.push()
        self.assertEqual(result['applied'], 1, result['results'])
        teacher = self.current()
        self.assertEqual(teacher.center, self.center)
        self.assertEqual(str(teacher), self.payload['fields']['facilitator_name'])
        self.assertIsNone(teacher.round_id)
        self.assertEqual(teacher.program_staff_details, self.payload['fields']['program_staff_details'])

    def test_identical_numeric_legacy_id_is_preserved(self):
        old = Teacher.objects.create(bma_id='17', center=self.center, first_name='Old Dirasa source')
        self.assertEqual(self.push()['applied'], 1)
        self.assertNotEqual(self.current().pk, old.pk)
        old.refresh_from_db()
        self.assertEqual(old.first_name, 'Old Dirasa source')

    def test_repeating_sync_updates_one_row(self):
        self.push()
        old_pk = self.current().pk
        self.payload['fields']['facilitator_name'] = 'Changed facilitator'
        self.assertEqual(self.push()['applied'], 1)
        self.assertEqual(self.current().pk, old_pk)
        self.assertEqual(self.current().facilitator_name, 'Changed facilitator')
        self.assertEqual(Teacher.objects.count(), 1)
        self.assertEqual(SyncedRecord.objects.filter(resource=RESOURCE_PROGRAM_STAFF).count(), 1)

    def test_move_to_another_center_updates_same_teacher(self):
        self.push()
        pk = self.current().pk
        other = Center.objects.create(name='Other centre', bma_id='center-2')
        self.payload['center'] = {'source_id': 'center-2'}
        self.assertEqual(self.push()['applied'], 1)
        self.assertEqual(self.current().pk, pk)
        self.assertEqual(self.current().center, other)
        self.assertEqual(Teacher.objects.count(), 1)

    def test_database_prevents_duplicate_programstaff_across_centers(self):
        self.push()
        other = Center.objects.create(name='Other centre', bma_id='center-2')
        with self.assertRaises(IntegrityError), transaction.atomic():
            Teacher.objects.create(bma_source=RESOURCE_PROGRAM_STAFF, bma_id='17', center=other)

    def test_delete_keeps_legacy_teacher_with_same_number(self):
        old = Teacher.objects.create(bma_id='17', center=self.center, first_name='Legacy')
        self.push()
        result = self.push('delete', {'scope': 'makani'})
        self.assertEqual(result['applied'], 1, result['results'])
        self.assertFalse(Teacher.objects.filter(bma_source=RESOURCE_PROGRAM_STAFF).exists())
        self.assertTrue(Teacher.objects.filter(pk=old.pk).exists())

    def test_wrong_source_model_and_tls_staff_are_rejected(self):
        self.payload['source_model'] = 'students.teacher'
        self.assertEqual(self.push()['failed'], 1)
        self.payload['source_model'] = 'locations.programstaff'
        self.payload['fields']['program_staff_details']['programs'] = ['TLS']
        self.assertEqual(self.push()['failed'], 1)
        self.assertFalse(Teacher.objects.exists())

    def test_source_email_length_is_preserved(self):
        email = 'a' * 100 + '@example.test'
        self.payload['fields']['email'] = email
        self.assertEqual(self.push()['applied'], 1)
        self.assertEqual(self.current().email, email)

    def test_legacy_teacher_is_not_advertised_by_the_receiver(self):
        from ..api_views import SyncIngestView
        capabilities = SyncIngestView().get(None).data
        self.assertIn(RESOURCE_PROGRAM_STAFF, capabilities['resources'])
        self.assertNotIn('mscc.teacher', capabilities['resources'])

    def test_tls_registration_rejected_before_embedded_child_write(self):
        payload = registration_payload()
        payload['fields']['type'] = 'TLS'
        result = ingest_events([event(RESOURCE_REGISTRATION, 'tls-1', payload)], SOURCE_SYSTEM_COMPILER)
        self.assertEqual(result['failed'], 1)
        self.assertFalse(Registration.objects.exists())
