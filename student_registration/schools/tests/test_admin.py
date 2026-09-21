from django.contrib import admin
from django.test import SimpleTestCase

from student_registration.schools.admin import SchoolAdmin
from student_registration.schools.models import School
from student_registration.alp.forms import ALPSchoolProfileForm


class SchoolAdminRegistrationTests(SimpleTestCase):
    def test_school_is_available_in_admin_portal(self):
        self.assertIsInstance(admin.site._registry[School], SchoolAdmin)

    def test_school_admin_fields_pass_system_checks(self):
        school_admin = admin.site._registry[School]

        self.assertEqual(school_admin.check(), [])

    def test_school_admin_fields_match_alp_school_profile(self):
        school_admin = admin.site._registry[School]

        self.assertEqual(school_admin.fields, ALPSchoolProfileForm.Meta.fields)
