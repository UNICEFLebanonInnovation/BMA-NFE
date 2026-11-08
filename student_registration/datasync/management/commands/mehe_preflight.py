"""Fail before serving requests if MEHE's database or actual share is absent."""
from django.conf import settings
from django.core.files.storage import storages
from django.core.management.base import BaseCommand, CommandError
from django.db import DatabaseError, connection
from student_registration.media_storage import VMFileShareStorage

class Command(BaseCommand):
    help = 'Check the MEHE database and mounted-share origin without printing credentials'

    def handle(self, *args, **options):
        if settings.SETTINGS_MODULE != 'config.settings.mehe':
            raise CommandError('Use config.settings.mehe for this deployment check')
        try:
            with connection.cursor() as cursor:
                cursor.execute('SELECT 1')
                cursor.fetchone()
        except DatabaseError as error:
            raise CommandError('MEHE PostgreSQL connection failed; check the DB parameters and routing') from error
        storage = storages['default']
        if not isinstance(storage, VMFileShareStorage):
            raise CommandError('MEHE must use VMFileShareStorage')
        try:
            storage.check_available()
        except OSError as error:
            raise CommandError('MEHE file share is unavailable or its mount origin is incorrect') from error
        self.stdout.write('MEHE PostgreSQL: reachable')
        self.stdout.write('MEHE mounted share: verified')
