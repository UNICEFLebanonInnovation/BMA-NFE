"""Regression tests for the ALP dashboard pages and their JSON datasets.

Two schools are seeded so that every dataset can be checked for school
scoping: an ALP focal point only ever sees their own school, while staff
and superusers report across both.
"""
import json
from collections import Counter
from datetime import date

from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from student_registration.alp.models import (
    ALPAttendance,
    ALPAttendanceChild,
    ALPGrading,
    ALPGradingDefinition,
    ALPProgram,
    ALPRegistration,
    ALPRound,
    ALPTeacher,
)
from student_registration.child.models import Child
from student_registration.clm.models import Disability
from student_registration.schools.models import School
from student_registration.students.models import Nationality, Training
from student_registration.users.models import User

DASHBOARD_KEYS = {
    'nationality', 'gender', 'round', 'programme', 'learning_outcomes',
    'children_per_gender', 'children_gender_age', 'children_per_nationality',
    'children_per_source', 'children_per_status', 'children_per_disability',
    'children_cash_support', 'children_per_round', 'children_per_programme',
    'children_moved_rounds',
}
PIVOT_KEYS = {
    'school_number', 'school', 'governorate', 'district', 'cadaster', 'gender',
    'nationality', 'birth_year', 'round', 'programme', 'registration_date',
    'participates_in_work', 'work_type', 'weekly_income', 'referral_source',
    'registration_type',
}
TEACHER_KEYS = {
    'total', 'schools', 'trained', 'trained_percent', 'contact_percent',
    'average_experience', 'average_sessions', 'gender', 'nationality', 'school',
    'round', 'assignment', 'coaching', 'subjects', 'levels', 'trainings', 'hours',
}
NO_HOURS = [{'name': 'ALP', 'y': 0}, {'name': 'Private school', 'y': 0}]


def make_alp_user(username, school, **extra):
    """Return a user of the ALP_SCHOOL group attached to ``school``."""
    group, _ = Group.objects.get_or_create(name='ALP_SCHOOL')
    user = User.objects.create_user(username=username, password='password', school=school, **extra)
    user.groups.add(group)
    return user


def make_child(first_name, gender, nationality, birthday_year, living_arrangement, disability):
    return Child.objects.create(
        first_name=first_name, father_name='Ahmad', last_name='Sayed', mother_fullname='Fatima Ali',
        gender=gender, nationality=nationality, birthday_year=str(birthday_year),
        birthday_month='5', birthday_day='10', living_arrangement=living_arrangement,
        disability=disability,
    )


def make_registration(child, school, alp_round, programme, owner, **extra):
    fields = {
        'registration_date': date(2026, 9, 1),
        'cash_support_programmes': ['None'],
        'source_of_identification': 'Dirassa',
    }
    fields.update(extra)
    return ALPRegistration.objects.create(
        child=child, school=school, round=alp_round, programme=programme, owner=owner, **fields
    )


def make_teacher(school, owner, alp_round, **extra):
    fields = {'first_name': 'Mohamad', 'last_name': 'Al Sayed', 'sex': 'Male'}
    fields.update(extra)
    return ALPTeacher.objects.create(school=school, owner=owner, round=alp_round, **fields)


def make_attendance_day(school, alp_round, programme, attendance_date, rows):
    """Create an attendance day with one child row per ``(registration, attended)``."""
    day = ALPAttendance.objects.create(
        school=school, round=alp_round, programme=programme,
        attendance_date=attendance_date, day_off='No',
    )
    for registration, attended in rows:
        ALPAttendanceChild.objects.create(
            attendance_day=day, registration=registration, child=registration.child, attended=attended,
        )
    return day


