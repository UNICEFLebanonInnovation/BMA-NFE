from django.core.exceptions import ValidationError
from django.test import TestCase

from student_registration.schools.forms import SchoolForm


class SchoolFormAdditionalFieldsTests(TestCase):
    def setUp(self):
        self.form = SchoolForm()

    def test_school_form_includes_digital_service_fields(self):
        for field_name in ('offer_digital_learning', 'have_digital_hub'):
            field = self.form.fields[field_name]

            self.assertFalse(field.required)
            self.assertEqual(
                list(field.choices),
                [('', '----------'), ('yes', 'Yes'), ('no', 'No')],
            )

    def test_admin_staff_number_is_a_required_non_negative_integer(self):
        field = self.form.fields['admin_staff_number']

        self.assertTrue(field.required)
        self.assertEqual(field.min_value, 0)

    def test_school_form_includes_nearby_phcc_name(self):
        field = self.form.fields['neaby_phcc']

        self.assertFalse(field.required)
        self.assertEqual(field.label, 'Nearby PHCC name')

    def test_phone_number_uses_generic_label_and_numeric_input_hints(self):
        field = self.form.fields['land_phone_number']

        self.assertEqual(field.label, 'Phone Number')
        self.assertEqual(field.widget.attrs['inputmode'], 'numeric')
        self.assertEqual(field.widget.attrs['pattern'], '[0-9]+')

    def test_phone_number_accepts_digits_only(self):
        field = self.form.fields['land_phone_number']

        self.assertEqual(field.clean('01234567'), '01234567')
        for invalid_value in ('01-234567', '+9611234567', 'phone'):
            with self.subTest(invalid_value=invalid_value):
                with self.assertRaisesMessage(ValidationError, 'Enter a valid value.'):
                    field.clean(invalid_value)
