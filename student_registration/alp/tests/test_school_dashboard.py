from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse

from student_registration.schools.models import School
from student_registration.users.models import User


class ALPSchoolDashboardTests(TestCase):
    def setUp(self):
        self.school = School.objects.create(
            number='100', name='Mapped ALP School', latitude=33.9,
            longitude=35.5, school_capacity=120,
        )
        self.other_school = School.objects.create(
            number='200', name='Other ALP School', latitude=34.1,
            longitude=35.7,
        )
        group = Group.objects.create(name='ALP_SCHOOL')
        self.user = User.objects.create_user(
            username='focal-point', password='password', school=self.school
        )
        self.user.groups.add(group)
        self.client.force_login(self.user)

    def test_dashboard_includes_mapping_interface(self):
        response = self.client.get(reverse('alp:dashboard_school'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="alp-school-map"')
        self.assertContains(response, reverse('alp:school_geo_data'))
        self.assertContains(response, self.school.name)
        self.assertNotContains(response, self.other_school.name)

    def test_geo_data_is_limited_to_focal_points_school(self):
        response = self.client.get(reverse('alp:school_geo_data'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        school = response.json()[0]
        self.assertEqual(school['id'], self.school.id)
        self.assertEqual(school['name'], self.school.name)
        self.assertEqual(school['latitude'], self.school.latitude)
        self.assertEqual(school['capacity'], 120)

    def test_geo_data_excludes_schools_without_coordinates(self):
        self.school.latitude = None
        self.school.save(update_fields=['latitude'])

        response = self.client.get(reverse('alp:school_geo_data'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    def test_geo_data_requires_alp_permission(self):
        outsider = User.objects.create_user(
            username='outsider', password='password', school=self.school
        )
        self.client.force_login(outsider)

        response = self.client.get(reverse('alp:school_geo_data'))

        self.assertEqual(response.status_code, 403)
