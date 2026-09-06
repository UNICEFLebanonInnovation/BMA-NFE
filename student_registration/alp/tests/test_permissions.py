"""Access matrix for every URL of the ALP app.

Covers anonymous, logged-in non-ALP, staff, ALP focal point, superuser and
"ALP user without a school" access, the numeric-only pk routes and the school
boundary between two focal points.
"""
import codecs
import json
from unittest.mock import patch

from django.conf import settings
from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import NoReverseMatch, reverse
from django.utils import timezone

from student_registration.alp import urls as alp_urls
from student_registration.alp.models import (
    ALPGrading, ALPGradingDefinition, ALPProgram, ALPRegistration, ALPRound, ALPTeacher,
)
from student_registration.child.models import Child
from student_registration.schools.models import School
from student_registration.users.models import User

LOGIN_URL = '/'

# Every ALP url that answers a GET (HTML page or JSON) for an ALP focal point.
PAGE_VIEWS = (
    'registration_list', 'registration_add', 'registration_edit', 'registration_delete', 'child_profile',
    'teacher_list', 'teacher_add', 'teacher_edit', 'teacher_delete',
    'attendance_list', 'load_attendance_children', 'teacher_attendance_list', 'load_attendance_teachers',
    'grading_add', 'grading_edit', 'school_profile',
    'dashboard_registration', 'dashboard_teacher', 'dashboard_teacher_data', 'dashboard_attendance',
    'dashboard_school', 'school_geo_data', 'pivot_dashboard', 'pivot_data', 'alp_dashboard_data',
    'landing_page',
)
# Function views that only accept POST.
POST_ONLY_VIEWS = ('child_duplication_check', 'save_attendance_children', 'save_attendance_teachers')
# Views guarded by ALPEditPermissionMixin (no superusers, school required).
MUTATING_VIEWS = (
    'registration_add', 'registration_edit', 'registration_delete',
    'teacher_add', 'teacher_edit', 'teacher_delete',
    'grading_add', 'grading_edit',
)
READ_VIEWS = tuple(name for name in PAGE_VIEWS if name not in MUTATING_VIEWS)
# Views that take a pk, mapped to the fixture attribute holding the object.
PK_VIEWS = {
    'registration_edit': 'registration', 'registration_delete': 'registration', 'child_profile': 'registration',
    'teacher_edit': 'teacher', 'teacher_delete': 'teacher', 'grading_edit': 'grading',
}
# Reporting views that staff users may open without the ALP_SCHOOL group.
STAFF_VIEWS = ('pivot_dashboard', 'pivot_data')

NO_API = patch('student_registration.alp.views.generate_one_unique_id', return_value='UID-1')


def make_alp_user(username, school, **extra):
    """Return a member of ALP_SCHOOL attached to ``school`` (which may be None)."""
    group, _ = Group.objects.get_or_create(name='ALP_SCHOOL')
    user = User.objects.create_user(username=username, password='password', school=school, **extra)
    user.groups.add(group)
    return user


def make_registration(school, first_name, alp_round, programme, owner=None, **extra):
    child = Child.objects.create(
        first_name=first_name, father_name='Ahmad', last_name='Sayed', mother_fullname='Fatima Ali',
        gender='Female', birthday_year='2015', birthday_month='5', birthday_day='10',
    )
    return ALPRegistration.objects.create(
        child=child, school=school, round=alp_round, programme=programme, owner=owner, **extra
    )


def make_teacher(school, first_name):
    return ALPTeacher.objects.create(school=school, first_name=first_name, last_name='Teacher', phone_number='70-1')


def make_grading(registration, definition, owner):
    return ALPGrading.objects.create(registration=registration, grading_data={str(definition.pk): 15}, owner=owner)


def today():
    """Today as the views compute it (the test settings may run with USE_TZ off)."""
    if settings.USE_TZ:
        return timezone.localdate()
    return timezone.now().date()


def attendance_body(**extra):
    body = {'attendance_date': today().isoformat(), 'children_attendance': [], 'teachers_attendance': []}
    body.update(extra)
    return body


