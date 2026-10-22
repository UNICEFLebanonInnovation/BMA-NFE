"""Keep the profile photograph linked to the child's saved registration image."""

import io
import tempfile
from html.parser import HTMLParser
from unittest.mock import patch

from PIL import Image

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.files.base import ContentFile
from django.core.files.storage import Storage
from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import HttpResponse
from django.test import RequestFactory, SimpleTestCase, TestCase, override_settings
from django.urls import reverse

from student_registration.cache_control_middleware import CacheControlMiddleware
from student_registration.child.models import Child
from student_registration.clm.models import Disability
from student_registration.locations.models import Center, Location, LocationType
from student_registration.mscc.document_exports import build_examination_card
from student_registration.mscc.models import Registration
from student_registration.schools.models import PartnerOrganization
from student_registration.students.models import Nationality

from .test_document_exports import portrait_bytes, word_text_and_photos


class ProfilePhotoMarkup(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.photo = None
        self.fallback = None
        self.feed(html)

    def handle_starttag(self, tag, attributes):
        attributes = dict(attributes)
        if tag == 'img' and 'data-profile-photo' in attributes:
            self.photo = attributes
        if 'data-profile-photo-fallback' in attributes:
            self.fallback = attributes


class PrivatePhotoStorage(Storage):
    """A private object store that only supports reading the registered file."""

    def __init__(self, name, content=None, error=None):
        self.name = name
        self.content = content
        self.error = error
        self.opened = []

    def _open(self, name, mode='rb'):
        self.opened.append(name)
        if self.error:
            raise self.error
        if name != self.name:
            raise FileNotFoundError(name)
        return ContentFile(self.content, name=name)

    def url(self, name):
        raise AssertionError('Private child photographs have no public URL.')

    def path(self, name):
        raise AssertionError('Private child photographs have no local path.')


@override_settings(
    LANGUAGE_CODE='en',
    DEFAULT_FILE_STORAGE='django.core.files.storage.FileSystemStorage',
)
class MSCCProfilePhotoTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.partner = PartnerOrganization.objects.create(name='Photo partner')
        cls.outside_partner = PartnerOrganization.objects.create(name='Outside partner')
        cls.center = Center.objects.create(name='Photo centre', partner=cls.partner)
        cls.second_center = Center.objects.create(name='Second centre', partner=cls.partner)
        cls.outside_center = Center.objects.create(name='Outside centre', partner=cls.outside_partner)
        cls.first_child = Child.objects.create(
            first_name='First', father_name='Photo', last_name='Child', gender='Female',
            birthday_year='2015', birthday_month='3', birthday_day='12',
        )
        cls.second_child = Child.objects.create(first_name='Second', last_name='Photo child')
        cls.outside_child = Child.objects.create(first_name='Outside', last_name='Photo child')
        cls.first_registration = Registration.objects.create(
            child=cls.first_child, partner=cls.partner, center=cls.center,
        )
        cls.second_registration = Registration.objects.create(
            child=cls.second_child, partner=cls.partner, center=cls.second_center,
        )
        cls.outside_registration = Registration.objects.create(
            child=cls.outside_child, partner=cls.outside_partner, center=cls.outside_center,
        )
        cls.deleted_registration = Registration.objects.create(
            child=cls.first_child, partner=cls.partner, center=cls.center, deleted=True,
        )
        cls.childless_registration = Registration.objects.create(
            child=None, partner=cls.partner, center=cls.center,
        )
        cls.unicef_user = cls.make_user('profile-photo-unicef', ['MSCC', 'MSCC_UNICEF'])
        cls.partner_user = cls.make_user('profile-photo-partner', ['MSCC', 'MSCC_PARTNER'], partner=cls.partner)
        cls.center_user = cls.make_user('profile-photo-centre', ['MSCC', 'MSCC_CENTER'], center=cls.center)
        cls.assigned_user = cls.make_user('profile-photo-assigned', ['MSCC'], center=cls.center, partner=cls.partner)
        cls.unassigned_user = cls.make_user('profile-photo-unassigned', ['MSCC'])
        cls.unassigned_center_user = cls.make_user('profile-photo-unassigned-centre', ['MSCC', 'MSCC_CENTER'])
        cls.unassigned_partner_user = cls.make_user('profile-photo-unassigned-partner', ['MSCC', 'MSCC_PARTNER'])
        cls.unrelated_user = cls.make_user('profile-photo-unrelated', [], center=cls.center)
        cls.staff_user = cls.make_user('profile-photo-staff', [], is_staff=True)
        cls.superuser = cls.make_user('profile-photo-admin', [], is_superuser=True)
        cls.nationality = Nationality.objects.create(pk=1001, name='Test nationality', name_en='Test nationality')
        cls.disability = Disability.objects.create(name='None', name_en='None')
        governorate_type = LocationType.objects.create(pk=1, name='Governorate')
        district_type = LocationType.objects.create(pk=2, name='District')
        cadaster_type = LocationType.objects.create(pk=3, name='Cadaster')
        cls.governorate = Location.objects.create(type=governorate_type, name='Beirut')
        cls.district = Location.objects.create(type=district_type, name='Beirut', parent=cls.governorate)
        cls.cadaster = Location.objects.create(type=cadaster_type, name='Ras Beirut', parent=cls.district)

    @staticmethod
    def make_user(username, groups, **fields):
        user = get_user_model().objects.create_user(username=username, **fields)
        user.groups.add(*(Group.objects.get_or_create(name=name)[0] for name in groups))
        return user

    def setUp(self):
        media = tempfile.TemporaryDirectory()
        self.addCleanup(media.cleanup)
        settings_override = override_settings(MEDIA_ROOT=media.name)
        settings_override.enable()
        self.addCleanup(settings_override.disable)
        self.first_child.photo.save('first.png', ContentFile(portrait_bytes('red')))
        self.second_child.photo.save('second.png', ContentFile(portrait_bytes('blue')))
        self.outside_child.photo.save('outside.png', ContentFile(portrait_bytes('purple')))
        self.client.force_login(self.unicef_user)

    @staticmethod
    def photo_url(registration):
        return reverse('mscc:profile_photo', args=[registration.pk])

    def assert_photo(self, response, colour):
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'image/png')
        content = b''.join(response.streaming_content) if response.streaming else response.content
        with Image.open(io.BytesIO(content)) as image:
            self.assertEqual(image.format, 'PNG')
            self.assertEqual(image.convert('RGB').getpixel((0, 0)), colour)
        return content

    def profile_markup(self, registration):
        response = self.client.get(reverse('mscc:child_profile', args=[registration.pk]))
        self.assertEqual(response.status_code, 200)
        return ProfilePhotoMarkup(response.content.decode())

    def registration_data(self, colour):
        return {
            'child_first_name': 'Ali', 'child_father_name': 'Ahmad',
            'child_last_name': 'Hassan', 'child_mother_fullname': 'Mariam',
            'child_gender': 'Male', 'child_nationality': self.nationality.pk,
            'child_birthday_year': '2015', 'child_birthday_month': '3',
            'child_birthday_day': '12', 'child_disability': self.disability.pk,
            'first_phone_number': '70-123456', 'nfe_programme': 'BLN Level 1',
            'child_country_of_birth': 'LB', 'child_place_of_birth': 'Beirut',
            'child_governorate': self.governorate.pk,
            'child_district': self.district.pk, 'child_cadaster': self.cadaster.pk,
            'child_village': 'ras_beirut',
            'child_photo': SimpleUploadedFile('portrait.png', portrait_bytes(colour), content_type='image/png'),
        }

    def test_registration_and_replacement_upload_appear_in_profile_and_same_word_card(self):
        self.client.force_login(self.assigned_user)
        response = self.client.post(reverse('mscc:child_add'), self.registration_data('red'))
        self.assertEqual(response.status_code, 302)
        registration = Registration.objects.get(pk=self.client.session['instance_id'])
        self.assertEqual(response.url, reverse('mscc:child_profile', args=[registration.pk]))

        for colour, expected in (('red', (255, 0, 0)), ('green', (0, 128, 0))):
            with self.subTest(photo=colour):
                if colour == 'green':
                    response = self.client.post(
                        reverse('mscc:child_edit', args=[registration.pk]), self.registration_data(colour),
                    )
                    self.assertEqual(response.status_code, 302)
                    registration.refresh_from_db()
                markup = self.profile_markup(registration)
                self.assertEqual(markup.photo['src'], self.photo_url(registration))
                self.assertIn('hidden', markup.fallback)
                self.assertTrue(registration.child.photo.name)
                photo = self.assert_photo(self.client.get(self.photo_url(registration)), expected)
                _, word_photos = word_text_and_photos(build_examination_card(registration))
                self.assertEqual(word_photos, [photo])

    def test_profile_and_photo_endpoint_support_private_remote_storage_without_public_url(self):
        storage = PrivatePhotoStorage(self.first_child.photo.name, portrait_bytes('purple'))
        with patch.object(Child._meta.get_field('photo'), 'storage', storage):
            markup = self.profile_markup(self.first_registration)
            self.assertEqual(markup.photo['src'], self.photo_url(self.first_registration))
            self.assertIn('hidden', markup.fallback)
            photo = self.assert_photo(self.client.get(self.photo_url(self.first_registration)), (128, 0, 128))
            registration = Registration.objects.select_related('child').get(pk=self.first_registration.pk)
            _, word_photos = word_text_and_photos(build_examination_card(registration))
            self.assertEqual(word_photos, [photo])
        self.assertEqual(storage.opened, [self.first_child.photo.name, self.first_child.photo.name])

    def test_each_profile_url_returns_its_own_child_photo(self):
        for registration, colour in (
            (self.first_registration, (255, 0, 0)),
            (self.second_registration, (0, 0, 255)),
        ):
            with self.subTest(child=registration.child_id):
                markup = self.profile_markup(registration)
                self.assertEqual(markup.photo['src'], self.photo_url(registration))
                photo = self.assert_photo(self.client.get(markup.photo['src']), colour)
                registration.refresh_from_db()
                _, word_photos = word_text_and_photos(build_examination_card(registration))
                self.assertEqual(word_photos, [photo])

    def test_photo_endpoint_obeys_mscc_role_and_assignment_scope(self):
        all_registrations = {self.first_registration.pk, self.second_registration.pk, self.outside_registration.pk}
        for user, accessible in (
            (self.unicef_user, all_registrations),
            (self.staff_user, all_registrations),
            (self.superuser, all_registrations),
            (self.partner_user, {self.first_registration.pk, self.second_registration.pk}),
            (self.center_user, {self.first_registration.pk}),
            (self.assigned_user, {self.first_registration.pk}),
            (self.unassigned_user, set()),
            (self.unassigned_center_user, set()),
            (self.unassigned_partner_user, set()),
            (self.unrelated_user, set()),
        ):
            self.client.force_login(user)
            for registration in (self.first_registration, self.second_registration, self.outside_registration):
                with self.subTest(user=user.username, registration=registration.pk):
                    self.assertEqual(
                        self.client.get(self.photo_url(registration)).status_code,
                        200 if registration.pk in accessible else 404,
                    )

    def test_photo_endpoint_requires_login_and_get(self):
        self.client.logout()
        response = self.client.get(self.photo_url(self.first_registration))
        self.assertEqual(response.status_code, 302)
        self.assertIn('next=', response.url)
        self.client.force_login(self.unicef_user)
        self.assertEqual(self.client.post(self.photo_url(self.first_registration)).status_code, 405)

    def test_deleted_childless_and_unknown_registrations_do_not_return_photos(self):
        for pk in (self.deleted_registration.pk, self.childless_registration.pk, 999999):
            with self.subTest(registration=pk):
                self.assertEqual(self.client.get(reverse('mscc:profile_photo', args=[pk])).status_code, 404)

    def test_missing_photo_shows_profile_placeholder_and_returns_404(self):
        self.first_child.photo = ''
        self.first_child.save(update_fields=['photo'])
        markup = self.profile_markup(self.first_registration)
        self.assertIsNone(markup.photo)
        self.assertIsNotNone(markup.fallback)
        self.assertNotIn('hidden', markup.fallback)
        self.assertEqual(self.client.get(self.photo_url(self.first_registration)).status_code, 404)

    def test_unreadable_or_invalid_photo_never_returns_storage_errors_as_image(self):
        for storage in (
            PrivatePhotoStorage(self.first_child.photo.name, error=FileNotFoundError('missing object')),
            PrivatePhotoStorage(self.first_child.photo.name, error=OSError('private storage offline')),
            PrivatePhotoStorage(self.first_child.photo.name, b'not an image'),
        ):
            with self.subTest(error=storage.error):
                with patch.object(Child._meta.get_field('photo'), 'storage', storage):
                    markup = self.profile_markup(self.first_registration)
                    self.assertIsNotNone(markup.fallback)
                    response = self.client.get(self.photo_url(self.first_registration))
                self.assertEqual(response.status_code, 404)
                self.assertNotEqual(response['Content-Type'], 'image/png')
                self.assertNotContains(response, 'private storage offline', status_code=404)

    def test_photo_responses_are_private_uncacheable_and_vary_by_session(self):
        response = self.client.get(self.photo_url(self.first_registration))
        self.assert_photo(response, (255, 0, 0))
        directives = {value.strip().lower() for value in response['Cache-Control'].split(',')}
        self.assertTrue({'private', 'no-store', 'no-cache'}.issubset(directives))
        self.assertIn('cookie', response['Vary'].lower())
        self.assertNotIn('ETag', response)
        self.assertNotIn('Last-Modified', response)


class ProfilePhotoCacheMiddlewareTests(SimpleTestCase):
    def test_existing_private_no_store_policy_survives_cache_middleware(self):
        response = HttpResponse(b'photo', content_type='image/png')
        response['Cache-Control'] = 'max-age=0, no-cache, no-store, must-revalidate, private'
        protected_policy = response['Cache-Control']
        middleware = CacheControlMiddleware(lambda request: response)

        result = middleware(RequestFactory().get('/mscc/profile-photo/123/', secure=True))

        self.assertEqual(result['Cache-Control'], protected_policy)