class DashboardDataTestCase(TestCase):
    """Two schools with registrations, gradings, teachers and attendance."""

    @classmethod
    def setUpTestData(cls):
        # ``_current_date`` uses the naive local date when USE_TZ is off.
        cls.year = timezone.now().year
        cls.school_a = School.objects.create(number='A-100', name='Alpha School', latitude=33.9, longitude=35.5)
        cls.school_b = School.objects.create(number='B-200', name='Beta School', latitude=34.1, longitude=35.7)
        cls.user = make_alp_user('focal-a', cls.school_a)
        cls.user_b = make_alp_user('focal-b', cls.school_b)
        cls.staff = make_alp_user('staff-a', cls.school_a, is_staff=True)
        cls.superuser = User.objects.create_superuser('root', 'root@example.org', 'password')

        cls.syrian = Nationality.objects.create(pk=1, name='Syrian', name_en='Syrian', code='SY')
        cls.lebanese = Nationality.objects.create(pk=2, name='Lebanese', name_en='Lebanese', code='LB')
        cls.no_disability = Disability.objects.create(name='No disability', name_en='No disability')
        cls.visual = Disability.objects.create(name='Visual impairment', name_en='Visual impairment')
        cls.round_1 = ALPRound.objects.create(name='Round 2025', current_year=False)
        cls.round_2 = ALPRound.objects.create(name='Round 2026', current_year=True)
        cls.level_1 = ALPProgram.objects.create(name='Level 1')
        cls.level_2 = ALPProgram.objects.create(name='Level 2')

        # School A: Lina moved from round 1 to round 2, Omar only attends round 1
        # and Ghost's registration is soft deleted, so it must not be reported.
        cls.lina = make_child('Lina', 'Female', cls.syrian, cls.year - 12, 'Living with caregivers', cls.no_disability)
        cls.omar = make_child('Omar', 'Male', cls.lebanese, cls.year - 16, 'Unaccompanied', cls.visual)
        cls.ghost = make_child('Ghost', 'Male', cls.syrian, cls.year - 12, 'Living with caregivers', cls.no_disability)
        cls.reg_lina_r1 = make_registration(
            cls.lina, cls.school_a, cls.round_1, cls.level_1, cls.user, cash_support_programmes=['Haddi'],
        )
        cls.reg_lina_r2 = make_registration(cls.lina, cls.school_a, cls.round_2, cls.level_1, cls.user)
        cls.reg_omar = make_registration(
            cls.omar, cls.school_a, cls.round_1, cls.level_2, cls.user, source_of_identification='Awareness Session',
        )
        cls.reg_deleted = make_registration(
            cls.ghost, cls.school_a, cls.round_1, cls.level_1, cls.user,
            deleted=True, cash_support_programmes=['Haddi'],
        )

        # School B: a single registration.
        cls.sara = make_child('Sara', 'Female', cls.syrian, cls.year - 8, 'Living with caregivers', cls.no_disability)
        cls.reg_sara = make_registration(
            cls.sara, cls.school_b, cls.round_1, cls.level_1, cls.user_b,
            cash_support_programmes=['Haddi', 'WFP cash assistance'], source_of_identification='From Other NGO',
        )

        cls.arabic = ALPGradingDefinition.objects.create(material='Arabic', min_grade=0, max_grade=20)
        ALPGrading.objects.create(registration=cls.reg_lina_r1, grading_data={str(cls.arabic.pk): 15}, owner=cls.user)
        ALPGrading.objects.create(registration=cls.reg_sara, grading_data={str(cls.arabic.pk): 5}, owner=cls.user_b)

        cls.training = Training.objects.create(name='Pedagogy')
        cls.teacher_a1 = make_teacher(
            cls.school_a, cls.user, cls.round_2, phone_number='70-123456',
            subjects_provided=['arabic', 'math'], registration_level=['Level one'],
            teaching_hours_mscc=10, teaching_hours_private_school=5,
            years_of_experience=4, training_sessions_attended=2,
        )
        cls.teacher_a1.trainings.add(cls.training)
        cls.teacher_a2 = make_teacher(
            cls.school_a, cls.user, cls.round_2, first_name='Rania', sex='Female', phone_number=None,
            subjects_provided=['math'], registration_level=['Level two'], years_of_experience=2,
        )
        cls.teacher_b1 = make_teacher(
            cls.school_b, cls.user_b, cls.round_1, first_name='Ali', phone_number='71-000000',
            subjects_provided=['english'], registration_level=['Level one'], teaching_hours_mscc=8,
        )
        cls.teacher_b1.trainings.add(cls.training)

        cls.day_1 = date(cls.year, 1, 15)
        cls.day_2 = date(cls.year, 2, 10)
        cls.previous_year_day = date(cls.year - 1, 11, 3)
        make_attendance_day(
            cls.school_a, cls.round_1, cls.level_1, cls.day_1, [(cls.reg_lina_r1, 'Yes'), (cls.reg_omar, 'No')],
        )
        make_attendance_day(cls.school_a, cls.round_1, cls.level_1, cls.day_2, [(cls.reg_lina_r1, 'Yes')])
        make_attendance_day(cls.school_b, cls.round_1, cls.level_1, cls.day_1, [(cls.reg_sara, 'No')])
        make_attendance_day(cls.school_b, cls.round_1, cls.level_1, cls.previous_year_day, [(cls.reg_sara, 'Yes')])

    def setUp(self):
        self.client.force_login(self.user)

    def get_json(self, name, **params):
        response = self.client.get(reverse('alp:{0}'.format(name)), params)
        self.assertEqual(response.status_code, 200)
        return response.json()


