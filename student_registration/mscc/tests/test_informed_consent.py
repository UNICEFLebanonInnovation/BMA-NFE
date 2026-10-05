from io import BytesIO
from types import SimpleNamespace
from unittest.mock import patch

from django.http import Http404
from django.test import RequestFactory, SimpleTestCase
from django.urls import resolve, reverse

from student_registration.mscc import views


class InformedConsentFileTests(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = SimpleNamespace(is_authenticated=True)

    def test_url_resolves_to_download_view(self):
        url = reverse('mscc:informed_consent_file', args=[42])

        self.assertEqual(url, '/mscc/informed-consent/42/')
        self.assertIs(resolve(url).func, views.informed_consent_file)

    @patch('student_registration.mscc.views.get_object_or_404')
    def test_serves_file_inline_from_field_storage(self, get_object_or_404):
        consent = SimpleNamespace(
            name='uploads/mscc_registration/informed_consent/Informed_Consent_Form.docx',
            open=lambda mode: BytesIO(b'consent contents'),
        )
        get_object_or_404.return_value = SimpleNamespace(informed_consent=consent)
        request = self.factory.get('/mscc/informed-consent/42/')
        request.user = self.user

        response = views.informed_consent_file(request, pk=42)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response['Content-Type'],
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        )
        self.assertIn('inline;', response['Content-Disposition'])
        self.assertIn('Informed_Consent_Form.docx', response['Content-Disposition'])
        self.assertEqual(b''.join(response.streaming_content), b'consent contents')

    @patch('student_registration.mscc.views.get_object_or_404')
    def test_returns_not_found_when_registration_has_no_file(self, get_object_or_404):
        get_object_or_404.return_value = SimpleNamespace(informed_consent=None)
        request = self.factory.get('/mscc/informed-consent/42/')
        request.user = self.user

        with self.assertRaises(Http404):
            views.informed_consent_file(request, pk=42)

    def test_requires_authentication(self):
        request = self.factory.get('/mscc/informed-consent/42/')
        request.user = SimpleNamespace(is_authenticated=False)

        response = views.informed_consent_file(request, pk=42)

        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)
