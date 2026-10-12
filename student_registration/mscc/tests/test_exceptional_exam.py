"""Exercise exceptional-exam data, document choices and registration access."""

import csv
import io
import tempfile

from PIL import Image

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.db import IntegrityError, transaction
from django.test import SimpleTestCase, TestCase, override_settings
from django.urls import reverse

from student_registration.child.models import Child
from student_registration.locations.models import Center
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

    def test_choice_labels_include_arabic_and_english(self):
        choices = list(PROGRAMME_CHOICES + GRADE_CHOICES + MATH_LANGUAGE_CHOICES + LANGUAGE_EXAM_CHOICES)
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

    def test_cascade_rejects_unknown_or_wrong_parent_selections(self):
        self.assertEqual(district_choices('unknown'), ())
        self.assertEqual(town_choices('beirut', 'baabda'), ())
        self.assertFalse(valid_residence('beirut', 'beirut', 'baabda'))
        self.assertFalse(valid_residence('beirut', 'baabda', 'aley'))
        self.assertTrue(valid_residence('mount_lebanon', 'baabda', 'aley'))
        self.assertTrue(valid_residence('mount_lebanon', 'aley', 'aley'))
        self.assertEqual(residence_labels('beirut', 'baabda', 'aley'), ('Beirut / بيروت', '', ''))


