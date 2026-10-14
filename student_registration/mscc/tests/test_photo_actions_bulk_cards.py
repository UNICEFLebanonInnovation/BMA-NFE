"""Verify child-photo editing and scoped, programme-aware Word card downloads."""

import io
import tempfile
import zipfile
from html.parser import HTMLParser
from unittest.mock import patch
from urllib.parse import urlparse

from PIL import Image

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from student_registration.backends.models import ExportHistory
from student_registration.child.models import Child
from student_registration.locations.models import Center
from student_registration.mscc.document_exports import build_examination_card
from student_registration.mscc.examination_card_access import (
    RS_PROGRAMMES,
    filter_examination_card_registrations,
    registration_can_have_examination_card,
)
from student_registration.mscc.models import (
    EducationRSService, EducationService, Registration, Round,
)
from student_registration.mscc.tasks import generate_examination_cards_export
from student_registration.schools.models import PartnerOrganization

from .test_document_exports import portrait_bytes, word_text_and_photos


class LinkedProfilePhoto(HTMLParser):
    """Locate the actual image/fallback inside a profile's upload link."""

    def __init__(self, html, upload_url):
        super().__init__()
        self.upload_url = upload_url
        self.in_upload_link = False
        self.has_image = False
        self.has_fallback = False
        self.feed(html)

    def handle_starttag(self, tag, attributes):
        attributes = dict(attributes)
        if tag == 'a':
            self.in_upload_link = attributes.get('href', '').startswith(self.upload_url)
        if self.in_upload_link and 'data-profile-photo' in attributes:
            self.has_image = True
        if self.in_upload_link and 'data-profile-photo-fallback' in attributes:
            self.has_fallback = True

    def handle_endtag(self, tag):
        if tag == 'a':
            self.in_upload_link = False


