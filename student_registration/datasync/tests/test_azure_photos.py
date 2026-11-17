"""Optional real Azure SDK round trips against Microsoft's local Blob emulator.

Run with NFE_AZURITE_TEST_URL=http://127.0.0.1:10020/nfeqa and start Azurite
with AZURITE_ACCOUNTS=nfeqa:<base64 encoding of the synthetic key below>.
Only a loopback emulator is accepted; no cloud account credentials are used.
"""
import base64
import hashlib
import io
import os
from unittest import skipUnless
from unittest.mock import patch
from urllib.parse import parse_qs, urlparse
import uuid

from azure.core.exceptions import ResourceNotFoundError
from azure.storage.blob import BlobServiceClient
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse
import requests
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
from storages.backends.azure_storage import AzureStorage

from student_registration.child.models import Child
from student_registration.mscc.models import Registration
from ..models import SyncedChildPhoto, SyncEventLog
from . import test_photos as photo_tests
from .test_photos import image_bytes


EMULATOR_KEY = base64.b64encode(b'synthetic-local-nfe-azure-blob-test-key-0000000000000000000000000000').decode()


@skipUnless(os.environ.get('NFE_AZURITE_TEST_URL'), 'Local Azurite endpoint not configured')
class AzurePhotoIngestTests(TestCase):
    body = photo_tests.PhotoIngestTests.body
    request_body = photo_tests.PhotoIngestTests.request_body
    post = photo_tests.PhotoIngestTests.post

    def setUp(self):
        endpoint = os.environ['NFE_AZURITE_TEST_URL'].rstrip('/')
        parsed = urlparse(endpoint)
        assert parsed.scheme == 'http' and parsed.hostname in ('127.0.0.1', 'localhost')
        assert parsed.path == '/nfeqa', 'Only the synthetic local account is permitted'
        self.container = 'nfe-photos-' + uuid.uuid4().hex
        connection = ('DefaultEndpointsProtocol=http;AccountName=nfeqa;AccountKey=' + EMULATOR_KEY +
                      ';BlobEndpoint=' + endpoint + ';')
        self.service = BlobServiceClient.from_connection_string(connection, retry_total=0)
        self.service.create_container(self.container)
        self.addCleanup(self.service.close)
        self.addCleanup(self.delete_container)
        self.storage = AzureStorage(connection_string=connection, account_name='nfeqa',
            account_key=EMULATOR_KEY, azure_container=self.container, expiration_secs=3600)
        flags = self.settings(DATASYNC_INGEST_ENABLED=True, STORAGES={
            'default': {'BACKEND': 'storages.backends.azure_storage.AzureStorage',
                'OPTIONS': {'connection_string': connection, 'account_name': 'nfeqa',
                    'account_key': EMULATOR_KEY, 'azure_container': self.container, 'expiration_secs': 3600}},
            'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
        })
        flags.enable(); self.addCleanup(flags.disable)
        field_patch = patch.object(Child._meta.get_field('photo'), 'storage', self.storage)
        field_patch.start(); self.addCleanup(field_patch.stop)
        user = get_user_model().objects.create(username='synthetic-azure-photo-sync')
        user.groups.add(Group.objects.get_or_create(name='DataSync')[0])
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + Token.objects.create(user=user).key)
        self.url = reverse('datasync:ingest')
        self.child = Child.objects.create(bma_id='900', first_name='Synthetic Azure test child')

    def delete_container(self):
        try:
            self.service.delete_container(self.container)
        except ResourceNotFoundError:
            pass

    def test_photo_round_trip_and_read_only_signed_url(self):
        response = self.post(self.body())
        self.assertEqual(response.data['status'], 'applied', response.data)
        self.child.refresh_from_db()
        with self.child.photo.open('rb') as stream:
            self.assertEqual(stream.read(), image_bytes())
        url = self.child.photo.url
        query = parse_qs(urlparse(url).query)
        self.assertEqual(query['sp'], ['r'])
        self.assertIn('se', query)
        fetched = requests.get(url, timeout=5)
        self.assertEqual(fetched.status_code, 200)
        self.assertEqual(hashlib.sha256(fetched.content).hexdigest(), hashlib.sha256(image_bytes()).hexdigest())
        capabilities = self.client.get(self.url)
        self.assertEqual(capabilities.data['child_photo_sync']['storage_backend'],
                         'storages.backends.azure_storage.AzureStorage')

    def test_verify_reuses_existing_blob_without_an_upload(self):
        self.assertEqual(self.post(self.body()).data['status'], 'applied')
        self.child.refresh_from_db(); name = self.child.photo.name
        body = self.body(day=2, action='verify'); body.pop('photo')
        with patch.object(self.storage, 'save', wraps=self.storage.save) as save:
            result = self.post(body)
        self.assertEqual(result.data['status'], 'applied', result.data)
        self.assertIn('no image transfer', result.data['detail'])
        save.assert_not_called()
        self.child.refresh_from_db(); self.assertEqual(self.child.photo.name, name)
        self.assertEqual(len(list(self.service.get_container_client(self.container).list_blobs())), 1)

    def test_replacement_preserves_child_and_registration_identity(self):
        self.assertEqual(self.post(self.body()).data['status'], 'applied')
        registration_id = Registration.objects.get().pk
        child_id = self.child.pk
        result = self.post(self.body(data=image_bytes('green'), day=2))
        self.assertEqual(result.data['status'], 'applied', result.data)
        self.assertEqual(Registration.objects.get().pk, registration_id)
        self.child.refresh_from_db(); self.assertEqual(self.child.pk, child_id)
        with self.child.photo.open('rb') as stream:
            self.assertEqual(stream.read(), image_bytes('green'))

    def test_clear_removes_the_reference_and_preserves_identity(self):
        self.assertEqual(self.post(self.body()).data['status'], 'applied')
        registration_id = Registration.objects.get().pk
        body = self.body(day=2, action='remove'); body.pop('photo')
        self.assertEqual(self.post(body).data['status'], 'applied')
        self.child.refresh_from_db(); self.assertFalse(self.child.photo)
        self.assertEqual(Registration.objects.get().pk, registration_id)
        self.assertEqual(SyncedChildPhoto.objects.get().storage_name, '')

    def test_deleted_blob_requests_bytes_and_recovers_with_the_same_event(self):
        self.assertEqual(self.post(self.body()).data['status'], 'applied')
        self.child.refresh_from_db(); self.storage.delete(self.child.photo.name)
        registration_id = Registration.objects.get().pk
        body = self.body(day=2, action='verify'); body.pop('photo')
        response = self.post(body)
        self.assertTrue(response.data.get('photo_upload_required'), response.data)
        self.assertFalse(SyncEventLog.objects.filter(event_id=body['event_id']).exists())
        body['action'] = 'put'
        body['photo'] = SimpleUploadedFile('replacement.png', image_bytes(), content_type='image/png')
        self.assertEqual(self.post(body).data['status'], 'applied')
        self.assertEqual(Registration.objects.get().pk, registration_id)
        self.child.refresh_from_db()
        with self.child.photo.open('rb') as stream:
            self.assertEqual(stream.read(), image_bytes())

    def test_private_blob_requires_the_signed_link(self):
        self.assertEqual(self.post(self.body()).data['status'], 'applied')
        self.child.refresh_from_db()
        plain_url = self.service.get_blob_client(self.container, self.child.photo.name).url
        self.assertIn(requests.get(plain_url, timeout=5).status_code, (403, 404))
        self.assertEqual(requests.get(self.child.photo.url, timeout=5).status_code, 200)

    def test_missing_container_keeps_the_complete_event_retryable(self):
        self.service.delete_container(self.container)
        response = self.post(self.body())
        self.assertEqual(response.data['status'], 'failed')
        self.assertTrue(response.data['retryable'])
        self.assertIn('Photo storage unavailable', response.data['detail'])
        self.assertFalse(Registration.objects.exists())
        self.assertFalse(SyncedChildPhoto.objects.exists())
        self.child.refresh_from_db(); self.assertFalse(self.child.photo)

    def test_storage_diagnostic_writes_reads_and_cleans_up_a_blob(self):
        output = io.StringIO()
        call_command('datasync_photo_storage_check', write_test=True, stdout=output)
        self.assertIn('Photo storage write/read succeeded', output.getvalue())
        self.assertEqual(list(self.service.get_container_client(self.container).list_blobs()), [])
