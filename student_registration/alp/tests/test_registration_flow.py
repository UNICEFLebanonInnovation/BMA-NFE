"""End-to-end regression tests for the ALP registration add / edit / delete flow."""
from unittest.mock import patch

from django.conf import settings
from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from student_registration.alp.models import ALPProgram, ALPRegistration, ALPRound
from student_registration.child.models import Child
from student_registration.clm.models import Disability, EducationalLevel
from student_registration.schools.models import School
from student_registration.students.models import IDType, Nationality
from student_registration.users.models import User

FORMS_UNIQUE_ID = 'student_registration.alp.forms.generate_one_unique_id'
VIEWS_UNIQUE_ID = 'student_registration.alp.views.generate_one_unique_id'


def today_iso():
    """Today's date as ISO text, safe whether or not USE_TZ is enabled."""
    today = timezone.localdate() if settings.USE_TZ else timezone.now().date()
    return today.isoformat()


def make_alp_school_user(username='focal', school=None, **extra):
    """Return an ALP_SCHOOL user attached to ``school`` (created when omitted)."""
    group, _ = Group.objects.get_or_create(name='ALP_SCHOOL')
    if school is None:
        school = School.objects.create(number=f'{username}-100', name=f'School of {username}')
    user = User.objects.create_user(username=username, password='password', school=school, **extra)
    user.groups.add(group)
    return user


def make_lookups():
    """Reference rows the ALP registration form/serializer need. Explicit pks avoid
    the id-specific branches in mscc MainForm.clean (IDType 1-6/9, Nationality 6)."""
    return {
        'nationality': Nationality.objects.create(pk=1, name='Syrian', name_en='Syrian', code='SY'),
        'id_type': IDType.objects.create(pk=7, name='Caregiver has no ID', active=True),
        'disability': Disability.objects.create(name='No disability', name_en='No'),
        'edu_level': EducationalLevel.objects.create(name='Primary'),
        'round': ALPRound.objects.create(name='Round 2026', current_year=True),
        'programme': ALPProgram.objects.create(name='ALP Level 1'),
    }


def registration_payload(lk, **overrides):
    data = {
        'child_first_name': 'Lina', 'child_father_name': 'Ahmad', 'child_last_name': 'Sayed',
        'child_mother_fullname': 'Fatima Ali', 'child_gender': 'Female',
        'child_nationality': lk['nationality'].pk,
        'child_birthday_year': '2015', 'child_birthday_month': '5', 'child_birthday_day': '10',
        'child_living_arrangement': 'Living with caregivers',
        'child_disability': lk['disability'].pk,
        'child_marital_status': 'Single', 'child_have_children': 'No',
        'child_have_sibling': 'No', 'child_mother_pregnant_expecting': 'No',
        'source_of_identification': 'Dirassa',
        'cash_support_programmes': ['None'],
        'father_educational_level': lk['edu_level'].pk,
        'mother_educational_level': lk['edu_level'].pk,
        'first_phone_owner': 'Phone Main Caregiver',
        'first_phone_number': '70-123456', 'first_phone_number_confirm': '70-123456',
        'main_caregiver': 'Mother', 'children_number_under18': 1,
        'caregiver_first_name': 'Fatima', 'caregiver_middle_name': 'Hassan',
        'caregiver_last_name': 'Ali', 'caregiver_mother_name': 'Mariam Ali',
        'have_labour': 'No',
        'id_type': lk['id_type'].pk,
        'round': lk['round'].pk, 'programme': lk['programme'].pk,
        'registration_date': '2026-09-01',
    }
    data.update(overrides)
    return data


class RegistrationFlowBase(TestCase):
    def setUp(self):
        self.lk = make_lookups()
        self.user = make_alp_school_user('focal')
        self.school = self.user.school
        self.client.force_login(self.user)

    def post_registration(self, url=None, unique_id='UID-1', **overrides):
        """POST the registration form with the unique-id API stubbed out."""
        with patch(FORMS_UNIQUE_ID, return_value=unique_id), patch(VIEWS_UNIQUE_ID, return_value=unique_id):
            return self.client.post(
                url or reverse('alp:registration_add'),
                registration_payload(self.lk, **overrides),
            )

    def add_registration(self, **overrides):
        response = self.post_registration(**overrides)
        self.assertEqual(response.status_code, 302)
        return ALPRegistration.objects.latest('pk')

    def assert_no_rows(self):
        self.assertEqual(ALPRegistration.objects.count(), 0)
        self.assertEqual(Child.objects.count(), 0)


