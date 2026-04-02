from django.test import TestCase
from student_registration.mscc.templatetags.education_tags import get_education_programme_assessments
from unittest.mock import MagicMock

class EducationTagsTest(TestCase):
    def test_get_education_programme_assessments(self):
        class MockResult1:
            pass
        class MockResult:
            pass
        class MockRequest:
            pass
        class MockUser:
            pass
        class MockCenter:
            pass

        result1 = MockResult1()
        result1.education_program = 'BLN Level 1'

        result = MockResult()
        result.pre_test = {'arabic_grade': 50, 'math_grade': 10}
        result.post_test = {'arabic_grade': 60, 'math_grade': 20}

        request = MockRequest()
        request.user = MockUser()
        request.user.center = MockCenter()
        request.user.center.provide_french_language = 'No'

        assessments = get_education_programme_assessments(result1, result, request)

        # Should have arabic, english, math
        self.assertEqual(len(assessments), 3)

        arabic = next(a for a in assessments if a['key'] == 'arabic_grade')
        self.assertEqual(arabic['label'], 'Arabic Language Development')
        self.assertEqual(arabic['max_score'], 68)
        self.assertEqual(arabic['pre'], 50)
        self.assertEqual(arabic['post'], 60)
        self.assertEqual(arabic['imp'], '20.0%')

        english = next(a for a in assessments if a['key'] == 'english_grade')
        self.assertEqual(english['label'], 'English Language Development')
        self.assertEqual(english['max_score'], 43)

        math = next(a for a in assessments if a['key'] == 'math_grade')
        self.assertEqual(math['label'], 'Mathematics')
        self.assertEqual(math['max_score'], 22)
        self.assertEqual(math['pre'], 10)
        self.assertEqual(math['post'], 20)
        self.assertEqual(math['imp'], '100.0%')
