from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse


class OCRProcessViewTests(TestCase):
    def test_missing_document_returns_bad_request(self):
        response = self.client.post(reverse('mscc:ocr_process'))

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], 'No document provided')

    def test_invalid_document_format_returns_bad_request(self):
        invalid_file = SimpleUploadedFile(
            'not-an-image.txt',
            b'plain text',
            content_type='text/plain'
        )

        response = self.client.post(
            reverse('mscc:ocr_process'),
            data={'document': invalid_file}
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()['error'],
            'Unsupported document format. Please upload an image file.'
        )
