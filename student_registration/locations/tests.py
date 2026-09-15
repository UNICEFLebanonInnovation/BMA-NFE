from django.test import SimpleTestCase

from student_registration.locations.forms import CenterForm


class CenterFormTests(SimpleTestCase):
    def test_staff_number_uses_alp_programme_label(self):
        field = CenterForm.base_fields['admin_staff_number']

        self.assertEqual(
            field.label,
            '# of staff assigned under the ALP programme within the school, '
            'including teaching and admin staff',
        )