@override_settings(
    LANGUAGE_CODE='en',
    DEFAULT_FILE_STORAGE='django.core.files.storage.FileSystemStorage',
)
class PhotoActionsAndBulkCardsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.partner = PartnerOrganization.objects.create(name='Photo-action partner')
        cls.outside_partner = PartnerOrganization.objects.create(name='Other photo-action partner')
        cls.center = Center.objects.create(name='Photo-action centre', partner=cls.partner)
        cls.other_center = Center.objects.create(name='Second photo-action centre', partner=cls.partner)
        cls.outside_center = Center.objects.create(name='Outside centre', partner=cls.outside_partner)
        cls.child = Child.objects.create(first_name='Current', father_name='Photo', last_name='Child')
        cls.other_child = Child.objects.create(first_name='Other', last_name='Child')
        cls.outside_child = Child.objects.create(first_name='Outside', last_name='Child')
        cls.historical_round = Round.objects.create(name='Historic round', year=2020, current_year=False)
        cls.registration = Registration.objects.create(
            child=cls.child, partner=cls.partner, center=cls.center, nfe_programme='BLN',
        )
        cls.historical_registration = Registration.objects.create(
            child=cls.child, partner=cls.partner, center=cls.center, round=cls.historical_round,
            nfe_programme='DIRASA',
        )
        cls.other_registration = Registration.objects.create(
            child=cls.other_child, partner=cls.partner, center=cls.other_center,
        )
        cls.outside_registration = Registration.objects.create(
            child=cls.outside_child, partner=cls.outside_partner, center=cls.outside_center,
        )
        cls.deleted_registration = Registration.objects.create(
            child=cls.child, partner=cls.partner, center=cls.center, deleted=True,
        )
        cls.childless_registration = Registration.objects.create(partner=cls.partner, center=cls.center)
        cls.editor = cls.make_user('actions-editor', ['MSCC', 'MSCC_CENTER'], center=cls.center)
        cls.base_editor = cls.make_user('actions-base-editor', ['MSCC'], center=cls.center)
        cls.partner_viewer = cls.make_user(
            'actions-partner-viewer', ['MSCC', 'MSCC_PARTNER'], partner=cls.partner, center=cls.center,
        )
        cls.unicef_viewer = cls.make_user('actions-unicef-viewer', ['MSCC', 'MSCC_UNICEF'], center=cls.center)
        cls.unassigned = cls.make_user('actions-unassigned', ['MSCC', 'MSCC_CENTER'])
        cls.admin = cls.make_user('actions-admin', [], is_staff=True)

    @staticmethod
    def make_user(username, groups, **fields):
        user = get_user_model().objects.create_user(username=username, **fields)
        user.groups.add(*(Group.objects.get_or_create(name=name)[0] for name in groups))
        return user

    def setUp(self):
        media = tempfile.TemporaryDirectory()
        self.addCleanup(media.cleanup)
        settings = override_settings(MEDIA_ROOT=media.name)
        settings.enable()
        self.addCleanup(settings.disable)
        self.child.photo.save('original.png', ContentFile(portrait_bytes('red')))
        self.other_child.photo.save('other.png', ContentFile(portrait_bytes('blue')))
        self.client.force_login(self.editor)

    @staticmethod
    def image_upload(colour='green'):
        return SimpleUploadedFile('replacement.png', portrait_bytes(colour), content_type='image/png')

    def upload_url(self, registration=None):
        return reverse('mscc:photo_upload', args=[(registration or self.registration).pk])

    def profile_url(self, registration=None):
        return reverse('mscc:child_profile', args=[(registration or self.registration).pk])

    def assert_photo_colour(self, content, colour):
        with Image.open(io.BytesIO(content)) as photo:
            pixel = photo.convert('RGB').getpixel((photo.width // 2, photo.height // 2))
        self.assertEqual(pixel, colour)

    @staticmethod
    def response_content(response):
        return b''.join(response.streaming_content) if response.streaming else response.content

    def generate_bulk(self, user=None, filters=None, notification_error=False, fake_cards=False):
        export = ExportHistory.objects.create(
            created_by=user or self.editor, export_type='NFR Sector List', file_format='zip',
        )
        files = {}

        def save_file(name, content):
            files[name] = content.read()
            return name

        with patch('student_registration.mscc.tasks.ExportStorage') as storage:
            storage.return_value.save.side_effect = save_file
            with patch('student_registration.mscc.tasks.send_push_to_web') as notification:
                if notification_error:
                    notification.side_effect = RuntimeError('Notification unavailable')
                if fake_cards:
                    with patch('student_registration.mscc.tasks.build_examination_card', return_value=b'card'):
                        generate_examination_cards_export(export.pk, filters=filters)
                else:
                    generate_examination_cards_export(export.pk, filters=filters)
        export.refresh_from_db()
        return export, files

    def test_photo_replacement_updates_shared_child_profile_and_each_round_card(self):
        response = self.client.post(self.upload_url(), {'photo': self.image_upload(), 'return_to': 'profile'})
        self.assertRedirects(response, self.profile_url(), fetch_redirect_response=False)
        self.registration.refresh_from_db()
        self.assertEqual(self.registration.modified_by_id, self.editor.pk)
        self.child.refresh_from_db()
        self.assertTrue(self.child.photo.name.startswith('child_photos/'))
        for registration in (self.registration, self.historical_registration):
            with self.subTest(registration=registration.pk):
                registration.refresh_from_db()
                response = self.client.get(reverse('mscc:profile_photo', args=[registration.pk]))
                self.assertEqual(response.status_code, 200)
                self.assert_photo_colour(self.response_content(response), (0, 128, 0))
                text, photos = word_text_and_photos(build_examination_card(registration))
                self.assertIn('Current Photo Child', text)
                self.assertEqual(len(photos), 1)
                self.assert_photo_colour(photos[0], (0, 128, 0))
        self.other_child.refresh_from_db()
        with self.other_child.photo.open('rb') as original:
            self.assert_photo_colour(original.read(), (0, 0, 255))

    def test_upload_return_destination_is_internal_and_preserves_list_entry_point(self):
        for destination, expected in (
            ('list', reverse('mscc:list')),
            ('profile', self.profile_url()),
            ('https://outside.example/redirect', self.profile_url()),
        ):
            with self.subTest(destination=destination):
                response = self.client.post(self.upload_url(), {
                    'photo': self.image_upload(), 'return_to': destination,
                })
                self.assertEqual(response.status_code, 302)
                self.assertEqual(response.url, expected)

    def test_missing_or_invalid_upload_keeps_existing_photo(self):
        original_name = self.child.photo.name
        jpeg = io.BytesIO()
        Image.new('RGB', (48, 64), 'green').save(jpeg, format='JPEG')
        for payload in (
            {},
            {'photo': SimpleUploadedFile('bad.png', b'not an image', content_type='image/png')},
            # JPEG headers can pass image verification even when decoding the
            # complete photograph would fail; reject it before replacing one.
            {'photo': SimpleUploadedFile('truncated.jpg', jpeg.getvalue()[:-2], content_type='image/jpeg')},
        ):
            with self.subTest(payload=bool(payload)):
                response = self.client.post(self.upload_url(), payload)
                self.assertEqual(response.status_code, 200)
                self.assertTrue(response.context['form'].errors)
                self.child.refresh_from_db()
                self.assertEqual(self.child.photo.name, original_name)
                with self.child.photo.open('rb') as original:
                    self.assert_photo_colour(original.read(), (255, 0, 0))
        self.registration.refresh_from_db()
        self.assertIsNone(self.registration.modified_by_id)

    def test_upload_permissions_allow_assigned_service_editor_and_administrator(self):
        for user, registration in (
            (self.base_editor, self.registration),
            (self.admin, self.outside_registration),
        ):
            with self.subTest(user=user.username):
                self.client.force_login(user)
                response = self.client.post(self.upload_url(registration), {'photo': self.image_upload()})
                self.assertEqual(response.status_code, 302)

    def test_read_only_roles_cannot_upload_even_when_assigned_a_centre(self):
        for user in (self.partner_viewer, self.unicef_viewer):
            self.client.force_login(user)
            for method in (self.client.get, self.client.post):
                with self.subTest(user=user.username, method=method.__name__):
                    response = method(self.upload_url(), {'photo': self.image_upload()})
                    self.assertEqual(response.status_code, 403)
            response = self.client.get(self.profile_url())
            self.assertFalse(response.context['can_upload_photo'])
            self.assertNotContains(response, self.upload_url())
        self.child.refresh_from_db()
        with self.child.photo.open('rb') as original:
            self.assert_photo_colour(original.read(), (255, 0, 0))

    def test_upload_rejects_foreign_deleted_childless_and_unassigned_requests(self):
        for registration in (
            self.other_registration, self.outside_registration,
            self.deleted_registration, self.childless_registration,
        ):
            for method in (self.client.get, self.client.post):
                with self.subTest(registration=registration.pk, method=method.__name__):
                    response = method(self.upload_url(registration), {'photo': self.image_upload()})
                    self.assertEqual(response.status_code, 404)
        self.client.force_login(self.unassigned)
        response = self.client.post(self.upload_url(), {'photo': self.image_upload()})
        self.assertIn(response.status_code, (403, 404))
        self.client.logout()
        for method in (self.client.get, self.client.post):
            self.assertEqual(method(self.upload_url(), {'photo': self.image_upload()}).status_code, 302)

    def test_photo_upload_keeps_csrf_protection(self):
        csrf_client = Client(enforce_csrf_checks=True)
        csrf_client.force_login(self.editor)
        response = csrf_client.post(self.upload_url(), {'photo': self.image_upload()})
        self.assertEqual(response.status_code, 403)
        response = csrf_client.get(self.upload_url())
        self.assertEqual(response.status_code, 200)
        token = csrf_client.cookies['csrftoken'].value
        response = csrf_client.post(self.upload_url(), {
            'photo': self.image_upload(), 'csrfmiddlewaretoken': token,
        })
        self.assertEqual(response.status_code, 302)

    def test_profile_image_and_empty_photo_placeholder_link_to_upload_for_editors(self):
        for has_photo in (True, False):
            if not has_photo:
                self.child.photo = ''
                self.child.save(update_fields=['photo'])
            with self.subTest(has_photo=has_photo):
                response = self.client.get(self.profile_url())
                self.assertTrue(response.context['can_upload_photo'])
                markup = LinkedProfilePhoto(response.content.decode(), self.upload_url())
                self.assertEqual(markup.has_image, has_photo)
                self.assertTrue(markup.has_fallback)

    def test_registration_dropdown_exposes_upload_only_for_editable_records(self):
        response = self.client.get(reverse('mscc:list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.upload_url() + '?return_to=list')
        self.assertNotContains(response, self.upload_url(self.other_registration))
        self.assertContains(response, 'Word examination cards (ZIP)')
        self.client.force_login(self.partner_viewer)
        response = self.client.get(reverse('mscc:list'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, self.upload_url())
        self.assertNotContains(response, self.upload_url(self.other_registration))

    def test_rs_grades_and_mixed_rs_programmes_hide_and_reject_individual_cards(self):
        for programme in sorted(RS_PROGRAMMES):
            EducationService.objects.create(registration=self.registration, education_program=programme)
            with self.subTest(programme=programme):
                self.registration.refresh_from_db()
                self.assertFalse(registration_can_have_examination_card(self.registration))
                response = self.client.get(self.profile_url())
                self.assertFalse(response.context['can_export_examination_card'])
                self.assertNotContains(response, reverse('mscc:examination_card', args=[self.registration.pk]))
                response = self.client.get(reverse('mscc:examination_card', args=[self.registration.pk]))
                self.assertEqual(response.status_code, 404)

    def test_only_latest_education_programme_controls_card_eligibility(self):
        EducationService.objects.create(registration=self.registration, education_program='RS Grade 6')
        EducationRSService.objects.create(registration=self.registration, grade_level='Level six')
        EducationService.objects.create(registration=self.registration, education_program='BLN Level 2')
        self.registration.refresh_from_db()
        self.assertTrue(registration_can_have_examination_card(self.registration))
        response = self.client.get(self.profile_url())
        self.assertTrue(response.context['can_export_examination_card'])
        self.assertEqual(
            self.client.get(reverse('mscc:examination_card', args=[self.registration.pk])).status_code, 200,
        )
        queryset = Registration.objects.filter(pk=self.registration.pk).prefetch_related('education_service')
        self.assertTrue(registration_can_have_examination_card(queryset.get()))
        self.assertEqual(list(filter_examination_card_registrations(queryset)), [self.registration])

    def test_bulk_zip_contains_real_cards_and_photos_only_for_eligible_authorised_records(self):
        EducationService.objects.create(registration=self.other_registration, education_program='RS Grade 3')
        export, files = self.generate_bulk(self.partner_viewer, filters={'export_scope': 'all'})
        self.assertEqual(export.status, 'done')
        self.assertEqual(len(files), 1)
        filename, content = next(iter(files.items()))
        self.assertTrue(filename.endswith('.zip'))
        self.assertEqual(export.file_url, reverse('mscc:export_download', args=[filename]))
        with zipfile.ZipFile(io.BytesIO(content)) as archive:
            expected = {
                'examination_card_child_{}_registration_{}.docx'.format(self.child.pk, registration.pk)
                for registration in (self.registration, self.historical_registration)
            }
            self.assertEqual(set(archive.namelist()), expected)
            for registration in (self.registration, self.historical_registration):
                card_name = 'examination_card_child_{}_registration_{}.docx'.format(self.child.pk, registration.pk)
                text, photos = word_text_and_photos(archive.read(card_name))
                self.assertIn('Current Photo Child', text)
                self.assertIn('ID: {}'.format(registration.pk), text)
                self.assertEqual(len(photos), 1)
                self.assert_photo_colour(photos[0], (255, 0, 0))

    def test_bulk_download_includes_more_than_a_page_and_every_authorised_round(self):
        added = Registration.objects.bulk_create([
            Registration(child=self.child, partner=self.partner, center=self.center, round=self.historical_round)
            for _ in range(101)
        ])
        export, files = self.generate_bulk(
            filters={'export_scope': 'all', 'child__first_name': 'Does not match'}, fake_cards=True,
        )
        self.assertEqual(export.status, 'done')
        with zipfile.ZipFile(io.BytesIO(next(iter(files.values())))) as archive:
            expected_ids = {self.registration.pk, self.historical_registration.pk} | {item.pk for item in added}
            self.assertEqual(
                set(archive.namelist()),
                {'examination_card_child_{}_registration_{}.docx'.format(self.child.pk, pk) for pk in expected_ids},
            )

    def test_filtered_bulk_download_respects_list_round_filters_and_cannot_widen_scope(self):
        export, files = self.generate_bulk(filters={'export_scope': 'filtered'}, fake_cards=True)
        self.assertEqual(export.status, 'done')
        with zipfile.ZipFile(io.BytesIO(next(iter(files.values())))) as archive:
            self.assertEqual(archive.namelist(), [
                'examination_card_child_{}_registration_{}.docx'.format(self.child.pk, self.registration.pk),
            ])
        export, files = self.generate_bulk(
            filters={'export_scope': 'filtered', 'center': str(self.outside_center.pk)}, fake_cards=True,
        )
        self.assertEqual(export.status, 'failed')
        self.assertEqual(export.file_url, '')
        self.assertEqual(files, {})

    def test_worker_rechecks_role_before_generating_private_archive(self):
        export, files = self.generate_bulk(self.unassigned, fake_cards=True)
        self.assertEqual(export.status, 'failed')
        self.assertEqual(export.file_url, '')
        self.assertEqual(files, {})

    def test_bulk_export_survives_notification_failure_without_losing_download(self):
        export, files = self.generate_bulk(notification_error=True, fake_cards=True)
        self.assertEqual(export.status, 'done')
        self.assertEqual(len(files), 1)
        self.assertTrue(urlparse(export.file_url).path.rstrip('/').endswith('.zip'))
        filename, content = next(iter(files.items()))
        self.assertTrue(filename.endswith('.zip'))
        with zipfile.ZipFile(io.BytesIO(content)) as archive:
            self.assertEqual(set(archive.namelist()), {
                'examination_card_child_{}_registration_{}.docx'.format(self.child.pk, registration.pk)
                for registration in (self.registration, self.historical_registration)
            })

    def test_cards_request_queues_zip_job_with_current_filters(self):
        filters = {'format': 'cards', 'export_scope': 'filtered', 'child__first_name': 'Current'}
        with patch('student_registration.mscc.tasks.queue_examination_cards_export') as queue:
            response = self.client.get(reverse('mscc:export_list_background'), filters)
        self.assertEqual(response.status_code, 200)
        export = ExportHistory.objects.get(pk=response.json()['export_id'])
        self.assertEqual(export.created_by_id, self.editor.pk)
        self.assertEqual(export.file_format, 'zip')
        queue.assert_called_once_with(export.pk, filters=filters)

    def test_legacy_async_endpoint_also_queues_word_cards(self):
        for method in ('get', 'post'):
            with self.subTest(method=method):
                with patch('student_registration.mscc.tasks.queue_examination_cards_export') as queue:
                    if method == 'post':
                        response = self.client.post(
                            reverse('mscc:export_list_async'),
                            data='{"format": "cards"}', content_type='application/json',
                        )
                    else:
                        response = self.client.get(reverse('mscc:export_list_async'), {'format': 'cards'})
                self.assertEqual(response.status_code, 200)
                export = ExportHistory.objects.get(pk=response.json()['export_id'])
                self.assertEqual(export.file_format, 'zip')
                queue.assert_called_once_with(export.pk)

    def test_all_rs_or_unassigned_scope_cannot_start_a_bulk_card_job(self):
        for registration in (self.registration, self.historical_registration):
            EducationService.objects.create(registration=registration, education_program='RS Grade 5')
        for url_name in ('mscc:export_list_background', 'mscc:export_list_async'):
            with self.subTest(url_name=url_name):
                with patch('student_registration.mscc.tasks.queue_examination_cards_export') as queue:
                    response = self.client.get(reverse(url_name), {'format': 'cards', 'export_scope': 'all'})
                self.assertEqual(response.status_code, 400)
                queue.assert_not_called()
        self.client.force_login(self.unassigned)
        with patch('student_registration.mscc.tasks.queue_examination_cards_export') as queue:
            response = self.client.get(reverse('mscc:export_list_background'), {'format': 'cards'})
        self.assertEqual(response.status_code, 403)
        queue.assert_not_called()
        self.assertFalse(ExportHistory.objects.exists())

    def test_bulk_zip_download_is_private_to_completed_export_creator(self):
        filename = 'examination_cards_private.zip'
        url = reverse('mscc:export_download', args=[filename])
        export = ExportHistory.objects.create(
            created_by=self.editor, export_type='NFR Sector List', file_format='zip',
            status='done', file_url=url,
        )
        self.client.force_login(self.partner_viewer)
        with patch('student_registration.mscc.views.ExportStorage') as storage:
            self.assertEqual(self.client.get(url).status_code, 404)
            storage.assert_not_called()
        self.client.force_login(self.editor)
        with patch('student_registration.mscc.views.ExportStorage') as storage:
            storage.return_value.open.return_value = io.BytesIO(b'private-zip')
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(self.response_content(response), b'private-zip')
        export.status = 'pending'
        export.save(update_fields=['status'])
        self.assertEqual(self.client.get(url).status_code, 404)
