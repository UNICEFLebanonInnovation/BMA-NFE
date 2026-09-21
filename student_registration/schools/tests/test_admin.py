from django.contrib import admin
from django.test import SimpleTestCase, TestCase

from student_registration.locations.models import Location, LocationType
from student_registration.schools.admin import SchoolAdmin
from student_registration.schools.models import School
from student_registration.alp.forms import ALPSchoolProfileForm


class SchoolAdminRegistrationTests(SimpleTestCase):
    def test_school_is_available_in_admin_portal(self):
        self.assertIsInstance(admin.site._registry[School], SchoolAdmin)

    def test_school_admin_fields_pass_system_checks(self):
        school_admin = admin.site._registry[School]

        self.assertEqual(school_admin.check(), [])

    def test_school_admin_fields_match_alp_school_profile(self):
        school_admin = admin.site._registry[School]

        self.assertEqual(school_admin.fields, ALPSchoolProfileForm.Meta.fields)

class SchoolAdminLocationChoicesTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        for location_type_id, name in (
            (1, 'Governorate'),
            (2, 'District'),
            (3, 'Cadaster'),
            (4, 'Other'),
        ):
            location_type = LocationType.objects.create(
                id=location_type_id,
                name=name,
            )
            Location.objects.create(
                name='{} location'.format(name),
                type=location_type,
            )

    def test_location_fields_only_offer_their_location_type(self):
        school_admin = admin.site._registry[School]
        form = school_admin.get_form(request=None)

        expected_type_ids = {
            'governorate': 1,
            'district': 2,
            'cadaster': 3,
        }
        for field_name, expected_type_id in expected_type_ids.items():
            with self.subTest(field_name=field_name):
                self.assertEqual(
                    set(form.base_fields[field_name].queryset.values_list(
                        'type_id', flat=True
                    )),
                    {expected_type_id},
                )
