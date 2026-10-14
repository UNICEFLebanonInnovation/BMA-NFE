"""Regression tests for UNICEF Compiler -> BMA-NFE phase-one replication."""

from django.test import TestCase

from student_registration.child.models import Child
from student_registration.mscc.models import EducationAssessment, Registration
from ..constants import (
    RESOURCE_EDUCATION_ASSESSMENT, RESOURCE_REGISTRATION,
    SOURCE_SYSTEM_COMPILER,
)
from ..services import ingest_events
from .test_ingest import event, registration_payload


class PhaseOneSyncTests(TestCase):
    def push(self, *events):
        return ingest_events(list(events), SOURCE_SYSTEM_COMPILER)

    def test_education_assessment_uses_mapped_registration(self):
        self.assertEqual(
            self.push(event(RESOURCE_REGISTRATION, 10, registration_payload()))['applied'], 1
        )
        result = self.push(event(RESOURCE_EDUCATION_ASSESSMENT, 30, {
            'fields': {'pre_math_grade': 12, 'post_math_grade': 17},
            'registration': {'source_id': 10},
        }))
        self.assertEqual(result['applied'], 1, result['results'])
        row = EducationAssessment.objects.get(bma_id='30')
        self.assertEqual(row.registration_id, Registration.objects.get().pk)
        self.assertEqual(row.post_math_grade, 17)

    def test_outdated_registration_and_delete_cannot_undo_latest(self):
        latest = registration_payload()
        latest['child']['fields']['first_name'] = 'Latest Demo'
        current = event(RESOURCE_REGISTRATION, 10, latest)
        current['source_modified'] = '2026-10-14T15:05:00Z'
        old = event(RESOURCE_REGISTRATION, 10, registration_payload())
        old['source_modified'] = '2026-10-14T15:00:00Z'
        deletion = event(RESOURCE_REGISTRATION, 10, operation='delete')
        deletion['source_modified'] = '2026-10-14T15:01:00Z'
        self.assertEqual(self.push(current)['applied'], 1)
        self.assertEqual(self.push(old, deletion)['skipped'], 2)
        self.assertEqual(Child.objects.get().first_name, 'Latest Demo')
        self.assertEqual(Registration.objects.count(), 1)

    def test_partner_rename_does_not_change_registration_partner_id(self):
        self.push(event(RESOURCE_REGISTRATION, 10, registration_payload()))
        before = Registration.objects.get().partner_id
        newer = registration_payload()
        newer['partner']['name'] = 'Demo New Partner Name'
        self.assertEqual(
            self.push(event(RESOURCE_REGISTRATION, 10, newer))['applied'], 1
        )
        row = Registration.objects.get()
        self.assertEqual(row.partner_id, before)
        self.assertEqual(row.partner.bma_id, '7')

    def test_missing_nationality_is_retryable(self):
        payload = registration_payload()
        payload['child']['nationality'] = {'source_id': 999, 'name': 'Demo Unknown'}
        result = self.push(event(RESOURCE_REGISTRATION, 10, payload))
        self.assertEqual(result['failed'], 1)
        self.assertTrue(result['results'][0]['retryable'])
        self.assertEqual(Child.objects.count(), 0)
