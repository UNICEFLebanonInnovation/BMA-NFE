"""Exercise the actual Office documents and their child/photo associations."""

import csv
import io
import posixpath
import tempfile
import zipfile
from pathlib import Path
from unittest.mock import patch
from uuid import UUID
from xml.etree import ElementTree

from PIL import Image

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.files.base import ContentFile
from django.core.files.storage import Storage
from django.test import TestCase, override_settings
from django.urls import reverse

from student_registration.backends.models import ExportHistory
from student_registration.child.models import Child
from student_registration.clm.models import Disability
from student_registration.locations.models import Center, Location, LocationType
from student_registration.mscc.card_fonts import ARABIC_CARD_FONT
from student_registration.mscc.document_exports import (
    build_children_workbook,
    build_examination_card,
)
from student_registration.mscc.models import ExceptionalExam, Registration, Round
from student_registration.mscc.tasks import (
    _generate_filtered_mscc_export,
    _generate_mscc_export,
)
from student_registration.schools.models import PartnerOrganization
from student_registration.students.models import Nationality


SPREADSHEET_NS = {'s': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
DRAWING_NS = {
    'xdr': 'http://schemas.openxmlformats.org/drawingml/2006/spreadsheetDrawing',
    'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
    'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
}
WORD_NS = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
WORD_DRAWING_NS = 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing'
RELATIONSHIP_NS = 'http://schemas.openxmlformats.org/package/2006/relationships'
CARD_HEADING = 'الامتحان الاستثنائي لطلاب التعليم الغير نظامي'


def portrait_bytes(colour):
    output = io.BytesIO()
    Image.new('RGB', (48, 64), colour).save(output, format='PNG')
    return output.getvalue()


def workbook_rows(content):
    """Read real cell values without relying on a writer's internal objects."""
    with zipfile.ZipFile(io.BytesIO(content)) as archive:
        shared_strings = []
        if 'xl/sharedStrings.xml' in archive.namelist():
            root = ElementTree.fromstring(archive.read('xl/sharedStrings.xml'))
            shared_strings = [
                ''.join(value.itertext()) for value in root.findall('s:si', SPREADSHEET_NS)
            ]
        root = ElementTree.fromstring(archive.read('xl/worksheets/sheet1.xml'))
        rows = []
        for row in root.findall('s:sheetData/s:row', SPREADSHEET_NS):
            values = {}
            for cell in row.findall('s:c', SPREADSHEET_NS):
                value = cell.find('s:v', SPREADSHEET_NS)
                if cell.get('t') == 's':
                    values[cell.get('r')] = shared_strings[int(value.text)]
                elif cell.get('t') == 'inlineStr':
                    values[cell.get('r')] = ''.join(
                        cell.find('s:is', SPREADSHEET_NS).itertext()
                    )
                else:
                    values[cell.get('r')] = value.text if value is not None else ''
            rows.append((int(row.get('r')), values))
    headers = {}
    for address, value in rows[0][1].items():
        headers[''.join(character for character in address if character.isalpha())] = value
    return [
        (number, {
            headers[''.join(character for character in address if character.isalpha())]: value
            for address, value in values.items()
        }) for number, values in rows[1:]
    ]


def workbook_photos_by_row(content):
    """Follow each drawing's relationship to its image and its real row anchor."""
    photos = {}
    with zipfile.ZipFile(io.BytesIO(content)) as archive:
        for drawing_name in archive.namelist():
            if not drawing_name.startswith('xl/drawings/drawing') or not drawing_name.endswith('.xml'):
                continue
            relation_name = posixpath.join(
                posixpath.dirname(drawing_name), '_rels',
                posixpath.basename(drawing_name) + '.rels',
            )
            relationships = ElementTree.fromstring(archive.read(relation_name))
            targets = {
                relation.get('Id'): posixpath.normpath(posixpath.join(
                    posixpath.dirname(drawing_name), relation.get('Target'),
                ))
                for relation in relationships.findall('{%s}Relationship' % RELATIONSHIP_NS)
            }
            drawing = ElementTree.fromstring(archive.read(drawing_name))
            for anchor in drawing:
                row = anchor.find('xdr:from/xdr:row', DRAWING_NS)
                blip = anchor.find('.//a:blip', DRAWING_NS)
                if row is not None and blip is not None:
                    image_id = blip.get('{%s}embed' % DRAWING_NS['r'])
                    photos[int(row.text) + 1] = archive.read(targets[image_id])
    return photos


def word_text_and_photos(content):
    with zipfile.ZipFile(io.BytesIO(content)) as archive:
        document = ElementTree.fromstring(archive.read('word/document.xml'))
        text = '\n'.join(
            ''.join(value.text or '' for value in paragraph.findall('.//w:t', WORD_NS))
            for paragraph in document.findall('.//w:p', WORD_NS)
        )
        photos = [archive.read(name) for name in archive.namelist() if name.startswith('word/media/')]
    return text, photos


def card_field(text, label):
    """Read a reference-card label and value after joining its editable runs."""
    return next(
        line.partition(':')[2].strip() for line in text.splitlines()
        if line.strip().startswith(label + ':')
    )


def field_value(row, label, field=None):
    # The old free-text address fields share a label with the new location FKs.
    # Prefer the explicitly disambiguated field when a duplicate exists.
    qualified_label = '{} ({})'.format(label, field) if field else label
    return row[qualified_label] if qualified_label in row else row[label]


class MemoryPhotoStorage(Storage):
    """Model a remote store that has neither filesystem paths nor public URLs."""

    def __init__(self, data):
        self.data = data

    def _open(self, name, mode='rb'):
        return ContentFile(self.data, name=name)


@override_settings(LANGUAGE_CODE='en', DEFAULT_FILE_STORAGE='django.core.files.storage.FileSystemStorage')
class MSCCDocumentExportTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.nationality = Nationality.objects.create(name='Test nationality', name_en='Test nationality')
        cls.disability = Disability.objects.create(name='Registered special need', name_en='Registered special need')
        governorate_type = LocationType.objects.create(pk=1, name='Governorate')
        district_type = LocationType.objects.create(pk=2, name='District')
        cadaster_type = LocationType.objects.create(pk=3, name='Cadaster')
        cls.governorate = Location.objects.create(
            type=governorate_type, name='محافظة التحقق', name_en='Verification governorate',
        )
        cls.district = Location.objects.create(
            type=district_type, parent=cls.governorate,
            name='قضاء التحقق', name_en='Verification district',
        )
        cls.cadaster = Location.objects.create(
            type=cadaster_type, parent=cls.district,
            name='عقار التحقق', name_en='Verification cadaster',
        )
        cls.partner = PartnerOrganization.objects.create(name='Test export partner')
        cls.other_partner = PartnerOrganization.objects.create(name='Other export partner')
        cls.center = Center.objects.create(name='Test export centre', partner=cls.partner)
        cls.other_center = Center.objects.create(name='Second export centre', partner=cls.partner)
        cls.outside_center = Center.objects.create(name='Outside export centre', partner=cls.other_partner)
        cls.round = Round.objects.create(name='Historic export round', current_year=False, year=2021)
        cls.first_child = Child.objects.create(
            first_name='Rania', father_name='Samir', last_name='Example',
            mother_fullname='Mother of Rania', gender='Female', nationality=cls.nationality,
            birthday_year='2014', birthday_month='3', birthday_day='12',
            governorate=cls.governorate, district=cls.district, cadaster=cls.cadaster,
            governorate_legacy='Old governorate text', district_legacy='Old district text',
            cadaster_legacy='Old cadaster text', municipality='Verification municipality',
            village='Verification village', street='Verification street', building_camp='Building 12',
            first_phone_number='70-123456', unicef_id='PHOTO-CHILD-001',
            national_number='Stored legacy document number',
            disability=cls.disability, disability_other='Registered additional support need',
            fe_unique_id='FORMAL-EDUCATION-123',
        )
        cls.second_child = Child.objects.create(
            first_name='Karim', father_name='Ibrahim', last_name='Second',
            mother_fullname='Mother of Karim', gender='Male', unicef_id='PHOTO-CHILD-002',
        )
        cls.outside_child = Child.objects.create(first_name='Outside', last_name='Private')
        cls.first_registration = Registration.objects.create(
            child=cls.first_child, partner=cls.partner, center=cls.center,
            round=cls.round, nfe_programme='BLN',
        )
        cls.second_registration = Registration.objects.create(
            child=cls.second_child, partner=cls.partner, center=cls.other_center,
            nfe_programme='DIRASA',
        )
        cls.outside_registration = Registration.objects.create(
            child=cls.outside_child, partner=cls.other_partner, center=cls.outside_center,
            nfe_programme='DIRASA',
        )
        cls.deleted_registration = Registration.objects.create(
            child=cls.first_child, partner=cls.partner, center=cls.center,
            nfe_programme='BLN', deleted=True,
        )
        cls.unicef_user = cls.make_user('photo-unicef', ['MSCC', 'MSCC_UNICEF'])
        cls.center_user = cls.make_user('photo-centre', ['MSCC', 'MSCC_CENTER'], center=cls.center)
        cls.partner_user = cls.make_user('photo-partner', ['MSCC', 'MSCC_PARTNER'], partner=cls.partner)
        cls.base_user = cls.make_user('photo-basic', ['MSCC'])
        cls.unassigned_user = cls.make_user('photo-unassigned', ['MSCC', 'MSCC_CENTER'])

    @staticmethod
    def make_user(username, groups, **fields):
        user = get_user_model().objects.create_user(username=username, **fields)
        user.groups.add(*(Group.objects.get_or_create(name=name)[0] for name in groups))
        return user

    def setUp(self):
        temporary_media = tempfile.TemporaryDirectory()
        self.addCleanup(temporary_media.cleanup)
        media_settings = override_settings(MEDIA_ROOT=temporary_media.name)
        media_settings.enable()
        self.addCleanup(media_settings.disable)
        self.first_child.photo.save('rania.png', ContentFile(portrait_bytes('red')))
        self.second_child.photo.save('karim.png', ContentFile(portrait_bytes('blue')))
        self.client.force_login(self.unicef_user)

    def assertPhotoColour(self, content, expected):
        with Image.open(io.BytesIO(content)) as photo:
            pixel = photo.convert('RGB').getpixel((photo.width // 2, photo.height // 2))
        self.assertEqual(pixel, expected)

    def registration_queryset(self):
        return Registration.objects.filter(deleted=False).order_by('pk')

    def generate_export(self, user, filtered=True, filters=None, notification_error=False, file_format='xlsx'):
        export = ExportHistory.objects.create(
            created_by=user, export_type='NFR Sector List', file_format=file_format,
        )
        files = {}

        def save_file(name, content):
            files[name] = content.read()
            return name

        with patch('student_registration.mscc.tasks.ExportStorage') as storage_class:
            storage_class.return_value.save.side_effect = save_file
            with patch('student_registration.mscc.tasks.send_push_to_web') as notification:
                if notification_error:
                    notification.side_effect = RuntimeError('Notification temporarily unavailable')
                if filtered:
                    _generate_filtered_mscc_export(export.pk, filters=filters, file_format=file_format)
                else:
                    _generate_mscc_export(export.pk, file_format=file_format)
        export.refresh_from_db()
        self.assertEqual(export.status, 'done')
        self.assertEqual(len(files), 1)
        name, content = next(iter(files.items()))
        if name.endswith('.zip'):
            with zipfile.ZipFile(io.BytesIO(content)) as archive:
                content = archive.read('mscc_data.{}'.format(file_format))
        return export, content

    def test_excel_keeps_each_photo_on_the_corresponding_record_with_current_information(self):
        content = build_children_workbook(self.registration_queryset())
        rows = workbook_rows(content)
        photos = workbook_photos_by_row(content)
        self.assertEqual(len(rows), 3)
        records = {row['Registration ID']: (number, row) for number, row in rows}
        first_row_number, first = records[str(self.first_registration.pk)]
        second_row_number, second = records[str(self.second_registration.pk)]
        self.assertEqual(first['Child ID'], str(self.first_child.pk))
        self.assertEqual(second['Child ID'], str(self.second_child.pk))
        self.assertEqual(first['First name'], 'Rania')
        self.assertEqual(second['First name'], 'Karim')
        self.assertIn('BLN', first['Type of NFE Programme'])
        self.assertEqual(second['Type of NFE Programme'], 'DIRASA')
        self.assertEqual(
            field_value(first, 'Governorate (محافظة)', 'governorate'), str(self.governorate),
        )
        self.assertEqual(
            field_value(first, 'District/Caza (قضاء)', 'district'), str(self.district),
        )
        self.assertEqual(field_value(first, 'Cadaster (منطقة عقارية)', 'cadaster'), str(self.cadaster))
        for value in (
            'Verification municipality', 'Verification village', 'Verification street', 'Building 12',
            '70-123456', 'Stored legacy document number', 'Old governorate text',
            'Registered special need', 'Registered additional support need', 'FORMAL-EDUCATION-123',
        ):
            self.assertIn(value, first.values())
        self.assertPhotoColour(photos[first_row_number], (255, 0, 0))
        self.assertPhotoColour(photos[second_row_number], (0, 0, 255))
        self.assertEqual(first['Photograph status'], 'Photograph included')

    def test_multiple_registrations_for_one_child_keep_the_same_photo_and_distinct_programme(self):
        newer_registration = Registration.objects.create(
            child=self.first_child, center=self.center, partner=self.partner, nfe_programme='DIRASA',
        )
        content = build_children_workbook(
            Registration.objects.filter(pk__in=[self.first_registration.pk, newer_registration.pk]),
        )
        rows = workbook_rows(content)
        photos = workbook_photos_by_row(content)
        self.assertEqual(len(rows), 2)
        self.assertEqual({row['Child ID'] for _, row in rows}, {str(self.first_child.pk)})
        self.assertEqual(
            {row['Registration ID'] for _, row in rows},
            {str(self.first_registration.pk), str(newer_registration.pk)},
        )
        self.assertTrue(any('BLN' in row['Type of NFE Programme'] for _, row in rows))
        self.assertTrue(any(row['Type of NFE Programme'] == 'DIRASA' for _, row in rows))
        for number, _ in rows:
            self.assertPhotoColour(photos[number], (255, 0, 0))

    def test_excel_writes_registered_formula_like_text_as_literal_values(self):
        self.first_child.first_name = '=HYPERLINK("https://example.invalid","name")'
        self.first_child.street = '=1+2'
        self.first_child.save(update_fields=['first_name', 'street'])
        content = build_children_workbook(
            Registration.objects.filter(pk=self.first_registration.pk),
        )
        row = workbook_rows(content)[0][1]
        self.assertEqual(row['First name'], self.first_child.first_name)
        self.assertEqual(row['Street (شارع)'], '=1+2')
        with zipfile.ZipFile(io.BytesIO(content)) as archive:
            worksheet = ElementTree.fromstring(archive.read('xl/worksheets/sheet1.xml'))
        self.assertEqual(worksheet.findall('.//s:f', SPREADSHEET_NS), [])

    def test_missing_and_corrupt_photos_have_explicit_status_and_no_wrong_image(self):
        self.first_child.photo.save('corrupt.png', ContentFile(b'not-an-image'))
        content = build_children_workbook(
            Registration.objects.filter(pk__in=[self.first_registration.pk, self.outside_registration.pk]),
        )
        rows = {row['Registration ID']: row for _, row in workbook_rows(content)}
        self.assertEqual(rows[str(self.first_registration.pk)]['Photograph status'], 'Photograph unavailable')
        self.assertEqual(rows[str(self.outside_registration.pk)]['Photograph status'], 'No photograph uploaded')
        self.assertEqual(workbook_photos_by_row(content), {})
        for registration, status in (
            (self.first_registration, 'Photograph unavailable'),
            (self.outside_registration, 'No photograph uploaded'),
        ):
            registration.refresh_from_db()
            text, photos = word_text_and_photos(build_examination_card(registration))
            self.assertIn(status, text)
            self.assertEqual(photos, [])

    def test_word_card_uses_the_registered_child_information_and_matching_photo(self):
        self.first_registration.refresh_from_db()
        text, photos = word_text_and_photos(build_examination_card(self.first_registration))
        for value in (
            CARD_HEADING, 'Round', self.round.name, str(self.round.year),
            'Rania Samir Example', '12/3/14', self.nationality.name_en,
            self.governorate.name_en, self.partner.name, self.disability.name_en,
        ):
            self.assertIn(value, text)
        self.assertEqual(card_field(text, 'ID'), str(self.first_registration.pk))
        self.assertEqual(card_field(text, 'Place of Birth'), '')
        for value in (
            'PHOTO-CHILD-001', 'BLN', '70-123456', self.district.name, self.cadaster.name,
            'Verification municipality', 'Verification village', 'Verification street', 'Building 12',
            'Registered additional support need', 'FORMAL-EDUCATION-123',
        ):
            self.assertNotIn(value, text)
        self.assertNotIn('Karim', text)
        self.assertNotIn('PHOTO-CHILD-002', text)
        self.assertEqual(len(photos), 1)
        self.assertPhotoColour(photos[0], (255, 0, 0))

    def test_word_card_uses_registration_id_stored_round_and_preferred_labels(self):
        self.partner.short_name = 'REFERENCE-NGO'
        self.partner.save(update_fields=['short_name'])
        self.nationality.name = 'جنسية مسجلة'
        self.nationality.name_en = 'Preferred nationality'
        self.nationality.save(update_fields=['name', 'name_en'])
        self.disability.name = 'صعوبة مسجلة'
        self.disability.name_en = 'Preferred physical difficulty'
        self.disability.save(update_fields=['name', 'name_en'])
        self.governorate.name_en = ''
        self.governorate.save(update_fields=['name_en'])
        self.first_child.nationality_other = 'Detail for an unselected Other nationality'
        self.first_child.save(update_fields=['nationality_other'])
        round = Round.objects.create(name='Stored card round', year=2037, current_year=False)
        registration = Registration.objects.create(
            pk=876543, child=self.first_child, partner=self.partner, center=self.center, round=round,
        )
        content = build_examination_card(registration)
        text, photos = word_text_and_photos(content)
        self.assertNotEqual(registration.pk, self.first_child.pk)
        self.assertEqual(card_field(text, 'ID'), str(registration.pk))
        self.assertEqual(card_field(text, 'NGO'), 'REFERENCE-NGO')
        self.assertEqual(card_field(text, 'Nationality'), 'Preferred nationality')
        self.assertEqual(card_field(text, 'Governorate'), self.governorate.name)
        self.assertEqual(card_field(text, 'Physical difficulties'), 'Preferred physical difficulty')
        self.assertEqual(card_field(text, 'Place of Birth'), '')
        self.assertIn('Stored card round', text)
        self.assertIn('2037', text)
        self.assertNotIn('Historic export round', text)
        self.assertNotIn('Detail for an unselected Other nationality', text)
        self.assertNotIn('Registered additional support need', text)
        self.assertPhotoColour(photos[0], (255, 0, 0))
        with zipfile.ZipFile(io.BytesIO(content)) as archive:
            properties = ElementTree.fromstring(archive.read('docProps/core.xml'))
        namespace = '{http://purl.org/dc/elements/1.1/}'
        self.assertIn('Child {}'.format(self.first_child.pk), properties.find(namespace + 'title').text)
        self.assertIn(str(registration.pk), properties.find(namespace + 'subject').text)

    def test_word_card_and_excel_use_the_place_of_birth_from_the_examination_application(self):
        ExceptionalExam.objects.create(
            registration=self.first_registration, governorate=self.governorate,
            district=self.district, nearest_town='achrafieh', place_of_birth='بيروت',
            programme='BLN', grade='2', math_language='ar', language_exam='en',
        )
        registration = Registration.objects.get(pk=self.first_registration.pk)
        text, _ = word_text_and_photos(build_examination_card(registration))
        self.assertEqual(card_field(text, 'Place of Birth'), 'بيروت')
        row = workbook_rows(build_children_workbook(
            Registration.objects.filter(pk=self.first_registration.pk),
        ))[0][1]
        self.assertEqual(row['Exceptional Exam - Place of Birth'], 'بيروت')

    def test_word_card_leaves_unrecorded_fields_blank_and_preserves_partial_birthdate(self):
        registration = Registration.objects.get(pk=self.second_registration.pk)
        text, photos = word_text_and_photos(build_examination_card(registration))
        for label in ('Date of Birth', 'Place of Birth', 'Nationality', 'Governorate', 'Physical difficulties'):
            with self.subTest(label=label):
                self.assertEqual(card_field(text, label), '')
        self.assertNotIn('Not recorded', text)
        self.assertNotIn('No', card_field(text, 'Physical difficulties'))
        self.assertNotIn(str(self.round.year), text)
        self.assertPhotoColour(photos[0], (0, 0, 255))
        self.second_child.birthday_year = '2015'
        self.second_child.birthday_month = None
        self.second_child.birthday_day = None
        self.second_child.save(update_fields=['birthday_year', 'birthday_month', 'birthday_day'])
        registration.refresh_from_db()
        text, _ = word_text_and_photos(build_examination_card(registration))
        self.assertEqual(card_field(text, 'Date of Birth'), '2015')

    def test_word_card_uses_arabic_and_legacy_fallbacks_and_only_selected_other_details(self):
        self.nationality.name = 'جنسية عربية مسجلة'
        self.nationality.name_en = None
        self.nationality.save(update_fields=['name', 'name_en'])
        self.disability.name = 'صعوبة مسجلة'
        self.disability.name_en = ''
        self.disability.save(update_fields=['name', 'name_en'])
        self.first_child.governorate = None
        self.first_child.save(update_fields=['governorate'])
        self.first_registration.refresh_from_db()
        text, _ = word_text_and_photos(build_examination_card(self.first_registration))
        self.assertEqual(card_field(text, 'Nationality'), self.nationality.name)
        self.assertEqual(card_field(text, 'Governorate'), self.first_child.governorate_legacy)
        self.assertEqual(card_field(text, 'Physical difficulties'), self.disability.name)
        self.disability.name_en = 'None'
        self.disability.save(update_fields=['name_en'])
        self.first_registration.refresh_from_db()
        text, _ = word_text_and_photos(build_examination_card(self.first_registration))
        self.assertEqual(card_field(text, 'Physical difficulties'), 'No')
        self.disability.name_en = 'Other'
        self.disability.save(update_fields=['name_en'])
        self.nationality.name_en = 'Other'
        self.nationality.save(update_fields=['name_en'])
        self.first_child.nationality_other = 'Registered other nationality'
        self.first_child.save(update_fields=['nationality_other'])
        self.first_registration.refresh_from_db()
        text, _ = word_text_and_photos(build_examination_card(self.first_registration))
        self.assertIn('Registered additional support need', card_field(text, 'Physical difficulties'))
        self.assertIn('Registered other nationality', card_field(text, 'Nationality'))

    def test_word_card_keeps_reference_print_size_border_floating_photo_and_arabic_direction(self):
        content = build_examination_card(Registration.objects.get(pk=self.first_registration.pk))
        with zipfile.ZipFile(io.BytesIO(content)) as archive:
            document = ElementTree.fromstring(archive.read('word/document.xml'))
        page = document.find('.//w:sectPr/w:pgSz', WORD_NS)
        namespace = '{%s}' % WORD_NS['w']
        self.assertEqual(page.get(namespace + 'orient'), 'landscape')
        self.assertAlmostEqual(int(page.get(namespace + 'w')), 210 / 25.4 * 1440, delta=2)
        self.assertAlmostEqual(int(page.get(namespace + 'h')), 148 / 25.4 * 1440, delta=2)
        borders = (
            document.findall('.//w:tblBorders', WORD_NS)
            + document.findall('.//w:pBdr', WORD_NS)
            + document.findall('.//w:pgBorders', WORD_NS)
        )
        self.assertTrue(any(
            all(border.find('w:' + side, WORD_NS) is not None for side in ('top', 'left', 'bottom', 'right'))
            for border in borders
        ))
        self.assertEqual(len(document.findall('.//{%s}anchor' % WORD_DRAWING_NS)), 1)
        heading = next(
            paragraph for paragraph in document.findall('.//w:p', WORD_NS)
            if CARD_HEADING in ''.join(value.text or '' for value in paragraph.findall('.//w:t', WORD_NS))
        )
        self.assertIsNotNone(heading.find('w:pPr/w:bidi', WORD_NS))
        self.assertIsNotNone(heading.find('.//w:rtl', WORD_NS))

    def test_word_card_embeds_editable_arabic_font_and_preserves_it_after_word_roundtrip(self):
        from docx import Document

        self.first_child.first_name = 'يوسف'
        self.first_child.father_name = 'أحمد'
        self.first_child.last_name = 'خليل'
        self.first_child.save(update_fields=['first_name', 'father_name', 'last_name'])
        content = build_examination_card(Registration.objects.get(pk=self.first_registration.pk))
        roundtrip = io.BytesIO()
        Document(io.BytesIO(content)).save(roundtrip)
        expected_font = Path(__file__).resolve().parents[1].joinpath(
            'fonts', 'NotoNaskhArabic-Bold.ttf',
        ).read_bytes()
        namespace = '{%s}' % WORD_NS['w']
        relationship_namespace = '{%s}' % DRAWING_NS['r']
        content_type_namespace = '{http://schemas.openxmlformats.org/package/2006/content-types}'

        for document_bytes in (content, roundtrip.getvalue()):
            with self.subTest(roundtrip=document_bytes is not content):
                with zipfile.ZipFile(io.BytesIO(document_bytes)) as archive:
                    font_table = ElementTree.fromstring(archive.read('word/fontTable.xml'))
                    font = next(
                        value for value in font_table.findall('w:font', WORD_NS)
                        if value.get(namespace + 'name') == ARABIC_CARD_FONT
                    )
                    embedding = font.find('w:embedBold', WORD_NS)
                    self.assertIsNotNone(embedding)
                    self.assertNotIn(embedding.get(namespace + 'subsetted'), ('1', 'true'))
                    relationships = ElementTree.fromstring(
                        archive.read('word/_rels/fontTable.xml.rels'),
                    )
                    relationship = next(
                        value for value in relationships.findall('{%s}Relationship' % RELATIONSHIP_NS)
                        if value.get('Id') == embedding.get(relationship_namespace + 'id')
                    )
                    self.assertEqual(
                        relationship.get('Type'), DRAWING_NS['r'] + '/font',
                    )
                    self.assertNotEqual(relationship.get('TargetMode'), 'External')
                    font_path = posixpath.normpath(posixpath.join('word', relationship.get('Target')))
                    self.assertTrue(font_path.startswith('word/fonts/'))
                    self.assertTrue(font_path.endswith('.odttf'))
                    font_bytes = archive.read(font_path)
                    key_bytes = UUID(embedding.get(namespace + 'fontKey')).bytes[::-1]
                    decoded_font = bytes(
                        value ^ key_bytes[index % 16] for index, value in enumerate(font_bytes[:32])
                    ) + font_bytes[32:]
                    self.assertEqual(decoded_font, expected_font)
                    content_types = ElementTree.fromstring(archive.read('[Content_Types].xml'))
                    font_content_type = next(
                        value for value in content_types.findall(content_type_namespace + 'Override')
                        if value.get('PartName') == '/' + font_path
                    )
                    self.assertEqual(
                        font_content_type.get('ContentType'),
                        'application/vnd.openxmlformats-officedocument.obfuscatedFont',
                    )
                    document = ElementTree.fromstring(archive.read('word/document.xml'))
                    for text in (CARD_HEADING, 'الاسم الثلاثي: يوسف أحمد خليل'):
                        paragraph = next(
                            value for value in document.findall('.//w:p', WORD_NS)
                            if ''.join(node.text or '' for node in value.findall('.//w:t', WORD_NS)) == text
                        )
                        self.assertIsNotNone(paragraph.find('w:pPr/w:bidi', WORD_NS))
                        self.assertIsNotNone(paragraph.find('.//w:rtl', WORD_NS))
                        fonts = paragraph.find('.//w:rFonts', WORD_NS)
                        self.assertEqual(fonts.get(namespace + 'cs'), font.get(namespace + 'name'))

    def test_excel_and_word_use_saved_edits_and_replacement_photo(self):
        self.first_child.first_name = 'Updated Rania'
        self.first_child.street = 'Updated registered street'
        self.first_child.birthday_day = '9'
        self.first_child.birthday_month = '11'
        self.first_child.birthday_year = '2016'
        self.first_child.save(update_fields=['first_name', 'street', 'birthday_day', 'birthday_month', 'birthday_year'])
        self.first_child.photo.save('replacement.png', ContentFile(portrait_bytes('green')))
        self.first_registration.nfe_programme = 'DIRASA'
        self.first_registration.save(update_fields=['nfe_programme'])
        current_registration = Registration.objects.get(pk=self.first_registration.pk)
        text, photos = word_text_and_photos(build_examination_card(current_registration))
        self.assertIn('Updated Rania', text)
        self.assertIn('9/11/16', text)
        self.assertNotIn('Updated registered street', text)
        self.assertNotIn('DIRASA', text)
        self.assertPhotoColour(photos[0], (0, 128, 0))
        content = build_children_workbook(Registration.objects.filter(pk=current_registration.pk))
        row_number, row = workbook_rows(content)[0]
        self.assertEqual(row['First name'], 'Updated Rania')
        self.assertEqual(row['Street (شارع)'], 'Updated registered street')
        self.assertEqual(row['Type of NFE Programme'], 'DIRASA')
        self.assertPhotoColour(workbook_photos_by_row(content)[row_number], (0, 128, 0))

    def test_document_generators_read_remote_photo_storage_without_path_or_url(self):
        self.first_registration.refresh_from_db()
        photo = self.first_registration.child.photo
        photo.storage = MemoryPhotoStorage(portrait_bytes('purple'))
        word_text, word_photos = word_text_and_photos(build_examination_card(self.first_registration))
        self.assertIn('Rania', word_text)
        self.assertPhotoColour(word_photos[0], (128, 0, 128))
        content = build_children_workbook([self.first_registration])
        number, row = workbook_rows(content)[0]
        self.assertEqual(row['Photograph status'], 'Photograph included')
        self.assertPhotoColour(workbook_photos_by_row(content)[number], (128, 0, 128))

    def test_both_background_excel_export_paths_work_without_legacy_sql_views_and_scope_records(self):
        for filtered in (True, False):
            with self.subTest(filtered=filtered):
                _, content = self.generate_export(self.center_user, filtered=filtered)
                rows = workbook_rows(content)
                self.assertEqual(
                    {row['Registration ID'] for _, row in rows}, {str(self.first_registration.pk)},
                )
                number, row = rows[0]
                self.assertEqual(row['First name'], 'Rania')
                self.assertPhotoColour(workbook_photos_by_row(content)[number], (255, 0, 0))

    def test_all_export_includes_historical_records_and_more_than_a_page_while_filters_are_optional(self):
        Registration.objects.bulk_create([
            Registration(child=self.first_child, partner=self.partner, center=self.center, round=self.round)
            for _ in range(105)
        ])
        _, content = self.generate_export(
            self.center_user, filters={'export_scope': 'all', 'child__first_name': 'Does not match'},
        )
        self.assertEqual(len(workbook_rows(content)), 106)
        _, content = self.generate_export(
            self.center_user, filters={'export_scope': 'filtered', 'child__first_name': 'Does not match'},
        )
        self.assertEqual(workbook_rows(content), [])

    def test_filtered_export_uses_list_round_scope_while_all_includes_historic_rounds(self):
        _, filtered_content = self.generate_export(
            self.partner_user, filters={'export_scope': 'filtered'},
        )
        self.assertEqual(
            {row['Registration ID'] for _, row in workbook_rows(filtered_content)},
            {str(self.second_registration.pk)},
        )
        _, all_content = self.generate_export(
            self.partner_user, filters={'export_scope': 'all'},
        )
        self.assertEqual(
            {row['Registration ID'] for _, row in workbook_rows(all_content)},
            {str(self.first_registration.pk), str(self.second_registration.pk)},
        )

    def test_partner_export_and_forged_filters_cannot_widen_access(self):
        _, content = self.generate_export(self.partner_user, filters={'export_scope': 'all'})
        self.assertEqual(
            {row['Registration ID'] for _, row in workbook_rows(content)},
            {str(self.first_registration.pk), str(self.second_registration.pk)},
        )
        for user, filters in (
            (self.center_user, {'center': str(self.outside_center.pk)}),
            (self.partner_user, {'partner': str(self.other_partner.pk)}),
        ):
            with self.subTest(username=user.username):
                _, content = self.generate_export(user, filters={'export_scope': 'filtered', **filters})
                self.assertEqual(workbook_rows(content), [])

    def test_csv_background_exports_keep_utf8_scope_ids_photo_references_and_literal_text(self):
        self.second_child.first_name = '=SUM(1,2)'
        self.second_child.street = 'شارع السجل المسجل'
        self.second_child.save(update_fields=['first_name', 'street'])
        for filtered in (True, False):
            with self.subTest(filtered=filtered):
                _, content = self.generate_export(
                    self.partner_user, filtered=filtered,
                    filters={'export_scope': 'filtered'}, file_format='csv',
                )
                self.assertTrue(content.startswith(b'\xef\xbb\xbf'))
                rows = list(csv.DictReader(io.StringIO(content.decode('utf-8-sig'))))
                expected_ids = {str(self.second_registration.pk)}
                if not filtered:
                    expected_ids.add(str(self.first_registration.pk))
                self.assertEqual({row['Registration ID'] for row in rows}, expected_ids)
                record = next(row for row in rows if row['Registration ID'] == str(self.second_registration.pk))
                self.assertEqual(record['Child ID'], str(self.second_child.pk))
                self.assertEqual(record['Photograph'], self.second_child.photo.name)
                self.assertEqual(record['First name'], "'=SUM(1,2)")
                self.assertEqual(record['Street (شارع)'], 'شارع السجل المسجل')
                self.assertEqual(record['Type of NFE Programme'], 'DIRASA')

    def test_export_remains_downloadable_when_push_notification_fails(self):
        export, content = self.generate_export(self.center_user, notification_error=True)
        self.assertEqual(export.status, 'done')
        self.assertTrue(export.file_url.rstrip('/').endswith('.xlsx'))
        self.assertEqual(len(workbook_rows(content)), 1)

    def test_card_endpoint_downloads_a_real_word_document_only_for_accessible_records(self):
        self.client.force_login(self.center_user)
        response = self.client.get(reverse('mscc:examination_card', args=[self.first_registration.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response['Content-Type'],
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        )
        self.assertIn('.docx', response['Content-Disposition'])
        content = b''.join(response.streaming_content) if response.streaming else response.content
        text, photos = word_text_and_photos(content)
        self.assertIn('Rania', text)
        self.assertPhotoColour(photos[0], (255, 0, 0))
        for pk in (self.second_registration.pk, self.outside_registration.pk, self.deleted_registration.pk):
            with self.subTest(registration=pk):
                self.assertEqual(
                    self.client.get(reverse('mscc:examination_card', args=[pk])).status_code, 404,
                )
        self.client.force_login(self.partner_user)
        self.assertEqual(
            self.client.get(reverse('mscc:examination_card', args=[self.second_registration.pk])).status_code,
            200,
        )
        self.assertEqual(
            self.client.get(reverse('mscc:examination_card', args=[self.outside_registration.pk])).status_code,
            404,
        )

    def test_unassigned_and_basic_users_cannot_start_exports_or_generate_cards(self):
        for user in (self.base_user, self.unassigned_user):
            self.client.force_login(user)
            with self.subTest(username=user.username):
                for name in ('mscc:export_list_background', 'mscc:export_list_async'):
                    with patch('student_registration.mscc.views.queue_filtered_mscc_export') as queue:
                        response = self.client.get(reverse(name), {'format': 'xlsx'})
                    self.assertEqual(response.status_code, 403)
                    queue.assert_not_called()
                response = self.client.get(
                    reverse('mscc:examination_card', args=[self.first_registration.pk]),
                )
                self.assertIn(response.status_code, (403, 404))
        self.assertFalse(ExportHistory.objects.exists())

    def test_photo_export_downloads_are_restricted_to_the_job_creator(self):
        filename = 'private_export.xlsx'
        url = reverse('mscc:export_download', args=[filename])
        export = ExportHistory.objects.create(
            created_by=self.center_user, export_type='NFR Sector List', file_format='xlsx',
            status='done', file_url=url,
        )
        self.client.force_login(self.partner_user)
        with patch('student_registration.mscc.views.ExportStorage') as storage:
            self.assertEqual(self.client.get(url).status_code, 404)
            storage.assert_not_called()
        self.client.force_login(self.center_user)
        with patch('student_registration.mscc.views.ExportStorage') as storage:
            storage.return_value.open.return_value = io.BytesIO(b'creator-owned-file')
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            content = b''.join(response.streaming_content) if response.streaming else response.content
            self.assertEqual(content, b'creator-owned-file')
        export.status = 'pending'
        export.save(update_fields=['status'])
        self.assertEqual(self.client.get(url).status_code, 404)

    def test_csv_download_alias_cannot_bypass_export_creator_check(self):
        filename = 'private_children.csv'
        canonical_url = reverse('mscc:export_download', args=[filename])
        alias_url = reverse('mscc:export_download_csv', args=[filename])
        ExportHistory.objects.create(
            created_by=self.center_user, export_type='NFR Sector List', file_format='csv',
            status='done', file_url=canonical_url,
        )
        self.client.force_login(self.partner_user)
        with patch('student_registration.mscc.views.ExportStorage') as storage:
            for url in (canonical_url, alias_url):
                with self.subTest(url=url):
                    self.assertEqual(self.client.get(url).status_code, 404)
            storage.assert_not_called()
        self.client.force_login(self.center_user)
        with patch('student_registration.mscc.views.ExportStorage') as storage:
            storage.return_value.open.return_value = io.BytesIO(b'owned-csv-file')
            response = self.client.get(alias_url)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response['Content-Type'], 'text/csv')
            self.assertEqual(b''.join(response.streaming_content), b'owned-csv-file')

    def test_anonymous_users_cannot_download_photo_exports_or_cards(self):
        self.client.logout()
        for url in (
            reverse('mscc:examination_card', args=[self.first_registration.pk]),
            reverse('mscc:export_list_background'),
            reverse('mscc:export_download', args=['private_export.xlsx']),
        ):
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 302)
