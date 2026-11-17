from django.core.exceptions import ValidationError
from django.forms import ChoiceField, Select
from django.test import TestCase, override_settings

from student_registration.child.models import Child
from student_registration.locations.models import Location, LocationType
from student_registration.mscc.forms import MSCCRegistrationForm
from student_registration.mscc.models import Registration
from student_registration.mscc.serializers import MSCCRegistrationSerializer


@override_settings(LANGUAGE_CODE='en')
class MSCCRegistrationVillageTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        governorate_type = LocationType.objects.create(pk=1, name='Governorate')
        district_type = LocationType.objects.create(pk=2, name='District')
        cls.beirut = Location.objects.create(type=governorate_type, name='بيروت', name_en='Beirut')
        cls.beirut_district = Location.objects.create(
            type=district_type, name='بيروت', name_en='Beirut', parent=cls.beirut,
        )
        cls.mount_lebanon = Location.objects.create(
            type=governorate_type, name='جبل لبنان', name_en='Mount Lebanon',
        )
        cls.metn = Location.objects.create(
            type=district_type, name='المتن', name_en='Metn', parent=cls.mount_lebanon,
        )

    def make_form(self, *, governorate=None, district=None, village='achrafieh', instance=None):
        return MSCCRegistrationForm(data={
            'child_governorate': str((governorate or self.beirut).pk),
            'child_district': str((district or self.beirut_district).pk),
            'child_village': village,
        }, instance=instance)

    def test_village_is_a_required_dropdown_of_the_selected_district(self):
        field = self.make_form().fields['child_village']

        self.assertIsInstance(field, ChoiceField)
        self.assertIsInstance(field.widget, Select)
        self.assertTrue(field.required)
        self.assertEqual(field.clean('achrafieh'), 'achrafieh')
        self.assertEqual(field.clean('ras_beirut'), 'ras_beirut')
        for invalid in ('', '   ', 'Achrafieh', 'قرية غير مدرجة', 'jdeideh'):
            with self.subTest(value=invalid), self.assertRaises(ValidationError):
                field.clean(invalid)

    def test_changing_district_replaces_village_choices_and_rejects_stale_selection(self):
        field = self.make_form(
            governorate=self.mount_lebanon, district=self.metn,
        ).fields['child_village']

        self.assertEqual(field.clean('jdeideh'), 'jdeideh')
        with self.assertRaises(ValidationError):
            field.clean('achrafieh')

    def test_villages_are_unavailable_without_valid_linked_parents(self):
        selections = (
            {},
            {'child_governorate': str(self.beirut.pk)},
            {'child_district': str(self.beirut_district.pk)},
            {'child_governorate': 'not-a-location', 'child_district': str(self.beirut_district.pk)},
            {'child_governorate': str(self.beirut.pk), 'child_district': str(self.metn.pk)},
        )
        for data in selections:
            with self.subTest(data=data):
                field = MSCCRegistrationForm(data=data).fields['child_village']
                self.assertFalse([value for value, label in field.choices if value])
                with self.assertRaises(ValidationError):
                    field.clean('achrafieh')

    def test_saved_codes_and_exact_legacy_names_prefill_the_same_village_code(self):
        for value in ('achrafieh', 'Achrafieh', 'الأشرفية'):
            with self.subTest(value=value):
                child = Child.objects.create(
                    governorate=self.beirut, district=self.beirut_district, village=value,
                )
                registration = Registration.objects.create(child=child)
                form = MSCCRegistrationForm(instance=registration)

                self.assertEqual(form['child_village'].value(), 'achrafieh')
                self.assertEqual(MSCCRegistrationSerializer(registration).data['child_village'], 'achrafieh')
                child.refresh_from_db()
                self.assertEqual(child.village, value)

    def test_unknown_legacy_text_is_preserved_until_a_valid_village_is_selected(self):
        child = Child.objects.create(
            governorate=self.beirut, district=self.beirut_district,
            village='Unlisted legacy village',
        )
        registration = Registration.objects.create(child=child)
        form = MSCCRegistrationForm(instance=registration)

        self.assertFalse(form['child_village'].value())
        self.assertNotIn(child.village, dict(form.fields['child_village'].choices))
        self.assertEqual(MSCCRegistrationSerializer(registration).data['child_village'], child.village)
        child.refresh_from_db()
        self.assertEqual(child.village, 'Unlisted legacy village')
