"""Real multipart uploads, file storage, replacement and retry behavior."""

import hashlib
import io
import json
import tempfile
import uuid
from pathlib import Path
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.files.storage import FileSystemStorage
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, TransactionTestCase
from django.urls import reverse
from PIL import Image
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from student_registration.child.models import Child
from ..models import SyncedChildPhoto


def image_bytes(color='red'):
    result = io.BytesIO()
    Image.new('RGB', (3, 3), color).save(result, format='PNG')
    return result.getvalue()


class PhotoIngestTests(TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.storage = FileSystemStorage(location=self.temp.name)
        self.storage_patch = patch.object(Child._meta.get_field('photo'), 'storage', self.storage)
        self.storage_patch.start()
        self.addCleanup(self.storage_patch.stop)
        self.flags = self.settings(DATASYNC_INGEST_ENABLED=True)
        self.flags.enable()
        self.addCleanup(self.flags.disable)
        user = get_user_model().objects.create(username='photo-sync-test')
        group, _ = Group.objects.get_or_create(name='DataSync')
        user.groups.add(group)
        token = Token.objects.create(user=user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Token {}'.format(token.key))
        self.url = reverse('datasync:ingest')
        self.child = Child.objects.create(bma_id='900', first_name='Test child')

    def body(self, data=None, day=1, **overrides):
        data = image_bytes() if data is None else data
        body = {
            'source_system': 'compiler', 'contract_version': '1.0',
            'event_id': str(uuid.uuid4()), 'source_id': '900',
            'source_modified': '2026-03-{:02d}T10:00:00Z'.format(day),
            'action': 'put', 'sha256': hashlib.sha256(data).hexdigest(),
            'photo': SimpleUploadedFile('../../unsafe.png', data, content_type='text/plain'),
        }
        body.update(overrides)
        return body

    def request_body(self, body):
        from ..constants import RESOURCE_REGISTRATION
        from .test_ingest import event, registration_payload
        descriptor = {'action': body['action'], 'sha256': body.get('sha256'),
                      'source_modified': body['source_modified'],
                      'file_key': 'photo_' + body['event_id'].replace('-', '')}
        payload = registration_payload()
        payload['child'] = {'source_id': body['source_id'], 'fields': {'first_name': 'Synced child'},
                            'photo_sync': descriptor}
        wire = event(RESOURCE_REGISTRATION, 1234, payload, event_id=body['event_id'])
        wire['source_modified'] = body['source_modified']
        result = {'envelope': json.dumps({'contract_version': body['contract_version'],
                                        'source_system': body['source_system'], 'events': [wire]})}
        if 'photo' in body:
            result[descriptor['file_key']] = body['photo']
        return result

    def post(self, body):
        response = self.client.post(self.url, self.request_body(body), format='multipart')
        if response.status_code == 200:
            response.data = response.data['results'][0]
        return response

    def test_unchanged_photo_is_not_written_again_for_a_new_registration_event(self):
        self.assertEqual(self.post(self.body()).data['status'], 'applied')
        self.assertEqual(self.post(self.body(day=2)).data['status'], 'applied')
        self.assertEqual(len(list(Path(self.temp.name).rglob('*.png'))), 1)

    def test_verified_reuse_sends_no_file_and_preserves_the_existing_copy(self):
        self.assertEqual(self.post(self.body()).data['status'], 'applied')
        body = self.body(day=2, action='verify')
        body.pop('photo')
        with patch.object(self.storage, 'save', wraps=self.storage.save) as save:
            response = self.post(body)
        self.assertEqual(response.data['status'], 'applied', response.data)
        self.assertIn('no image transfer', response.data['detail'])
        save.assert_not_called()

    def test_verify_missing_photo_requests_bytes_without_committing_metadata(self):
        from student_registration.mscc.models import Registration
        from ..models import SyncEventLog
        body = self.body(action='verify')
        body.pop('photo')
        response = self.post(body)
        self.assertTrue(response.data['photo_upload_required'])
        self.child.refresh_from_db()
        self.assertEqual(self.child.first_name, 'Test child')
        self.assertFalse(Registration.objects.exists())
        self.assertFalse(SyncEventLog.objects.filter(event_id=body['event_id']).exists())
        body['action'] = 'put'
        body['photo'] = SimpleUploadedFile('photo.png', image_bytes())
        self.assertEqual(self.post(body).data['status'], 'applied')

    def test_reuse_detects_an_in_place_local_edit_and_full_upload_restores_source(self):
        self.assertEqual(self.post(self.body()).data['status'], 'applied')
        self.child.refresh_from_db()
        Path(self.storage.path(self.child.photo.name)).write_bytes(image_bytes('green'))
        body = self.body(day=2, action='verify')
        body.pop('photo')
        self.assertTrue(self.post(body).data['photo_upload_required'])
        body['action'] = 'put'
        body['photo'] = SimpleUploadedFile('photo.png', image_bytes())
        response = self.post(body)
        self.assertEqual(response.data['status'], 'applied')
        self.assertTrue(response.data['conflict'])
        self.child.refresh_from_db()
        with self.child.photo.open('rb') as stream:
            self.assertEqual(stream.read(), image_bytes())

    def test_verify_storage_outage_does_not_request_unnecessary_upload(self):
        self.assertEqual(self.post(self.body()).data['status'], 'applied')
        body = self.body(day=2, action='verify')
        body.pop('photo')
        with patch.object(self.storage, 'open', side_effect=OSError('unmounted')):
            response = self.post(body)
        self.assertEqual(response.data['status'], 'failed')
        self.assertTrue(response.data['retryable'])
        self.assertNotIn('photo_upload_required', response.data)

    def test_database_failure_after_file_write_rolls_back_and_cleans_new_file(self):
        from django.db import IntegrityError
        from student_registration.mscc.models import Registration
        original_save = Child.save
        def fail_photo(instance, *args, **kwargs):
            if kwargs.get('update_fields') == ['photo']:
                raise IntegrityError('simulated database failure')
            return original_save(instance, *args, **kwargs)
        with patch.object(Child, 'save', new=fail_photo):
            response = self.post(self.body())
        self.assertEqual(response.data['status'], 'failed')
        self.assertFalse(Registration.objects.exists())
        self.assertEqual(len(list(Path(self.temp.name).rglob('*.png'))), 0)
        self.child.refresh_from_db()
        self.assertEqual(self.child.first_name, 'Test child')

    def test_photo_bytes_are_saved_and_linked_using_bma_identity(self):
        response = self.post(self.body())
        self.assertEqual(response.status_code, 200, response.data)
        self.child.refresh_from_db()
        self.assertTrue(self.child.photo.name.startswith('child_photos/sync/'))
        self.assertNotIn('unsafe', self.child.photo.name)
        with self.child.photo.open('rb') as photo:
            self.assertEqual(photo.read(), image_bytes())
        self.assertEqual(SyncedChildPhoto.objects.get().child_id, self.child.pk)

    def test_replay_does_not_write_another_file(self):
        event_id = str(uuid.uuid4())
        self.assertEqual(self.post(self.body(event_id=event_id)).data['status'], 'applied')
        response = self.post(self.body(event_id=event_id))
        self.assertEqual(response.data['status'], 'skipped')
        self.assertEqual(len(list(Path(self.temp.name).rglob('*.png'))), 1)

    def test_older_upload_cannot_replace_newer_photo(self):
        self.post(self.body(image_bytes('blue'), day=3))
        response = self.post(self.body(day=2))
        self.assertEqual(response.data['status'], 'skipped')
        self.child.refresh_from_db()
        with self.child.photo.open('rb') as photo:
            self.assertEqual(photo.read(), image_bytes('blue'))

    def test_new_version_replaces_reference_and_retains_previous_file(self):
        self.post(self.body())
        self.child.refresh_from_db()
        previous = self.child.photo.name
        self.assertEqual(self.post(self.body(image_bytes('blue'), day=2)).data['status'], 'applied')
        self.child.refresh_from_db()
        self.assertNotEqual(previous, self.child.photo.name)
        self.assertTrue(self.storage.exists(previous))

    def test_record_and_photo_create_the_child_in_one_request(self):
        result = self.post(self.body(source_id='901'))
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.data['status'], 'applied', result.data)
        self.assertTrue(Child.objects.get(bma_id='901').photo)
        self.assertEqual(SyncedChildPhoto.objects.get().source_id, '901')

    def test_normal_photo_replacement_has_no_local_edit_conflict(self):
        self.assertFalse(self.post(self.body()).data['conflict'])
        result = self.post(self.body(image_bytes('blue'), day=2)).data
        self.assertFalse(result['conflict'])
        self.assertIn('existing photo replaced', result['detail'])

    def test_local_photo_override_is_reported_audited_and_retained_on_replay(self):
        from ..models import SyncConflict, SyncEventLog
        self.post(self.body())
        self.child.refresh_from_db()
        synced = self.child.photo.name
        self.child.photo.save('manual-green.png', ContentFile(image_bytes('green')))
        manual = self.child.photo.name
        event_id = str(uuid.uuid4())
        result = self.post(self.body(day=2, event_id=event_id)).data
        self.assertTrue(result['conflict'], result)
        self.assertIn('local NFE photo edit overwritten', result['detail'])
        self.child.refresh_from_db()
        with self.child.photo.open('rb') as photo:
            self.assertEqual(photo.read(), image_bytes())
        audit = SyncConflict.objects.get(event_id=event_id)
        self.assertEqual(audit.diverged_fields['photo'], {'synced': synced, 'local': manual})
        self.assertTrue(self.storage.exists(manual))
        receipt = SyncEventLog.objects.get(event_id=event_id).applied_result
        self.assertTrue(receipt['conflict'])
        replay = self.post(self.body(day=2, event_id=event_id)).data
        self.assertEqual(replay['status'], 'skipped')
        self.assertTrue(replay['conflict'])
        self.assertEqual(replay['local_id'], result['local_id'])
        self.assertEqual(SyncConflict.objects.filter(event_id=event_id).count(), 1)

    def test_restoring_a_locally_cleared_photo_reports_an_override(self):
        self.post(self.body())
        self.child.refresh_from_db()
        self.child.photo = ''
        self.child.save(update_fields=['photo'])
        result = self.post(self.body(day=2)).data
        self.assertTrue(result['conflict'], result)
        self.child.refresh_from_db()
        self.assertTrue(self.child.photo)

    def test_first_source_photo_reports_replacement_of_existing_local_photo(self):
        self.child.photo.save('manual.png', ContentFile(image_bytes('green')))
        result = self.post(self.body()).data
        self.assertTrue(result['conflict'], result)
        self.assertIn('existing photo replaced', result['detail'])

    def test_failed_storage_preserves_previous_photo_and_allows_retry(self):
        self.post(self.body())
        self.child.refresh_from_db()
        previous = self.child.photo.name
        event_id = str(uuid.uuid4())
        with patch.object(self.storage, 'save', side_effect=OSError('share unavailable')):
            response = self.post(self.body(image_bytes('blue'), day=2, event_id=event_id))
        self.assertEqual(response.data['status'], 'failed')
        self.assertTrue(response.data['retryable'])
        self.child.refresh_from_db()
        self.assertEqual(self.child.photo.name, previous)
        self.assertEqual(self.post(self.body(image_bytes('blue'), day=2, event_id=event_id)).data['status'], 'applied')

    def test_explicit_remove_clears_managed_photo_and_blocks_old_retry(self):
        self.post(self.body())
        remove = self.body(day=3, action='remove')
        del remove['photo']
        self.assertEqual(self.post(remove).data['status'], 'applied')
        self.child.refresh_from_db()
        self.assertFalse(self.child.photo)
        self.assertEqual(self.post(self.body(day=2)).data['status'], 'skipped')

    def test_first_remove_does_not_clear_a_manually_uploaded_photo(self):
        self.child.photo.save('manual.png', SimpleUploadedFile('manual.png', image_bytes()))
        previous = self.child.photo.name
        body = self.body(action='remove')
        del body['photo']
        self.post(body)
        self.child.refresh_from_db()
        self.assertEqual(self.child.photo.name, previous)

    def test_invalid_bytes_and_wrong_checksum_are_rejected(self):
        for body in (self.body(b'not an image'), self.body(sha256='0' * 64)):
            response = self.post(body)
            self.assertEqual(response.data['status'], 'failed', response.data)
        self.assertFalse(SyncedChildPhoto.objects.exists())

    def test_large_files_are_rejected(self):
        with self.settings(DATASYNC_PHOTO_MAX_BYTES=10):
            response = self.post(self.body())
        self.assertEqual(response.data['status'], 'failed', response.data)

    def test_pixel_limit_is_checked(self):
        with self.settings(DATASYNC_PHOTO_MAX_PIXELS=1):
            response = self.post(self.body())
        self.assertEqual(response.data['status'], 'failed', response.data)

    def test_missing_timestamp_and_unknown_contract_are_rejected(self):
        for overrides in ({'source_modified': ''}, {'contract_version': '99.0'}):
            response = self.post(self.body(**overrides))
            self.assertTrue(response.status_code == 400 or response.data.get('status') == 'failed', response.data)

    def test_feature_disabled_is_retryable(self):
        with self.settings(DATASYNC_INGEST_ENABLED=False):
            response = self.post(self.body())
        self.assertEqual(response.status_code, 503)
        self.assertIn('disabled', response.data['detail'].lower())

    def test_authentication_and_group_are_required(self):
        self.client.credentials()
        self.assertIn(self.post(self.body()).status_code, (401, 403))
        user = get_user_model().objects.create(username='unprivileged-photo-test')
        token = Token.objects.create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION='Token {}'.format(token.key))
        self.assertEqual(self.post(self.body()).status_code, 403)

    def test_storage_check_round_trips_a_temporary_image_without_child_changes(self):
        from django.core.management import call_command
        output = io.StringIO()
        call_command('datasync_photo_storage_check', '--write-test', stdout=output)
        self.assertIn('write/read succeeded', output.getvalue())
        self.assertEqual(len(list(Path(self.temp.name).rglob('*.png'))), 0)
        self.child.refresh_from_db()
        self.assertFalse(self.child.photo)

    def test_unmounted_share_defers_entire_registration_and_retries_after_mount(self):
        from student_registration.media_storage import VMFileShareStorage
        from student_registration.mscc.models import Registration
        shared = VMFileShareStorage(location=self.temp.name, share_root=self.temp.name)
        event_id = str(uuid.uuid4())
        with patch.object(Child._meta.get_field('photo'), 'storage', shared):
            with patch('student_registration.media_storage.os.path.ismount', return_value=False):
                result = self.post(self.body(event_id=event_id)).data
            self.assertEqual(result['status'], 'failed')
            self.assertTrue(result['retryable'])
            self.assertFalse(Registration.objects.exists())
            self.assertEqual(len(list(Path(self.temp.name).rglob('*.png'))), 0)
            with patch('student_registration.media_storage.os.path.ismount', return_value=True):
                result = self.post(self.body(event_id=event_id)).data
            self.assertEqual(result['status'], 'applied', result)

    def test_require_share_check_rejects_a_regular_local_backend(self):
        from django.core.management import call_command
        from django.core.management.base import CommandError
        with self.assertRaisesRegex(CommandError, 'does not enforce a mounted file share'):
            call_command('datasync_photo_storage_check', '--require-share', stdout=io.StringIO())

    def test_regular_registration_json_cannot_replace_a_photo_with_a_path(self):
        from ..constants import RESOURCE_REGISTRATION
        from ..services import ingest_events
        from .test_ingest import event, registration_payload
        self.post(self.body())
        self.child.refresh_from_db()
        previous = self.child.photo.name
        payload = registration_payload()
        payload['child']['fields']['photo'] = 'unverified/path.png'
        result = ingest_events([event(RESOURCE_REGISTRATION, 1234, payload)], 'compiler')
        self.assertEqual(result['applied'], 1, result)
        self.child.refresh_from_db()
        self.assertEqual(self.child.photo.name, previous)


class PhotoConcurrencyTests(TransactionTestCase):
    setUp = PhotoIngestTests.setUp
    body = PhotoIngestTests.body
    request_body = PhotoIngestTests.request_body

    def test_two_workers_replaying_one_event_write_one_file(self):
        from concurrent.futures import ThreadPoolExecutor
        from threading import Barrier
        from django.db import connections

        barrier = Barrier(2)
        event_id = str(uuid.uuid4())
        credentials = self.client._credentials.copy()

        def send(_index):
            client = APIClient()
            client.credentials(**credentials)
            try:
                barrier.wait(timeout=10)
                response = client.post(self.url, self.request_body(self.body(event_id=event_id)), format='multipart')
                return response.data['results'][0]
            finally:
                connections.close_all()

        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(send, range(2)))
        self.assertEqual(sorted(item['status'] for item in results), ['applied', 'skipped'])
        self.assertEqual(len(list(Path(self.temp.name).rglob('*.png'))), 1)