class ALPAccessTestCase(TestCase):
    """School A with one registration, teacher and grading, owned by an ALP focal point."""

    def setUp(self):
        self.alp_round = ALPRound.objects.create(name='Round 2026', current_year=True)
        self.programme = ALPProgram.objects.create(name='ALP Level 1')
        self.definition = ALPGradingDefinition.objects.create(material='Arabic', min_grade=0, max_grade=20)
        self.school = School.objects.create(number='100', name='School A')
        self.user = make_alp_user('focal-a', self.school)
        self.registration = make_registration(self.school, 'Amina', self.alp_round, self.programme, self.user)
        self.teacher = make_teacher(self.school, 'Adel')
        self.grading = make_grading(self.registration, self.definition, self.user)

    def url(self, name):
        kwargs = {}
        if name in PK_VIEWS:
            kwargs = {'pk': getattr(self, PK_VIEWS[name]).pk}
        return reverse('alp:{0}'.format(name), kwargs=kwargs)

    def post_json(self, name, body=None):
        return self.client.post(self.url(name), data=json.dumps(body or attendance_body()),
                                content_type='application/json')

    def assertLoginRedirect(self, response, url):
        self.assertRedirects(response, '{0}?next={1}'.format(LOGIN_URL, url), fetch_redirect_response=False)


class URLMatrixCoverageTests(TestCase):
    def test_matrix_lists_every_alp_url_name(self):
        self.assertEqual(
            {pattern.name for pattern in alp_urls.urlpatterns},
            set(PAGE_VIEWS) | set(POST_ONLY_VIEWS),
        )
        self.assertTrue(set(MUTATING_VIEWS) <= set(PAGE_VIEWS))
        self.assertTrue(set(PK_VIEWS) <= set(PAGE_VIEWS))


class AnonymousAccessTests(ALPAccessTestCase):
    def test_pages_redirect_anonymous_users_to_login(self):
        for name in PAGE_VIEWS:
            with self.subTest(view=name):
                url = self.url(name)
                self.assertLoginRedirect(self.client.get(url), url)

    def test_post_only_endpoints_redirect_anonymous_users_to_login(self):
        for name in POST_ONLY_VIEWS:
            with self.subTest(view=name):
                self.assertLoginRedirect(self.post_json(name), self.url(name))


class NonALPUserAccessTests(ALPAccessTestCase):
    def setUp(self):
        super().setUp()
        self.outsider = User.objects.create_user(username='outsider', password='password', school=self.school)
        self.client.force_login(self.outsider)

    def test_pages_are_forbidden_without_alp_group(self):
        for name in PAGE_VIEWS:
            with self.subTest(view=name):
                self.assertEqual(self.client.get(self.url(name)).status_code, 403)

    def test_post_only_endpoints_are_forbidden_without_alp_group(self):
        for name in POST_ONLY_VIEWS:
            with self.subTest(view=name):
                self.assertEqual(self.post_json(name).status_code, 403)

    def test_staff_without_alp_group_only_reaches_pivot_reporting(self):
        staff = User.objects.create_user(username='staff', password='password', is_staff=True)
        self.client.force_login(staff)
        for name in PAGE_VIEWS:
            with self.subTest(view=name):
                expected = 200 if name in STAFF_VIEWS else 403
                self.assertEqual(self.client.get(self.url(name)).status_code, expected)
        for name in POST_ONLY_VIEWS:
            with self.subTest(view=name):
                self.assertEqual(self.post_json(name).status_code, 403)


class ALPUserAccessTests(ALPAccessTestCase):
    def setUp(self):
        super().setUp()
        self.client.force_login(self.user)

    def test_focal_point_can_open_every_page(self):
        for name in PAGE_VIEWS:
            with self.subTest(view=name):
                self.assertEqual(self.client.get(self.url(name)).status_code, 200)

    def test_post_only_endpoints_reject_get(self):
        for name in POST_ONLY_VIEWS:
            with self.subTest(view=name):
                self.assertEqual(self.client.get(self.url(name)).status_code, 405)

    def test_non_numeric_pk_routes_do_not_resolve(self):
        for path in ('/alp/registrations/edit/abc/', '/alp/registrations/delete/abc/', '/alp/child-profile/abc/',
                     '/alp/teachers/edit/abc/', '/alp/teachers/delete/abc/', '/alp/grading/edit/abc/'):
            with self.subTest(path=path):
                self.assertEqual(self.client.get(path).status_code, 404)
                self.assertEqual(self.client.post(path).status_code, 404)
        for name in PK_VIEWS:
            with self.subTest(view=name):
                with self.assertRaises(NoReverseMatch):
                    reverse('alp:{0}'.format(name), kwargs={'pk': 'abc'})


