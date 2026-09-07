"""Regression tests for ALP grading: ``ALPGradingDynamicForm``, ``grading_add`` and ``grading_edit``."""
from types import SimpleNamespace

from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse

from student_registration.alp.forms import ALPGradingDynamicForm
from student_registration.alp.models import (
    ALPGrading,
    ALPGradingDefinition,
    ALPProgram,
    ALPRegistration,
    ALPRound,
)
from student_registration.child.models import Child
from student_registration.schools.models import School
from student_registration.users.models import User


# --------------------------------------------------------------------------- helpers

def make_alp_school_user(username='focal', school=None, **extra):
    """Return an ALP_SCHOOL user attached to ``school`` (created when omitted)."""
    group, _ = Group.objects.get_or_create(name='ALP_SCHOOL')
    if school is None:
        school = School.objects.create(number=f'{username}-100', name=f'School of {username}')
    user = User.objects.create_user(username=username, password='password', school=school, **extra)
    user.groups.add(group)
    return user


def make_child(first_name='Lina'):
    return Child.objects.create(
        first_name=first_name, father_name='Ahmad', last_name='Sayed', mother_fullname='Fatima Ali',
        gender='Female', birthday_year='2015', birthday_month='5', birthday_day='10',
    )


def make_registration(school, round_, programme, owner=None, first_name='Lina', **extra):
    return ALPRegistration.objects.create(
        school=school, child=make_child(first_name), round=round_, programme=programme, owner=owner, **extra,
    )


class GradingTestCase(TestCase):
    def setUp(self):
        self.round = ALPRound.objects.create(name='Round 2026', current_year=True)
        self.programme = ALPProgram.objects.create(name='ALP Level 1')
        self.user = make_alp_school_user('focal')
        self.school = self.user.school
        self.registration = make_registration(self.school, self.round, self.programme, owner=self.user)
        self.arabic = ALPGradingDefinition.objects.create(material='Arabic', min_grade=0, max_grade=20)
        self.math = ALPGradingDefinition.objects.create(material='Math', min_grade=0, max_grade=20)
        self.client.force_login(self.user)

    def field(self, definition):
        return f'grade_{definition.pk}'

    def payload(self, registration=None, **grades):
        data = {'registration': (registration or self.registration).pk}
        for definition, value in grades.items():
            data[self.field(getattr(self, definition))] = value
        return data

    def other_registration(self, username='other', **extra):
        other_user = make_alp_school_user(username)
        return make_registration(other_user.school, self.round, self.programme, owner=other_user,
                                 first_name='Foreign', **extra)


# --------------------------------------------------------------------------- registration choices

class GradingRegistrationChoicesTests(GradingTestCase):
    def setUp(self):
        super().setUp()
        self.foreign = self.other_registration()
        self.deleted = make_registration(self.school, self.round, self.programme, owner=self.user,
                                         first_name='Deleted', deleted=True, deleted_by=self.user)

    def test_form_with_user_kwarg_limits_choices_to_active_school_registrations(self):
        form = ALPGradingDynamicForm(user=self.user)

        self.assertQuerySetEqual(form.fields['registration'].queryset, [self.registration])

    def test_form_with_request_kwarg_limits_choices_to_active_school_registrations(self):
        form = ALPGradingDynamicForm(request=SimpleNamespace(user=self.user))

        self.assertQuerySetEqual(form.fields['registration'].queryset, [self.registration])

    def test_add_view_only_offers_active_school_registrations(self):
        response = self.client.get(reverse('alp:grading_add'))

        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(response.context['form'].fields['registration'].queryset, [self.registration])
        self.assertContains(
            response,
            f'<option value="{self.registration.pk}">Registration {self.registration.pk} for Lina Ahmad Sayed</option>',
            html=True,
        )
        self.assertNotContains(response, 'Foreign Ahmad Sayed')
        self.assertNotContains(response, 'Deleted Ahmad Sayed')

    def test_posting_another_schools_registration_is_rejected(self):
        response = self.client.post(reverse('alp:grading_add'), self.payload(registration=self.foreign, arabic=10))

        self.assertEqual(response.status_code, 200)
        self.assertIn('registration', response.context['form'].errors)
        self.assertEqual(ALPGrading.objects.count(), 0)

    def test_posting_a_soft_deleted_registration_is_rejected(self):
        response = self.client.post(reverse('alp:grading_add'), self.payload(registration=self.deleted, arabic=10))

        self.assertEqual(response.status_code, 200)
        self.assertIn('registration', response.context['form'].errors)
        self.assertEqual(ALPGrading.objects.count(), 0)


