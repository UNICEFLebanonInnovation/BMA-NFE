from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse

from student_registration.alp.forms import ALPTeacherForm
from student_registration.alp.models import ALPRound
from student_registration.schools.models import School
from student_registration.users.models import User


class ALPTeacherDashboardTests(TestCase):
    def setUp(self):
        self.school = School.objects.create(
            number='100', name='Mapped ALP School', latitude=33.9,
            longitude=35.5,
        )
        group = Group.objects.create(name='ALP_SCHOOL')
        self.user = User.objects.create_user(
            username='focal-point', password='password', school=self.school
        )
        self.user.groups.add(group)
        self.client.force_login(self.user)

    def test_dashboard_includes_available_rounds(self):
        alp_round = ALPRound.objects.create(name='Round 1', current_year=True)

        response = self.client.get(reverse('alp:dashboard_teacher'))

        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(response.context['rounds'], [alp_round])

    def test_teacher_grade_levels_only_include_levels_one_to_four(self):
        form = ALPTeacherForm(user=self.user)

        self.assertEqual(
            list(form.fields['registration_level'].choices),
            [
                ('Level one', 'Level one'),
                ('Level two', 'Level two'),
                ('Level three', 'Level three'),
                ('Level four', 'Level four'),
            ],
        )

    def test_teacher_assignment_options_match_alp_programme(self):
        form = ALPTeacherForm(user=self.user)

        self.assertEqual(
            list(form.fields['teacher_assignment'].choices),
            [
                ('ALP only', 'ALP only'),
                ('ALP and FE', 'ALP and FE'),
                ('ALP and private', 'ALP and private'),
                ('other', 'other'),
            ],
        )

    def test_other_teacher_assignment_requires_details(self):
        form = ALPTeacherForm(
            data={'teacher_assignment': 'other'},
            user=self.user,
        )

        form.is_valid()

        self.assertIn('teacher_assignment_other', form.errors)
