from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse

from student_registration.schools.models import School
from student_registration.users.models import User


class AttendanceNavigationTests(TestCase):
    def setUp(self):
        school = School.objects.create(number='100', name='ALP school')
        group = Group.objects.create(name='ALP_SCHOOL')
        self.user = User.objects.create_user(
            username='alp-focal-point', password='password', school=school
        )
        self.user.groups.add(group)
        self.client.force_login(self.user)

    def test_child_attendance_home_link_returns_to_alp_landing_page(self):
        response = self.client.get(reverse('alp:attendance_list'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            'href="{}"'.format(reverse('alp:landing_page')),
        )

    def test_teacher_attendance_home_link_returns_to_alp_landing_page(self):
        response = self.client.get(reverse('alp:teacher_attendance_list'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            'href="{}"'.format(reverse('alp:landing_page')),
        )

    def test_alp_landing_page_is_available_from_attendance(self):
        response = self.client.get(reverse('alp:landing_page'))

        self.assertEqual(response.status_code, 200)
