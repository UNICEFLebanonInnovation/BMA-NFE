"""Regression tests for ``alp:child_duplication_check``."""
import json
from unittest.mock import patch

from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse

from student_registration.alp.models import ALPProgram, ALPRegistration, ALPRound
from student_registration.child.models import Child
from student_registration.schools.models import School
from student_registration.students.models import Nationality
from student_registration.users.models import User

UNIQUE_ID = 'student_registration.alp.views.generate_one_unique_id'


class ChildDuplicationCheckTests(TestCase):
    def setUp(self):
        group = Group.objects.create(name='ALP_SCHOOL')
        self.school = School.objects.create(number='100', name='School A')
        self.other_school = School.objects.create(number='200', name='School B')
        self.user = User.objects.create_user(username='focal-a', password='password', school=self.school)
        self.user.groups.add(group)
        self.nationality = Nationality.objects.create(pk=1, name='Syrian', name_en='Syrian', code='SY')
        self.alp_round = ALPRound.objects.create(name='Round 2026', current_year=True)
        self.programme = ALPProgram.objects.create(name='ALP Level 1')
        self.url = reverse('alp:child_duplication_check')
        self.client.force_login(self.user)

    def identity(self, **overrides):
        data = {
            'nationality': self.nationality.pk,
            'first_name': 'Lina', 'father_name': 'Ahmad', 'last_name': 'Sayed', 'mother_fullname': 'Fatima Ali',
            'birthday_year': '2015', 'birthday_month': '5', 'birthday_day': '10', 'sex': 'Female',
        }
        data.update(overrides)
        return data

    def make_registration(self, school, unicef_id='UID-1', child=None, **extra):
        if child is None:
            child = Child.objects.create(
                first_name='Lina', father_name='Ahmad', last_name='Sayed', mother_fullname='Fatima Ali',
                gender='Female', nationality=self.nationality, unicef_id=unicef_id,
                birthday_year='2015', birthday_month='5', birthday_day='10',
            )
        return ALPRegistration.objects.create(
            child=child, school=school, round=self.alp_round, programme=self.programme, **extra
        )

    def check(self, body, unique_id='UID-1'):
        """POST ``body`` (a dict, list or raw string) with the unique-id API patched."""
        payload = body if isinstance(body, str) else json.dumps(body)
        with patch(UNIQUE_ID, return_value=unique_id) as mocked:
            response = self.client.post(self.url, data=payload, content_type='application/json')
        return response, mocked

    def result_ids(self, response):
        return [row['id'] for row in response.json()['result']]

    def test_get_is_not_allowed(self):
        self.assertEqual(self.client.get(self.url).status_code, 405)

    def test_anonymous_post_redirects_to_login(self):
        self.client.logout()

        response, mocked = self.check(self.identity())

        self.assertRedirects(response, '/?next={0}'.format(self.url), fetch_redirect_response=False)
        mocked.assert_not_called()

    def test_user_without_alp_group_is_forbidden(self):
        outsider = User.objects.create_user(username='outsider', password='password', school=self.school)
        self.client.force_login(outsider)

        response, mocked = self.check(self.identity())

        self.assertEqual(response.status_code, 403)
        mocked.assert_not_called()

    def test_identity_without_duplicate_returns_empty_result(self):
        response, mocked = self.check(self.identity(), unique_id='NO-MATCH')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'result': []})
        mocked.assert_called_once_with(
            '0', 'Lina', 'Ahmad', 'Sayed', 'Fatima Ali', '2015-5-10', 'Syrian', 'Female',
        )

    def test_json_list_body_returns_empty_result(self):
        response, mocked = self.check([self.identity()])

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'result': []})
        mocked.assert_not_called()

    def test_invalid_json_body_returns_empty_result(self):
        response, mocked = self.check('{not json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'result': []})
        mocked.assert_not_called()

    def test_unknown_nationality_skips_the_lookup(self):
        for nationality in (None, 'abc', 999):
            with self.subTest(nationality=nationality):
                response, mocked = self.check(self.identity(nationality=nationality))

                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.json(), {'result': []})
                mocked.assert_not_called()

    def test_failed_unique_id_lookup_does_not_match_children_with_id_zero(self):
        self.make_registration(self.other_school, unicef_id='0')

        response, _mocked = self.check(self.identity(), unique_id=0)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'result': []})

    def test_match_in_another_school_is_returned_with_school_name(self):
        other = self.make_registration(self.other_school)

        response, _mocked = self.check(self.identity())

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'result': [{
            'id': other.pk,
            'school__name': 'School B',
            'child__first_name': 'Lina',
            'child__father_name': 'Ahmad',
            'child__last_name': 'Sayed',
            'child__mother_fullname': 'Fatima Ali',
            'child__birthday_day': '10',
            'child__birthday_month': '5',
            'child__birthday_year': '2015',
        }]})

    def test_soft_deleted_registrations_are_not_reported(self):
        self.make_registration(self.other_school, deleted=True)

        response, _mocked = self.check(self.identity())

        self.assertEqual(response.json(), {'result': []})

    def test_non_numeric_registration_id_is_ignored(self):
        other = self.make_registration(self.other_school)

        response, _mocked = self.check(self.identity(registration_id='abc'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.result_ids(response), [other.pk])

    def test_registration_id_excludes_the_current_registrations_own_child(self):
        current = self.make_registration(self.school)
        same_child_again = self.make_registration(self.school, child=current.child)
        other = self.make_registration(self.other_school)

        response, _mocked = self.check(self.identity(registration_id=current.pk))

        self.assertEqual(self.result_ids(response), [other.pk])
        self.assertNotIn(same_child_again.pk, self.result_ids(response))

        response, _mocked = self.check(self.identity())
        self.assertEqual(sorted(self.result_ids(response)), sorted([current.pk, same_child_again.pk, other.pk]))

    def test_registration_id_of_a_registration_without_child_excludes_only_itself(self):
        orphan = ALPRegistration.objects.create(
            child=None, school=self.school, round=self.alp_round, programme=self.programme,
        )
        other = self.make_registration(self.other_school)

        response, _mocked = self.check(self.identity(registration_id=orphan.pk))

        self.assertEqual(self.result_ids(response), [other.pk])
