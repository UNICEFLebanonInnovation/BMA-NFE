"""Pick the upload storage backend from the deployment's configuration."""

import base64

from django.test import SimpleTestCase

from config.settings import media_storage


class MediaStorageSelectionTests(SimpleTestCase):
    valid_key = base64.b64encode(b'account-key-bytes').decode()

    def test_sftp_host_wins_then_a_valid_azure_key_then_the_filesystem(self):
        self.assertEqual(media_storage.select_backend(sftp_host='files.ministry.local'), 'sftp')
        self.assertEqual(
            media_storage.select_backend(sftp_host='files.ministry.local', azure_account_key=self.valid_key),
            'sftp',
        )
        self.assertEqual(media_storage.select_backend(azure_account_key=self.valid_key), 'azure')
        self.assertEqual(media_storage.select_backend(azure_account_key='NO_AZURE_ACCOUNT_KEY'), 'filesystem')
        self.assertEqual(media_storage.select_backend(), 'filesystem')

    def test_explicit_backend_overrides_detection_and_rejects_unknown_names(self):
        self.assertEqual(
            media_storage.select_backend(explicit='filesystem', sftp_host='files.ministry.local'),
            'filesystem',
        )
        self.assertEqual(media_storage.select_backend(explicit=' Azure '), 'azure')
        with self.assertRaises(ValueError):
            media_storage.select_backend(explicit='s3')

    def test_sftp_storage_configuration(self):
        config = media_storage.media_storage(
            'sftp', sftp_host='files.ministry.local', sftp_root='/srv/bma/media',
            sftp_connect=media_storage.sftp_params(
                username='bma', password='secret', port='2222', timeout='30',
            ),
            sftp_known_host_file='/etc/bma/known_hosts',
        )
        self.assertEqual(config['BACKEND'], 'storages.backends.sftpstorage.SFTPStorage')
        self.assertEqual(config['OPTIONS'], {
            'host': 'files.ministry.local',
            'params': {'username': 'bma', 'password': 'secret', 'port': 2222, 'timeout': 30},
            'root_path': '/srv/bma/media',
            'interactive': False,
            'known_host_file': '/etc/bma/known_hosts',
        })
        self.assertEqual(
            media_storage.sftp_params(username='bma', key_file='/etc/bma/id_ed25519'),
            {'username': 'bma', 'key_filename': '/etc/bma/id_ed25519'},
        )
        with self.assertRaises(ValueError):
            media_storage.media_storage('sftp')

    def test_azure_and_filesystem_configurations(self):
        config = media_storage.media_storage('azure', azure_container='media', azure_url_expiry=600)
        self.assertEqual(config['BACKEND'], 'storages.backends.azure_storage.AzureStorage')
        self.assertEqual(config['OPTIONS'], {'azure_container': 'media', 'expiration_secs': 600})
        self.assertEqual(
            media_storage.media_storage('filesystem'),
            {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
        )
        with self.assertRaises(ValueError):
            media_storage.media_storage('ftp')

    def test_sftp_backend_can_be_instantiated_without_connecting(self):
        from django.core.files.storage import storages
        from django.test import override_settings

        config = media_storage.media_storage(
            'sftp', sftp_host='files.ministry.local', sftp_root='/srv/bma/media',
            sftp_connect={'username': 'bma', 'password': 'secret'},
        )
        with override_settings(STORAGES={
            'default': config,
            'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
        }):
            storage = storages['default']
            self.assertEqual(type(storage).__name__, 'SFTPStorage')
            self.assertEqual(storage._host, 'files.ministry.local')
            self.assertEqual(storage._root_path, '/srv/bma/media')
