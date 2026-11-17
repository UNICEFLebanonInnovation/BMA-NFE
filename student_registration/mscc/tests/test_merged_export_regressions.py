"""Regression coverage for dashboard links, scoped governorate exports and filenames."""
import io
import tempfile
from datetime import datetime
from unittest.mock import patch
from zoneinfo import ZoneInfo

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings
from django.urls import reverse

from student_registration.backends.models import ExportHistory
from student_registration.child.models import Child
from student_registration.locations.models import Center, Location, LocationType
from student_registration.mscc.export_access import filter_registrations, scoped_registrations
from student_registration.mscc.models import Registration, Round
from student_registration.mscc.tasks import _generate_filtered_mscc_export
from student_registration.schools.models import PartnerOrganization, School

from .test_document_exports import workbook_rows


@override_settings(LANGUAGE_CODE='en')
class MergedExportRegressionTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        users = get_user_model()
        cls.owner = users.objects.create_user(username='export-owner')
        cls.owner.groups.add(Group.objects.get_or_create(name='MSCC_MEHE')[0])
        cls.other = users.objects.create_user(username='other-requester')
        school = School.objects.create(number='EXPORT-REGRESSION', name='Export school')
        cls.alp_user = users.objects.create_user(username='alp-export-owner', school=school)
        cls.alp_user.groups.add(Group.objects.get_or_create(name='ALP_SCHOOL')[0])
        kind = LocationType.objects.create(pk=1, name='Governorate')
        cls.beirut = Location.objects.create(type=kind, name='Beirut')
        cls.north = Location.objects.create(type=kind, name='North')
        cls.partner = PartnerOrganization.objects.create(name='Assigned partner')
        cls.other_partner = PartnerOrganization.objects.create(name='Other partner')
        cls.partner_user = users.objects.create_user(username='partner-export-owner', partner=cls.partner)
        cls.partner_user.groups.add(Group.objects.get_or_create(name='MSCC_PARTNER')[0])
        center = Center.objects.create(name='Beirut center', partner=cls.partner, governorate=cls.beirut)
        north_center = Center.objects.create(name='North center', partner=cls.partner, governorate=cls.north)
        outside_center = Center.objects.create(name='Other partner center', partner=cls.other_partner,
                                               governorate=cls.beirut)
        current = Round.objects.create(name='Current', current_year=True)
        old = Round.objects.create(name='Previous', current_year=False)
        # The child's home address differs deliberately from the center's governorate.
        child = Child.objects.create(first_name='Local', last_name='Export', governorate=cls.north)
        cls.selected = Registration.objects.create(child=child, center=center, partner=cls.partner, round=current)
        cls.north_registration = Registration.objects.create(child=child, center=north_center,
                                                              partner=cls.partner, round=current)
        cls.historic = Registration.objects.create(child=child, center=center, partner=cls.partner, round=old)
        cls.no_round = Registration.objects.create(child=child, center=center, partner=cls.partner)
        cls.outside = Registration.objects.create(child=child, center=outside_center,
                                                  partner=cls.other_partner, round=current)

    def setUp(self):
        self.client.force_login(self.owner)

    def export_record(self, export_type='NFR Sector List', owner=None, **kwargs):
        defaults = dict(status='done', file_format='xlsx', file_url='/mscc/export-download/example.xlsx/')
        defaults.update(kwargs)
        return ExportHistory.objects.create(export_type=export_type, created_by=owner or self.owner, **defaults)

    def test_governorate_export_filter_uses_the_center_and_current_round_scope(self):
        rows = filter_registrations(scoped_registrations(self.owner), {
            'export_scope': 'filtered', 'governorate': str(self.beirut.pk),
        })
        self.assertSetEqual(set(rows.values_list('pk', flat=True)),
                            {self.selected.pk, self.no_round.pk, self.outside.pk})

    def test_governorate_filter_preserves_partner_scope(self):
        rows = filter_registrations(scoped_registrations(self.partner_user), {
            'export_scope': 'filtered', 'governorate': str(self.beirut.pk),
        })
        self.assertSetEqual(set(rows.values_list('pk', flat=True)), {self.selected.pk, self.no_round.pk})

    def test_invalid_governorate_is_rejected(self):
        for value in ('invalid', '-1', '0'):
            with self.subTest(value=value), self.assertRaises(ValidationError):
                filter_registrations(scoped_registrations(self.owner), {'governorate': value})

    def test_all_export_scope_still_includes_all_authorized_governorates(self):
        rows = filter_registrations(scoped_registrations(self.owner), {
            'export_scope': 'all', 'governorate': str(self.beirut.pk),
        })
        self.assertEqual(rows.count(), 5)

    def test_filtered_governorate_workbook_download_contains_only_matching_rows(self):
        export = self.export_record(owner=self.partner_user, status='pending', file_url='')
        with tempfile.TemporaryDirectory() as directory, override_settings(MEDIA_ROOT=directory), \
             patch.dict('os.environ', {'AZURE_ACCOUNT_KEY': ''}), \
             patch('student_registration.mscc.tasks.send_push_to_web', return_value=False):
            _generate_filtered_mscc_export(export.pk, {
                'export_scope': 'filtered', 'governorate': str(self.beirut.pk),
            }, 'xlsx')
            export.refresh_from_db()
            self.assertEqual(export.status, 'done')
            self.client.force_login(self.partner_user)
            response = self.client.get(export.file_url)
            self.assertEqual(response.status_code, 200)
            rows = workbook_rows(b''.join(response.streaming_content))
            self.assertSetEqual({int(row['Registration ID']) for _, row in rows},
                                {self.selected.pk, self.no_round.pk})

    def test_nfr_dashboard_renders_the_saved_download_link(self):
        export = self.export_record()
        response = self.client.get(reverse('landing_page'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['recent_exports'][0]['file_url'], export.file_url)
        self.assertContains(response, 'href="%s"' % export.file_url)

    def test_nfr_dashboard_only_lists_the_requesters_exports(self):
        mine = self.export_record()
        self.export_record(owner=self.other, export_type='NFR Sector Other Requester')
        response = self.client.get(reverse('landing_page'))
        self.assertEqual([row['export_type'] for row in response.context['recent_exports']], [mine.export_type])

    def test_alp_dashboard_with_export_history_renders_the_saved_link(self):
        export = self.export_record(export_type='ALP List', owner=self.alp_user,
                                    file_url='/alp/example.csv', file_format='csv')
        self.client.force_login(self.alp_user)
        response = self.client.get(reverse('alp:landing_page'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['recent_exports'][0]['file_url'], export.file_url)
        self.assertContains(response, 'href="%s"' % export.file_url)

    def test_alp_dashboard_only_lists_the_requesters_exports(self):
        self.export_record(export_type='ALP Mine', owner=self.alp_user)
        self.export_record(export_type='ALP Other Requester', owner=self.other)
        self.client.force_login(self.alp_user)
        response = self.client.get(reverse('alp:landing_page'))
        self.assertEqual([row['export_type'] for row in response.context['recent_exports']], ['ALP Mine'])

    def test_dashboard_does_not_render_download_buttons_without_a_completed_url(self):
        for route, owner, export_type in (
            ('landing_page', self.owner, 'NFR Sector List'),
            ('alp:landing_page', self.alp_user, 'ALP List'),
        ):
            with self.subTest(route=route):
                self.export_record(export_type=export_type, owner=owner, status='done', file_url='')
                self.export_record(export_type=export_type, owner=owner, status='pending', file_url='/pending.xlsx')
                self.export_record(export_type=export_type, owner=owner, status='failed', file_url='/failed.xlsx')
                self.client.force_login(owner)
                response = self.client.get(reverse(route))
                self.assertEqual(response.status_code, 200)
                self.assertNotContains(response, 'title="Download"')

    def test_downloads_use_the_beirut_date_for_every_supported_format(self):
        for extension, route in (('xlsx', 'mscc:export_download'), ('zip', 'mscc:export_download'),
                                 ('csv', 'mscc:export_download'), ('csv', 'mscc:export_download_csv')):
            with self.subTest(extension=extension, route=route), \
                 patch('student_registration.mscc.views.datetime') as clock, \
                 patch('student_registration.mscc.views.ExportStorage') as storage:
                clock.now.return_value = datetime(2026, 11, 16, 0, 30, tzinfo=ZoneInfo('Asia/Beirut'))
                filename = 'dated-export.' + extension
                url = reverse('mscc:export_download', args=[filename])
                ExportHistory.objects.get_or_create(created_by=self.owner, status='done', file_url=url)
                storage.return_value.open.return_value = io.BytesIO(b'export contents')
                response = self.client.get(reverse(route, args=[filename]))
                self.assertEqual(response.status_code, 200)
                contents = b''.join(response.streaming_content)
                self.assertIn('nfr_export_2026-11-16.' + extension,
                              response['Content-Disposition'])
                self.assertEqual(contents, b'export contents')
