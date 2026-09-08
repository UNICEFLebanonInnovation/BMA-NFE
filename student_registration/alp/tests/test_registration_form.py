from types import SimpleNamespace

from django.http import QueryDict
from django.test import TestCase

from student_registration.alp.forms import ALPRegistrationForm, ALPTeacherForm
from student_registration.alp.models import ALPProgram, ALPRound
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

    def test_submitted_school_is_replaced_with_users_school(self):
        request = SimpleNamespace(
            user=self.user,
            POST=QueryDict(f'school={self.other_school.pk}&programme=ALP'),
        )

        data = ALPRegistrationForm._registration_data(request)

        self.assertEqual(data['school'], str(self.school.pk))
        self.assertEqual(data['programme'], 'ALP')
        self.assertEqual(request.POST['school'], str(self.other_school.pk))

    def test_round_and_programme_are_required_registration_fields(self):
        form = ALPRegistrationForm(request=SimpleNamespace(user=self.user))

        self.assertTrue(form.fields['round'].required)
        self.assertEqual(form.fields['round'].label, 'Round')
        self.assertTrue(form.fields['programme'].required)
        self.assertEqual(form.fields['programme'].label, 'Program')

    def test_round_and_programme_choices_include_configured_records(self):
        old_round = ALPRound.objects.create(name='2024/2025', current_year=False)
        current_round = ALPRound.objects.create(name='2025/2026', current_year=True)
        programme = ALPProgram.objects.create(name='ALP')

        form = ALPRegistrationForm(request=SimpleNamespace(user=self.user))

        self.assertQuerySetEqual(
            form.fields['round'].queryset,
            [old_round, current_round],
        )
        self.assertQuerySetEqual(
            form.fields['programme'].queryset,
            [programme],
        )


class ALPTeacherAcademicYearTests(TestCase):
    def test_academic_year_includes_all_configured_rounds(self):
        old_round = ALPRound.objects.create(name='2024/2025', current_year=False)
        current_round = ALPRound.objects.create(name='2025/2026', current_year=True)

        form = ALPTeacherForm()

        self.assertEqual(form.fields['round'].label, 'Academic year')
        self.assertTrue(form.fields['round'].required)
        self.assertQuerySetEqual(
            form.fields['round'].queryset,
            [old_round, current_round],
        )
