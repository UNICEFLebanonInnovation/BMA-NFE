from django.test import SimpleTestCase

from student_registration.schools.forms import SchoolForm
from student_registration.schools.models import School
from student_registration.schools.serializers import SchoolSerializer


class SchoolServicesProgramsFormTests(SimpleTestCase):

    def test_services_and_programs_use_school_options(self):
        form = SchoolForm()

        self.assertEqual(
            list(form.fields['provided_packages'].choices),
            list(School.PROVIDED_PACKAGES),
        )
        self.assertEqual(
            list(form.fields['programs'].choices),
            list(School.PROGRAM),
        )
        self.assertIn(('ALP', 'ALP'), form.fields['programs'].choices)

    def test_services_and_programs_are_serialized(self):
        self.assertIn('provided_packages', SchoolSerializer.Meta.fields)
        self.assertIn('programs', SchoolSerializer.Meta.fields)
