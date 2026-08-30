from types import SimpleNamespace

from django.test import SimpleTestCase

from student_registration.alp.models import ALPAttendance
from student_registration.alp.utils import filter_by_school
from student_registration.schools.models import School


class FilterBySchoolTests(SimpleTestCase):
    def test_attendance_is_filtered_by_its_direct_school(self):
        user = SimpleNamespace(is_superuser=False, school_id=42)
        user.school = School(pk=user.school_id)

        queryset = filter_by_school(ALPAttendance.objects.all(), user)

        self.assertEqual(queryset.query.sql_with_params()[1], (user.school_id,))
