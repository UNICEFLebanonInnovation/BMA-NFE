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