class PivotDataTests(DashboardDataTestCase):
    def test_alp_user_gets_only_active_registrations_of_own_school(self):
        data = self.get_json('pivot_data')

        self.assertEqual(len(data), 3)
        self.assertEqual({row['school'] for row in data}, {'Alpha School'})
        self.assertEqual(Counter(row['round'] for row in data), {'Round 2025': 2, 'Round 2026': 1})
        self.assertNotIn(str(self.year - 12), [row['birth_year'] for row in data if row['gender'] == 'Male'])

    def test_pivot_rows_expose_the_flattened_registration_dimensions(self):
        data = self.get_json('pivot_data')

        lina = [row for row in data if row['gender'] == 'Female' and row['round'] == 'Round 2025']
        self.assertEqual(lina, [{
            'school_number': 'A-100',
            'school': 'Alpha School',
            'governorate': '',
            'district': '',
            'cadaster': '',
            'gender': 'Female',
            'nationality': 'Syrian',
            'birth_year': str(self.year - 12),
            'round': 'Round 2025',
            'programme': 'Level 1',
            'registration_date': '2026-09-01',
            'participates_in_work': '',
            'work_type': '',
            'weekly_income': '',
            'referral_source': 'Dirassa',
            'registration_type': '',
        }])
        self.assertEqual(set(data[0]), PIVOT_KEYS)

    def test_other_school_user_only_gets_their_own_rows(self):
        self.client.force_login(self.user_b)

        data = self.get_json('pivot_data')

        self.assertEqual([row['school'] for row in data], ['Beta School'])

    def test_staff_and_superuser_get_both_schools(self):
        for user in (self.staff, self.superuser):
            with self.subTest(user=user.username):
                self.client.force_login(user)

                data = self.get_json('pivot_data')

                self.assertEqual(Counter(row['school'] for row in data), {'Alpha School': 3, 'Beta School': 1})

    def test_staff_user_without_alp_group_can_read_pivot_data(self):
        reporter = User.objects.create_user(username='reporter', password='password', is_staff=True)
        self.client.force_login(reporter)

        data = self.get_json('pivot_data')

        self.assertEqual(len(data), 4)


