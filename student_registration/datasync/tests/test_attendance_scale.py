"""Large complete attendance days stay atomic without per-child SQL loops."""
from copy import deepcopy

from django.db import connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext

from student_registration.attendances.models import MSCCAttendance, MSCCAttendanceChild
from student_registration.child.models import Child
from student_registration.locations.models import Center
from student_registration.mscc.models import Registration, Round
from student_registration.schools.models import PartnerOrganization
from ..services import ingest_events
from .test_ingest import event


class AttendanceScaleTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        partner = PartnerOrganization.objects.create(name='Scale', bma_id='scale-partner')
        center = Center.objects.create(name='Scale', bma_id='scale-center', partner=partner)
        round_row = Round.objects.create(name='Scale', bma_id='scale-round')
        children = Child.objects.bulk_create([
            Child(first_name='Child ' + str(i), bma_id='scale-child-' + str(i)) for i in range(2000)])
        Registration.objects.bulk_create([
            Registration(bma_id='scale-reg-' + str(i), child=child, center=center,
                         partner=partner, round=round_row, type='Core-Package')
            for i, child in enumerate(children)])
        cls.payload = dict(center={'source_id': 'scale-center'}, round={'source_id': 'scale-round'},
            fields={'class_section': 'A'}, children=[dict(registration={'source_id': 'scale-reg-' + str(i)},
                child={'source_id': 'scale-child-' + str(i)}, fields={'attended': 'Yes'}) for i in range(2000)])

    def push(self, payload):
        return ingest_events([event('attendances.mscc_attendance', 'scale-day', payload)], 'compiler')

    def test_two_thousand_rows_create_update_remove_and_keep_primary_keys(self):
        with CaptureQueriesContext(connection) as queries:
            self.assertEqual(self.push(self.payload)['applied'], 1)
        self.assertLess(len(queries), 80)
        original = dict(MSCCAttendanceChild.objects.values_list('registration_id', 'pk'))
        self.assertEqual(len(original), 2000)
        payload = deepcopy(self.payload)
        for row in payload['children']:
            row['fields'] = {'attended': 'No', 'absence_reason': 'Sick'}
        with CaptureQueriesContext(connection) as queries:
            self.assertEqual(self.push(payload)['applied'], 1)
        self.assertLess(len(queries), 80)
        self.assertEqual(dict(MSCCAttendanceChild.objects.values_list('registration_id', 'pk')), original)
        self.assertEqual(MSCCAttendanceChild.objects.filter(attended='No', absence_reason='Sick').count(), 2000)
        payload['children'] = payload['children'][:1000]
        self.assertEqual(self.push(payload)['applied'], 1)
        self.assertEqual(MSCCAttendanceChild.objects.count(), 1000)
        payload['children'] = []
        self.assertEqual(self.push(payload)['applied'], 1)
        self.assertFalse(MSCCAttendanceChild.objects.exists())

    def test_invalid_last_row_rolls_back_complete_existing_day(self):
        self.assertEqual(self.push(self.payload)['applied'], 1)
        original = list(MSCCAttendanceChild.objects.values_list('pk', 'attended'))
        for failure in ('missing', 'wrong-child', 'duplicate', 'non-makani'):
            with self.subTest(failure=failure):
                payload = deepcopy(self.payload)
                payload['fields']['class_section'] = 'Invalid update'
                payload['children'][0]['fields']['attended'] = 'No'
                if failure == 'missing':
                    payload['children'][-1]['registration'] = {'source_id': 'absent'}
                elif failure == 'wrong-child':
                    payload['children'][-1]['child'] = {'source_id': 'scale-child-0'}
                elif failure == 'duplicate':
                    payload['children'].append(payload['children'][0])
                else:
                    Registration.objects.filter(bma_id='scale-reg-1999').update(type='TLS')
                self.assertEqual(self.push(payload)['failed'], 1)
                self.assertEqual(list(MSCCAttendanceChild.objects.values_list('pk', 'attended')), original)
                self.assertEqual(MSCCAttendance.objects.get().class_section, 'A')
                Registration.objects.filter(bma_id='scale-reg-1999').update(type='Core-Package')
