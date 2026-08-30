from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse

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
