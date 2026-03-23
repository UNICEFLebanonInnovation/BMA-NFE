import datetime
from django.core.exceptions import ValidationError
from django.test import TestCase
from student_registration.mscc.utils import validate_date, TrimmedDateField

class TestDateValidation(TestCase):

    def test_validate_date_valid(self):
        d = validate_date('2024-05-20')
        self.assertEqual(d, datetime.date(2024, 5, 20))

    def test_validate_date_invalid(self):
        with self.assertRaises(ValidationError) as e:
            validate_date('20-05-2024')
        self.assertEqual(str(e.exception.message), "Date is not valid. Please use the format YYYY-MM-DD.")

    def test_trimmed_date_field_valid(self):
        f = TrimmedDateField()
        v = f.to_python('2024-05-20  ')
        self.assertEqual(v, datetime.date(2024, 5, 20))

    def test_trimmed_date_field_invalid(self):
        f = TrimmedDateField()
        with self.assertRaises(ValidationError) as e:
            f.to_python('2024/05/20')
        self.assertEqual(str(e.exception.message), "Date is not valid. Please use the format YYYY-MM-DD.")