class RegistrationAddTests(RegistrationFlowBase):
    def test_valid_post_creates_registration_and_redirects_to_child_profile(self):
        response = self.post_registration()

        registration = ALPRegistration.objects.get()
        self.assertRedirects(
            response, reverse('alp:child_profile', kwargs={'pk': registration.pk}),
            fetch_redirect_response=False,
        )
        self.assertEqual(registration.school, self.school)
        self.assertEqual(registration.owner, self.user)
        self.assertEqual(registration.modified_by, self.user)
        self.assertEqual(registration.round, self.lk['round'])
        self.assertEqual(registration.programme, self.lk['programme'])
        self.assertEqual(registration.cash_support_programmes, ['None'])
        self.assertFalse(registration.deleted)

        child = Child.objects.get()
        self.assertEqual(registration.child, child)
        self.assertEqual(child.first_name, 'Lina')
        self.assertEqual(child.nationality, self.lk['nationality'])
        self.assertEqual(child.disability, self.lk['disability'])
        self.assertEqual(child.id_type, self.lk['id_type'])
        self.assertEqual(child.unicef_id, 'UID-1')
        self.assertEqual(self.client.session['instance_id'], registration.pk)

        profile = self.client.get(response['Location'])
        self.assertEqual(profile.status_code, 200)
        self.assertContains(profile, 'Lina')

    def test_posted_school_is_replaced_with_users_school(self):
        other_school = School.objects.create(number='999', name='Other school')

        response = self.post_registration(school=other_school.pk)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(ALPRegistration.objects.get().school, self.school)

    def test_missing_cash_support_programmes_rerenders_form_without_saving(self):
        payload = registration_payload(self.lk)
        del payload['cash_support_programmes']

        with patch(FORMS_UNIQUE_ID, return_value='UID-1'):
            response = self.client.post(reverse('alp:registration_add'), payload)

        self.assertEqual(response.status_code, 200)
        self.assertIn('cash_support_programmes', response.context['form'].errors)
        self.assert_no_rows()
        self.assertNotIn('instance_id', self.client.session)

    def test_serializer_invalid_registration_date_rerenders_form_without_saving(self):
        # The Django form accepts MM/DD/YYYY, the DRF serializer only ISO dates.
        response = self.post_registration(registration_date='09/01/2026')

        self.assertEqual(response.status_code, 200)
        self.assertNotIn('Location', response)
        self.assertIn('registration_date', response.context['form'].errors)
        self.assert_no_rows()
        self.assertNotIn('instance_id', self.client.session)

    def test_serializer_invalid_post_after_earlier_save_does_not_redirect_to_previous_child(self):
        first = self.add_registration()
        self.assertEqual(self.client.session['instance_id'], first.pk)

        response = self.post_registration(child_first_name='Second', registration_date='09/01/2026')

        self.assertEqual(response.status_code, 200)
        self.assertNotIn('Location', response)
        self.assertIn('registration_date', response.context['form'].errors)
        self.assertEqual(ALPRegistration.objects.count(), 1)
        self.assertEqual(Child.objects.count(), 1)
        self.assertEqual(Child.objects.get().first_name, 'Lina')

    def test_overlong_child_first_name_reports_error_on_that_field(self):
        # Passes the form (letters only, no max_length) but exceeds Child.first_name (64).
        response = self.post_registration(child_first_name='A' * 70)

        self.assertEqual(response.status_code, 200)
        self.assertIn('child_first_name', response.context['form'].errors)
        self.assert_no_rows()
        self.assertNotIn('instance_id', self.client.session)

    def test_posted_child_id_and_owner_are_ignored(self):
        other_user = make_alp_school_user('other')
        other_child = Child.objects.create(
            first_name='Other', father_name='Person', last_name='Child', gender='Male',
        )

        response = self.post_registration(child_id=other_child.pk, owner=other_user.pk)

        self.assertEqual(response.status_code, 302)
        registration = ALPRegistration.objects.get()
        self.assertEqual(registration.owner, self.user)
        self.assertNotEqual(registration.child_id, other_child.pk)
        self.assertEqual(registration.child.first_name, 'Lina')
        self.assertEqual(Child.objects.count(), 2)
        other_child.refresh_from_db()
        self.assertEqual(other_child.first_name, 'Other')


