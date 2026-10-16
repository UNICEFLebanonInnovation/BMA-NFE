"""Exercise exceptional-exam data, document choices and registration access."""

import csv
import io
import tempfile
from datetime import date, datetime, timedelta, timezone as datetime_timezone
from unittest.mock import patch

from PIL import Image

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.db import IntegrityError, transaction
from django.test import SimpleTestCase, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone, translation

from student_registration.child.models import Child
from student_registration.locations.models import Center, Location, LocationType
from student_registration.mscc.exceptional_exam_choices import (
    GRADE_CHOICES,
    LANGUAGE_EXAM_CHOICES,
    MATH_LANGUAGE_CHOICES,
    PROGRAMME_CHOICES,
    RESIDENCE_CATALOG,
    district_choices,
    residence_labels,
    town_choices,
    valid_residence,
)
from student_registration.mscc.exceptional_exam_forms import ExceptionalExamForm
from student_registration.mscc.exceptional_exam_grades import (
    completed_age, programme_grade_choices,
)
from student_registration.mscc.document_exports import build_children_csv, build_children_workbook
from student_registration.mscc.models import ExceptionalExam, Registration, Round
from student_registration.mscc.tests.test_document_exports import (
    portrait_bytes, workbook_photos_by_row, workbook_rows,
)
from student_registration.schools.models import PartnerOrganization
from student_registration.students.models import Nationality


REQUIRED_FIELDS = (
    'governorate', 'district', 'nearest_town', 'programme', 'grade',
    'math_language', 'language_exam',
)

# An independent transcription of the attached document's residence table.
# Repeated towns intentionally remain in their original parent districts.
DOCUMENT_RESIDENCES = (
    ('بيروت', 'بيروت', 'الأشرفية، المصيطبة، رأس بيروت، المزرعة، المدور، ميناء الحصن، زقاق البلاط'),
    ('جبل لبنان', 'بعبدا', 'بعبدا، الحدث، الحازمية، الشياح، فرن الشباك، كفرشيما، عاليه'),
    ('جبل لبنان', 'المتن', 'الجديدة، البوشرية، سد البوشرية، برج حمود، أنطلياس، جل الديب، بكفيا، برمانا'),
    ('جبل لبنان', 'كسروان', 'جونية، غزير، ذوق مكايل، ذوق مصبح، عجلتون، فاريا'),
    ('جبل لبنان', 'جبيل', 'جبيل، عمشيت، حالات، قرطبا، لاسا'),
    ('جبل لبنان', 'عاليه', 'عاليه، بحمدون، سوق الغرب، عرمون، بشامون، شويفات'),
    ('جبل لبنان', 'الشوف', 'بيت الدين، دير القمر، بعقلين، المختارة، برجا، شحيم، الدامور'),
    ('الشمال', 'طرابلس', 'طرابلس، الميناء، القبة، أبي سمراء، التبانة'),
    ('الشمال', 'المنية–الضنية', 'المنية، بحنين، دير عمار، سير الضنية، بخعون'),
    ('الشمال', 'زغرتا', 'زغرتا، إهدن، رشعين'),
    ('الشمال', 'الكورة', 'أميون، أنفه، كوسبا، كفرعقا'),
    ('الشمال', 'بشري', 'بشري، حدث الجبة، بقاعكفرا'),
    ('الشمال', 'البترون', 'البترون، شكا، تنورين، كفرعبيدا'),
    ('عكار', 'عكار', 'حلبا، القبيات، ببنين، العبدة، وادي خالد، برقايل، مشمش'),
    ('البقاع', 'زحلة', 'زحلة، تعنايل، شتورا، قب إلياس، بر الياس، مجدل عنجر'),
    ('البقاع', 'البقاع الغربي', 'جب جنين، القرعون، مشغرة، سحمر، غزة'),
    ('البقاع', 'راشيا', 'راشيا، كفرمشكي، بكا'),
    ('بعلبك–الهرمل', 'بعلبك', 'بعلبك، دورس، عرسال، اللبوة، النبي شيت، شمسطار'),
    ('بعلبك–الهرمل', 'الهرمل', 'الهرمل، القصر'),
    ('الجنوب', 'صيدا', 'صيدا، عبرا، الهلالية، مغدوشة، الغازية'),
    ('الجنوب', 'صور', 'صور، العباسية، برج الشمالي، قانا، جويا، الناقورة'),
    ('الجنوب', 'جزين', 'جزين، بكاسين، لبعا'),
    ('النبطية', 'النبطية', 'النبطية، كفررمان، حبوش، الدوير'),
    ('النبطية', 'بنت جبيل', 'بنت جبيل، تبنين، عيناتا، عيترون، رميش'),
    ('النبطية', 'مرجعيون', 'مرجعيون، الخيام، كفركلا، العديسة، القليعة'),
    ('النبطية', 'حاصبيا', 'حاصبيا، شبعا، كفرشوبا، الهبارية'),
)


def arabic_part(label):
    return str(label).partition(' / ')[2]


class ExceptionalExamResidenceCatalogTests(SimpleTestCase):
    def test_all_residence_rows_match_the_supplied_document(self):
        rows = []
        for governorate in RESIDENCE_CATALOG.values():
            for district in governorate['districts'].values():
                rows.append((
                    arabic_part(governorate['label']),
                    arabic_part(district['label']),
                    '، '.join(arabic_part(label) for _, label in district['towns']),
                ))
        self.assertEqual(rows, list(DOCUMENT_RESIDENCES))
        self.assertEqual(len(RESIDENCE_CATALOG), 8)

    def test_source_residence_labels_preserve_the_supplied_arabic_and_english(self):
        choices = []
        for code, governorate in RESIDENCE_CATALOG.items():
            choices.append((code, governorate['label']))
            for district_code, district in governorate['districts'].items():
                choices.append((district_code, district['label']))
                choices.extend(district['towns'])
        for code, label in choices:
            with self.subTest(code=code, label=label):
                self.assertRegex(str(label), '[A-Za-z]')
                self.assertRegex(str(label), '[\u0600-\u06ff]')
                self.assertIn(' / ', str(label))

    def test_programme_grade_and_language_choices_follow_the_active_language(self):
        expected = {
            'en': ('Basic Literacy and Numeracy (BLN)', 'Grade 2', 'Arabic', 'English'),
            'ar': (
                'برنامج المهارات الأساسية في القراءة والكتابة والحساب (BLN)',
                'الصف الثاني', 'اللغة العربية', 'الانكليزية',
            ),
        }
        choices = (PROGRAMME_CHOICES, GRADE_CHOICES, MATH_LANGUAGE_CHOICES, LANGUAGE_EXAM_CHOICES)
        for language, labels in expected.items():
            with self.subTest(language=language), translation.override(language):
                self.assertEqual(tuple(str(values[0][1]) for values in choices), labels)
                for values in choices:
                    for code, label in values:
                        self.assertNotIn(' / ', str(label))

    def test_cascade_rejects_unknown_or_wrong_parent_selections(self):
        self.assertEqual(district_choices('unknown'), ())
        self.assertEqual(town_choices('beirut', 'baabda'), ())
        self.assertFalse(valid_residence('beirut', 'beirut', 'baabda'))
        self.assertFalse(valid_residence('beirut', 'baabda', 'aley'))
        self.assertTrue(valid_residence('mount_lebanon', 'baabda', 'aley'))
        self.assertTrue(valid_residence('mount_lebanon', 'aley', 'aley'))
        with translation.override('en'):
            self.assertEqual(residence_labels('beirut', 'baabda', 'aley'), ('Beirut', '', ''))


