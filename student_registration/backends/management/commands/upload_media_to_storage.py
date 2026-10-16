"""Copy files from the local MEDIA_ROOT into the configured default storage.

Child photographs were written to the server's own disk while the Azure
storage setting was ignored. Run this once on the server so the same files
exist in Azure Blob Storage under the names the database already holds::

    python manage.py upload_media_to_storage --prefix child_photos

Files already present in the storage are skipped, so the command can be
re-run safely. Use ``--dry-run`` to list what would be uploaded, and
``--source`` to upload a copy of the media folder from another machine.
"""

import os

from django.conf import settings
from django.core.files import File
from django.core.files.storage import FileSystemStorage, default_storage
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Upload files under MEDIA_ROOT to the default storage, keeping their relative names.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--prefix', action='append', default=[],
            help='Only upload files whose relative name starts with this prefix. '
                 'May be given several times; defaults to every file under the source.',
        )
        parser.add_argument(
            '--dry-run', action='store_true',
            help='List the files that would be uploaded without uploading them.',
        )
        parser.add_argument(
            '--overwrite', action='store_true',
            help='Upload a file even when the storage already has one with that name.',
        )
        parser.add_argument(
            '--source', default=None,
            help='Folder to upload instead of MEDIA_ROOT, for example a copy of the '
                 "server's media folder saved on another machine.",
        )

    def handle(self, *args, **options):
        storage = default_storage
        media_root = str(options['source'] or settings.MEDIA_ROOT)
        if isinstance(storage, FileSystemStorage) and os.path.abspath(
            storage.location,
        ) == os.path.abspath(media_root):
            raise CommandError(
                'The default storage is the source folder itself; configure the '
                'Azure backend in STORAGES before uploading.'
            )
        if not os.path.isdir(media_root):
            raise CommandError('Source folder does not exist: {}'.format(media_root))
        prefixes = tuple(prefix.strip('/').replace(os.sep, '/') for prefix in options['prefix'])

        uploaded = skipped = 0
        for directory, _, file_names in os.walk(media_root):
            for file_name in sorted(file_names):
                path = os.path.join(directory, file_name)
                name = os.path.relpath(path, media_root).replace(os.sep, '/')
                if prefixes and not name.startswith(prefixes):
                    continue
                if not options['overwrite'] and storage.exists(name):
                    skipped += 1
                    continue
                if options['dry_run']:
                    self.stdout.write('would upload {}'.format(name))
                    uploaded += 1
                    continue
                if options['overwrite'] and storage.exists(name):
                    storage.delete(name)
                with open(path, 'rb') as source:
                    saved_name = storage.save(name, File(source, name=name))
                if saved_name != name:
                    # The storage renamed the file, so the database reference
                    # would not match it. Remove the copy and report it.
                    storage.delete(saved_name)
                    raise CommandError(
                        'Storage would save {} as {}; upload aborted.'.format(name, saved_name)
                    )
                uploaded += 1
                self.stdout.write('uploaded {}'.format(name))
        self.stdout.write(self.style.SUCCESS(
            '{} {} file(s), {} already present.'.format(
                'Would upload' if options['dry_run'] else 'Uploaded', uploaded, skipped,
            )
        ))