# --------------------------------------------------------------------------- grading_add

class GradingAddViewTests(GradingTestCase):
    def test_get_lists_a_grade_field_per_definition(self):
        response = self.client.get(reverse('alp:grading_add'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context['form'].fields),
                         ['registration', self.field(self.arabic), self.field(self.math)])
        self.assertContains(response, 'New Grading')
        self.assertContains(response, f'name="{self.field(self.arabic)}"')
        self.assertContains(response, f'name="{self.field(self.math)}"')
        self.assertContains(response, 'Arabic')
        self.assertContains(response, 'Math')

    def test_post_creates_a_grading_owned_by_the_user(self):
        response = self.client.post(reverse('alp:grading_add'), self.payload(arabic=15, math=8))

        self.assertRedirects(response, reverse('alp:registration_list'), fetch_redirect_response=False)
        grading = ALPGrading.objects.get()
        self.assertEqual(grading.registration, self.registration)
        self.assertEqual(grading.owner, self.user)
        self.assertEqual(grading.grading_data, {str(self.arabic.pk): 15, str(self.math.pk): 8})

    def test_omitted_grades_are_not_stored(self):
        response = self.client.post(reverse('alp:grading_add'), self.payload(arabic=15))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(ALPGrading.objects.get().grading_data, {str(self.arabic.pk): 15})

    def test_value_above_max_grade_is_rejected(self):
        response = self.client.post(reverse('alp:grading_add'), self.payload(arabic=25, math=8))

        self.assertEqual(response.status_code, 200)
        errors = response.context['form'].errors
        self.assertIn(self.field(self.arabic), errors)
        self.assertNotIn(self.field(self.math), errors)
        self.assertEqual(ALPGrading.objects.count(), 0)

    def test_value_below_min_grade_is_rejected(self):
        response = self.client.post(reverse('alp:grading_add'), self.payload(arabic=-1))

        self.assertEqual(response.status_code, 200)
        self.assertIn(self.field(self.arabic), response.context['form'].errors)
        self.assertEqual(ALPGrading.objects.count(), 0)

    def test_non_numeric_grade_is_rejected(self):
        response = self.client.post(reverse('alp:grading_add'), self.payload(arabic='abc'))

        self.assertEqual(response.status_code, 200)
        self.assertIn(self.field(self.arabic), response.context['form'].errors)
        self.assertEqual(ALPGrading.objects.count(), 0)

    def test_anonymous_is_redirected_to_login(self):
        self.client.logout()
        url = reverse('alp:grading_add')

        self.assertRedirects(self.client.get(url), f'/?next={url}', fetch_redirect_response=False)
        self.assertRedirects(self.client.post(url, self.payload(arabic=15)), f'/?next={url}',
                             fetch_redirect_response=False)
        self.assertEqual(ALPGrading.objects.count(), 0)

    def test_user_without_alp_group_is_forbidden(self):
        self.client.force_login(User.objects.create_user('outsider', password='password', school=self.school))

        self.assertEqual(self.client.get(reverse('alp:grading_add')).status_code, 403)
        self.assertEqual(self.client.post(reverse('alp:grading_add'), self.payload(arabic=15)).status_code, 403)
        self.assertEqual(ALPGrading.objects.count(), 0)

    def test_superuser_is_forbidden(self):
        self.client.force_login(User.objects.create_superuser('root', 'r@x.com', 'password', school=self.school))

        self.assertEqual(self.client.get(reverse('alp:grading_add')).status_code, 403)
        self.assertEqual(self.client.post(reverse('alp:grading_add'), self.payload(arabic=15)).status_code, 403)
        self.assertEqual(ALPGrading.objects.count(), 0)

    def test_alp_user_without_school_is_forbidden(self):
        User.objects.filter(pk=self.user.pk).update(school=None)

        self.assertEqual(self.client.get(reverse('alp:grading_add')).status_code, 403)
        self.assertEqual(self.client.post(reverse('alp:grading_add'), self.payload(arabic=15)).status_code, 403)
        self.assertEqual(ALPGrading.objects.count(), 0)


