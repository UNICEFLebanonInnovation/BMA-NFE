"""BMA entity IDs, composite teacher identities and real local foreign keys."""

from django.db import IntegrityError, connection, transaction
from django.test import TestCase

from student_registration.attendances.models import MSCCAttendance, MSCCAttendanceChild
from student_registration.child.models import Child
from student_registration.locations.models import Center
from student_registration.mscc.models import (
    EducationProgrammeAssessment, EducationService, Referral, Registration, Round, Teacher,
)

from ..constants import (
    RESOURCE_ATTENDANCE, RESOURCE_CENTER, RESOURCE_EDUCATION_SERVICE,
    RESOURCE_GRADING, RESOURCE_REFERRAL, RESOURCE_REGISTRATION, RESOURCE_ROUND,
    RESOURCE_TEACHER, SOURCE_SYSTEM_COMPILER,
)
from ..models import SyncedRecord
from ..services import ingest_events
from .test_ingest import event, registration_payload


class BmaIdentityTests(TestCase):
    def setUp(self):
        self.payload = registration_payload()
        self.payload['center']['source_id'] = 'center-41'
        self.payload['round']['source_id'] = 'round-3'
        self.payload['child']['source_id'] = 'child-900'
        result = self.push(RESOURCE_REGISTRATION, 'reg-1234', self.payload)
        self.assertEqual(result['applied'], 1, result['results'])
        self.registration = Registration.objects.get(bma_id='reg-1234')
        self.child = self.registration.child
        self.center = self.registration.center
        self.round = self.registration.round

    def push(self, resource, source_id, payload=None, operation='upsert'):
        return ingest_events([event(resource, source_id, payload, operation=operation)],
                             SOURCE_SYSTEM_COMPILER)

    def test_same_bma_round_id_updates_existing_row_despite_different_name(self):
        old_pk = self.round.pk
        result = self.push(RESOURCE_ROUND, 'round-3', {'fields': {'name': 'New round name'}})
        self.assertEqual(result['applied'], 1, result['results'])
        self.round.refresh_from_db()
        self.assertEqual(self.round.name, 'New round name')
        self.assertEqual(result['results'][0]['local_id'], old_pk)
        self.assertEqual(Round.objects.count(), 1)

    def test_same_round_name_with_different_bma_ids_stays_separate(self):
        result = self.push(RESOURCE_ROUND, 'round-4', {'fields': {'name': self.round.name}})
        self.assertEqual(result['applied'], 1, result['results'])
        self.assertEqual(Round.objects.count(), 2)
        self.assertNotEqual(result['results'][0]['local_id'], self.round.pk)

    def test_same_bma_center_id_updates_existing_row_despite_name_and_pcode(self):
        result = self.push(RESOURCE_CENTER, 'center-41', {
            'fields': {'name': 'Different centre name', 'p_code': 'DIFFERENT'},
        })
        self.assertEqual(result['applied'], 1, result['results'])
        self.assertEqual(result['results'][0]['local_id'], self.center.pk)
        self.center.refresh_from_db()
        self.assertEqual(self.center.name, 'Different centre name')
        self.assertEqual(Center.objects.count(), 1)

    def test_same_center_name_and_pcode_with_different_ids_stays_separate(self):
        result = self.push(RESOURCE_CENTER, 'center-42', {
            'fields': {'name': self.center.name, 'p_code': self.center.p_code},
        })
        self.assertEqual(result['applied'], 1, result['results'])
        self.assertEqual(Center.objects.count(), 2)

    def test_local_rows_without_bma_ids_are_not_adopted_by_name_or_unicef_id(self):
        local_round = Round.objects.create(name=self.round.name)
        local_center = Center.objects.create(name=self.center.name, p_code=self.center.p_code)
        local_child = Child.objects.create(unicef_id=self.child.unicef_id)
        local_registration = Registration.objects.create(
            child=local_child, round=local_round, center=local_center,
        )
        self.push(RESOURCE_REGISTRATION, 'reg-1234', self.payload)
        for row in (local_round, local_center, local_child, local_registration):
            row.refresh_from_db()
            self.assertIsNone(row.bma_id)
        self.assertEqual(self.registration.pk, Registration.objects.get(bma_id='reg-1234').pk)

    def test_child_bma_id_stays_the_same_when_unicef_id_changes(self):
        self.payload['child']['fields']['unicef_id'] = 'NEW-UNICEF-ID'
        result = self.push(RESOURCE_REGISTRATION, 'reg-1234', self.payload)
        self.assertEqual(result['applied'], 1, result['results'])
        self.child.refresh_from_db()
        self.assertEqual(self.child.unicef_id, 'NEW-UNICEF-ID')
        self.assertEqual(Child.objects.count(), 1)

    def test_same_unicef_id_with_different_bma_child_ids_stays_separate(self):
        self.payload['child']['source_id'] = 'child-901'
        result = self.push(RESOURCE_REGISTRATION, 'reg-1235', self.payload)
        self.assertEqual(result['applied'], 1, result['results'])
        self.assertEqual(Child.objects.filter(unicef_id='UNI-900').count(), 2)
        self.assertEqual(Registration.objects.count(), 2)

    def test_child_can_have_multiple_registrations_with_distinct_bma_ids(self):
        result = self.push(RESOURCE_REGISTRATION, 'reg-1235', self.payload)
        self.assertEqual(result['applied'], 1, result['results'])
        self.assertEqual(Child.objects.count(), 1)
        self.assertEqual(Registration.objects.filter(child=self.child).count(), 2)

    def test_embedded_child_reference_can_reuse_existing_bma_entity(self):
        self.payload['child'] = {'bma_id': 'child-900'}
        result = self.push(RESOURCE_REGISTRATION, 'reg-1235', self.payload)
        self.assertEqual(result['applied'], 1, result['results'])
        self.assertEqual(Registration.objects.get(bma_id='reg-1235').child_id, self.child.pk)

    def test_embedded_child_reference_waits_for_unknown_entity(self):
        self.payload['child'] = {'bma_id': 'missing-child'}
        result = self.push(RESOURCE_REGISTRATION, 'reg-1235', self.payload)
        self.assertEqual(result['failed'], 1, result['results'])
        self.assertTrue(result['results'][0]['retryable'])
        self.assertEqual(Registration.objects.count(), 1)

    def test_reference_bma_id_alias_resolves_local_foreign_keys(self):
        self.payload['center'] = {'bma_id': 'center-41', 'name': 'Wrong name'}
        self.payload['round'] = {'bma_id': 'round-3', 'name': 'Wrong name'}
        result = self.push(RESOURCE_REGISTRATION, 'reg-1234', self.payload)
        self.assertEqual(result['applied'], 1, result['results'])
        self.registration.refresh_from_db()
        self.assertEqual(self.registration.center_id, self.center.pk)
        self.assertEqual(self.registration.round_id, self.round.pk)
        self.assertEqual(self.registration.child_id, self.child.pk)

    def test_name_only_reference_is_rejected_without_writing_child_changes(self):
        self.payload['round'] = {'name': self.round.name}
        self.payload['child']['fields']['first_name'] = 'Should roll back'
        result = self.push(RESOURCE_REGISTRATION, 'reg-1234', self.payload)
        self.assertEqual(result['failed'], 1, result['results'])
        self.child.refresh_from_db()
        self.assertEqual(self.child.first_name, 'Lina')

    def test_conflicting_reference_ids_are_rejected(self):
        self.payload['center'] = {'source_id': 'center-41', 'bma_id': 'center-42'}
        result = self.push(RESOURCE_REGISTRATION, 'reg-1234', self.payload)
        self.assertEqual(result['failed'], 1, result['results'])
        self.assertIn('different BMA records', result['results'][0]['detail'])

    def test_conflicting_payload_identity_is_rejected(self):
        self.payload['fields']['bma_id'] = 'other-registration'
        result = self.push(RESOURCE_REGISTRATION, 'reg-1234', self.payload)
        self.assertEqual(result['failed'], 1, result['results'])
        self.assertEqual(Registration.objects.count(), 1)

    def test_invalid_bma_ids_are_rejected(self):
        for source_id in ('   ', 'X' * 65, True, {'id': 1}):
            with self.subTest(source_id=source_id):
                result = self.push(RESOURCE_CENTER, source_id, {'fields': {'name': 'Invalid'}})
                self.assertEqual(result['failed'], 1, result['results'])
        self.assertEqual(Center.objects.count(), 1)

    def test_teacher_identity_is_teacher_id_plus_center(self):
        for center_id, first_name in (('center-41', 'Teacher One'), ('center-42', 'Teacher Two')):
            result = self.push(RESOURCE_TEACHER, 'teacher-7', {
                'fields': {'first_name': first_name, 'unicef_id': 'SAME-UNICEF-ID'},
                'center': {'source_id': center_id},
            })
            self.assertEqual(result['applied'], 1, result['results'])
        self.assertEqual(Teacher.objects.filter(bma_id='teacher-7').count(), 2)
        first = Teacher.objects.get(bma_id='teacher-7', center=self.center)
        result = self.push(RESOURCE_TEACHER, 'teacher-7', {
            'fields': {'first_name': 'Updated'}, 'center': {'source_id': 'center-41'},
        })
        self.assertEqual(result['results'][0]['local_id'], first.pk)
        first.refresh_from_db()
        self.assertEqual(first.first_name, 'Updated')
        self.assertEqual(Teacher.objects.exclude(pk=first.pk).get().first_name, 'Teacher Two')
        scopes = set(SyncedRecord.objects.filter(resource=RESOURCE_TEACHER).values_list('source_scope', flat=True))
        self.assertEqual(scopes, {'center-41', 'center-42'})

    def test_teacher_without_center_is_rejected(self):
        result = self.push(RESOURCE_TEACHER, 'teacher-7', {'fields': {'first_name': 'No centre'}})
        self.assertEqual(result['failed'], 1, result['results'])
        self.assertEqual(Teacher.objects.count(), 0)

    def test_teacher_delete_targets_only_one_center(self):
        for center_id in ('center-41', 'center-42'):
            self.push(RESOURCE_TEACHER, 'teacher-7', {'center': {'source_id': center_id}})
        result = self.push(RESOURCE_TEACHER, 'teacher-7',
                           {'center': {'source_id': 'center-41'}}, operation='delete')
        self.assertEqual(result['applied'], 1, result['results'])
        self.assertEqual(Teacher.objects.get().center.bma_id, 'center-42')
        self.assertTrue(SyncedRecord.objects.get(resource=RESOURCE_TEACHER, source_scope='center-41').deleted)

    def test_teacher_delete_without_center_cannot_delete_an_arbitrary_row(self):
        self.push(RESOURCE_TEACHER, 'teacher-7', {'center': {'source_id': 'center-41'}})
        result = self.push(RESOURCE_TEACHER, 'teacher-7', operation='delete')
        self.assertEqual(result['failed'], 1, result['results'])
        self.assertEqual(Teacher.objects.count(), 1)

    def test_existing_services_grading_and_referrals_update_by_bma_id_without_mapping(self):
        cases = (
            (EducationService, RESOURCE_EDUCATION_SERVICE, 'education_status', 'No'),
            (EducationProgrammeAssessment, RESOURCE_GRADING, 'programme_type', 'Updated'),
            (Referral, RESOURCE_REFERRAL, 'referred_formal_education', 'Yes'),
        )
        for Model, resource, field, value in cases:
            with self.subTest(resource=resource):
                row = Model.objects.create(bma_id='service-55', registration=self.registration)
                result = self.push(resource, 'service-55', {
                    'fields': {field: value}, 'registration': {'source_id': 'reg-1234'},
                })
                self.assertEqual(result['applied'], 1, result['results'])
                self.assertEqual(result['results'][0]['local_id'], row.pk)
                self.assertEqual(Model.objects.count(), 1)
                row.refresh_from_db()
                self.assertEqual(getattr(row, field), value)
                self.assertEqual(row.registration_id, self.registration.pk)

    def test_registration_reference_does_not_use_a_coincident_local_id(self):
        result = self.push(RESOURCE_EDUCATION_SERVICE, 'service-55', {
            'fields': {'education_status': 'No'},
            'registration': {'source_id': self.registration.pk},
        })
        self.assertEqual(result['failed'], 1, result['results'])
        self.assertTrue(result['results'][0]['retryable'])
        self.assertEqual(EducationService.objects.count(), 0)

    def test_delete_finds_a_bma_identified_record_without_mapping(self):
        row = Referral.objects.create(bma_id='referral-77', registration=self.registration)
        result = self.push(RESOURCE_REFERRAL, 'referral-77', operation='delete')
        self.assertEqual(result['applied'], 1, result['results'])
        self.assertFalse(Referral.objects.filter(pk=row.pk).exists())

    def test_unknown_attendance_registration_rolls_back_replacement(self):
        payload = {
            'fields': {'attendance_date': '2026-10-08'},
            'center': {'source_id': 'center-41'}, 'round': {'source_id': 'round-3'},
            'children': [{'registration': {'source_id': 'reg-1234'}, 'fields': {'attended': 'Yes'}}],
        }
        self.push(RESOURCE_ATTENDANCE, 'day-500', payload)
        day = MSCCAttendance.objects.get(bma_id='day-500')
        self.assertEqual(day.round_id, self.round.pk)
        old_child_pk = MSCCAttendanceChild.objects.get().pk
        payload['children'] = [{'registration': {'source_id': 'missing'}, 'fields': {'attended': 'No'}}]
        result = self.push(RESOURCE_ATTENDANCE, 'day-500', payload)
        self.assertEqual(result['failed'], 1, result['results'])
        self.assertTrue(result['results'][0]['retryable'])
        self.assertEqual(MSCCAttendanceChild.objects.get().pk, old_child_pk)
        self.assertEqual(MSCCAttendanceChild.objects.get().attended, 'Yes')

    def test_database_rejects_duplicate_bma_ids(self):
        models = (Round, Center, Child, Registration, EducationService,
                  EducationProgrammeAssessment, Referral, MSCCAttendance)
        for Model in models:
            with self.subTest(model=Model.__name__):
                Model.objects.create(bma_id='unique-id')
                with self.assertRaises(IntegrityError), transaction.atomic():
                    Model.objects.create(bma_id='unique-id')

    def test_database_enforces_teacher_composite_identity_and_required_center(self):
        Teacher.objects.create(bma_id='teacher-7', center=self.center)
        with self.assertRaises(IntegrityError), transaction.atomic():
            Teacher.objects.create(bma_id='teacher-7', center=self.center)
        with self.assertRaises(IntegrityError), transaction.atomic():
            Teacher.objects.create(bma_id='teacher-8', center=None)

    def test_database_enforces_attendance_round_foreign_key(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            MSCCAttendance.objects.create(round_id=999999999)
            connection.check_constraints()