class ExceptionalExamAgeGradeTests(SimpleTestCase):
    today = date(2026, 10, 13)

    def child_with_birthdate(self, year, month='1', day='1'):
        return Child(birthday_year=str(year), birthday_month=str(month), birthday_day=str(day))

    def grade_codes(self, programme, child):
        return tuple(value for value, _ in programme_grade_choices(programme, child, on_date=self.today))

    def test_bln_mapping_uses_completed_age_and_never_offers_grade_seven(self):
        for age, grade in ((7, '2'), (8, '2'), (9, '3'), (10, '4'), (11, '5'),
                           (12, '6'), (13, '6'), (14, '6')):
            with self.subTest(age=age):
                child = self.child_with_birthdate(self.today.year - age)
                self.assertEqual(completed_age(child, on_date=self.today), age)
                self.assertEqual(self.grade_codes('BLN', child), (grade,))

    def test_birthday_boundary_changes_the_grade_on_the_ninth_birthday(self):
        child = self.child_with_birthdate(2017, 10, 14)
        self.assertEqual(completed_age(child, on_date=self.today), 8)
        self.assertEqual(self.grade_codes('BLN', child), ('2',))
        birthday = self.today + timedelta(days=1)
        self.assertEqual(completed_age(child, on_date=birthday), 9)
        self.assertEqual(
            tuple(code for code, _ in programme_grade_choices('BLN', child, on_date=birthday)),
            ('3',),
        )

    def test_bln_requires_a_complete_valid_nonfuture_birthdate(self):
        birthdates = (
            ('', '', ''), ('2018', '', '1'), ('2018', '1', ''), ('', '1', '1'),
            ('unknown', '1', '1'), ('2018', '13', '1'), ('2018', '2', '30'),
            ('2018', '2', '29'), ('2018', '1', '0'), ('2026', '10', '14'),
        )
        for year, month, day in birthdates:
            with self.subTest(birthdate=(year, month, day)):
                child = self.child_with_birthdate(year, month, day)
                self.assertIsNone(completed_age(child, on_date=self.today))
                self.assertEqual(self.grade_codes('BLN', child), ())
        self.assertEqual(self.grade_codes('BLN', None), ())

    def test_bln_has_no_allowed_grade_outside_ages_seven_through_fourteen(self):
        for age in (0, 6, 15, 18):
            with self.subTest(age=age):
                child = self.child_with_birthdate(self.today.year - age)
                self.assertEqual(completed_age(child, on_date=self.today), age)
                self.assertEqual(self.grade_codes('BLN', child), ())

    def test_dirasa_retains_all_grades_regardless_of_age_or_birthdate(self):
        children = (
            None, self.child_with_birthdate('', '', ''),
            self.child_with_birthdate(2020), self.child_with_birthdate(2008),
            self.child_with_birthdate(2018, 2, 30),
        )
        for child in children:
            with self.subTest(child=child):
                self.assertEqual(self.grade_codes('DIRASA', child), ('2', '3', '4', '5', '6', '7'))

    @override_settings(USE_TZ=False)
    def test_default_age_calculation_accepts_the_projects_naive_clock(self):
        child = self.child_with_birthdate(2017, 10, 13)
        with patch('student_registration.mscc.exceptional_exam_grades.timezone.now',
                   return_value=datetime(2026, 10, 13, 0, 1)):
            self.assertEqual(completed_age(child), 9)
            self.assertEqual(tuple(code for code, _ in programme_grade_choices('BLN', child)), ('3',))

    @override_settings(USE_TZ=True, TIME_ZONE='Asia/Beirut')
    def test_default_age_calculation_uses_local_date_at_the_birthday_boundary(self):
        child = self.child_with_birthdate(2017, 10, 13)
        utc_now = datetime(2026, 10, 12, 22, 1, tzinfo=datetime_timezone.utc)
        with timezone.override('Asia/Beirut'), patch(
            'student_registration.mscc.exceptional_exam_grades.timezone.now', return_value=utc_now,
        ):
            self.assertEqual(completed_age(child), 9)
            self.assertEqual(tuple(code for code, _ in programme_grade_choices('BLN', child)), ('3',))


