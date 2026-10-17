"""Copy server-side media into the configured default storage."""

import io
import os
import tempfile

from django.core.management import CommandError, call_command
from django.test import SimpleTestCase, override_settings


class UploadMediaToStorageTests(SimpleTestCase):
    def setUp(self):
        media = tempfile.TemporaryDirectory()
        target = tempfile.TemporaryDirectory()
        self.addCleanup(media.cleanup)
        self.addCleanup(target.cleanup)
        self.media_root = media.name
        self.target = target.name
        for name, content in (
            ('child_photos/child-1.png', b'photo'),
            ('uploads/consent.pdf', b'consent'),
        ):
            path = os.path.join(self.media_root, name)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'wb') as handle:
                handle.write(content)
        settings = override_settings(
            MEDIA_ROOT=self.media_root,
            STORAGES={
                'default': {
                    'BACKEND': 'django.core.files.storage.FileSystemStorage',
                    'OPTIONS': {'location': self.target},
                },
                'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
            },
        )
        settings.enable()
        self.addCleanup(settings.disable)

    def run_command(self, *args):
        output = io.StringIO()
        call_command('upload_media_to_storage', *args, stdout=output)
        return output.getvalue()

    def uploaded(self):
        names = []
        for directory, _, files in os.walk(self.target):
            names.extend(
                os.path.relpath(os.path.join(directory, name), self.target) for name in files
            )
        return sorted(names)

    def test_uploads_only_the_requested_prefix_and_keeps_names(self):
        output = self.run_command('--prefix', 'child_photos')
        self.assertEqual(self.uploaded(), ['child_photos/child-1.png'])
        self.assertIn('Uploaded 1 file(s), 0 already present.', output)
        with open(os.path.join(self.target, 'child_photos/child-1.png'), 'rb') as handle:
            self.assertEqual(handle.read(), b'photo')

    def test_rerun_skips_existing_files_and_dry_run_uploads_nothing(self):
        self.run_command('--prefix', 'child_photos')
        output = self.run_command()
        self.assertIn('Uploaded 1 file(s), 1 already present.', output)
        self.assertEqual(len(self.uploaded()), 2)
        with open(os.path.join(self.media_root, 'uploads/new.pdf'), 'wb') as handle:
            handle.write(b'new')
        output = self.run_command('--dry-run')
        self.assertIn('would upload uploads/new.pdf', output)
        self.assertEqual(len(self.uploaded()), 2)

    def test_source_folder_can_replace_media_root(self):
        backup = tempfile.TemporaryDirectory()
        self.addCleanup(backup.cleanup)
        path = os.path.join(backup.name, 'child_photos/backup.png')
        os.makedirs(os.path.dirname(path))
        with open(path, 'wb') as handle:
            handle.write(b'backup')
        output = self.run_command('--source', backup.name)
        self.assertEqual(self.uploaded(), ['child_photos/backup.png'])
        self.assertIn('Uploaded 1 file(s), 0 already present.', output)
        with self.assertRaises(CommandError):
            self.run_command('--source', os.path.join(backup.name, 'missing'))

    def test_refuses_when_the_default_storage_is_media_root_itself(self):
        with override_settings(STORAGES={
            'default': {
                'BACKEND': 'django.core.files.storage.FileSystemStorage',
                'OPTIONS': {'location': self.media_root},
            },
            'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
        }):
            with self.assertRaises(CommandError):
                self.run_command()