class SuperuserAccessTests(ALPAccessTestCase):
    def setUp(self):
        super().setUp()
        self.superuser = User.objects.create_superuser('root', 'root@example.com', 'password', school=self.school)
        self.client.force_login(self.superuser)

    def test_superuser_can_read_every_page(self):
        for name in READ_VIEWS:
            with self.subTest(view=name):
                self.assertEqual(self.client.get(self.url(name)).status_code, 200)

    def test_superuser_can_run_the_duplication_check(self):
        with NO_API:
            response = self.post_json('child_duplication_check', {'nationality': 1})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'result': []})

    def test_superuser_cannot_open_or_submit_mutating_views(self):
        for name in MUTATING_VIEWS:
            with self.subTest(view=name):
                self.assertEqual(self.client.get(self.url(name)).status_code, 403)
                self.assertEqual(self.client.post(self.url(name), {}).status_code, 403)
        self.registration.refresh_from_db()
        self.assertFalse(self.registration.deleted)
        self.assertTrue(ALPTeacher.objects.filter(pk=self.teacher.pk).exists())

    def test_superuser_cannot_update_the_school_profile(self):
        response = self.client.post(self.url('school_profile'), {'number': self.school.number, 'name': 'Renamed'})

        self.assertEqual(response.status_code, 403)
        self.school.refresh_from_db()
        self.assertEqual(self.school.name, 'School A')

    def test_superuser_cannot_save_attendance(self):
        for name in ('save_attendance_children', 'save_attendance_teachers'):
            with self.subTest(view=name):
                self.assertEqual(self.post_json(name).status_code, 403)