# --------------------------------------------------------------------------- grading_edit

class GradingEditViewTests(GradingTestCase):
    def setUp(self):
        super().setUp()
        self.grading = ALPGrading.objects.create(
            registration=self.registration,
            grading_data={str(self.arabic.pk): 15, str(self.math.pk): 8},
            owner=self.user,
        )
        self.url = reverse('alp:grading_edit', kwargs={'pk': self.grading.pk})

    def test_get_is_prefilled_from_grading_data(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertEqual(form.instance, self.grading)
        self.assertEqual(form.fields[self.field(self.arabic)].initial, 15)
        self.assertEqual(form.fields[self.field(self.math)].initial, 8)
        self.assertContains(response, 'Edit Grading')
        self.assertContains(response, f'name="{self.field(self.arabic)}" value="15"')
        self.assertContains(response, f'name="{self.field(self.math)}" value="8"')
        self.assertContains(response, f'<option value="{self.registration.pk}" selected>'
                                      f'Registration {self.registration.pk} for Lina Ahmad Sayed</option>', html=True)

    def test_post_updates_grading_data_in_place(self):
        response = self.client.post(self.url, self.payload(arabic=18, math=9))

        self.assertRedirects(response, reverse('alp:registration_list'), fetch_redirect_response=False)
        self.assertEqual(ALPGrading.objects.count(), 1)
        self.grading.refresh_from_db()
        self.assertEqual(self.grading.grading_data, {str(self.arabic.pk): 18, str(self.math.pk): 9})
        self.assertEqual(self.grading.registration, self.registration)
        self.assertEqual(self.grading.owner, self.user)

    def test_value_above_max_grade_is_rejected_on_edit(self):
        response = self.client.post(self.url, self.payload(arabic=21, math=9))

        self.assertEqual(response.status_code, 200)
        self.assertIn(self.field(self.arabic), response.context['form'].errors)
        self.grading.refresh_from_db()
        self.assertEqual(self.grading.grading_data, {str(self.arabic.pk): 15, str(self.math.pk): 8})

    def test_another_schools_grading_is_not_found(self):
        self.client.force_login(make_alp_school_user('other'))

        self.assertEqual(self.client.get(self.url).status_code, 404)
        self.assertEqual(self.client.post(self.url, self.payload(arabic=1)).status_code, 404)
        self.grading.refresh_from_db()
        self.assertEqual(self.grading.grading_data, {str(self.arabic.pk): 15, str(self.math.pk): 8})

    def test_unknown_or_non_numeric_pk_is_not_found(self):
        self.assertEqual(self.client.get(reverse('alp:grading_edit', kwargs={'pk': self.grading.pk + 999})).status_code,
                         404)
        self.assertEqual(self.client.get('/alp/grading/edit/abc/').status_code, 404)

    def test_superuser_is_forbidden(self):
        self.client.force_login(User.objects.create_superuser('root', 'r@x.com', 'password', school=self.school))

        self.assertEqual(self.client.get(self.url).status_code, 403)
        self.assertEqual(self.client.post(self.url, self.payload(arabic=1)).status_code, 403)
        self.grading.refresh_from_db()
        self.assertEqual(self.grading.grading_data, {str(self.arabic.pk): 15, str(self.math.pk): 8})

    def test_alp_user_without_school_is_forbidden(self):
        User.objects.filter(pk=self.user.pk).update(school=None)

        self.assertEqual(self.client.get(self.url).status_code, 403)
        self.assertEqual(self.client.post(self.url, self.payload(arabic=1)).status_code, 403)
