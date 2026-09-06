"""Regression tests for the ALP teacher form and the teacher add / edit / delete views."""
from types import SimpleNamespace

from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse

from student_registration.alp.forms import ALPTeacherForm
from student_registration.alp.models import ALPRound, ALPTeacher
from student_registration.schools.models import School
from student_registration.students.models import Training
from student_registration.users.models import User


def make_alp_school_user(username='focal', school=None, **extra):
    """Return an ALP_SCHOOL user attached to ``school`` (created when omitted)."""
    group, _ = Group.objects.get_or_create(name='ALP_SCHOOL')
    if school is None:
        school = School.objects.create(number=f'{username}-100', name=f'School of {username}')
    user = User.objects.create_user(username=username, password='password', school=school, **extra)
    user.groups.add(group)
    return user


def teacher_payload(alp_round, training, **overrides):
    data = {
        'round': alp_round.pk,
        'first_name': 'Mohamad', 'father_name': 'Ahmad', 'last_name': 'Al Sayed',
        'mother_fullname': 'Fatima Al Ali',
        'phone_number': '70-123456',
        'subjects_provided': ['arabic', 'math'],
        'registration_level': ['Level one'],
        'trainings': [training.pk],
        'extra_coaching': 'no',
    }
    data.update(overrides)
    return data


def make_teacher(school, owner, alp_round, training, **extra):
    """Create a teacher directly in the database (bypassing the form)."""
    fields = {
        'first_name': 'Mohamad', 'father_name': 'Ahmad', 'last_name': 'Al Sayed',
        'mother_fullname': 'Fatima Al Ali', 'phone_number': '70-123456',
        'subjects_provided': ['arabic'], 'registration_level': ['Level one'],
        'extra_coaching': 'no',
    }
    fields.update(extra)
    teacher = ALPTeacher.objects.create(school=school, owner=owner, round=alp_round, **fields)
    teacher.trainings.add(training)
    return teacher


class TeacherFlowBase(TestCase):
    def setUp(self):
        self.user = make_alp_school_user('focal')
        self.school = self.user.school
        self.current_round = ALPRound.objects.create(name='Round 2026', current_year=True)
        self.past_round = ALPRound.objects.create(name='Round 2020', current_year=False)
        self.training = Training.objects.create(name='Pedagogy')
        self.client.force_login(self.user)

    def round_pks(self, form):
        return sorted(form.fields['round'].queryset.values_list('pk', flat=True))


class ALPTeacherFormTests(TeacherFlowBase):
    def test_form_accepts_request_and_user_keyword_with_identical_choices(self):
        by_request = ALPTeacherForm(request=SimpleNamespace(user=self.user))
        by_user = ALPTeacherForm(user=self.user)

        self.assertEqual(by_request.user, self.user)
        self.assertEqual(by_user.user, self.user)
        self.assertEqual(
            list(by_request.fields['round'].choices),
            list(by_user.fields['round'].choices),
        )
        self.assertEqual(self.round_pks(by_request), self.round_pks(by_user))

    def test_round_choices_are_current_year_rounds_when_adding(self):
        form = ALPTeacherForm(user=self.user)

        self.assertEqual(self.round_pks(form), [self.current_round.pk])
        self.assertNotIn(self.past_round.pk, self.round_pks(form))

    def test_round_choices_include_the_instance_past_round_when_editing(self):
        other_past_round = ALPRound.objects.create(name='Round 2019', current_year=False)
        teacher = make_teacher(self.school, self.user, self.past_round, self.training)

        form = ALPTeacherForm(instance=teacher, user=self.user)

        self.assertEqual(self.round_pks(form), sorted([self.current_round.pk, self.past_round.pk]))
        self.assertNotIn(other_past_round.pk, self.round_pks(form))