class ALPUserWithoutSchoolTests(ALPAccessTestCase):
    def setUp(self):
        super().setUp()
        self.orphan = make_alp_user('no-school', None)
        self.client.force_login(self.orphan)

    def test_mutating_views_and_school_profile_are_forbidden(self):
        for name in MUTATING_VIEWS + ('school_profile',):
            with self.subTest(view=name):
                self.assertEqual(self.client.get(self.url(name)).status_code, 403)
                self.assertEqual(self.client.post(self.url(name), {}).status_code, 403)

    def test_attendance_saves_fail_with_no_school_assigned(self):
        for name in ('save_attendance_children', 'save_attendance_teachers'):
            with self.subTest(view=name):
                response = self.post_json(name)
                self.assertEqual(response.status_code, 400)
                self.assertEqual(response.content, b'No school assigned')

    def test_lists_render_empty(self):
        for name in ('registration_list', 'teacher_list'):
            with self.subTest(view=name):
                response = self.client.get(self.url(name))
                self.assertEqual(response.status_code, 200)
                self.assertEqual(len(response.context['table'].rows), 0)

    def test_other_schools_records_are_not_found(self):
        self.assertEqual(self.client.get(self.url('child_profile')).status_code, 404)

    def test_dashboards_and_data_endpoints_render_empty(self):
        for name in ('dashboard_registration', 'dashboard_teacher', 'dashboard_attendance', 'dashboard_school',
                     'pivot_dashboard', 'attendance_list', 'teacher_attendance_list'):
            with self.subTest(view=name):
                self.assertEqual(self.client.get(self.url(name)).status_code, 200)

        self.assertEqual(self.client.get(self.url('pivot_data')).json(), [])
        self.assertEqual(self.client.get(self.url('school_geo_data')).json(), [])
        self.assertEqual(self.client.get(self.url('dashboard_teacher_data')).json()['total'], 0)
        registration_data = self.client.get(self.url('alp_dashboard_data')).json()
        self.assertEqual(registration_data['nationality'], [])
        self.assertEqual(registration_data['children_per_gender'], [])

        response = self.client.get(self.url('load_attendance_children'), {
            'attendance_date': today().isoformat(),
            'round_id': self.alp_round.pk, 'programme': self.programme.pk,
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['instances'], [])
        self.assertEqual(response.context['new_instances'], [])

        response = self.client.get(self.url('landing_page'))
        self.assertEqual(response.status_code, 200)
        for key in ('kpi_today', 'kpi_week', 'kpi_schools', 'kpi_attendance'):
            self.assertEqual(response.context[key], 0, key)


class SchoolBoundaryTests(ALPAccessTestCase):
    """Focal point A must never see or touch school B's records."""

    def setUp(self):
        super().setUp()
        self.other_school = School.objects.create(number='200', name='School B')
        self.other_user = make_alp_user('focal-b', self.other_school)
        self.other_registration = make_registration(
            self.other_school, 'Bushra', self.alp_round, self.programme, self.other_user,
        )
        self.other_teacher = make_teacher(self.other_school, 'Bilal')
        self.other_grading = make_grading(self.other_registration, self.definition, self.other_user)
        self.client.force_login(self.user)

    def other_url(self, name, obj):
        return reverse('alp:{0}'.format(name), kwargs={'pk': obj.pk})

    def test_other_schools_child_profile_is_not_found(self):
        self.assertEqual(self.client.get(self.url('child_profile')).status_code, 200)
        self.assertEqual(self.client.get(self.other_url('child_profile', self.other_registration)).status_code, 404)

    def test_other_schools_registration_cannot_be_edited(self):
        url = self.other_url('registration_edit', self.other_registration)

        self.assertEqual(self.client.get(url).status_code, 404)
        with NO_API:
            self.assertEqual(self.client.post(url, {'child_first_name': 'Hacked'}).status_code, 404)
        self.other_registration.child.refresh_from_db()
        self.assertEqual(self.other_registration.child.first_name, 'Bushra')

    def test_other_schools_registration_cannot_be_deleted(self):
        url = self.other_url('registration_delete', self.other_registration)

        self.assertEqual(self.client.get(url).status_code, 404)
        self.assertEqual(self.client.post(url).status_code, 404)
        self.other_registration.refresh_from_db()
        self.assertFalse(self.other_registration.deleted)

    def test_other_schools_teacher_cannot_be_edited_or_deleted(self):
        edit_url = self.other_url('teacher_edit', self.other_teacher)
        delete_url = self.other_url('teacher_delete', self.other_teacher)

        self.assertEqual(self.client.get(edit_url).status_code, 404)
        self.assertEqual(self.client.post(edit_url, {'first_name': 'Hacked'}).status_code, 404)
        self.assertEqual(self.client.get(delete_url).status_code, 404)
        self.assertEqual(self.client.post(delete_url).status_code, 404)
        self.other_teacher.refresh_from_db()
        self.assertEqual(self.other_teacher.first_name, 'Bilal')

    def test_other_schools_grading_cannot_be_edited(self):
        url = self.other_url('grading_edit', self.other_grading)

        self.assertEqual(self.client.get(url).status_code, 404)
        self.assertEqual(self.client.post(url, {'registration': self.other_registration.pk}).status_code, 404)
        self.other_grading.refresh_from_db()
        self.assertEqual(self.other_grading.grading_data, {str(self.definition.pk): 15})

    def test_registration_list_only_shows_own_school(self):
        response = self.client.get(self.url('registration_list'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual([row.record.pk for row in response.context['table'].rows], [self.registration.pk])
        self.assertContains(response, 'Amina')
        self.assertNotContains(response, 'Bushra')

    def test_teacher_list_only_shows_own_school(self):
        response = self.client.get(self.url('teacher_list'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual([row.record.pk for row in response.context['table'].rows], [self.teacher.pk])
        self.assertContains(response, 'Adel')
        self.assertNotContains(response, 'Bilal')

    def test_csv_exports_only_contain_own_school(self):
        for name, own, other in (('registration_list', 'Amina', 'Bushra'), ('teacher_list', 'Adel', 'Bilal')):
            with self.subTest(view=name):
                response = self.client.get(self.url(name), {'_export': 'csv'})

                self.assertEqual(response.status_code, 200)
                self.assertEqual(response['Content-Type'], 'text/csv; charset=utf-8')
                self.assertTrue(response.content.startswith(codecs.BOM_UTF8))
                content = response.content.decode('utf-8-sig')
                self.assertIn(own, content)
                self.assertNotIn(other, content)