@override_settings(LANGUAGE_CODE='en')
class ExceptionalExamWorkflowTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        for pk, name in ((1, 'Governorate'), (2, 'District'), (3, 'Cadaster')):
            LocationType.objects.create(pk=pk, name=name)
        cls.governorate = Location.objects.create(
            name='بيروت', name_en='Beirut', type_id=1,
        )
        cls.district = Location.objects.create(
            name='بيروت', name_en='Beirut', type_id=2, parent=cls.governorate,
        )
        cls.other_governorate = Location.objects.create(
            name='جبل لبنان', name_en='Mount Lebanon', type_id=1,
        )
        cls.baabda = Location.objects.create(
            name='بعبدا', name_en='Baabda', type_id=2, parent=cls.other_governorate,
        )
        cls.keserwan = Location.objects.create(
            name='كسروان', name_en='Keserwan', type_id=2, parent=cls.other_governorate,
        )
        cls.aley = Location.objects.create(
            name='عاليه', name_en='Aley', type_id=2, parent=cls.other_governorate,
        )
        cls.cadaster = Location.objects.create(
            name='الأشرفية', name_en='Achrafieh', type_id=3, parent=cls.district,
        )
        cls.partner = PartnerOrganization.objects.create(name='Exam partner')
        cls.other_partner = PartnerOrganization.objects.create(name='Outside exam partner')
        cls.center = Center.objects.create(name='Assigned exam centre', partner=cls.partner)
        cls.second_center = Center.objects.create(name='Other partner centre', partner=cls.partner)
        cls.outside_center = Center.objects.create(name='Outside centre', partner=cls.other_partner)
        cls.nationality = Nationality.objects.create(name='Test nationality', name_en='Test nationality')
        cls.child = Child.objects.create(
            first_name='Rania', father_name='Samir', last_name='Example',
            mother_fullname='Mother of Rania', gender='Female', nationality=cls.nationality,
            birthday_year=str(date.today().year - 8), birthday_month='1', birthday_day='1',
            first_phone_number='70-123456', street='Original residential street',
            governorate=cls.governorate, district=cls.district,
        )
        cls.round = Round.objects.create(name='Exam registration round', year=2026, current_year=True)
        cls.other_round = Round.objects.create(name='Previous registration round', year=2025)
        cls.registration = Registration.objects.create(
            child=cls.child, partner=cls.partner, center=cls.center, round=cls.round,
            nfe_programme='BLN', source_of_identification='Other Sources',
        )
        cls.second_registration = Registration.objects.create(
            child=Child.objects.create(first_name='Second', last_name='Child'),
            partner=cls.partner, center=cls.second_center, nfe_programme='DIRASA',
        )
        cls.outside_registration = Registration.objects.create(
            child=Child.objects.create(first_name='Outside', last_name='Child'),
            partner=cls.other_partner, center=cls.outside_center, nfe_programme='DIRASA',
        )
        cls.deleted_registration = Registration.objects.create(
            child=cls.child, partner=cls.partner, center=cls.center, deleted=True,
        )
        cls.childless_registration = Registration.objects.create(
            child=None, partner=cls.partner, center=cls.center,
        )
        cls.center_user = cls.make_user('exam-centre', ['MSCC', 'MSCC_CENTER'], center=cls.center)
        cls.other_editor = cls.make_user('exam-second-editor', ['MSCC', 'MSCC_CENTER'], center=cls.center)
        cls.unicef_user = cls.make_user('exam-unicef', ['MSCC', 'MSCC_UNICEF'])
        cls.partner_user = cls.make_user('exam-partner', ['MSCC', 'MSCC_PARTNER'], partner=cls.partner)
        cls.unassigned_user = cls.make_user('exam-unassigned', ['MSCC'])
        cls.unassigned_center_user = cls.make_user('exam-unassigned-centre', ['MSCC', 'MSCC_CENTER'])
        cls.alp_user = cls.make_user('exam-alp-only', ['ALP'], center=cls.center)
        cls.staff_user = cls.make_user('exam-staff', [], is_staff=True)
        cls.super_user = cls.make_user('exam-superuser', [], is_superuser=True)
        cls.unicef_center_user = cls.make_user(
            'exam-unicef-centre', ['MSCC', 'MSCC_UNICEF', 'MSCC_CENTER'], center=cls.center,
        )
        cls.partner_center_user = cls.make_user(
            'exam-partner-centre', ['MSCC', 'MSCC_PARTNER', 'MSCC_CENTER'],
            center=cls.center, partner=cls.partner,
        )

    @staticmethod
    def make_user(username, groups, **fields):
        user = get_user_model().objects.create_user(username=username, **fields)
        user.groups.add(*(Group.objects.get_or_create(name=name)[0] for name in groups))
        return user

    def setUp(self):
        translation.activate('en')
        self.addCleanup(translation.deactivate)
        self.client.force_login(self.center_user)

    def set_language(self, language):
        self.client.cookies[settings.LANGUAGE_COOKIE_NAME] = language

    def exam_url(self, registration=None):
        return reverse('mscc:exceptional_exam_form', args=[(registration or self.registration).pk])

    def exam_data(self, **updates):
        data = {
            'governorate': self.governorate.pk, 'district': self.district.pk,
            'nearest_town': 'achrafieh',
            'programme': 'BLN', 'grade': '2', 'math_language': 'ar', 'language_exam': 'en',
        }
        data.update(updates)
        return data

    def set_child_age(self, age):
        self.child.birthday_year = str(date.today().year - age)
        self.child.birthday_month = '1'
        self.child.birthday_day = '1'
        self.child.save(update_fields=('birthday_year', 'birthday_month', 'birthday_day'))
        self.registration.child = self.child

    def create_exam(self, registration=None, **updates):
        data = self.exam_data(**updates)
        for field in ('governorate', 'district'):
            data[field + '_id'] = data.pop(field)
        return ExceptionalExam.objects.create(
            registration=registration or self.registration,
            created_by=self.center_user, modified_by=self.center_user,
            **data,
        )

    def test_get_prefills_programme_and_shows_required_questions_in_english(self):
        response = self.client.get(self.exam_url())
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertEqual(form['programme'].value(), 'BLN')
        self.assertEqual(form['grade'].value(), '2')
        self.assertEqual(tuple(value for value, _ in form.fields['grade'].choices if value), ('2',))
        self.assertEqual(
            tuple(option['id'] for option in form.grade_choices_by_programme['BLN']), ('2',),
        )
        self.assertEqual(
            tuple(option['id'] for option in form.grade_choices_by_programme['DIRASA']),
            ('2', '3', '4', '5', '6', '7'),
        )
        self.assertEqual(form['governorate'].value(), self.governorate.pk)
        self.assertEqual(form['district'].value(), self.district.pk)
        self.assertEqual(set(form.fields), set(REQUIRED_FIELDS))
        for field in form.fields.values():
            self.assertTrue(field.required)
            self.assertRegex(str(field.label), '[A-Za-z]')
            self.assertNotRegex(str(field.label), '[\u0600-\u06ff]')
        self.assertFalse(ExceptionalExam.objects.exists())

    def test_form_labels_help_and_options_follow_the_selected_ui_language(self):
        expected = {
            'en': {
                'labels': (
                    'Governorate', 'District/Caza', 'Village',
                    'Non-formal education programme', 'Grade applying for the examination',
                    'Mathematics examination language', 'Language examination',
                ),
                'help': (
                    'Required', 'Select a governorate first.', 'Select a district first.',
                    'Required', "For BLN, the grade is determined by the child's current age.",
                    'Required', 'Required',
                ),
                'prompt': 'Select an option',
                'options': ('Beirut', 'Achrafieh', 'Basic Literacy and Numeracy (BLN)', 'Grade 2', 'Arabic', 'English'),
                'title': 'Exceptional Exam',
                'instructions': 'All questions are required.',
            },
            'ar': {
                'labels': (
                    'المحافظة', 'القضاء', 'القرية', 'البرنامج التعليمي غير النظامي',
                    'الصف الدراسي الذي يتقدم للامتحان له', 'لغة امتحان الرياضيات', 'امتحان اللغة',
                ),
                'help': (
                    'مطلوب', 'اختر المحافظة أولاً.', 'اختر القضاء أولاً.',
                    'مطلوب', 'يُحدَّد الصف في برنامج المهارات الأساسية في القراءة والكتابة والحساب بحسب عمر الطفل الحالي.',
                    'مطلوب', 'مطلوب',
                ),
                'prompt': 'اختر خياراً',
                'options': (
                    'بيروت', 'الأشرفية', 'برنامج المهارات الأساسية في القراءة والكتابة والحساب (BLN)',
                    'الصف الثاني', 'اللغة العربية', 'الانكليزية',
                ),
                'title': 'الامتحان الاستثنائي',
                'instructions': 'جميع الأسئلة مطلوبة.',
            },
        }
        for language, values in expected.items():
            with self.subTest(language=language):
                self.set_language(language)
                response = self.client.get(self.exam_url(), HTTP_ACCEPT_LANGUAGE='ar' if language == 'en' else 'en')
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response['Content-Language'], language)
                with translation.override(language):
                    form = response.context['form']
                    self.assertEqual(tuple(str(form.fields[name].label) for name in REQUIRED_FIELDS), values['labels'])
                    self.assertEqual(tuple(str(form.fields[name].help_text) for name in REQUIRED_FIELDS), values['help'])
                    self.assertEqual(str(form.fields['governorate'].empty_label), values['prompt'])
                    displayed = (
                        form.fields['governorate'].label_from_instance(self.governorate),
                        dict(form.fields['nearest_town'].choices)['achrafieh'],
                        dict(form.fields['programme'].choices)['BLN'],
                        dict(form.fields['grade'].choices)['2'],
                        dict(form.fields['math_language'].choices)['ar'],
                        dict(form.fields['language_exam'].choices)['en'],
                    )
                    self.assertEqual(tuple(str(label) for label in displayed), values['options'])
                    for field in form.fields.values():
                        for _, label in field.choices:
                            self.assertNotIn(' / ', str(label))
                for text in values['labels'] + values['options'] + (values['title'], values['instructions']):
                    self.assertContains(response, text)
                self.assertNotContains(response, 'Exceptional Exam /')
                self.assertNotContains(response, 'Grade 2 /')

    def test_accept_language_selects_arabic_when_no_language_cookie_is_set(self):
        self.client.cookies.pop(settings.LANGUAGE_COOKIE_NAME, None)
        response = self.client.get(self.exam_url(), HTTP_ACCEPT_LANGUAGE='ar')
        self.assertEqual(response['Content-Language'], 'ar')
        self.assertContains(response, 'الامتحان الاستثنائي')
        self.assertContains(response, 'الصف الثاني')
        self.assertNotContains(response, 'Grade 2 /')

    def test_required_and_invalid_choice_errors_follow_the_ui_language(self):
        expected = {
            'en': ('This field is required.', 'Select a valid option.'),
            'ar': ('هذا الحقل مطلوب.', 'اختر خياراً صالحاً.'),
        }
        for language, (required_message, invalid_message) in expected.items():
            self.set_language(language)
            for field, value, message in (
                ('math_language', '', required_message),
                ('programme', 'ALP', invalid_message),
            ):
                with self.subTest(language=language, field=field):
                    response = self.client.post(self.exam_url(), self.exam_data(**{field: value}))
                    self.assertEqual(response.status_code, 200)
                    with translation.override(language):
                        self.assertEqual(list(response.context['form'].errors[field]), [message])
                    self.assertContains(response, message)
                    self.assertNotContains(response, 'This field is required. /')
                    self.assertNotContains(response, 'Select a valid option. /')
        self.assertFalse(ExceptionalExam.objects.exists())

    def test_changing_ui_language_does_not_change_saved_answer_codes_or_location_ids(self):
        for language in ('ar', 'en'):
            with self.subTest(language=language):
                self.set_language(language)
                response = self.client.post(self.exam_url(), self.exam_data())
                self.assertEqual(response.status_code, 302)
                exam = ExceptionalExam.objects.get(registration=self.registration)
                self.assertEqual((exam.governorate_id, exam.district_id), (self.governorate.pk, self.district.pk))
                self.assertEqual(
                    (exam.nearest_town, exam.programme, exam.grade, exam.math_language, exam.language_exam),
                    ('achrafieh', 'BLN', '2', 'ar', 'en'),
                )
                response = self.client.get(self.exam_url())
                self.assertEqual(response.context['form']['grade'].value(), '2')
        self.assertEqual(ExceptionalExam.objects.count(), 1)

    def test_bln_form_offers_and_accepts_only_the_grade_allowed_for_the_registered_child(self):
        for age, grade in ((7, '2'), (8, '2'), (9, '3'), (10, '4'), (11, '5'),
                           (12, '6'), (13, '6'), (14, '6')):
            self.set_child_age(age)
            with self.subTest(age=age, grade=grade):
                form = ExceptionalExamForm(
                    data=self.exam_data(grade=grade), registration=self.registration,
                )
                self.assertEqual(
                    tuple(value for value, _ in form.fields['grade'].choices if value), (grade,),
                )
                self.assertTrue(form.is_valid(), form.errors.as_json())
                for wrong_grade in {'2', '3', '4', '5', '6', '7'} - {grade}:
                    rejected = ExceptionalExamForm(
                        data=self.exam_data(grade=wrong_grade), registration=self.registration,
                    )
                    self.assertFalse(rejected.is_valid())
                    self.assertIn('grade', rejected.errors)

    def test_dirasa_forms_allow_every_grade_from_two_through_seven(self):
        for grade in range(2, 8):
            with self.subTest(grade=grade):
                form = ExceptionalExamForm(
                    data=self.exam_data(programme='DIRASA', grade=str(grade)),
                    registration=self.registration,
                )
                self.assertTrue(form.is_valid(), form.errors.as_json())
                self.assertEqual(
                    {value for value, _ in form.fields['grade'].choices if value},
                    {'2', '3', '4', '5', '6', '7'},
                )

    def test_bln_cannot_be_submitted_without_an_eligible_registered_birthdate(self):
        for year, month, day in (
            ('', '', ''), ('2018', '', '1'), ('2018', '2', '30'),
            (str(date.today().year + 1), '1', '1'),
            (str(date.today().year - 6), '1', '1'),
            (str(date.today().year - 15), '1', '1'),
        ):
            with self.subTest(birthdate=(year, month, day)):
                self.child.birthday_year, self.child.birthday_month, self.child.birthday_day = year, month, day
                self.child.save(update_fields=('birthday_year', 'birthday_month', 'birthday_day'))
                response = self.client.post(self.exam_url(), self.exam_data())
                self.assertEqual(response.status_code, 200)
                form = response.context['form']
                self.assertEqual(tuple(value for value, _ in form.fields['grade'].choices if value), ())
                self.assertIn('grade', form.errors)
                self.assertFalse(ExceptionalExam.objects.exists())

    def test_dirasa_can_be_saved_with_missing_birthdate_or_an_age_outside_bln_range(self):
        for year, month, day in (
            ('', '', ''), (str(date.today().year - 6), '1', '1'),
            (str(date.today().year - 15), '1', '1'),
        ):
            with self.subTest(birthdate=(year, month, day)):
                self.child.birthday_year, self.child.birthday_month, self.child.birthday_day = year, month, day
                self.child.save(update_fields=('birthday_year', 'birthday_month', 'birthday_day'))
                response = self.client.post(self.exam_url(), self.exam_data(programme='DIRASA', grade='7'))
                self.assertEqual(response.status_code, 302)
                exam = ExceptionalExam.objects.get(registration=self.registration)
                self.assertEqual((exam.programme, exam.grade), ('DIRASA', '7'))

    def test_posted_age_birthdate_child_and_registration_cannot_override_the_registered_age(self):
        response = self.client.post(self.exam_url(), self.exam_data(
            grade='3', age='9', child=str(self.second_registration.child_id),
            registration=str(self.second_registration.pk),
            birthday_year=str(date.today().year - 9), birthday_month='1', birthday_day='1',
        ))
        self.assertEqual(response.status_code, 200)
        self.assertIn('grade', response.context['form'].errors)
        self.assertFalse(ExceptionalExam.objects.exists())
        self.child.refresh_from_db()
        self.assertEqual(self.child.birthday_year, str(date.today().year - 8))

    def test_bln_without_a_registration_cannot_accept_a_grade(self):
        form = ExceptionalExamForm(data=self.exam_data())
        self.assertEqual(tuple(value for value, _ in form.fields['grade'].choices if value), ())
        self.assertFalse(form.is_valid())
        self.assertIn('grade', form.errors)

    def test_missing_required_answers_do_not_create_an_exam(self):
        for field in REQUIRED_FIELDS:
            with self.subTest(field=field):
                data = self.exam_data()
                del data[field]
                response = self.client.post(self.exam_url(), data)
                self.assertEqual(response.status_code, 200)
                self.assertIn(field, response.context['form'].errors)
                self.assertFalse(ExceptionalExam.objects.exists())

    def test_invalid_choices_and_wrong_residence_parents_are_rejected(self):
        invalid_choices = (
            ('governorate', 'unknown'), ('governorate', 999999999),
            ('governorate', self.district.pk), ('governorate', self.cadaster.pk),
            ('district', 'unknown'), ('district', 999999999),
            ('district', self.governorate.pk), ('district', self.cadaster.pk),
            ('district', self.baabda.pk),
            ('nearest_town', 'jounieh'), ('nearest_town', 'unknown'),
            ('programme', 'ALP'), ('grade', '1'), ('grade', '8'),
            ('math_language', 'de'), ('language_exam', 'ar'),
        )
        for field, value in invalid_choices:
            with self.subTest(field=field, value=value):
                response = self.client.post(self.exam_url(), self.exam_data(**{field: value}))
                self.assertEqual(response.status_code, 200)
                self.assertIn(field, response.context['form'].errors)
                self.assertFalse(ExceptionalExam.objects.exists())

    def test_math_language_accepts_arabic_english_and_french(self):
        for language in ('ar', 'en', 'fr'):
            with self.subTest(language=language):
                form = ExceptionalExamForm(registration=self.registration, data=self.exam_data(math_language=language))
                self.assertTrue(form.is_valid(), form.errors.as_json())

    def test_residence_fields_use_typed_location_records_and_english_labels(self):
        form = ExceptionalExamForm(registration=self.registration)
        self.assertEqual(
            set(form.fields['governorate'].queryset.values_list('pk', flat=True)),
            {self.governorate.pk, self.other_governorate.pk},
        )
        self.assertEqual(
            set(form.fields['district'].queryset.values_list('pk', flat=True)),
            {self.district.pk},
        )
        self.assertEqual(form.fields['governorate'].label_from_instance(self.governorate), 'Beirut')
        self.assertEqual(form.fields['district'].label_from_instance(self.district), 'Beirut')
        self.assertEqual(str(form.fields['nearest_town'].label), 'Village')

    def test_changing_governorate_requires_a_new_district_and_village(self):
        for updates, expected in (
            ({'governorate': self.other_governorate.pk}, 'district'),
            ({'governorate': self.other_governorate.pk, 'district': self.baabda.pk}, 'nearest_town'),
        ):
            with self.subTest(updates=updates):
                form = ExceptionalExamForm(registration=self.registration, data=self.exam_data(**updates))
                self.assertFalse(form.is_valid())
                self.assertIn(expected, form.errors)

    def test_repeated_document_villages_are_valid_only_in_their_document_districts(self):
        for district in (self.baabda, self.aley):
            with self.subTest(district=district.pk):
                form = ExceptionalExamForm(registration=self.registration, data=self.exam_data(
                    governorate=self.other_governorate.pk,
                    district=district.pk, nearest_town='aley',
                ))
                self.assertTrue(form.is_valid(), form.errors.as_json())
        form = ExceptionalExamForm(registration=self.registration, data=self.exam_data(
            governorate=self.other_governorate.pk,
            district=self.keserwan.pk, nearest_town='aley',
        ))
        self.assertFalse(form.is_valid())
        self.assertIn('nearest_town', form.errors)

    def test_district_options_use_existing_location_ids_and_correct_parent(self):
        url = reverse('mscc:exceptional_exam_location_options')
        response = self.client.get(url, {'type': '2', 'parent': self.other_governorate.pk})
        self.assertEqual(response.status_code, 200)
        results = response.json()['results']
        self.assertEqual({row['id'] for row in results}, {self.baabda.pk, self.keserwan.pk, self.aley.pk})
        self.assertIn({'id': self.keserwan.pk, 'text': 'Keserwan'}, results)
        self.assertNotIn(self.district.pk, {row['id'] for row in results})

    def test_village_options_follow_the_selected_existing_district(self):
        url = reverse('mscc:exceptional_exam_location_options')
        response = self.client.get(url, {'type': 'village', 'parent': self.keserwan.pk})
        self.assertEqual(response.status_code, 200)
        results = response.json()['results']
        self.assertIn({'id': 'jounieh', 'text': 'Jounieh'}, results)
        self.assertNotIn('achrafieh', {row['id'] for row in results})
        self.assertEqual(len(results), 6)

    def test_linked_dropdown_ajax_uses_the_selected_language_and_keeps_option_ids(self):
        url = reverse('mscc:exceptional_exam_location_options')
        for language, district_text, village_text in (
            ('en', 'Keserwan', 'Jounieh'),
            ('ar', 'كسروان', 'جونية'),
        ):
            with self.subTest(language=language):
                self.set_language(language)
                district_response = self.client.get(url, {'type': '2', 'parent': self.other_governorate.pk})
                village_response = self.client.get(url, {'type': 'village', 'parent': self.keserwan.pk})
                self.assertEqual(district_response.status_code, 200)
                self.assertEqual(village_response.status_code, 200)
                districts = district_response.json()['results']
                villages = village_response.json()['results']
                self.assertIn({'id': self.keserwan.pk, 'text': district_text}, districts)
                self.assertIn({'id': 'jounieh', 'text': village_text}, villages)
                self.assertEqual({row['id'] for row in districts}, {self.baabda.pk, self.keserwan.pk, self.aley.pk})
                self.assertEqual({row['id'] for row in villages}, {'jounieh', 'ghazir', 'zouk_mikael', 'zouk_mosbeh', 'ajaltoun', 'faraya'})
                self.assertTrue(all(' / ' not in row['text'] for row in districts + villages))

    def test_options_reject_malformed_missing_and_wrong_type_parents(self):
        url = reverse('mscc:exceptional_exam_location_options')
        for kind, parent in (
            ('2', 'not-an-id'), ('2', 999999999),
            ('2', self.district.pk), ('2', self.cadaster.pk),
            ('village', 'not-an-id'), ('village', 999999999),
            ('village', self.governorate.pk), ('village', self.cadaster.pk),
            ('unknown', self.governorate.pk),
        ):
            with self.subTest(kind=kind, parent=parent):
                response = self.client.get(url, {'type': kind, 'parent': parent})
                self.assertEqual(response.status_code, 400)
                self.assertIn('error', response.json())
        for kind in ('2', 'village'):
            response = self.client.get(url, {'type': kind})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()['results'], [])

    def test_options_require_mscc_scope(self):
        url = reverse('mscc:exceptional_exam_location_options')
        self.client.logout()
        self.assertEqual(self.client.get(url, {'type': '2', 'parent': self.governorate.pk}).status_code, 302)
        for user in (self.alp_user, self.unassigned_user, self.unassigned_center_user):
            self.client.force_login(user)
            with self.subTest(user=user.username):
                response = self.client.get(url, {'type': '2', 'parent': self.governorate.pk})
                self.assertEqual(response.status_code, 403)

    def test_registered_location_ids_prefill_without_matching_catalogue_codes(self):
        governorate = Location.objects.create(name='المحافظة المسجلة', name_en='Registered governorate', type_id=1)
        district = Location.objects.create(
            name='القضاء المسجل', name_en='Registered district', type_id=2, parent=governorate,
        )
        self.child.governorate = governorate
        self.child.district = district
        self.child.save()
        response = self.client.get(self.exam_url())
        form = response.context['form']
        self.assertEqual(form['governorate'].value(), governorate.pk)
        self.assertEqual(form['district'].value(), district.pk)
        self.assertEqual([value for value, _ in form.fields['nearest_town'].choices if value], [])

    def test_existing_location_parent_is_authoritative_when_document_uses_another_governorate(self):
        governorate = Location.objects.create(name='البقاع', name_en='Bekaa', type_id=1)
        district = Location.objects.create(
            name='بعلبك', name_en='Baalbek', type_id=2, parent=governorate,
        )
        form = ExceptionalExamForm(registration=self.registration, data=self.exam_data(
            governorate=governorate.pk, district=district.pk, nearest_town='douris',
        ))
        self.assertTrue(form.is_valid(), form.errors.as_json())
        response = self.client.get(reverse('mscc:exceptional_exam_location_options'), {
            'type': 'village', 'parent': district.pk,
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn({'id': 'douris', 'text': 'Douris'}, response.json()['results'])

    def test_village_lookup_matches_existing_governorate_alias_and_district_separator(self):
        governorate = Location.objects.create(name='الشمال', name_en='North', type_id=1)
        district = Location.objects.create(name='المنية الضنية', type_id=2, parent=governorate)
        form = ExceptionalExamForm(registration=self.registration, data=self.exam_data(
            governorate=governorate.pk, district=district.pk, nearest_town='minnieh',
        ))
        self.assertTrue(form.is_valid(), form.errors.as_json())
        response = self.client.get(reverse('mscc:exceptional_exam_location_options'), {
            'type': 'village', 'parent': district.pk,
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn({'id': 'minnieh', 'text': 'Minniyeh'}, response.json()['results'])

    def test_standalone_existing_hermel_governorate_can_use_the_document_hermel_villages(self):
        governorate = Location.objects.create(name='الهرمل', name_en='Hermel', type_id=1)
        district = Location.objects.create(name='الهرمل', name_en='Hermel', type_id=2, parent=governorate)
        form = ExceptionalExamForm(registration=self.registration, data=self.exam_data(
            governorate=governorate.pk, district=district.pk, nearest_town='qasr',
        ))
        self.assertTrue(form.is_valid(), form.errors.as_json())

    def test_ambiguous_existing_district_names_do_not_guess_a_village_list(self):
        governorate = Location.objects.create(name='Unknown governorate', type_id=1)
        district = Location.objects.create(name='بعلبك', name_en='Hermel', type_id=2, parent=governorate)
        form = ExceptionalExamForm(registration=self.registration, data=self.exam_data(
            governorate=governorate.pk, district=district.pk, nearest_town='douris',
        ))
        self.assertFalse(form.is_valid())
        self.assertIn('nearest_town', form.errors)
        response = self.client.get(reverse('mscc:exceptional_exam_location_options'), {
            'type': 'village', 'parent': district.pk,
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['results'], [])

    def test_unmapped_legacy_answers_remain_readable_and_edit_requires_linked_locations(self):
        exam = self.create_exam(
            governorate=None, district=None,
            governorate_legacy='beirut', district_legacy='beirut',
        )
        profile = self.client.get(reverse('mscc:child_profile', args=[self.registration.pk]), {
            'current_tab': 'exceptional_exam',
        })
        self.assertContains(profile, 'Beirut')
        self.assertContains(profile, 'Achrafieh')
        response = self.client.get(self.exam_url())
        self.assertIn(response.context['form']['governorate'].value(), ('', None))
        self.assertIn(response.context['form']['district'].value(), ('', None))
        response = self.client.post(self.exam_url(), self.exam_data(governorate='', district=''))
        self.assertEqual(response.status_code, 200)
        self.assertIn('governorate', response.context['form'].errors)
        self.assertIn('district', response.context['form'].errors)
        exam.refresh_from_db()
        self.assertEqual((exam.governorate_legacy, exam.district_legacy), ('beirut', 'beirut'))

    def test_invalid_registered_location_hierarchy_does_not_prefill_a_wrong_district(self):
        self.child.district = self.baabda
        self.child.save()
        self.registration.refresh_from_db()
        form = ExceptionalExamForm(registration=self.registration)
        self.assertEqual(form['governorate'].value(), self.governorate.pk)
        self.assertIn(form['district'].value(), ('', None))

    def test_model_grade_validation_handles_a_missing_registration(self):
        data = self.exam_data()
        for parent in ('governorate', 'district'):
            data[parent + '_id'] = data.pop(parent)
        exam = ExceptionalExam(registration_id=999999999, **data)
        with self.assertRaises(ValidationError) as error:
            exam.full_clean()
        self.assertIn('registration', error.exception.message_dict)

    def test_model_clean_protects_the_residence_hierarchy(self):
        for data, field in (
            (self.exam_data(district=self.baabda.pk), 'district'),
            (self.exam_data(governorate=self.district.pk), 'governorate'),
            (self.exam_data(district=self.cadaster.pk), 'district'),
            (self.exam_data(nearest_town='jounieh'), 'nearest_town'),
        ):
            with self.subTest(data=data):
                for parent in ('governorate', 'district'):
                    data[parent + '_id'] = data.pop(parent)
                exam = ExceptionalExam(registration=self.registration, **data)
                with self.assertRaises(ValidationError) as error:
                    exam.full_clean()
                self.assertIn(field, error.exception.message_dict)
        exam = ExceptionalExam(
            registration=self.registration,
            governorate=self.other_governorate, district=self.baabda, nearest_town='aley',
            programme='BLN', grade='2', math_language='ar', language_exam='en',
        )
        exam.full_clean()

    def test_model_clean_rejects_a_bln_grade_for_the_wrong_age_and_grade_seven(self):
        for grade in ('3', '4', '5', '6', '7'):
            with self.subTest(grade=grade):
                exam = ExceptionalExam(
                    registration=self.registration,
                    governorate=self.governorate, district=self.district, nearest_town='achrafieh',
                    programme='BLN', grade=grade, math_language='ar', language_exam='en',
                )
                with self.assertRaises(ValidationError) as error:
                    exam.full_clean()
                self.assertIn('grade', error.exception.message_dict)

    def test_existing_bln_grade_seven_remains_readable_until_a_valid_edit_is_saved(self):
        exam = self.create_exam(grade='7')
        profile = self.client.get(reverse('mscc:child_profile', args=[self.registration.pk]), {
            'current_tab': 'exceptional_exam',
        })
        self.assertContains(profile, 'Grade 7')
        csv_rows = list(csv.DictReader(io.StringIO(
            build_children_csv(Registration.objects.filter(pk=self.registration.pk)).decode('utf-8-sig'),
        )))
        self.assertEqual(csv_rows[0]['Exceptional Exam - Grade applying for the examination'], 'Grade 7')
        edit = self.client.get(self.exam_url())
        self.assertEqual(edit.context['form']['grade'].value(), '2')
        self.assertEqual(tuple(value for value, _ in edit.context['form'].fields['grade'].choices if value), ('2',))
        exam.refresh_from_db()
        self.assertEqual(exam.grade, '7')
        invalid_edit = self.client.post(self.exam_url(), self.exam_data(grade='7'))
        self.assertEqual(invalid_edit.status_code, 200)
        exam.refresh_from_db()
        self.assertEqual(exam.grade, '7')
        valid_edit = self.client.post(self.exam_url(), self.exam_data(grade='2'))
        self.assertEqual(valid_edit.status_code, 302)
        exam.refresh_from_db()
        self.assertEqual(exam.grade, '2')

    def test_save_binds_url_registration_and_audit_user_and_leaves_registration_untouched(self):
        response = self.client.post(self.exam_url(), self.exam_data(
            registration=str(self.outside_registration.pk),
            created_by=str(self.unicef_user.pk), modified_by=str(self.unicef_user.pk),
        ))
        self.assertRedirects(
            response,
            reverse('mscc:child_profile', args=[self.registration.pk]) + '?current_tab=exceptional_exam',
        )
        exam = ExceptionalExam.objects.get()
        self.assertEqual(exam.registration_id, self.registration.pk)
        self.assertEqual(exam.created_by_id, self.center_user.pk)
        self.assertEqual(exam.modified_by_id, self.center_user.pk)
        self.registration.refresh_from_db()
        self.child.refresh_from_db()
        self.assertEqual(self.registration.nfe_programme, 'BLN')
        self.assertEqual(self.registration.source_of_identification, 'Other Sources')
        self.assertEqual(self.child.street, 'Original residential street')
        self.assertEqual(self.child.first_phone_number, '70-123456')
        self.assertEqual(self.child.governorate_id, self.governorate.pk)
        self.assertEqual(self.child.district_id, self.district.pk)

    def test_edit_reuses_one_record_and_preserves_original_creator(self):
        exam = self.create_exam()
        self.client.force_login(self.other_editor)
        response = self.client.post(self.exam_url(), self.exam_data(
            programme='DIRASA', grade='7', math_language='fr', language_exam='fr',
            governorate=self.other_governorate.pk, district=self.keserwan.pk,
            nearest_town='jounieh',
        ))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(ExceptionalExam.objects.count(), 1)
        exam.refresh_from_db()
        self.assertEqual(exam.created_by_id, self.center_user.pk)
        self.assertEqual(exam.modified_by_id, self.other_editor.pk)
        self.assertEqual(exam.grade, '7')
        self.assertEqual(exam.programme, 'DIRASA')
        self.assertEqual(exam.nearest_town, 'jounieh')
        self.registration.refresh_from_db()
        self.assertEqual(self.registration.nfe_programme, 'BLN')

    def test_edit_preloads_stored_parent_choices_and_answers(self):
        self.set_child_age(12)
        exam = self.create_exam(
            governorate=self.other_governorate.pk, district=self.keserwan.pk,
            nearest_town='jounieh', grade='6',
        )
        response = self.client.get(self.exam_url())
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        for field in REQUIRED_FIELDS:
            value = getattr(exam, field + '_id') if field in ('governorate', 'district') else getattr(exam, field)
            self.assertEqual(form[field].value(), value)
        self.assertEqual(
            set(form.fields['district'].queryset.values_list('pk', flat=True)),
            {self.baabda.pk, self.keserwan.pk, self.aley.pk},
        )
        self.assertEqual(form.fields['district'].label_from_instance(self.keserwan), 'Keserwan')
        self.assertIn(('jounieh', 'Jounieh'), tuple(form.fields['nearest_town'].choices))
        self.assertNotIn(self.district.pk, form.fields['district'].queryset.values_list('pk', flat=True))
        self.assertNotIn('achrafieh', dict(form.fields['nearest_town'].choices))

    def test_invalid_edit_keeps_the_existing_answers(self):
        exam = self.create_exam()
        response = self.client.post(self.exam_url(), self.exam_data(district=self.baabda.pk))
        self.assertEqual(response.status_code, 200)
        exam.refresh_from_db()
        self.assertEqual(exam.district_id, self.district.pk)
        self.assertEqual(exam.nearest_town, 'achrafieh')
        self.assertEqual(ExceptionalExam.objects.count(), 1)

    def test_each_round_registration_has_its_own_exam_but_duplicates_are_prohibited(self):
        original = self.create_exam()
        previous_registration = Registration.objects.create(
            child=self.child, partner=self.partner, center=self.center, round=self.other_round,
        )
        self.create_exam(registration=previous_registration, programme='DIRASA', grade='7')
        self.assertEqual(ExceptionalExam.objects.count(), 2)
        with self.assertRaises(IntegrityError), transaction.atomic():
            self.create_exam()
        persisted_registration = Registration.objects.get(pk=self.registration.pk)
        self.assertEqual(persisted_registration.exceptional_exam.pk, original.pk)

    def test_anonymous_users_cannot_read_or_submit_the_exam_form(self):
        self.client.logout()
        for method in (self.client.get, self.client.post):
            response = method(self.exam_url(), self.exam_data())
            self.assertEqual(response.status_code, 302)
        self.assertFalse(ExceptionalExam.objects.exists())

    def test_deleted_unknown_and_childless_registrations_are_not_available(self):
        for user in (self.center_user, self.staff_user, self.super_user):
            self.client.force_login(user)
            for registration in (self.deleted_registration, self.childless_registration):
                for method in (self.client.get, self.client.post):
                    with self.subTest(user=user.username, registration=registration.pk, method=method.__name__):
                        response = method(self.exam_url(registration), self.exam_data())
                        self.assertEqual(response.status_code, 404)
            response = self.client.get(reverse('mscc:exceptional_exam_form', args=[999999999]))
            self.assertEqual(response.status_code, 404)
        self.assertFalse(ExceptionalExam.objects.exists())

    def test_centre_editor_cannot_access_other_centres_even_under_the_same_partner(self):
        for registration in (self.second_registration, self.outside_registration):
            for method in (self.client.get, self.client.post):
                with self.subTest(registration=registration.pk, method=method.__name__):
                    response = method(self.exam_url(registration), self.exam_data())
                    self.assertEqual(response.status_code, 404)
        self.assertFalse(ExceptionalExam.objects.exists())

    def test_staff_and_superusers_can_manage_outside_registrations(self):
        for user in (self.staff_user, self.super_user):
            with self.subTest(user=user.username):
                self.client.force_login(user)
                response = self.client.get(self.exam_url(self.outside_registration))
                self.assertEqual(response.status_code, 200)
                response = self.client.post(
                    self.exam_url(self.outside_registration), self.exam_data(programme='DIRASA'),
                )
                self.assertEqual(response.status_code, 302)
        exam = ExceptionalExam.objects.get()
        self.assertEqual(exam.created_by_id, self.staff_user.pk)
        self.assertEqual(exam.modified_by_id, self.super_user.pk)

    def test_unicef_and_partner_viewers_cannot_create_or_edit(self):
        exam = self.create_exam()
        for user in (self.unicef_user, self.partner_user):
            self.client.force_login(user)
            for method in (self.client.get, self.client.post):
                with self.subTest(user=user.username, method=method.__name__):
                    response = method(self.exam_url(), self.exam_data(grade='7'))
                    self.assertEqual(response.status_code, 403)
            response = self.client.get(reverse('mscc:child_profile', args=[self.registration.pk]))
            self.assertEqual(response.status_code, 200)
            self.assertTrue(response.context['can_view_exceptional_exam'])
            self.assertFalse(response.context['can_manage_exceptional_exam'])
            self.assertEqual(response.context['exceptional_exam'].pk, exam.pk)
        exam.refresh_from_db()
        self.assertEqual(exam.grade, '2')

    def test_unassigned_or_other_module_users_cannot_submit_even_with_a_centre_assignment(self):
        for user in (self.unassigned_user, self.unassigned_center_user, self.alp_user):
            self.client.force_login(user)
            for method in (self.client.get, self.client.post):
                with self.subTest(user=user.username, method=method.__name__):
                    response = method(self.exam_url(), self.exam_data())
                    self.assertIn(response.status_code, (403, 404))
        self.assertFalse(ExceptionalExam.objects.exists())

    def test_mixed_viewer_and_centre_roles_only_edit_the_assigned_centre(self):
        for user in (self.unicef_center_user, self.partner_center_user):
            self.client.force_login(user)
            with self.subTest(user=user.username):
                response = self.client.post(self.exam_url(), self.exam_data())
                self.assertEqual(response.status_code, 302)
                response = self.client.post(self.exam_url(self.second_registration), self.exam_data())
                self.assertIn(response.status_code, (403, 404))
        self.assertEqual(ExceptionalExam.objects.count(), 1)

    def test_base_mscc_service_editor_is_limited_to_the_assigned_centre(self):
        editor = self.make_user('exam-base-centre', ['MSCC'], center=self.center)
        self.client.force_login(editor)
        response = self.client.post(self.exam_url(), self.exam_data())
        self.assertEqual(response.status_code, 302)
        response = self.client.post(self.exam_url(self.second_registration), self.exam_data())
        self.assertEqual(response.status_code, 404)
        exam = ExceptionalExam.objects.get()
        self.assertEqual(exam.registration_id, self.registration.pk)
        self.assertEqual(exam.created_by_id, editor.pk)

    def test_assigning_a_centre_to_a_viewer_does_not_implicitly_grant_editing(self):
        viewers = (
            self.make_user(
                'exam-unicef-assigned', ['MSCC', 'MSCC_UNICEF'], center=self.center,
            ),
            self.make_user(
                'exam-partner-assigned', ['MSCC', 'MSCC_PARTNER'],
                center=self.center, partner=self.partner,
            ),
        )
        for viewer in viewers:
            with self.subTest(viewer=viewer.username):
                self.client.force_login(viewer)
                response = self.client.post(self.exam_url(), self.exam_data())
                self.assertEqual(response.status_code, 403)
        self.assertFalse(ExceptionalExam.objects.exists())

    def test_profile_shows_editor_summary_in_english(self):
        exam = self.create_exam()
        response = self.client.get(
            reverse('mscc:child_profile', args=[self.registration.pk]),
            {'current_tab': 'exceptional_exam'},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['current_tab'], 'exceptional_exam')
        self.assertTrue(response.context['can_view_exceptional_exam'])
        self.assertTrue(response.context['can_manage_exceptional_exam'])
        self.assertEqual(response.context['exceptional_exam'].pk, exam.pk)
        self.assertContains(response, 'Exceptional Exam')
        for text in ('Beirut', 'Achrafieh', 'Grade 2', 'English'):
            self.assertContains(response, text)

    def test_saved_exam_profile_summary_follows_the_selected_ui_language(self):
        exam = self.create_exam()
        expected = {
            'en': (
                ('Governorate', 'Beirut'), ('District/Caza', 'Beirut'), ('Village', 'Achrafieh'),
                ('Non-formal education programme', 'Basic Literacy and Numeracy (BLN)'),
                ('Grade applying for the examination', 'Grade 2'),
                ('Mathematics examination language', 'Arabic'), ('Language examination', 'English'),
            ),
            'ar': (
                ('المحافظة', 'بيروت'), ('القضاء', 'بيروت'), ('القرية', 'الأشرفية'),
                ('البرنامج التعليمي غير النظامي', 'برنامج المهارات الأساسية في القراءة والكتابة والحساب (BLN)'),
                ('الصف الدراسي الذي يتقدم للامتحان له', 'الصف الثاني'),
                ('لغة امتحان الرياضيات', 'اللغة العربية'), ('امتحان اللغة', 'الانكليزية'),
            ),
        }
        for language, rows in expected.items():
            with self.subTest(language=language):
                self.set_language(language)
                response = self.client.get(
                    reverse('mscc:child_profile', args=[self.registration.pk]),
                    {'current_tab': 'exceptional_exam'},
                )
                self.assertEqual(response.status_code, 200)
                with translation.override(language):
                    displayed = tuple((str(label), str(value)) for label, value in response.context['exceptional_exam_rows'])
                self.assertEqual(displayed, rows)
                for label, value in rows:
                    self.assertContains(response, label)
                    self.assertContains(response, value)
                self.assertNotContains(response, 'Achrafieh /')
                self.assertNotContains(response, 'Grade 2 /')
        exam.refresh_from_db()
        self.assertEqual(exam.nearest_town, 'achrafieh')
        self.assertEqual(exam.grade, '2')

    def test_excel_and_csv_keep_exam_answers_and_current_photos_on_the_correct_registration(self):
        self.create_exam()
        previous_registration = Registration.objects.create(
            child=self.child, partner=self.partner, center=self.center, round=self.other_round,
        )
        self.create_exam(
            registration=previous_registration, programme='DIRASA', grade='7',
            governorate=self.other_governorate.pk, district=self.keserwan.pk,
            nearest_town='jounieh',
            math_language='fr', language_exam='fr',
        )
        with tempfile.TemporaryDirectory() as media_root, override_settings(
            MEDIA_ROOT=media_root,
            STORAGES={
                'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
                'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
            },
        ):
            self.child.photo.save('registered-child.png', ContentFile(portrait_bytes('red')))
            self.second_registration.child.photo.save('second-child.png', ContentFile(portrait_bytes('blue')))
            # A replacement must be picked up by a new export along with the
            # saved exam: stale image bytes must not be reused across exports.
            self.child.photo.save('updated-child.png', ContentFile(portrait_bytes('green')))
            queryset = Registration.objects.filter(pk__in=(
                self.registration.pk, previous_registration.pk, self.second_registration.pk,
            )).order_by('pk')
            workbook = build_children_workbook(queryset)
            photos = workbook_photos_by_row(workbook)
            rows = {row['Registration ID']: (number, row) for number, row in workbook_rows(workbook)}
            first_number, first = rows[str(self.registration.pk)]
            previous_number, previous = rows[str(previous_registration.pk)]
            second_number, second = rows[str(self.second_registration.pk)]
            self.assertEqual(first['Child ID'], previous['Child ID'])
            self.assertEqual(first['Child ID'], str(self.child.pk))
            self.assertEqual(first['Exceptional Exam - Governorate ID'], str(self.governorate.pk))
            self.assertEqual(first['Exceptional Exam - District/Caza ID'], str(self.district.pk))
            self.assertEqual(previous['Exceptional Exam - Governorate ID'], str(self.other_governorate.pk))
            self.assertEqual(previous['Exceptional Exam - District/Caza ID'], str(self.keserwan.pk))
            grade_header = 'Exceptional Exam - Grade applying for the examination'
            self.assertEqual(first[grade_header], 'Grade 2')
            self.assertEqual(previous[grade_header], 'Grade 7')
            for header, expected in (
                ('Governorate', 'Beirut'),
                ('District/Caza', 'Beirut'),
                ('Village', 'Achrafieh'),
                ('Non-formal education programme', dict(PROGRAMME_CHOICES)['BLN']),
                ('Mathematics examination language', 'Arabic'),
                ('Language examination', 'English'),
            ):
                self.assertEqual(first['Exceptional Exam - ' + header], expected)
            self.assertEqual(
                previous['Exceptional Exam - Village'], 'Jounieh',
            )
            exam_headers = [name for name in first if name.startswith('Exceptional Exam - ')]
            self.assertTrue(exam_headers)
            self.assertTrue(all(second[name] == '' for name in exam_headers))
            for number, expected_colour in (
                (first_number, (0, 128, 0)), (previous_number, (0, 128, 0)),
                (second_number, (0, 0, 255)),
            ):
                with Image.open(io.BytesIO(photos[number])) as photo:
                    self.assertEqual(photo.convert('RGB').getpixel((0, 0)), expected_colour)

            csv_rows = list(csv.DictReader(io.StringIO(
                build_children_csv(queryset).decode('utf-8-sig'),
            )))
            csv_records = {row['Registration ID']: row for row in csv_rows}
            self.assertEqual(csv_records[str(self.registration.pk)][grade_header], 'Grade 2')
            self.assertEqual(csv_records[str(previous_registration.pk)][grade_header], 'Grade 7')
            self.assertEqual(csv_records[str(self.second_registration.pk)][grade_header], '')