class RegistrationDashboardDataTests(DashboardDataTestCase):
    def test_response_contains_every_chart_dataset(self):
        data = self.get_json('alp_dashboard_data')

        self.assertEqual(set(data), DASHBOARD_KEYS)
        self.assertEqual(data['children_per_gender'], data['gender'])
        self.assertEqual(data['children_per_nationality'], data['nationality'])
        self.assertEqual(data['children_per_programme'], data['programme'])
        self.assertEqual(set(data['children_moved_rounds']), {'categories', 'moved', 'new'})

    def test_alp_user_datasets_only_cover_active_registrations_of_own_school(self):
        data = self.get_json('alp_dashboard_data')

        self.assertEqual(data['gender'], [{'name': 'Female', 'y': 2}, {'name': 'Male', 'y': 1}])
        self.assertEqual(data['nationality'], [{'name': 'Lebanese', 'y': 1}, {'name': 'Syrian', 'y': 2}])
        self.assertEqual(data['round'], [{'name': 'Round 2025', 'y': 2}, {'name': 'Round 2026', 'y': 1}])
        self.assertEqual(data['programme'], [{'name': 'Level 1', 'y': 2}, {'name': 'Level 2', 'y': 1}])
        self.assertEqual(
            data['children_per_source'],
            [{'name': 'Awareness Session', 'y': 1}, {'name': 'Dirassa', 'y': 2}],
        )
        self.assertEqual(
            data['children_per_status'],
            [{'name': 'Living with caregivers', 'y': 2}, {'name': 'Unaccompanied', 'y': 1}],
        )
        self.assertEqual(
            data['children_per_disability'],
            [{'name': 'No disability', 'y': 2}, {'name': 'Visual impairment', 'y': 1}],
        )

    def test_children_gender_age_labels_combine_gender_and_age_group(self):
        data = self.get_json('alp_dashboard_data')

        self.assertEqual(
            data['children_gender_age'],
            [{'name': 'Female - 10-14', 'y': 2}, {'name': 'Male - 15-17', 'y': 1}],
        )

    def test_children_cash_support_counts_every_programme_choice(self):
        data = self.get_json('alp_dashboard_data')

        self.assertEqual(data['children_cash_support'], [
            {'name': 'None', 'y': 2},
            {'name': 'Haddi', 'y': 1},
            {'name': 'Education Cash assistance', 'y': 0},
            {'name': 'UNHCR cash assistance', 'y': 0},
            {'name': 'WFP cash assistance', 'y': 0},
        ])

    def test_children_moved_rounds_splits_each_round_into_moved_and_new_children(self):
        data = self.get_json('alp_dashboard_data')

        # Lina is counted once per round; only she attended more than one round.
        self.assertEqual(
            data['children_per_round'],
            [{'name': 'Round 2025', 'y': 2}, {'name': 'Round 2026', 'y': 1}],
        )
        self.assertEqual(data['children_moved_rounds'], {
            'categories': ['Round 2025', 'Round 2026'],
            'moved': [1, 1],
            'new': [1, 0],
        })

    def test_learning_outcomes_only_cover_own_school(self):
        data = self.get_json('alp_dashboard_data')

        outcomes = data['learning_outcomes']
        self.assertEqual(outcomes['assessed_children'], 1)
        self.assertEqual(outcomes['average_achievement'], 75.0)
        self.assertEqual(outcomes['children_with_follow_up'], 0)
        self.assertEqual(outcomes['improved_children'], 0)
        self.assertEqual(outcomes['performance_bands'], [
            {'name': 'On track', 'y': 1}, {'name': 'Developing', 'y': 0}, {'name': 'Needs support', 'y': 0},
        ])
        self.assertEqual(outcomes['subjects'], [{'name': 'Arabic', 'y': 75.0}])

    def test_staff_and_superuser_see_both_schools(self):
        for user in (self.staff, self.superuser):
            with self.subTest(user=user.username):
                self.client.force_login(user)

                data = self.get_json('alp_dashboard_data')

                self.assertEqual(data['gender'], [{'name': 'Female', 'y': 3}, {'name': 'Male', 'y': 1}])
                self.assertEqual(data['nationality'], [{'name': 'Lebanese', 'y': 1}, {'name': 'Syrian', 'y': 3}])
                self.assertEqual(
                    data['children_gender_age'],
                    [
                        {'name': 'Female - 10-14', 'y': 2},
                        {'name': 'Female - 5-9', 'y': 1},
                        {'name': 'Male - 15-17', 'y': 1},
                    ],
                )
                self.assertEqual(data['children_cash_support'], [
                    {'name': 'None', 'y': 2},
                    {'name': 'Haddi', 'y': 2},
                    {'name': 'Education Cash assistance', 'y': 0},
                    {'name': 'UNHCR cash assistance', 'y': 0},
                    {'name': 'WFP cash assistance', 'y': 1},
                ])
                self.assertEqual(data['children_moved_rounds'], {
                    'categories': ['Round 2025', 'Round 2026'],
                    'moved': [1, 1],
                    'new': [2, 0],
                })
                self.assertEqual(data['learning_outcomes']['assessed_children'], 2)
                self.assertEqual(data['learning_outcomes']['average_achievement'], 50.0)

    def test_school_filter_cannot_widen_alp_user_scope(self):
        data = self.get_json('alp_dashboard_data', schools=self.school_b.pk)

        self.assertEqual(data['gender'], [])
        self.assertEqual(data['nationality'], [])
        self.assertEqual(data['children_gender_age'], [])
        self.assertEqual(data['children_moved_rounds'], {'categories': [], 'moved': [], 'new': []})
        self.assertEqual([item['y'] for item in data['children_cash_support']], [0, 0, 0, 0, 0])
        self.assertEqual(data['learning_outcomes']['assessed_children'], 0)

    def test_school_filter_narrows_admin_scope(self):
        self.client.force_login(self.superuser)

        data = self.get_json('alp_dashboard_data', schools=self.school_b.pk)

        self.assertEqual(data['gender'], [{'name': 'Female', 'y': 1}])
        self.assertEqual(data['children_per_source'], [{'name': 'From Other NGO', 'y': 1}])

    def test_round_and_programme_filters_narrow_results(self):
        by_round = self.get_json('alp_dashboard_data', rounds=self.round_2.pk)
        by_programme = self.get_json('alp_dashboard_data', programmes=self.level_2.pk)

        self.assertEqual(by_round['round'], [{'name': 'Round 2026', 'y': 1}])
        self.assertEqual(by_round['gender'], [{'name': 'Female', 'y': 1}])
        self.assertEqual(by_programme['gender'], [{'name': 'Male', 'y': 1}])

    def test_non_numeric_or_empty_filters_are_ignored(self):
        unfiltered = self.get_json('alp_dashboard_data')

        response = self.client.get(
            reverse('alp:alp_dashboard_data'), {'schools': 'abc', 'rounds': '', 'programmes': 'x'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), unfiltered)


