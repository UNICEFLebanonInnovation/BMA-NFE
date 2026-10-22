from unittest.mock import MagicMock, patch

from django.core.exceptions import ValidationError
from django.forms import CharField, TextInput
from django.test import SimpleTestCase

from student_registration.child.models import Child
from student_registration.locations.models import Location
from student_registration.mscc.forms import MSCCRegistrationForm
from student_registration.mscc.models import Registration


class MSCCRegistrationVillageTests(SimpleTestCase):
    """Registration accepts a required village name entered as free text."""

    def make_form(self, *, data=None, instance=None):
        locations = MagicMock()
        locations.all.return_value = locations
        locations.order_by.return_value = locations
        with patch.object(Location.objects, 'filter', return_value=locations):
            return MSCCRegistrationForm(data=data, instance=instance)

    def test_village_accepts_free_text_in_a_text_input(self):
        field = self.make_form().fields['child_village']
        self.assertIsInstance(field, CharField)
        self.assertIsInstance(field.widget, TextInput)
        self.assertEqual(field.clean('  قرية غير مدرجة في قائمة المواقع  '), 'قرية غير مدرجة في قائمة المواقع')
        self.assertEqual(field.clean('A' * 255), 'A' * 255)

    def test_village_still_requires_nonempty_text_within_the_length_limit(self):
        field = self.make_form().fields['child_village']
        for invalid in ('', '   ', 'A' * 256):
            with self.subTest(value=invalid), self.assertRaises(ValidationError):
                field.clean(invalid)

    def test_existing_village_remains_editable_when_parents_change(self):
        child = Child(pk=1, governorate_id=11, district_id=22, village='Existing village')
        registration = Registration(pk=1, child=child)
        initial_form = self.make_form(instance=registration)
        self.assertEqual(initial_form['child_village'].value(), 'Existing village')
        bound_form = self.make_form(instance=registration, data={
            'child_governorate': '12', 'child_district': '23',
            'child_village': 'Updated free-text village',
        })
        self.assertEqual(bound_form['child_village'].value(), 'Updated free-text village')
        self.assertEqual(
            bound_form.fields['child_village'].clean('Updated free-text village'),
            'Updated free-text village',
        )
