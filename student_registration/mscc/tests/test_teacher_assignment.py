from django.test import SimpleTestCase

from student_registration.mscc.models import Teacher


class TeacherAssignmentTests(SimpleTestCase):
    def test_mscc_teacher_assignment_uses_makani_options(self):
        self.assertEqual(
            list(Teacher.TEACHER_ASSIGNMENT),
            [
                ('Makani only', 'Makani only'),
                ('Private and Makani', 'Private and Makani'),
            ],
        )
