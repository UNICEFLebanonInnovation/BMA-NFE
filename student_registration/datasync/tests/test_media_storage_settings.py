"""Exercise deployed settings selection in fresh interpreters without connecting to storage."""
import json
import os
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace
from unittest.mock import MagicMock

from azure.core.exceptions import ResourceNotFoundError
from django.test import SimpleTestCase

from ..photos import stored_photo_digest


class MediaStorageSettingsTests(SimpleTestCase):
    def configured(self, **values):
        environment = os.environ.copy()
        for name in ('WEBSITE_SITE_NAME', 'NFE_MEDIA_STORAGE_BACKEND', 'AZURE_URL_EXPIRATION_SECS'):
            environment.pop(name, None)
        environment.update(DJANGO_READ_DOT_ENV_FILE='False',
            AZURE_ACCOUNT_NAME='synthetic-nfe-account', AZURE_ACCOUNT_KEY='synthetic-unused-key',
            AZURE_CONTAINER='synthetic-nfe-container')
        environment.update(values)
        code = (
            'import json; from config.settings import base; '
            'print(json.dumps({"backend": base.STORAGES["default"]["BACKEND"], '
            '"legacy": base.DEFAULT_FILE_STORAGE, "expiry": base.AZURE_URL_EXPIRATION_SECS, '
            '"account": base.AZURE_ACCOUNT_NAME, "container": base.AZURE_CONTAINER}))'
        )
        result = subprocess.run([sys.executable, '-c', code], env=environment,
            cwd=Path(__file__).resolve().parents[3], capture_output=True, text=True, check=True)
        return json.loads(result.stdout.splitlines()[-1])

    def test_app_service_uses_existing_blob_settings_and_expiring_links(self):
        result = self.configured(WEBSITE_SITE_NAME='leb-container-test-sector-api')
        self.assertEqual(result['backend'], 'storages.backends.azure_storage.AzureStorage')
        self.assertEqual(result['legacy'], result['backend'])
        self.assertEqual(result['expiry'], 3600)
        self.assertEqual(result['account'], 'synthetic-nfe-account')
        self.assertEqual(result['container'], 'synthetic-nfe-container')

    def test_mehe_vm_keeps_share_storage_even_with_azure_settings_present(self):
        result = self.configured()
        self.assertEqual(result['backend'], 'student_registration.media_storage.VMFileShareStorage')

    def test_explicit_share_override_on_app_service_is_preserved(self):
        backend = 'student_registration.media_storage.VMFileShareStorage'
        self.assertEqual(self.configured(WEBSITE_SITE_NAME='synthetic-app',
            NFE_MEDIA_STORAGE_BACKEND=backend)['backend'], backend)

    def test_explicit_local_storage_override_is_preserved(self):
        backend = 'django.core.files.storage.FileSystemStorage'
        self.assertEqual(self.configured(WEBSITE_SITE_NAME='synthetic-app',
            NFE_MEDIA_STORAGE_BACKEND=backend)['backend'], backend)

    def test_explicit_blob_override_on_other_hosts_is_supported(self):
        backend = 'storages.backends.azure_storage.AzureStorage'
        self.assertEqual(self.configured(NFE_MEDIA_STORAGE_BACKEND=backend)['backend'], backend)

    def test_signed_link_duration_can_be_configured(self):
        self.assertEqual(self.configured(AZURE_URL_EXPIRATION_SECS='900')['expiry'], 900)


class AzureMissingPhotoTests(SimpleTestCase):
    def failing_child(self, code):
        error = ResourceNotFoundError('Synthetic local test')
        error.error_code = code
        field = MagicMock()
        field.open.return_value.__enter__.return_value.read.side_effect = error
        return SimpleNamespace(photo=field), error

    def test_a_missing_blob_is_treated_as_a_missing_photo(self):
        child, _ = self.failing_child('BlobNotFound')
        self.assertIsNone(stored_photo_digest(child))

    def test_a_missing_container_remains_a_storage_failure(self):
        child, error = self.failing_child('ContainerNotFound')
        with self.assertRaises(ResourceNotFoundError) as raised:
            stored_photo_digest(child)
        self.assertIs(raised.exception, error)
