"""Assessment screens must accept zero and optional blank grades safely."""
from django.contrib.messages.storage.fallback import FallbackStorage
from django.test import RequestFactory, TestCase

from student_registration.mscc.education_form import EducationAssessmentForm
from student_registration.mscc.models import EducationAssessment, Registration


class AssessmentFormTests(TestCase):
    def setUp(self):
        self.registration = Registration.objects.create()

    def form(self, **changes):
        values = dict(participation='No Absence', post_test_done='No', school_year_completed='No',
            post_attended_arabic='No', post_attended_language='No', post_attended_math='No',
            post_arabic_grade='', post_language_grade='', post_math_grade='')
        values.update(changes)
        request = RequestFactory().post('/assessment/', values)
        request.session = {}
        request._messages = FallbackStorage(request)
        return EducationAssessmentForm(values, request=request, registry=self.registration.pk), request

    def test_zero_is_a_valid_completed_grade_in_each_subject(self):
        values = dict(post_test_done='Yes')
        for subject in ('arabic', 'language', 'math'):
            values.update({f'post_attended_{subject}': 'Yes', f'post_modality_{subject}': 'Offline (F2F)',
                           f'post_{subject}_grade': '0'})
        form, request = self.form(**values)
        self.assertTrue(form.is_valid(), form.errors)
        row = form.save(request=request, registry=self.registration.pk)
        self.assertEqual((row.post_arabic_grade, row.post_language_grade, row.post_math_grade), (0, 0, 0))

    def test_optional_blank_grades_save_one_complete_record(self):
        form, request = self.form()
        self.assertTrue(form.is_valid(), form.errors)
        row = form.save(request=request, registry=self.registration.pk)
        self.assertEqual(row.post_arabic_grade, 0)
        self.assertEqual(EducationAssessment.objects.count(), 1)

    def test_required_missing_grade_remains_invalid(self):
        form, _ = self.form(post_test_done='Yes', post_attended_arabic='Yes', post_modality_arabic='Offline (F2F)')
        self.assertFalse(form.is_valid())
        self.assertIn('post_arabic_grade', form.errors)

    def test_invalid_save_cannot_leave_a_partial_record(self):
        form, request = self.form(post_math_grade='invalid')
        self.assertFalse(form.is_valid())
        with self.assertRaises(ValueError):
            form.save(request=request, registry=self.registration.pk)
        self.assertFalse(EducationAssessment.objects.exists())
