from types import SimpleNamespace

from django.http import QueryDict
from django.test import TestCase

from student_registration.alp.forms import ALPRegistrationForm
from student_registration.schools.models import School


class ALPRegistrationFormSchoolTests(TestCase):
    def setUp(self):
        self.school = School.objects.create(number='100', name='Assigned school')
        self.other_school = School.objects.create(number='200', name='Other school')
        self.user = SimpleNamespace(is_superuser=False, school_id=self.school.pk)

    def test_school_is_not_in_registration_form(self):
        request = SimpleNamespace(user=self.user)

        form = ALPRegistrationForm(request=request)

        self.assertNotIn('school', form.fields)

    def test_child_work_participation_is_marked_required(self):
        request = SimpleNamespace(user=self.user)

        form = ALPRegistrationForm(request=request)

        self.assertTrue(form.fields['have_labour'].required)

    def test_consent_form_accepts_document_or_photo_upload(self):
        request = SimpleNamespace(user=self.user)

        form = ALPRegistrationForm(request=request)

        consent_form = form.fields['consent_form']
        self.assertFalse(consent_form.required)
        self.assertEqual(
            consent_form.widget.attrs['accept'],
            'application/pdf,image/*',
        )

    def test_alp_referral_sources_include_bln_and_national_nfe_assessment(self):
        request = SimpleNamespace(user=self.user)

        form = ALPRegistrationForm(request=request)

        choices = dict(form.fields['source_of_identification'].choices)
        self.assertIn('BLN programme', choices)
        self.assertIn('Transitioned from National NFE assessment', choices)

    def test_submitted_school_is_replaced_with_users_school(self):
        request = SimpleNamespace(
            user=self.user,
            POST=QueryDict(f'school={self.other_school.pk}&programme=ALP'),
        )

        data = ALPRegistrationForm._registration_data(request)

        self.assertEqual(data['school'], str(self.school.pk))
        self.assertEqual(data['programme'], 'ALP')
        self.assertEqual(request.POST['school'], str(self.other_school.pk))
