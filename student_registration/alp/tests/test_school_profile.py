from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse

from student_registration.schools.models import School
from student_registration.users.models import User


class SchoolProfileViewTests(TestCase):
    def setUp(self):
        self.school = School.objects.create(number='100', name='Old name')
        group = Group.objects.create(name='ALP_SCHOOL')
        self.user = User.objects.create_user(
            username='focal-point', password='password', school=self.school
        )
        self.user.groups.add(group)
        self.client.force_login(self.user)

    def test_focal_point_can_view_school_edit_form(self):
        response = self.client.get(reverse('alp:school_profile'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="name"')
        self.assertContains(response, self.school.name)

    def test_focal_point_can_only_update_assigned_school(self):
        other_school = School.objects.create(number='200', name='Other school')

        response = self.client.post(reverse('alp:school_profile'), {
            'number': self.school.number,
            'name': 'Updated name',
        })

        self.assertRedirects(response, reverse('alp:school_profile'))
        self.school.refresh_from_db()
        other_school.refresh_from_db()
        self.assertEqual(self.school.name, 'Updated name')
        self.assertEqual(other_school.name, 'Other school')
        self.assertEqual(self.school.modified_by, self.user)

    def test_user_without_assigned_school_cannot_open_profile(self):
        self.user.school = None
        self.user.save(update_fields=['school'])

        response = self.client.get(reverse('alp:school_profile'))

        self.assertEqual(response.status_code, 403)
