"""Report the actual Child.photo backend without revealing storage credentials."""

import io
import uuid

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage, storages
from django.core.management.base import BaseCommand, CommandError
from PIL import Image
from student_registration.child.models import Child


class Command(BaseCommand):
    help = 'Show Child.photo storage; optionally verify a temporary image write/read/delete'

    def add_arguments(self, parser):
        parser.add_argument('--write-test', action='store_true')
        parser.add_argument('--require-share', action='store_true',
                            help='Reject storage backends that do not enforce a mounted share')

    def handle(self, *args, **options):
        storage = Child._meta.get_field('photo').storage
        if storage is default_storage:
            storage = storages['default']
        self.stdout.write('Backend: {}.{}'.format(type(storage).__module__, type(storage).__name__))
        location = getattr(storage, 'location', None)
        if location:
            self.stdout.write('Location: {}'.format(location))
        if options['require_share'] and not hasattr(storage, 'check_available'):
            raise CommandError('NFE media storage does not enforce a mounted file share')
        if hasattr(storage, 'check_available'):
            try:
                storage.check_available()
            except OSError as error:
                raise CommandError('NFE file-share mount is unavailable; mount the share and check NFE_FILE_SHARE_ROOT.') from error
            self.stdout.write('File-share mount: available')
        elif location:
            self.stdout.write('Mount enforcement: disabled for this storage backend')
        if not options['write_test']:
            self.stdout.write('Read-only check. Use --write-test to verify storage I/O.')
            return
        name = None
        try:
            image = io.BytesIO()
            Image.new('RGB', (1, 1), 'white').save(image, format='PNG')
            data = image.getvalue()
            name = storage.save('child_photos/sync-check/{}.png'.format(uuid.uuid4().hex), ContentFile(data))
            with storage.open(name, 'rb') as stream:
                if stream.read() != data:
                    raise ValueError('Read-back did not match')
            self.stdout.write(self.style.SUCCESS('Photo storage write/read succeeded'))
        except Exception as error:
            raise CommandError('Photo storage check failed ({})'.format(type(error).__name__)) from error
        finally:
            if name:
                storage.delete(name)