class RegistrationEditTests(RegistrationFlowBase):
    def setUp(self):
        super().setUp()
        self.registration = self.add_registration()
        self.edit_url = reverse('alp:registration_edit', kwargs={'pk': self.registration.pk})

    def test_edit_get_renders_form_with_initial_values(self):
        response = self.client.get(self.edit_url)

        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertFalse(form.is_bound)
        initial = form.initial
        self.assertEqual(initial['child_first_name'], 'Lina')
        self.assertEqual(initial['child_mother_fullname'], 'Fatima Ali')
        self.assertEqual(str(initial['child_nationality']), str(self.lk['nationality'].pk))
        self.assertEqual(str(initial['id_type']), str(self.lk['id_type'].pk))
        self.assertEqual(str(initial['child_disability']), str(self.lk['disability'].pk))
        self.assertEqual(initial['round'], self.lk['round'].pk)
        self.assertEqual(initial['programme'], self.lk['programme'].pk)
        self.assertEqual(form.helper.form_action, self.edit_url)

    def test_edit_post_updates_child_in_place_and_keeps_original_owner(self):
        editor = make_alp_school_user('colleague', school=self.school)
        self.client.force_login(editor)
        new_programme = ALPProgram.objects.create(name='ALP Level 2')
        original_child_pk = self.registration.child_id

        response = self.post_registration(
            url=self.edit_url, child_first_name='Rana', programme=new_programme.pk,
        )

        self.assertRedirects(
            response, reverse('alp:child_profile', kwargs={'pk': self.registration.pk}),
            fetch_redirect_response=False,
        )
        self.registration.refresh_from_db()
        self.assertEqual(self.registration.child_id, original_child_pk)
        self.assertEqual(self.registration.child.first_name, 'Rana')
        self.assertEqual(self.registration.programme, new_programme)
        self.assertEqual(self.registration.school, self.school)
        self.assertEqual(self.registration.owner, self.user)
        self.assertEqual(self.registration.modified_by, editor)
        self.assertEqual(Child.objects.count(), 1)
        self.assertEqual(ALPRegistration.objects.count(), 1)
        self.assertEqual(self.client.session['instance_id'], self.registration.pk)

    def test_unique_id_lookup_failure_keeps_previous_unicef_id(self):
        Child.objects.filter(pk=self.registration.child_id).update(unicef_id='OLD')

        response = self.post_registration(url=self.edit_url, unique_id=0, child_first_name='Rana')

        self.assertEqual(response.status_code, 302)
        child = Child.objects.get()
        self.assertEqual(child.first_name, 'Rana')
        self.assertEqual(child.unicef_id, 'OLD')

    def test_registration_without_child_returns_404_on_edit(self):
        ALPRegistration.objects.filter(pk=self.registration.pk).update(child=None)

        self.assertEqual(self.client.get(self.edit_url).status_code, 404)
        response = self.post_registration(url=self.edit_url, child_first_name='Rana')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(Child.objects.get().first_name, 'Lina')

    def test_registration_without_child_returns_404_on_profile(self):
        # A registration whose child row is gone is unusable: the profile
        # answers 404 exactly like registration_edit does.
        ALPRegistration.objects.filter(pk=self.registration.pk).update(child=None)

        profile = self.client.get(reverse('alp:child_profile', kwargs={'pk': self.registration.pk}))

        self.assertEqual(profile.status_code, 404)


class RegistrationDeleteTests(RegistrationFlowBase):
    def setUp(self):
        super().setUp()
        self.registration = self.add_registration()
        self.delete_url = reverse('alp:registration_delete', kwargs={'pk': self.registration.pk})

    def test_delete_get_renders_confirmation_page(self):
        response = self.client.get(self.delete_url)

        self.assertEqual(response.status_code, 200)
        self.registration.refresh_from_db()
        self.assertFalse(self.registration.deleted)

    def test_delete_post_soft_deletes_registration_and_keeps_child(self):
        response = self.client.post(self.delete_url)

        self.assertRedirects(response, reverse('alp:registration_list'), fetch_redirect_response=False)
        self.assertEqual(ALPRegistration.objects.count(), 1)
        self.registration.refresh_from_db()
        self.assertTrue(self.registration.deleted)
        self.assertEqual(self.registration.deleted_by, self.user)
        self.assertEqual(self.registration.modified_by, self.user)
        self.assertEqual(Child.objects.count(), 1)
        self.assertEqual(self.registration.child, Child.objects.get())

    def test_soft_deleted_registration_disappears_from_every_page_and_dataset(self):
        self.client.post(self.delete_url)
        pk = {'pk': self.registration.pk}

        listing = self.client.get(reverse('alp:registration_list'))
        self.assertEqual(listing.status_code, 200)
        self.assertEqual(len(listing.context['table'].rows), 0)

        for name in ('child_profile', 'registration_edit', 'registration_delete'):
            response = self.client.get(reverse(f'alp:{name}', kwargs=pk))
            self.assertEqual(response.status_code, 404, name)
        self.assertEqual(self.client.post(self.delete_url).status_code, 404)

        pivot = self.client.get(reverse('alp:pivot_data'))
        self.assertEqual(pivot.status_code, 200)
        self.assertEqual(pivot.json(), [])

        dashboard = self.client.get(reverse('alp:alp_dashboard_data'))
        self.assertEqual(dashboard.status_code, 200)
        data = dashboard.json()
        self.assertEqual(data['gender'], [])
        self.assertEqual(data['children_per_gender'], [])
        self.assertEqual(data['children_per_round'], [])

        attendance = self.client.get(reverse('alp:load_attendance_children'), {
            'attendance_date': today_iso(),
            'round_id': self.lk['round'].pk,
            'programme': self.lk['programme'].pk,
        })
        self.assertEqual(attendance.status_code, 200)
        self.assertEqual(attendance.context['instances'], [])
        self.assertEqual(attendance.context['new_instances'], [])

    def test_active_registration_is_listed_before_deletion(self):
        listing = self.client.get(reverse('alp:registration_list'))
        self.assertEqual(len(listing.context['table'].rows), 1)

        attendance = self.client.get(reverse('alp:load_attendance_children'), {
            'attendance_date': today_iso(),
            'round_id': self.lk['round'].pk,
            'programme': self.lk['programme'].pk,
        })
        self.assertEqual(len(attendance.context['instances']), 1)
        self.assertEqual(attendance.context['instances'][0]['registration_id'], self.registration.pk)