class TeacherAddViewTests(TeacherFlowBase):
    def test_valid_post_creates_teacher_for_users_school(self):
        response = self.client.post(
            reverse('alp:teacher_add'), teacher_payload(self.current_round, self.training),
        )

        self.assertRedirects(response, reverse('alp:teacher_list'), fetch_redirect_response=False)
        teacher = ALPTeacher.objects.get()
        self.assertEqual(teacher.school, self.school)
        self.assertEqual(teacher.owner, self.user)
        self.assertEqual(teacher.modified_by, self.user)
        self.assertEqual(teacher.round, self.current_round)
        self.assertEqual(teacher.first_name, 'Mohamad')
        self.assertEqual(list(teacher.trainings.all()), [self.training])
        self.assertEqual(teacher.subjects_provided, ['arabic', 'math'])
        self.assertEqual(teacher.registration_level, ['Level one'])

    def test_posted_school_is_ignored_in_favour_of_users_school(self):
        other_school = School.objects.create(number='999', name='Other school')

        response = self.client.post(
            reverse('alp:teacher_add'),
            teacher_payload(self.current_round, self.training, school=other_school.pk),
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(ALPTeacher.objects.get().school, self.school)

    def test_past_round_is_not_a_valid_choice_when_adding(self):
        response = self.client.post(
            reverse('alp:teacher_add'), teacher_payload(self.past_round, self.training),
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn('round', response.context['form'].errors)
        self.assertEqual(ALPTeacher.objects.count(), 0)

    def test_extra_coaching_yes_requires_specify(self):
        response = self.client.post(
            reverse('alp:teacher_add'),
            teacher_payload(self.current_round, self.training, extra_coaching='yes'),
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn('extra_coaching_specify', response.context['form'].errors)
        self.assertEqual(ALPTeacher.objects.count(), 0)

    def test_other_teacher_assignment_requires_details(self):
        response = self.client.post(
            reverse('alp:teacher_add'),
            teacher_payload(self.current_round, self.training, teacher_assignment='other'),
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn('teacher_assignment_other', response.context['form'].errors)
        self.assertEqual(ALPTeacher.objects.count(), 0)

    def test_malformed_phone_number_is_rejected(self):
        response = self.client.post(
            reverse('alp:teacher_add'),
            teacher_payload(self.current_round, self.training, phone_number='12-3456'),
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn('phone_number', response.context['form'].errors)
        self.assertEqual(ALPTeacher.objects.count(), 0)


class TeacherEditViewTests(TeacherFlowBase):
    def test_editing_teacher_with_past_round_by_reposting_its_round_succeeds(self):
        teacher = make_teacher(self.school, self.user, self.past_round, self.training)
        url = reverse('alp:teacher_edit', kwargs={'pk': teacher.pk})

        page = self.client.get(url)
        self.assertEqual(page.status_code, 200)
        self.assertContains(page, self.past_round.name)

        response = self.client.post(url, teacher_payload(self.past_round, self.training, first_name='Ali'))

        if response.status_code == 200:
            self.assertNotContains(response, 'Select a valid choice')
        self.assertRedirects(response, reverse('alp:teacher_list'), fetch_redirect_response=False)
        teacher.refresh_from_db()
        self.assertEqual(teacher.first_name, 'Ali')
        self.assertEqual(teacher.round, self.past_round)
        self.assertEqual(teacher.owner, self.user)
        self.assertEqual(teacher.modified_by, self.user)
        self.assertEqual(ALPTeacher.objects.count(), 1)

    def test_edit_of_another_schools_teacher_returns_404(self):
        other_user = make_alp_school_user('other')
        teacher = make_teacher(other_user.school, other_user, self.current_round, self.training)
        url = reverse('alp:teacher_edit', kwargs={'pk': teacher.pk})

        self.assertEqual(self.client.get(url).status_code, 404)
        response = self.client.post(url, teacher_payload(self.current_round, self.training, first_name='Ali'))
        self.assertEqual(response.status_code, 404)
        teacher.refresh_from_db()
        self.assertEqual(teacher.first_name, 'Mohamad')


class TeacherDeleteViewTests(TeacherFlowBase):
    def test_delete_of_another_schools_teacher_returns_404(self):
        other_user = make_alp_school_user('other')
        teacher = make_teacher(other_user.school, other_user, self.current_round, self.training)
        url = reverse('alp:teacher_delete', kwargs={'pk': teacher.pk})

        self.assertEqual(self.client.get(url).status_code, 404)
        self.assertEqual(self.client.post(url).status_code, 404)
        self.assertTrue(ALPTeacher.objects.filter(pk=teacher.pk).exists())

    def test_delete_post_removes_the_teacher(self):
        teacher = make_teacher(self.school, self.user, self.current_round, self.training)
        url = reverse('alp:teacher_delete', kwargs={'pk': teacher.pk})

        self.assertEqual(self.client.get(url).status_code, 200)
        response = self.client.post(url)

        self.assertRedirects(response, reverse('alp:teacher_list'), fetch_redirect_response=False)
        self.assertFalse(ALPTeacher.objects.filter(pk=teacher.pk).exists())
        self.assertEqual(ALPTeacher.objects.count(), 0)
