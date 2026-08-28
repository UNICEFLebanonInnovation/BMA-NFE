from django.test import SimpleTestCase

from student_registration.mscc.models import EducationService


class EducationServiceStatusChoicesTests(SimpleTestCase):
    def test_education_status_choices_match_registration_options(self):
        expected_choices = [
            ('', '----------'),
            ('Never registered in any formal school before',
             'Never registered in any formal school before'),
            ("Was registered in formal school but didn't continue",
             "Was registered in formal school but didn't continue"),
            ('Was registered in non formal program and was referred',
             'Was registered in non formal program and was referred'),
            ("Was registered in non formal program but didn't continue",
             "Was registered in non formal program but didn't continue"),
            ('Was enrolled in TVET Programs',
             'Was enrolled in TVET Programs'),
            ('Was Registered in Formal Education but not attending',
             'Was Registered in Formal Education but not attending'),
            ('Currently registered in Formal Education school',
             'Currently registered in Formal Education school'),
            ('Currently registered in Formal Education school but not attending',
             'Currently registered in Formal Education school but not attending'),
            ('No', 'No'),
        ]

        self.assertEqual(
            [(value, str(label))
             for value, label in EducationService.EDUCATION_STATUS],
            expected_choices,
        )
