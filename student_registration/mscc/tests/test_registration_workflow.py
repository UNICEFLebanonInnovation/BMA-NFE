from html.parser import HTMLParser
from types import SimpleNamespace

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from student_registration.alp.forms import ALPRegistrationForm
from student_registration.child.models import Child
from student_registration.clm.models import Disability
from student_registration.mscc.forms import MSCCRegistrationForm
from student_registration.mscc.models import Registration
from student_registration.mscc.serializers import MSCCRegistrationSerializer
from student_registration.students.models import Nationality


ADDRESS = {
    'child_governorate': 'بيروت',
    'child_district': 'بيروت',
    'child_municipality': 'بلدية بيروت',
    'child_village': 'الحمرا',
    'child_street': 'شارع 12',
    'child_building_camp': 'مبنى الأمل 2 / طابق 3',
    'child_cadaster': 'منطقة رأس بيروت العقارية',
}

REMOVED_FIELDS = {
    'informed_consent', 'child_p_code', 'child_address',
    'source_of_identification', 'source_of_identification_specify',
    'partner_unique_number', 'child_living_arrangement',
    'child_marital_status', 'child_have_children', 'child_children_number',
    'main_caregiver_nationality', 'main_caregiver_nationality_other',
    'father_educational_level', 'mother_educational_level',
    'first_phone_owner', 'first_phone_number_confirm',
    'second_phone_owner', 'second_phone_number', 'second_phone_number_confirm',
    'main_caregiver', 'main_caregiver_other', 'children_number_under18',
    'caregiver_first_name', 'caregiver_middle_name', 'caregiver_last_name',
    'caregiver_mother_name', 'id_type', 'case_number', 'case_number_confirm',
    'parent_individual_case_number', 'parent_individual_case_number_confirm',
    'individual_case_number', 'individual_case_number_confirm',
    'recorded_number', 'recorded_number_confirm',
    'parent_national_number', 'parent_national_number_confirm',
    'national_number', 'national_number_confirm',
    'parent_extract_record', 'parent_extract_record_confirm',
    'parent_syrian_national_number', 'parent_syrian_national_number_confirm',
    'syrian_national_number', 'syrian_national_number_confirm',
    'parent_sop_national_number', 'parent_sop_national_number_confirm',
    'sop_national_number', 'sop_national_number_confirm',
    'parent_other_number', 'parent_other_number_confirm',
    'other_number', 'other_number_confirm',
    'have_labour', 'labour_type', 'labour_type_specify', 'labour_hours',
    'labour_weekly_income', 'labour_condition', 'cash_support_programmes',
    'child_have_sibling', 'child_siblings_have_disability',
    'child_mother_pregnant_expecting',
}


