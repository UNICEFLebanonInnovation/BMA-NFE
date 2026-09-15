from django.contrib import admin
from django.test import SimpleTestCase

from student_registration.schools.admin import SchoolAdmin
from student_registration.schools.models import School


class SchoolAdminRegistrationTests(SimpleTestCase):
    def test_school_is_available_in_admin_portal(self):
        self.assertIsInstance(admin.site._registry[School], SchoolAdmin)