@override_settings(LANGUAGE_CODE='en')
class ExceptionalExamWorkflowTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.partner = PartnerOrganization.objects.create(name='Exam partner')
        cls.other_partner = PartnerOrganization.objects.create(name='Outside exam partner')
        cls.center = Center.objects.create(name='Assigned exam centre', partner=cls.partner)
        cls.second_center = Center.objects.create(name='Other partner centre', partner=cls.partner)
        cls.outside_center = Center.objects.create(name='Outside centre', partner=cls.other_partner)
        cls.nationality = Nationality.objects.create(name='Test nationality', name_en='Test nationality')
        cls.child = Child.objects.create(
            first_name='Rania', father_name='Samir', last_name='Example',
            mother_fullname='Mother of Rania', gender='Female', nationality=cls.nationality,
            birthday_year='2014', birthday_month='3', birthday_day='12',
            first_phone_number='70-123456', street='Original residential street',
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
        self.client.force_login(self.center_user)

    def exam_url(self, registration=None):
        return reverse('mscc:exceptional_exam_form', args=[(registration or self.registration).pk])

    def exam_data(self, **updates):
        data = {
            'governorate': 'beirut', 'district': 'beirut', 'nearest_town': 'achrafieh',
            'programme': 'BLN', 'grade': '2', 'math_language': 'ar', 'language_exam': 'en',
        }
        data.update(updates)
        return data

    def create_exam(self, registration=None, **updates):
        return ExceptionalExam.objects.create(
            registration=registration or self.registration,
            created_by=self.center_user, modified_by=self.center_user,
            **self.exam_data(**updates),
        )

    def test_get_prefills_programme_and_shows_all_questions_in_both_languages(self):
        response = self.client.get(self.exam_url())
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertEqual(form['programme'].value(), 'BLN')
        self.assertEqual(set(form.fields), set(REQUIRED_FIELDS))
        for field in form.fields.values():
            self.assertTrue(field.required)
            self.assertRegex(str(field.label), '[A-Za-z]')
            self.assertRegex(str(field.label), '[\u0600-\u06ff]')
        self.assertFalse(ExceptionalExam.objects.exists())

    def test_both_programmes_allow_every_grade_from_two_through_seven(self):
        for programme in ('BLN', 'DIRASA'):
            for grade in range(2, 8):
                with self.subTest(programme=programme, grade=grade):
                    form = ExceptionalExamForm(data=self.exam_data(programme=programme, grade=str(grade)))
                    self.assertTrue(form.is_valid(), form.errors.as_json())
                    self.assertEqual(
                        {value for value, _ in form.fields['grade'].choices if value},
                        {'2', '3', '4', '5', '6', '7'},
                    )

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
            ('governorate', 'unknown'), ('district', 'baabda'),
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
                form = ExceptionalExamForm(data=self.exam_data(math_language=language))
                self.assertTrue(form.is_valid(), form.errors.as_json())

    def test_model_clean_protects_the_residence_hierarchy(self):
        for data, field in (
            (self.exam_data(district='baabda'), 'district'),
            (self.exam_data(nearest_town='jounieh'), 'nearest_town'),
        ):
            with self.subTest(data=data):
                exam = ExceptionalExam(registration=self.registration, **data)
                with self.assertRaises(ValidationError) as error:
                    exam.full_clean()
                self.assertIn(field, error.exception.message_dict)
        exam = ExceptionalExam(
            registration=self.registration,
            **self.exam_data(governorate='mount_lebanon', district='baabda', nearest_town='aley'),
        )
        exam.full_clean()

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

    def test_edit_reuses_one_record_and_preserves_original_creator(self):
        exam = self.create_exam()
        self.client.force_login(self.other_editor)
        response = self.client.post(self.exam_url(), self.exam_data(
            programme='DIRASA', grade='7', math_language='fr', language_exam='fr',
            governorate='mount_lebanon', district='keserwan', nearest_town='jounieh',
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
        exam = self.create_exam(
            governorate='mount_lebanon', district='keserwan', nearest_town='jounieh', grade='6',
        )
        response = self.client.get(self.exam_url())
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        for field in REQUIRED_FIELDS:
            self.assertEqual(form[field].value(), getattr(exam, field))
        self.assertIn(('keserwan', 'Keserwan / كسروان'), tuple(form.fields['district'].choices))
        self.assertIn(('jounieh', 'Jounieh / جونية'), tuple(form.fields['nearest_town'].choices))
        self.assertNotIn('beirut', dict(form.fields['district'].choices))
        self.assertNotIn('achrafieh', dict(form.fields['nearest_town'].choices))

    def test_invalid_edit_keeps_the_existing_answers(self):
        exam = self.create_exam()
        response = self.client.post(self.exam_url(), self.exam_data(district='baabda'))
        self.assertEqual(response.status_code, 200)
        exam.refresh_from_db()
        self.assertEqual(exam.district, 'beirut')
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
                response = self.client.post(self.exam_url(self.outside_registration), self.exam_data())
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
                response = self.client.post(self.exam_url(), self.exam_data(grade='5'))
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

    def test_profile_shows_editor_summary_in_both_languages(self):
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
        for text in ('بيروت', 'الأشرفية', 'Grade 2', 'الصف الثاني', 'English', 'الإنكليزية'):
            self.assertContains(response, text)

    def test_excel_and_csv_keep_exam_answers_and_current_photos_on_the_correct_registration(self):
        self.create_exam()
        previous_registration = Registration.objects.create(
            child=self.child, partner=self.partner, center=self.center, round=self.other_round,
        )
        self.create_exam(
            registration=previous_registration, programme='DIRASA', grade='7',
            governorate='mount_lebanon', district='keserwan', nearest_town='jounieh',
            math_language='fr', language_exam='fr',
        )
        with tempfile.TemporaryDirectory() as media_root, override_settings(
            MEDIA_ROOT=media_root,
            DEFAULT_FILE_STORAGE='django.core.files.storage.FileSystemStorage',
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
            grade_header = 'Exceptional Exam - Grade applying for the examination / الصف الدراسي الذي يتقدم للامتحان له'
            self.assertEqual(first[grade_header], 'Grade 2 / الصف الثاني')
            self.assertEqual(previous[grade_header], 'Grade 7 / الصف السابع')
            for header, expected in (
                ('Governorate / المحافظة', 'Beirut / بيروت'),
                ('District/Caza / القضاء', 'Beirut / بيروت'),
                ('Nearest town / البلدة الأقرب', 'Achrafieh / الأشرفية'),
                ('Non-formal education programme / البرنامج التعليمي غير النظامي', dict(PROGRAMME_CHOICES)['BLN']),
                ('Mathematics examination language / لغة امتحان الرياضيات', 'Arabic / العربية'),
                ('Language examination / امتحان اللغة', 'English / الإنكليزية'),
            ):
                self.assertEqual(first['Exceptional Exam - ' + header], expected)
            self.assertEqual(
                previous['Exceptional Exam - Nearest town / البلدة الأقرب'], 'Jounieh / جونية',
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
            self.assertEqual(csv_records[str(self.registration.pk)][grade_header], 'Grade 2 / الصف الثاني')
            self.assertEqual(csv_records[str(previous_registration.pk)][grade_header], 'Grade 7 / الصف السابع')
            self.assertEqual(csv_records[str(self.second_registration.pk)][grade_header], '')