class TeacherDashboardDataTests(DashboardDataTestCase):
    def test_alp_user_indicators_only_cover_own_school(self):
        data = self.get_json('dashboard_teacher_data')

        self.assertEqual(set(data), TEACHER_KEYS)
        self.assertEqual(data['total'], 2)
        self.assertEqual(data['schools'], 1)
        self.assertEqual(data['trained'], 1)
        self.assertEqual(data['trained_percent'], 50.0)
        self.assertEqual(data['contact_percent'], 50.0)
        self.assertEqual(data['average_experience'], 3.0)
        self.assertEqual(data['average_sessions'], 2.0)
        self.assertEqual(data['hours'], [{'name': 'ALP', 'y': 10}, {'name': 'Private school', 'y': 5}])
        self.assertCountEqual(data['subjects'], [{'name': 'arabic', 'y': 1}, {'name': 'math', 'y': 2}])
        self.assertCountEqual(data['levels'], [{'name': 'Level one', 'y': 1}, {'name': 'Level two', 'y': 1}])
        self.assertEqual(data['gender'], [{'name': 'Female', 'y': 1}, {'name': 'Male', 'y': 1}])
        self.assertEqual(data['school'], [{'name': 'Alpha School', 'y': 2}])
        self.assertEqual(data['round'], [{'name': 'Round 2026', 'y': 2}])
        self.assertEqual(data['trainings'], [{'name': 'Pedagogy', 'y': 1}])

    def test_staff_and_superuser_cover_both_schools(self):
        for user in (self.staff, self.superuser):
            with self.subTest(user=user.username):
                self.client.force_login(user)

                data = self.get_json('dashboard_teacher_data')

                self.assertEqual(data['total'], 3)
                self.assertEqual(data['schools'], 2)
                self.assertEqual(data['trained'], 2)
                self.assertEqual(data['trained_percent'], 66.7)
                self.assertEqual(data['contact_percent'], 66.7)
                self.assertEqual(data['hours'], [{'name': 'ALP', 'y': 18}, {'name': 'Private school', 'y': 5}])
                self.assertEqual(data['school'], [{'name': 'Alpha School', 'y': 2}, {'name': 'Beta School', 'y': 1}])
                self.assertCountEqual(
                    data['subjects'],
                    [{'name': 'arabic', 'y': 1}, {'name': 'math', 'y': 2}, {'name': 'english', 'y': 1}],
                )

    def test_school_filter_cannot_widen_alp_user_scope(self):
        data = self.get_json('dashboard_teacher_data', schools=self.school_b.pk)

        self.assertEqual(data['total'], 0)
        self.assertEqual(data['schools'], 0)
        self.assertEqual(data['trained'], 0)
        self.assertEqual(data['contact_percent'], 0)
        self.assertEqual(data['hours'], NO_HOURS)
        self.assertEqual(data['subjects'], [])

    def test_round_filter_narrows_results(self):
        self.client.force_login(self.superuser)

        data = self.get_json('dashboard_teacher_data', rounds=self.round_1.pk)

        self.assertEqual(data['total'], 1)
        self.assertEqual(data['school'], [{'name': 'Beta School', 'y': 1}])

    def test_non_numeric_or_empty_filters_are_ignored(self):
        unfiltered = self.get_json('dashboard_teacher_data')

        response = self.client.get(reverse('alp:dashboard_teacher_data'), {'schools': 'abc', 'rounds': ''})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), unfiltered)


