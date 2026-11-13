"""Standalone integration check: python tests/check_export_download.py.

Uses disposable SQLite tables and local export files, never production data.
Loads the real filters, export generator, storage, URL resolution and download view.
"""
import io
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from django.conf import settings

settings.configure(
    SECRET_KEY='isolated-export-check', USE_TZ=True, USE_I18N=False,
    AUTH_USER_MODEL='users.User', ROOT_URLCONF=__name__, LOGIN_URL='/login/',
    ALLOWED_HOSTS=['testserver'],
    MEDIA_URL='/media/', AZURE_ACCOUNT_KEY='',
    DATABASES={'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': ':memory:'}},
    INSTALLED_APPS=[
        'django.contrib.auth', 'django.contrib.contenttypes', 'mptt', 'dal', 'dal_select2',
        'student_registration.users', 'student_registration.students',
        'student_registration.schools', 'student_registration.locations',
        'student_registration.child', 'student_registration.clm',
        'student_registration.mscc', 'student_registration.attendances',
        'student_registration.backends',
    ],
)

import django
django.setup()

from django.db import connection
from django.test import RequestFactory, override_settings
from django.urls import include, path, resolve
from openpyxl import load_workbook
from student_registration.locations.models import Location, LocationType
from student_registration.mscc.filters import MainFilter, FullFilter
from student_registration.mscc.models import Registration
from student_registration.mscc import tasks
from student_registration.mscc.views import get_file

urlpatterns = [path('mscc/', include(([
    path('export-download/<str:file_name>/', get_file, name='export_download'),
], 'mscc'), namespace='mscc'))]


class ExportDownloadChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with connection.schema_editor() as schema:
            schema.create_model(LocationType)
            schema.create_model(Location)
        kind = LocationType.objects.create(id=1, name='Governorate')
        cls.first = Location.objects.create(name='Beirut', type=kind)
        cls.second = Location.objects.create(name='North', type=kind)
        with connection.cursor() as cursor:
            cursor.execute('CREATE TABLE locations_center (id integer, governorate_id integer)')
            cursor.execute('INSERT INTO locations_center VALUES (10, %s), (20, %s)',
                           [cls.first.pk, cls.second.pk])
            cursor.execute('CREATE TABLE mscc_registration (id integer, center_id integer, round_id integer)')
            cursor.execute('INSERT INTO mscc_registration VALUES (101, 10, 3), (202, 20, 3)')
            cursor.execute("CREATE VIEW vw_mscc_data AS SELECT id, center_id, round_id FROM mscc_registration")
            cursor.execute("CREATE VIEW vw_mscc_data_no_round AS SELECT * FROM vw_mscc_data")
        cls.user = SimpleNamespace(is_authenticated=True, is_staff=True,
                                   center_id=None, partner_id=None)

    def test_governorate_filters_list_rows_and_renders_selection(self):
        for filter_class in (MainFilter, FullFilter):
            with self.subTest(filter_class=filter_class.__name__):
                filters = filter_class(
                    {'governorate': str(self.first.pk)},
                    queryset=Registration.objects.all(),
                    request=SimpleNamespace(user=self.user),
                )
                self.assertTrue(filters.is_valid(), filters.errors)
                self.assertEqual(list(filters.qs.order_by('pk').values_list('pk', flat=True)), [101])
                self.assertIn('Beirut', str(filters.form['governorate']))
                self.assertIn('selected', str(filters.form['governorate']))

    def test_governorate_preserves_existing_queryset_scope(self):
        filters = MainFilter(
            {'governorate': str(self.first.pk)},
            queryset=Registration.objects.filter(pk=202),
            request=SimpleNamespace(user=self.user),
        )
        self.assertEqual(list(filters.qs.order_by('pk').values_list('pk', flat=True)), [])

    def test_blank_governorate_keeps_all_rows(self):
        filters = MainFilter(
            {'governorate': ''}, queryset=Registration.objects.all(),
            request=SimpleNamespace(user=self.user),
        )
        self.assertEqual(list(filters.qs.order_by('pk').values_list('pk', flat=True)), [101, 202])

    def test_excel_generation_and_repeated_download_with_governorate(self):
        for round_value in ('', '3', 'no_round'):
            with self.subTest(round=round_value), tempfile.TemporaryDirectory() as directory:
                export = SimpleNamespace(created_by=self.user, status='pending',
                                         file_url='', save=Mock())
                with override_settings(MEDIA_ROOT=directory), \
                     patch.dict('os.environ', {'AZURE_ACCOUNT_KEY': ''}), \
                     patch.object(tasks.ExportHistory.objects, 'get', return_value=export), \
                     patch.object(tasks, 'send_push_to_web', return_value=False):
                    tasks._generate_filtered_mscc_export(
                        1, {'governorate': str(self.first.pk), 'round': round_value}, 'xlsx'
                    )
                    self.assertEqual(export.status, 'done')
                    self.assertTrue(export.file_url.endswith('.xlsx/'))
                    # Visit the generated URL through the real authenticated view twice.
                    for attempt in range(2):
                        request = RequestFactory().get(export.file_url)
                        request.user = self.user
                        match = resolve(export.file_url)
                        response = match.func(request, **match.kwargs)
                        self.assertEqual(response.status_code, 200)
                        self.assertIn('attachment;', response['Content-Disposition'])
                        self.assertIn('exported_data.xlsx', response['Content-Disposition'])
                        self.assertEqual(response['Content-Type'],
                            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                        payload = b''.join(response.streaming_content)
                        response.close()
                        workbook = load_workbook(io.BytesIO(payload))
                        self.assertEqual(list(workbook.active.values),
                                         [('id', 'center_id', 'round_id'), ('101', '10', '3')])
                        workbook.close()

    def test_anonymous_download_redirects_to_login(self):
        request = RequestFactory().get('/mscc/export-download/example.xlsx/')
        request.user = SimpleNamespace(is_authenticated=False)
        response = get_file(request, 'example.xlsx')
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/users/login?next='))


if __name__ == '__main__':
    unittest.main(verbosity=2)