class FormControls(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.controls = {}
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        if tag in ('input', 'select', 'textarea'):
            attrs = dict(attrs)
            if attrs.get('name'):
                self.controls[attrs['name']] = attrs


@override_settings(LANGUAGE_CODE='en')
class MSCCRegistrationWorkflowTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.nationality = Nationality.objects.create(
            pk=1001, name='Test nationality', name_en='Test nationality',
        )
        cls.disability = Disability.objects.create(name='None', name_en='None')
        cls.user = get_user_model().objects.create_user(username='mscc-registration')
        cls.user.groups.add(Group.objects.get_or_create(name='MSCC')[0])

    def setUp(self):
        self.client.force_login(self.user)

    def registration_data(self, **updates):
        data = {
            'child_first_name': 'Ali',
            'child_father_name': 'Ahmad',
            'child_last_name': 'Hassan',
            'child_mother_fullname': 'Mariam',
            'child_gender': 'Male',
            'child_nationality': str(self.nationality.pk),
            'child_birthday_year': '2015',
            'child_birthday_month': '3',
            'child_birthday_day': '12',
            'child_disability': str(self.disability.pk),
            'first_phone_number': '70-123456',
            'nfe_programme': 'BLN',
            **ADDRESS,
        }
        data.update(updates)
        return data

    def create_registration(self):
        response = self.client.post(
            reverse('mscc:child_add'), self.registration_data(),
        )
        self.assertEqual(response.status_code, 302)
        return Registration.objects.get()

    def test_hidden_fields_are_excluded_and_primary_phone_remains_required(self):
        form = MSCCRegistrationForm()

        self.assertFalse(REMOVED_FIELDS.intersection(form.fields))
        self.assertTrue(form.fields['first_phone_number'].required)
        self.assertTrue(set(ADDRESS).issubset(form.fields))

    def test_each_address_field_and_programme_require_a_nonblank_value(self):
        for field in (*ADDRESS, 'nfe_programme'):
            for value in (None, '', '   '):
                with self.subTest(field=field, value=value):
                    data = self.registration_data()
                    if value is None:
                        del data[field]
                    else:
                        data[field] = value
                    form = MSCCRegistrationForm(data=data)

                    self.assertFalse(form.is_valid())
                    self.assertIn(field, form.errors)

    def test_bln_and_dirasa_are_the_only_nonblank_programme_choices(self):
        form = MSCCRegistrationForm()

        self.assertTrue(form.fields['nfe_programme'].required)
        self.assertEqual(
            {value for value, label in form.fields['nfe_programme'].choices if value},
            {'BLN', 'DIRASA'},
        )
        for programme in ('BLN', 'DIRASA'):
            with self.subTest(programme=programme):
                form = MSCCRegistrationForm(
                    data=self.registration_data(nfe_programme=programme),
                )
                self.assertTrue(form.is_valid(), form.errors.as_json())

    def test_invalid_programme_is_rejected(self):
        form = MSCCRegistrationForm(data=self.registration_data(nfe_programme='ALP'))

        self.assertFalse(form.is_valid())
        self.assertIn('nfe_programme', form.errors)

    def test_remaining_birthdate_and_phone_validation_is_enforced(self):
        for updates, error in (
            ({'child_birthday_month': '2', 'child_birthday_day': '31'}, 'child_birthday_year'),
            ({'first_phone_number': 'not a phone number'}, 'first_phone_number'),
            ({'first_phone_number': ''}, 'first_phone_number'),
        ):
            with self.subTest(updates=updates):
                form = MSCCRegistrationForm(data=self.registration_data(**updates))
                self.assertFalse(form.is_valid())
                self.assertIn(error, form.errors)

    def test_serializer_also_rejects_missing_address_and_invalid_programme(self):
        for field in ADDRESS:
            with self.subTest(field=field):
                data = self.registration_data()
                del data[field]
                serializer = MSCCRegistrationSerializer(data=data)
                self.assertFalse(serializer.is_valid())
                self.assertIn(field, serializer.errors)

        serializer = MSCCRegistrationSerializer(
            data=self.registration_data(nfe_programme='ALP'),
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn('nfe_programme', serializer.errors)

    def test_create_saves_separate_address_fields_and_both_programme_options(self):
        for programme in ('BLN', 'DIRASA'):
            with self.subTest(programme=programme):
                response = self.client.post(
                    reverse('mscc:child_add'),
                    self.registration_data(nfe_programme=programme),
                )
                self.assertEqual(response.status_code, 302)
                registration = Registration.objects.order_by('-pk').first()
                self.assertEqual(
                    response.url,
                    reverse('mscc:child_profile', args=[registration.pk]),
                )
                self.assertEqual(registration.nfe_programme, programme)
                self.assertEqual(registration.child.first_phone_number, '70-123456')
                for field, value in ADDRESS.items():
                    self.assertEqual(getattr(registration.child, field[6:]), value)

        self.assertEqual(Registration.objects.count(), 2)
        self.assertEqual(Child.objects.count(), 2)

    def test_missing_mandatory_address_does_not_create_a_partial_record(self):
        data = self.registration_data()
        del data['child_cadaster']

        response = self.client.post(reverse('mscc:child_add'), data)

        self.assertEqual(response.status_code, 200)
        self.assertIn('child_cadaster', response.context['form'].errors)
        self.assertFalse(Registration.objects.exists())
        self.assertFalse(Child.objects.exists())

    def test_edit_roundtrip_prefills_and_updates_address_programme_and_phone(self):
        registration = self.create_registration()
        url = reverse('mscc:child_edit', args=[registration.pk])

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertFalse(form.is_bound)
        for field, value in ADDRESS.items():
            self.assertEqual(form[field].value(), value)
        self.assertEqual(form['nfe_programme'].value(), 'BLN')

        response = self.client.post(url, self.registration_data(
            child_street='شارع 24', child_building_camp='مخيم 7',
            nfe_programme='DIRASA', first_phone_number='71-654321',
        ))

        self.assertEqual(response.status_code, 302)
        registration.refresh_from_db()
        self.assertEqual(registration.nfe_programme, 'DIRASA')
        self.assertEqual(registration.child.street, 'شارع 24')
        self.assertEqual(registration.child.building_camp, 'مخيم 7')
        self.assertEqual(registration.child.first_phone_number, '71-654321')
        self.assertEqual(Registration.objects.count(), 1)
        self.assertEqual(Child.objects.count(), 1)

    def test_edit_preserves_removed_data_even_with_forged_post_and_upload(self):
        registration = self.create_registration()
        child = registration.child
        existing_child_values = {
            'address': 'Legacy full address', 'p_code': 'LB-01-001',
            'living_arrangement': 'Living with caregivers',
            'marital_status': 'Single', 'have_children': 'Yes', 'children_number': 1,
            'caregiver_first_name': 'Saved caregiver', 'main_caregiver': 'Other',
            'main_caregiver_other': 'Saved guardian', 'first_phone_owner': 'Family Member',
            'first_phone_number_confirm': '70-123456', 'second_phone_number': '03-654321',
            'national_number': '123456789012', 'case_number': 'Saved case',
            'have_sibling': 'Yes',
        }
        for name, value in existing_child_values.items():
            setattr(child, name, value)
        child.save()
        existing_registration_values = {
            'partner_unique_number': 'Saved partner child number',
            'source_of_identification': 'Other Sources',
            'source_of_identification_specify': 'Saved referral',
            'have_labour': 'Yes - Morning', 'labour_type': 'Construction',
            'labour_hours': 12, 'labour_condition': ['Other'],
            'cash_support_programmes': ['None'],
            'informed_consent': 'uploads/mscc_registration/informed_consent/saved.pdf',
        }
        for name, value in existing_registration_values.items():
            setattr(registration, name, value)
        registration.save()

        data = self.registration_data(nfe_programme='DIRASA')
        data.update({name: 'forged value' for name in REMOVED_FIELDS})
        data['informed_consent'] = SimpleUploadedFile('forged.txt', b'forged consent')

        response = self.client.post(
            reverse('mscc:child_edit', args=[registration.pk]), data,
        )

        self.assertEqual(response.status_code, 302)
        registration.refresh_from_db()
        child.refresh_from_db()
        self.assertEqual(registration.nfe_programme, 'DIRASA')
        for name, value in existing_child_values.items():
            with self.subTest(child_field=name):
                self.assertEqual(getattr(child, name), value)
        for name, value in existing_registration_values.items():
            with self.subTest(registration_field=name):
                self.assertEqual(str(registration.informed_consent) if name == 'informed_consent'
                                 else getattr(registration, name), value)

    def test_legacy_records_can_remain_null_until_registration_is_edited(self):
        child = Child.objects.create(
            first_name='Legacy', father_name='Ahmad', last_name='Hassan',
            mother_fullname='Mariam', nationality=self.nationality, gender='Male',
            birthday_year='2015', birthday_month='3', birthday_day='12',
            address='Legacy home address',
        )
        registration = Registration.objects.create(child=child, owner=self.user)
        child.refresh_from_db()
        registration.refresh_from_db()

        self.assertIsNone(registration.nfe_programme)
        for field in ADDRESS:
            self.assertIsNone(getattr(child, field[6:]))

        response = self.client.get(reverse('mscc:child_edit', args=[registration.pk]))
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertFalse(form.is_bound)
        self.assertFalse(form.errors)
        self.assertEqual(form['child_first_name'].value(), 'Legacy')
        self.assertFalse(form['nfe_programme'].value())
        self.assertFalse(form['child_governorate'].value())

    def test_rendered_registration_omits_sections_and_has_required_new_controls(self):
        response = self.client.get(reverse('mscc:child_add'))

        self.assertEqual(response.status_code, 200)
        controls = FormControls(response.content.decode()).controls
        self.assertFalse(REMOVED_FIELDS.intersection(controls))
        self.assertIn('first_phone_number', controls)
        for field in (*ADDRESS, 'nfe_programme'):
            with self.subTest(field=field):
                self.assertIn(field, controls)
                self.assertIn('required', controls[field])
        self.assertNotContains(response, 'Identification Documentation')
        self.assertNotContains(response, 'Labour &amp; Vulnerability')

    def test_mscc_overview_omits_beneficiary_list_and_attendance_actions(self):
        response = self.client.get(reverse('landing_page'))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Beneficiary List')
        self.assertNotContains(response, 'Track Attendance')
        self.assertContains(response, reverse('mscc:child_add'))

    def test_alp_keeps_its_existing_fields_without_mscc_requirements(self):
        form = ALPRegistrationForm(request=SimpleNamespace(user=self.user))

        for field in (
            'child_address', 'source_of_identification', 'partner_unique_number',
            'child_living_arrangement', 'child_marital_status', 'child_have_children',
            'caregiver_first_name', 'first_phone_number_confirm', 'id_type', 'have_labour',
        ):
            with self.subTest(field=field):
                self.assertIn(field, form.fields)
        self.assertFalse(set(ADDRESS).intersection(form.fields))
        self.assertNotIn('nfe_programme', form.fields)
        self.assertTrue(form.fields['have_labour'].required)

    def test_alp_overview_keeps_beneficiary_list_and_attendance_actions(self):
        self.user.groups.add(Group.objects.get_or_create(name='ALP_SCHOOL')[0])

        response = self.client.get(reverse('alp:landing_page'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Beneficiary List')
        self.assertContains(response, 'Track Attendance')
        self.assertContains(response, reverse('alp:registration_list'))
        self.assertContains(response, reverse('alp:attendance_list'))