class SchoolGeoDataTests(DashboardDataTestCase):
    def test_alp_user_gets_own_school_with_active_student_and_teacher_counts(self):
        data = self.get_json('school_geo_data')

        # Three active registrations: the soft-deleted one is not a student.
        self.assertEqual(data, [{
            'id': self.school_a.pk,
            'number': 'A-100',
            'name': 'Alpha School',
            'type': 'N/A',
            'governorate': 'N/A',
            'district': 'N/A',
            'cadaster': 'N/A',
            'latitude': 33.9,
            'longitude': 35.5,
            'students': 3,
            'teachers': 2,
            'capacity': 0,
            'cwd_accessible': 'N/A',
            'internet_available': 'N/A',
        }])

    def test_staff_and_superuser_get_both_schools(self):
        for user in (self.staff, self.superuser):
            with self.subTest(user=user.username):
                self.client.force_login(user)

                data = self.get_json('school_geo_data')

                self.assertEqual(
                    [(row['name'], row['students'], row['teachers']) for row in data],
                    [('Alpha School', 3, 2), ('Beta School', 1, 1)],
                )

    def test_school_id_filter_cannot_widen_alp_user_scope(self):
        data = self.get_json('school_geo_data', school_id=self.school_b.pk)

        self.assertEqual(data, [])

    def test_school_id_filter_narrows_admin_scope(self):
        self.client.force_login(self.superuser)

        data = self.get_json('school_geo_data', school_id=self.school_b.pk)

        self.assertEqual([row['id'] for row in data], [self.school_b.pk])

    def test_non_numeric_school_id_is_ignored(self):
        unfiltered = self.get_json('school_geo_data')

        response = self.client.get(reverse('alp:school_geo_data'), {'school_id': 'abc'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), unfiltered)


