from types import SimpleNamespace

from django.test import SimpleTestCase

from student_registration.alp.models import (
    ALPAttendance,
    ALPRegistration,
    ALPTeacher,
)
from student_registration.alp.utils import filter_by_school
from student_registration.schools.models import School


class FilterBySchoolTests(SimpleTestCase):
    def _user(self, *, is_superuser=False):
        user = SimpleNamespace(is_superuser=is_superuser, school_id=42)
        user.school = School(pk=user.school_id)
        return user

    def test_attendance_is_filtered_by_its_direct_school(self):
        user = self._user()

        queryset = filter_by_school(ALPAttendance.objects.all(), user)

        self.assertEqual(queryset.query.sql_with_params()[1], (user.school_id,))

    def test_registration_is_filtered_by_connected_users_school(self):
        user = self._user()

        queryset = filter_by_school(ALPRegistration.objects.all(), user)

        self.assertEqual(queryset.query.sql_with_params()[1], (user.school_id,))

    def test_teacher_is_filtered_by_connected_users_school(self):
        user = self._user()

        queryset = filter_by_school(ALPTeacher.objects.all(), user)

        self.assertEqual(queryset.query.sql_with_params()[1], (user.school_id,))

    def test_superuser_with_school_is_still_filtered(self):
        user = self._user(is_superuser=True)

        queryset = filter_by_school(ALPRegistration.objects.all(), user)

        self.assertEqual(queryset.query.sql_with_params()[1], (user.school_id,))
