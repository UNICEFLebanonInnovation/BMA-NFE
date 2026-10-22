from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.core.exceptions import ValidationError
from django.forms import Select
from django.test import SimpleTestCase

from student_registration.child.models import Child
from student_registration.locations.models import Location
from student_registration.mscc.forms import MSCCRegistrationForm
from student_registration.mscc.models import Registration


class MSCCRegistrationVillageTests(SimpleTestCase):
    """Validate village choices without requiring a database or seed locations."""

    def make_form(self, *, data=None, initial=None, instance=None):
        locations = MagicMock()
        locations.all.return_value = locations
        locations.order_by.return_value = locations
        locations.__iter__.side_effect = lambda: iter([
            SimpleNamespace(name='Village in selected district'),
            SimpleNamespace(name='Village in selected district'),
        ])
        with patch.object(Location.objects, 'filter', return_value=locations):
            return MSCCRegistrationForm(data=data, initial=initial, instance=instance)

    def registration(self, village='Legacy village'):
        child = Child(pk=1, governorate_id=11, district_id=22, village=village)
        return Registration(pk=1, child=child)

    def test_new_registration_requires_a_village_in_the_selected_district(self):
        form = self.make_form(data={
            'child_governorate': '11', 'child_district': '22',
        })
        field = form.fields['child_village']

        self.assertIsInstance(field.widget, Select)
        self.assertEqual(
            field.clean('Village in selected district'), 'Village in selected district',
        )
        for invalid in ('', 'Village from another district', '22'):
            with self.subTest(value=invalid), self.assertRaises(ValidationError):
                field.clean(invalid)
        self.assertEqual(
            [value for value, _ in field.choices if value],
            ['Village in selected district'],
        )

    def test_no_village_can_be_selected_without_both_parents(self):
        for initial in ({}, {'child_governorate': 11}, {'child_district': 22}):
            with self.subTest(initial=initial):
                field = self.make_form(initial=initial).fields['child_village']
                with self.assertRaises(ValidationError):
                    field.clean('Village in selected district')

    def test_bound_parent_values_override_initial_values(self):
        form = self.make_form(
            data={'child_governorate': '11', 'child_district': ''},
            initial={'child_governorate': 11, 'child_district': 22},
        )
        with self.assertRaises(ValidationError):
            form.fields['child_village'].clean('Village in selected district')

    def test_existing_village_is_preselected_and_preserved_in_its_original_parents(self):
        form = self.make_form(instance=self.registration())
        self.assertEqual(form['child_village'].value(), 'Legacy village')
        self.assertEqual(form.fields['child_village'].clean('Legacy village'), 'Legacy village')
        bound_form = self.make_form(instance=self.registration(), data={
            'child_governorate': '11', 'child_district': '22',
            'child_village': 'Legacy village',
        })
        self.assertEqual(
            bound_form.fields['child_village'].clean('Legacy village'), 'Legacy village',
        )

    def test_legacy_village_is_rejected_after_either_parent_changes(self):
        for governorate, district in ((12, 22), (11, 23), (12, 23)):
            with self.subTest(governorate=governorate, district=district):
                form = self.make_form(
                    instance=self.registration(),
                    data={
                        'child_governorate': str(governorate),
                        'child_district': str(district),
                    },
                )
                with self.assertRaises(ValidationError):
                    form.fields['child_village'].clean('Legacy village')

    def test_missing_legacy_village_still_requires_a_selection(self):
        form = self.make_form(instance=self.registration(village=None))
        with self.assertRaises(ValidationError):
            form.fields['child_village'].clean('')