class AttendanceDashboardTests(DashboardDataTestCase):
    def attendance_context(self, **params):
        response = self.client.get(reverse('alp:dashboard_attendance'), params)
        self.assertEqual(response.status_code, 200)
        return response.context

    def test_alp_user_totals_per_date_only_cover_own_school(self):
        context = self.attendance_context()

        self.assertEqual(json.loads(context['attendance_json']), [
            {'attendance_day__attendance_date': self.day_1.isoformat(), 'total': 2, 'absent': 1},
            {'attendance_day__attendance_date': self.day_2.isoformat(), 'total': 1, 'absent': 0},
        ])
        self.assertEqual(json.loads(context['program_attendance_json']), {'Level 1': [
            {'attendance_day__attendance_date': self.day_1.isoformat(), 'total': 2, 'absent': 1},
            {'attendance_day__attendance_date': self.day_2.isoformat(), 'total': 1, 'absent': 0},
        ]})
        self.assertEqual(context['year'], self.year)
        self.assertEqual(context['years'], [self.year])

    def test_staff_and_superuser_totals_combine_both_schools(self):
        for user in (self.staff, self.superuser):
            with self.subTest(user=user.username):
                self.client.force_login(user)

                context = self.attendance_context()

                self.assertEqual(json.loads(context['attendance_json']), [
                    {'attendance_day__attendance_date': self.day_1.isoformat(), 'total': 3, 'absent': 2},
                    {'attendance_day__attendance_date': self.day_2.isoformat(), 'total': 1, 'absent': 0},
                ])
                self.assertEqual(context['years'], [self.year - 1, self.year])

    def test_admin_can_select_a_previous_year(self):
        self.client.force_login(self.superuser)

        context = self.attendance_context(year=self.year - 1)

        self.assertEqual(context['year'], self.year - 1)
        self.assertEqual(json.loads(context['attendance_json']), [
            {'attendance_day__attendance_date': self.previous_year_day.isoformat(), 'total': 1, 'absent': 0},
        ])

    def test_invalid_year_falls_back_to_current_year(self):
        for year in ('abc', '99999', '', '-1'):
            with self.subTest(year=year):
                context = self.attendance_context(year=year)

                self.assertEqual(context['year'], self.year)
                self.assertEqual(len(json.loads(context['attendance_json'])), 2)


class DashboardPageTests(DashboardDataTestCase):
    def test_registration_dashboard_page_renders_alp_assets_and_filters(self):
        response = self.client.get(reverse('alp:dashboard_registration'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'js/alp/alp_dashboard_d3.js')
        self.assertContains(response, 'id="programme_filter"')
        self.assertContains(response, 'id="school_filter"')
        self.assertContains(response, 'id="round_filter"')
        self.assertContains(response, reverse('alp:alp_dashboard_data'))

    def test_registration_dashboard_page_has_no_partner_filter(self):
        response = self.client.get(reverse('alp:dashboard_registration'))

        self.assertNotContains(response, 'id="partner_filter"')
        self.assertNotContains(response, 'partner_filter')
        self.assertNotIn('partners', response.context)

    def test_registration_dashboard_page_does_not_mention_partners(self):
        response = self.client.get(reverse('alp:dashboard_registration'))

        # The footer hint used to be copied from the MSCC dashboard and named
        # "regions or partners", filters the ALP dashboard does not offer.
        self.assertNotContains(response, 'partners')

    def test_registration_dashboard_context_is_school_scoped(self):
        response = self.client.get(reverse('alp:dashboard_registration'))

        self.assertEqual(response.context['total'], 3)
        self.assertQuerySetEqual(response.context['schools'], [self.school_a])
        self.assertQuerySetEqual(response.context['rounds'], [self.round_1, self.round_2])
        self.assertQuerySetEqual(response.context['programmes'], [self.level_1, self.level_2])

        self.client.force_login(self.superuser)
        response = self.client.get(reverse('alp:dashboard_registration'))

        self.assertEqual(response.context['total'], 4)
        self.assertQuerySetEqual(response.context['schools'], [self.school_a, self.school_b], ordered=False)

    def test_teacher_and_school_dashboard_contexts_are_school_scoped(self):
        teacher_page = self.client.get(reverse('alp:dashboard_teacher'))
        school_page = self.client.get(reverse('alp:dashboard_school'))

        self.assertEqual(teacher_page.status_code, 200)
        self.assertEqual(teacher_page.context['total'], 2)
        self.assertQuerySetEqual(teacher_page.context['schools'], [self.school_a])
        self.assertEqual(school_page.status_code, 200)
        self.assertEqual(school_page.context['total'], 1)
        self.assertContains(school_page, 'Alpha School')
        self.assertNotContains(school_page, 'Beta School')

    def test_reporting_and_attendance_pages_render_for_alp_user(self):
        for name in ('dashboard_teacher', 'dashboard_school', 'pivot_dashboard',
                     'attendance_list', 'teacher_attendance_list'):
            with self.subTest(page=name):
                response = self.client.get(reverse('alp:{0}'.format(name)))

                self.assertEqual(response.status_code, 200)
