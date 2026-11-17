from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from student_registration.alp.forms import ALPSchoolProfileForm
from student_registration.locations.models import Location, LocationType
from student_registration.schools.models import School
from student_registration.users.models import User


class SchoolProfileViewTests(TestCase):
    def setUp(self):
        self.school = School.objects.create(
            number='100', name='Old name', programs=['ALP']
        )
        group = Group.objects.create(name='ALP_SCHOOL')
        self.user = User.objects.create_user(
            username='focal-point', password='password', school=self.school
        )
        self.user.groups.add(group)
        self.client.force_login(self.user)

    def profile_data(self, **overrides):
        data = {
            'number': self.school.number,
            'name': self.school.name,
            'provided_packages': ['Education'],
            'offer_digital_learning': 'yes',
            'have_digital_hub': 'no',
            'admin_staff_number': 2,
            'neaby_phcc': 'Nearby clinic',
        }
        data.update(overrides)
        return data

    def test_nearby_phcc_name_is_optional(self):
        self.assertFalse(ALPSchoolProfileForm().fields['neaby_phcc'].required)

    def test_phone_number_uses_generic_label_and_numeric_input_hints(self):
        field = ALPSchoolProfileForm().fields['land_phone_number']

        self.assertEqual(field.label, 'Phone number')
        self.assertEqual(field.widget.attrs['inputmode'], 'numeric')
        self.assertEqual(field.widget.attrs['pattern'], '[0-9]+')

    def test_phone_number_accepts_digits_only(self):
        field = ALPSchoolProfileForm().fields['land_phone_number']

        self.assertEqual(field.clean('01234567'), '01234567')
        for invalid_value in ('01-234567', '+9611234567', 'phone'):
            with self.subTest(invalid_value=invalid_value):
                with self.assertRaises(ValidationError):
                    field.clean(invalid_value)

    def test_school_email_uses_email_input_with_format_placeholder(self):
        field = ALPSchoolProfileForm().fields['email']

        self.assertEqual(field.widget.input_type, 'email')
        self.assertEqual(
            field.widget.attrs['placeholder'],
            'Format: school@email.com',
        )

    def test_school_email_requires_a_valid_email_format(self):
        field = ALPSchoolProfileForm().fields['email']

        self.assertEqual(field.clean('school@example.com'), 'school@example.com')
        with self.assertRaisesMessage(ValidationError, 'Enter a valid email address.'):
            field.clean('not-an-email')

    def test_school_identifiers_are_read_only(self):
        form = ALPSchoolProfileForm(instance=self.school)

        for field_name in ('number', 'name'):
            with self.subTest(field_name=field_name):
                self.assertTrue(form.fields[field_name].disabled)
                self.assertTrue(
                    form.fields[field_name].widget.attrs['readonly']
                )

    def test_focal_point_can_view_school_edit_form(self):
        response = self.client.get(reverse('alp:school_profile'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="name"')
        self.assertContains(response, self.school.name)
        self.assertContains(response, 'name="operating_shift"')
        self.assertContains(response, 'Public School')
        self.assertContains(response, 'Morning shift')
        self.assertContains(response, 'Afternoon shift')
        self.assertNotContains(response, 'School Capacity')
        self.assertNotContains(response, 'name="registration_level"')
        self.assertNotContains(response, 'name="school_capacity"')
        self.assertContains(response, 'Provided Services')
        self.assertContains(response, 'name="provided_packages"')
        self.assertNotContains(response, 'name="programs"')
        self.assertContains(response, 'name="offer_digital_learning"')
        self.assertContains(
            response, 'Does the school offer digital learning services?'
        )
        self.assertContains(response, 'name="have_digital_hub"')
        self.assertContains(response, 'Does the school have a digital hub?')
        self.assertContains(response, 'name="admin_staff_number"')
        self.assertContains(
            response,
            '# of staff assigned under the ALP programme within the school, '
            'including teaching and admin staff',
        )
        self.assertContains(response, 'name="neaby_phcc"')

    def test_focal_point_can_only_update_assigned_school(self):
        other_school = School.objects.create(number='200', name='Other school')

        response = self.client.post(reverse('alp:school_profile'), self.profile_data(
            number='999',
            name='Updated name',
            type='Public School',
            operating_shift='afternoon shift',
        ))

        self.assertRedirects(response, reverse('alp:school_profile'))
        self.school.refresh_from_db()
        other_school.refresh_from_db()
        self.assertEqual(self.school.number, '100')
        self.assertEqual(self.school.name, 'Old name')
        self.assertEqual(self.school.type, 'Public School')
        self.assertEqual(self.school.operating_shift, 'afternoon shift')
        self.assertEqual(self.school.provided_packages, ['Education'])
        self.assertEqual(self.school.programs, ['ALP'])
        self.assertEqual(self.school.offer_digital_learning, 'yes')
        self.assertEqual(self.school.have_digital_hub, 'no')
        self.assertEqual(self.school.admin_staff_number, 2)
        self.assertEqual(self.school.neaby_phcc, 'Nearby clinic')
        self.assertEqual(other_school.name, 'Other school')
        self.assertEqual(self.school.modified_by, self.user)

    def test_user_without_assigned_school_cannot_open_profile(self):
        self.user.school = None
        self.user.save(update_fields=['school'])

        response = self.client.get(reverse('alp:school_profile'))

        self.assertEqual(response.status_code, 403)

    def test_location_fields_only_show_linked_choices(self):
        location_type = LocationType.objects.create(name='Administrative area')
        governorate = Location.objects.create(name='Governorate', type=location_type)
        other_governorate = Location.objects.create(
            name='Other governorate', type=location_type
        )
        district = Location.objects.create(
            name='District', type=location_type, parent=governorate
        )
        Location.objects.create(
            name='Other district', type=location_type, parent=other_governorate
        )
        cadaster = Location.objects.create(
            name='Cadaster', type=location_type, parent=district
        )
        self.school.governorate = governorate
        self.school.district = district
        self.school.cadaster = cadaster
        self.school.save()

        response = self.client.get(reverse('alp:school_profile'))

        self.assertQuerySetEqual(
            response.context['form'].fields['district'].queryset,
            [district],
        )
        self.assertQuerySetEqual(
            response.context['form'].fields['cadaster'].queryset,
            [cadaster],
        )
        self.assertContains(response, reverse('schools:load_districts'))
        self.assertContains(response, reverse('schools:load_cadasters'))
