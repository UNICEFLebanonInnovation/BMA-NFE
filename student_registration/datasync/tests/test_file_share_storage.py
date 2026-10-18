"""Shared media and exports must not fall back to local disk or Azure."""
import tempfile
from pathlib import Path
from unittest.mock import patch

from django.core.files.base import ContentFile
from django.test import SimpleTestCase

from student_registration.media_storage import FileShareUnavailable, VMFileShareStorage


class FileShareStorageTests(SimpleTestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.storage = VMFileShareStorage(location=str(self.root), share_root=str(self.root))

    def test_missing_mount_is_not_created_as_a_local_directory(self):
        missing = self.root / 'missing-share'
        storage = VMFileShareStorage(location=str(missing), share_root=str(missing))
        with self.assertRaises(FileShareUnavailable):
            storage.save('child_photos/photo.png', ContentFile(b'image'))
        self.assertFalse(missing.exists())

    def test_existing_local_directory_is_not_treated_as_a_share(self):
        with patch('student_registration.media_storage.os.path.ismount', return_value=False):
            with self.assertRaises(FileShareUnavailable):
                self.storage.save('child_photos/photo.png', ContentFile(b'image'))
        self.assertEqual(list(self.root.iterdir()), [])

    def test_available_mount_saves_under_its_media_subdirectory(self):
        storage = VMFileShareStorage(location=str(self.root / 'nfe'), share_root=str(self.root))
        with patch('student_registration.media_storage.os.path.ismount', return_value=True):
            name = storage.save('child_photos/photo.png', ContentFile(b'image'))
            with storage.open(name, 'rb') as stream:
                self.assertEqual(stream.read(), b'image')
        self.assertTrue((self.root / 'nfe/child_photos/photo.png').is_file())

    def test_unmounted_share_blocks_reads_and_writes_without_changing_files(self):
        (self.root / 'existing.png').write_bytes(b'previous')
        with patch('student_registration.media_storage.os.path.ismount', return_value=False):
            with self.assertRaises(FileShareUnavailable):
                self.storage.open('existing.png')
            with self.assertRaises(FileShareUnavailable):
                self.storage.save('new.png', ContentFile(b'new'))
        self.assertEqual((self.root / 'existing.png').read_bytes(), b'previous')
        self.assertFalse((self.root / 'new.png').exists())

    def test_media_location_outside_share_is_rejected(self):
        storage = VMFileShareStorage(location=str(self.root.parent / 'outside'), share_root=str(self.root))
        with patch('student_registration.media_storage.os.path.ismount', return_value=True):
            with self.assertRaises(FileShareUnavailable):
                storage.check_available()

    def test_exports_follow_default_storage_even_with_azure_credentials(self):
        from student_registration.backends.utils import ExportStorage
        with self.settings(
            AZURE_ACCOUNT_KEY='dmFsaWQtYnV0LXVudXNlZA==',
            STORAGES={'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage',
                                 'OPTIONS': {'location': str(self.root)}}},
        ):
            storage = ExportStorage()
            name = storage.save('report.csv', ContentFile(b'local export'))
            self.assertEqual(name, 'report.csv')
            self.assertEqual((self.root / 'export/report.csv').read_bytes(), b'local export')
            with storage.open(name, 'rb') as stream:
                self.assertEqual(stream.read(), b'local export')
            storage.delete(name)
            self.assertFalse((self.root / 'export/report.csv').exists())
