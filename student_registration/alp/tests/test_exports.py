import codecs
from unittest.mock import patch

from django.http import HttpResponse
from django.test import SimpleTestCase
from django_tables2.export.views import ExportMixin

from student_registration.alp.export import ALPExportMixin


class ALPExportMixinTests(SimpleTestCase):
    def test_csv_export_has_utf8_bom_and_charset(self):
        source = 'الاسم\nلينا\n'.encode('utf-8')

        with patch.object(
            ExportMixin,
            'create_export',
            return_value=HttpResponse(source, content_type='text/csv'),
        ):
            response = ALPExportMixin().create_export('csv')

        self.assertEqual(response.content, codecs.BOM_UTF8 + source)
        self.assertEqual(response['Content-Type'], 'text/csv; charset=utf-8')

    def test_csv_export_does_not_duplicate_existing_bom(self):
        source = codecs.BOM_UTF8 + 'الاسم\n'.encode('utf-8')

        with patch.object(
            ExportMixin,
            'create_export',
            return_value=HttpResponse(source, content_type='text/csv'),
        ):
            response = ALPExportMixin().create_export('CSV')

        self.assertEqual(response.content, source)

    def test_non_csv_export_is_unchanged(self):
        source = b'workbook data'
        original = HttpResponse(
            source,
            content_type=(
                'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            ),
        )

        with patch.object(ExportMixin, 'create_export', return_value=original):
            response = ALPExportMixin().create_export('xlsx')

        self.assertIs(response, original)
        self.assertEqual(response.content, source)
