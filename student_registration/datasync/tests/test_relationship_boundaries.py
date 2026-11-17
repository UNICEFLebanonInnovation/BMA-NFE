"""Reject invalid relationships even when a publisher bypasses its guards."""
from django.test import TestCase

from student_registration.attendances.models import MSCCAttendance, MSCCAttendanceChild
from student_registration.child.models import Child
from student_registration.locations.models import Center
from student_registration.mscc.models import Registration, Round
from student_registration.schools.models import PartnerOrganization
from ..services import ingest_events
from .test_ingest import event


class RelationshipBoundaryTests(TestCase):
    def setUp(self):
        self.partner = PartnerOrganization.objects.create(name='A', bma_id='partner-a')
        self.other_partner = PartnerOrganization.objects.create(name='B', bma_id='partner-b')
        self.center = Center.objects.create(name='A', bma_id='center-a', partner=self.partner)
        self.other_center = Center.objects.create(name='B', bma_id='center-b', partner=self.other_partner)
        self.round = Round.objects.create(name='A', bma_id='round-a')
        self.other_round = Round.objects.create(name='B', bma_id='round-b')
        self.child = Child.objects.create(first_name='A', bma_id='child-a')
        self.registration = Registration.objects.create(bma_id='reg-a', partner=self.partner,
            center=self.center, round=self.round, child=self.child, type='Core-Package')

    def push(self, resource, payload):
        return ingest_events([event(resource, 'guard-test', payload)], 'compiler')

    def attendance(self, **changes):
        payload = dict(center={'source_id': 'center-a'}, round={'source_id': 'round-a'},
            fields={'class_section': 'A'}, children=[{'registration': {'source_id': 'reg-a'},
                'child': {'source_id': 'child-a'}, 'fields': {'attended': 'Yes'}}])
        payload.update(changes)
        return payload

    def test_registration_cannot_use_another_partners_center(self):
        result = self.push('mscc.registration', dict(center={'source_id': 'center-a'},
            partner={'source_id': 'partner-b'}, round={'source_id': 'round-a'},
            child={'source_id': 'new-child', 'fields': {'first_name': 'Rolled back'}}))
        self.assertEqual(result['failed'], 1)
        self.assertFalse(Registration.objects.filter(bma_id='guard-test').exists())
        self.assertFalse(Child.objects.filter(bma_id='new-child').exists())

    def test_attendance_wrong_center_or_round_rolls_back_whole_day(self):
        for changes in (dict(center={'source_id': 'center-b'}), dict(round={'source_id': 'round-b'})):
            with self.subTest(changes=changes):
                self.assertEqual(self.push('attendances.mscc_attendance', self.attendance(**changes))['failed'], 1)
                self.assertFalse(MSCCAttendance.objects.exists())

    def test_mismatched_attendance_child_is_rejected(self):
        payload = self.attendance()
        payload['children'][0]['child'] = {'source_id': 'different-child'}
        self.assertEqual(self.push('attendances.mscc_attendance', payload)['failed'], 1)
        self.assertFalse(MSCCAttendanceChild.objects.exists())

    def test_valid_attendance_and_no_changes_after_invalid_update(self):
        self.assertEqual(self.push('attendances.mscc_attendance', self.attendance())['applied'], 1)
        payload = self.attendance(center={'source_id': 'center-b'}, fields={'class_section': 'B'})
        self.assertEqual(self.push('attendances.mscc_attendance', payload)['failed'], 1)
        day = MSCCAttendance.objects.get()
        self.assertEqual(day.center, self.center)
        self.assertEqual(day.class_section, 'A')
        self.assertEqual(MSCCAttendanceChild.objects.count(), 1)

    def test_service_round_must_match_registration(self):
        self.assertEqual(self.push('mscc.education_service', dict(registration={'source_id': 'reg-a'},
            round={'source_id': 'round-b'}))['failed'], 1)
