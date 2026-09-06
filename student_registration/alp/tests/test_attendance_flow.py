"""Regression tests for the ALP daily attendance flow (children and teachers).

Covers the loader views (``load_attendance_children`` / ``load_attendance_teachers``),
the JSON save endpoints (``save_attendance_children`` / ``save_attendance_teachers``)
and the helpers they rely on (``filter_by_school``, ``ALPAttendanceChild.attendance_date``).

NOTE on "today": the project runs with ``USE_TZ = False`` and Django's
``timezone.localdate()`` raises ``ValueError`` for naive datetimes, so the
``today()`` helper below mirrors ``alp.views._current_date`` instead of calling
``timezone.localdate()`` unconditionally.

The save tests double as a regression guard for ``alp.utils._today()``: an
earlier revision called ``timezone.localdate()`` unconditionally, which made
every save with a syntactically valid date crash with ``ValueError`` (500)
under ``USE_TZ = False``.
"""
import json
from datetime import date, timedelta
from types import SimpleNamespace

from django.conf import settings
from django.contrib.auth.models import Group
from django.db.models.query import EmptyQuerySet
from django.test import SimpleTestCase, TestCase
from django.urls import reverse
from django.utils import timezone

from student_registration.alp.models import (
    ALPAttendance,
    ALPAttendanceChild,
    ALPGrading,
    ALPProgram,
    ALPRegistration,
    ALPRound,
    ALPTeacher,
    ALPTeacherAttendance,
)
from student_registration.alp.utils import filter_by_school
from student_registration.child.models import Child
from student_registration.schools.models import School
from student_registration.students.models import Nationality
from student_registration.users.models import User


# --------------------------------------------------------------------------- helpers

def today():
    """Today's date the way the ALP views compute it (``localdate()`` raises when USE_TZ is off)."""
    if settings.USE_TZ:
        return timezone.localdate()
    return timezone.now().date()


def make_alp_school_user(username='focal', school=None, **extra):
    """Return an ALP_SCHOOL user attached to ``school`` (created when omitted)."""
    group, _ = Group.objects.get_or_create(name='ALP_SCHOOL')
    if school is None:
        school = School.objects.create(number=f'{username}-100', name=f'School of {username}')
    user = User.objects.create_user(username=username, password='password', school=school, **extra)
    user.groups.add(group)
    return user


def make_child(first_name='Lina', nationality=None, **extra):
    data = {
        'first_name': first_name, 'father_name': 'Ahmad', 'last_name': 'Sayed',
        'mother_fullname': 'Fatima Ali', 'gender': 'Female', 'nationality': nationality,
        'birthday_year': '2015', 'birthday_month': '5', 'birthday_day': '10',
    }
    data.update(extra)
    return Child.objects.create(**data)


def make_registration(school, round_, programme, owner=None, child=None, **extra):
    if child is None:
        child = make_child(first_name=extra.pop('first_name', 'Lina'), nationality=extra.pop('nationality', None))
    return ALPRegistration.objects.create(
        school=school, child=child, round=round_, programme=programme, owner=owner, **extra,
    )


def child_row(registration, attended='Yes', absence_reason='', absence_reason_other='', child_id=None):
    return {
        'registration_id': registration.pk,
        'child_id': registration.child_id if child_id is None else child_id,
        'attended': attended,
        'absence_reason': absence_reason,
        'absence_reason_other': absence_reason_other,
    }


class AttendanceTestCase(TestCase):
    """Common fixtures: lookups, an ALP focal point logged in, and a past attendance day."""

    def setUp(self):
        self.nationality = Nationality.objects.create(pk=1, name='Syrian', name_en='Syrian', code='SY')
        self.round = ALPRound.objects.create(name='Round 2026', current_year=True)
        self.programme = ALPProgram.objects.create(name='ALP Level 1')
        self.user = make_alp_school_user('focal')
        self.school = self.user.school
        self.today = today()
        self.day = self.today - timedelta(days=3)
        self.day_iso = self.day.isoformat()
        self.day_us = self.day.strftime('%m/%d/%Y')
        self.client.force_login(self.user)

    def other_school_user(self, username='other'):
        return make_alp_school_user(username)

    def add_registration(self, school=None, round_=None, programme=None, **extra):
        return make_registration(
            school or self.school, round_ or self.round, programme or self.programme, owner=self.user, **extra,
        )

    def post_json(self, url_name, body):
        return self.client.post(reverse(f'alp:{url_name}'), data=json.dumps(body), content_type='application/json')


# --------------------------------------------------------------------------- children: loader

class LoadAttendanceChildrenTests(AttendanceTestCase):
    def setUp(self):
        super().setUp()
        self.registration = self.add_registration(nationality=self.nationality)
        self.child = self.registration.child

    def load(self, **params):
        query = {'attendance_date': self.day_iso, 'round_id': self.round.pk, 'programme': self.programme.pk}
        query.update(params)
        return self.client.get(reverse('alp:load_attendance_children'), query)

    def assertEmptySheet(self, response):
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['instances'], [])
        self.assertEqual(response.context['new_instances'], [])

    def test_iso_date_lists_the_school_registration(self):
        response = self.load(attendance_date=self.day_iso)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['new_instances'], [])
        self.assertEqual(response.context['instances'], [{
            'registration_id': self.registration.pk,
            'child_id': self.child.pk,
            'child_fullname': 'Lina Ahmad Sayed',
            'child_mother_fullname': 'Fatima Ali',
            'child_birthday': '10/5/2015',
            'child_nationality': 'Syrian',
            'attended': 'Yes',
            'absence_reason': '',
            'absence_reason_other': '',
        }])
        self.assertContains(response, 'Lina Ahmad Sayed')
        self.assertContains(response, f'id="status_yes_{self.registration.pk}"')

    def test_us_date_format_lists_the_school_registration(self):
        response = self.load(attendance_date=self.day_us)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['instances']), 1)
        self.assertEqual(response.context['instances'][0]['registration_id'], self.registration.pk)
        self.assertEqual(response.context['new_instances'], [])

    def test_today_is_not_a_future_date(self):
        response = self.load(attendance_date=self.today.isoformat())

        self.assertEqual(len(response.context['instances']), 1)

    def test_future_date_returns_an_empty_sheet(self):
        tomorrow = (self.today + timedelta(days=1)).isoformat()

        self.assertEmptySheet(self.load(attendance_date=tomorrow))

    def test_missing_date_returns_an_empty_sheet(self):
        response = self.client.get(reverse('alp:load_attendance_children'),
                                   {'round_id': self.round.pk, 'programme': self.programme.pk})

        self.assertEmptySheet(response)

    def test_garbage_date_returns_an_empty_sheet(self):
        for value in ('garbage', '2026-13-45', '31/12/2025', ''):
            with self.subTest(attendance_date=value):
                self.assertEmptySheet(self.load(attendance_date=value))

    def test_non_numeric_round_returns_an_empty_sheet(self):
        self.assertEmptySheet(self.load(round_id='abc'))

    def test_non_numeric_programme_returns_an_empty_sheet(self):
        self.assertEmptySheet(self.load(programme='abc'))

    def test_missing_round_or_programme_returns_an_empty_sheet(self):
        response = self.client.get(reverse('alp:load_attendance_children'), {'attendance_date': self.day_iso})

        self.assertEmptySheet(response)

    def test_child_without_nationality_is_still_listed(self):
        Child.objects.filter(pk=self.child.pk).update(nationality=None)

        response = self.load()

        self.assertEqual(len(response.context['instances']), 1)
        self.assertEqual(response.context['instances'][0]['child_nationality'], '')
        self.assertEqual(response.context['instances'][0]['child_fullname'], 'Lina Ahmad Sayed')

    def test_soft_deleted_registration_is_not_listed(self):
        self.add_registration(first_name='Deleted', deleted=True, deleted_by=self.user)

        response = self.load()

        self.assertEqual([r['registration_id'] for r in response.context['instances']], [self.registration.pk])

    def test_registration_without_child_is_not_listed(self):
        ALPRegistration.objects.create(school=self.school, round=self.round, programme=self.programme, child=None)

        response = self.load()

        self.assertEqual([r['registration_id'] for r in response.context['instances']], [self.registration.pk])

    def test_other_school_round_and_programme_registrations_are_not_listed(self):
        other_school = self.other_school_user().school
        other_round = ALPRound.objects.create(name='Round 2025', current_year=False)
        other_programme = ALPProgram.objects.create(name='ALP Level 2')
        self.add_registration(school=other_school, first_name='OtherSchool')
        self.add_registration(round_=other_round, first_name='OtherRound')
        self.add_registration(programme=other_programme, first_name='OtherProgramme')

        response = self.load()

        self.assertEqual([r['registration_id'] for r in response.context['instances']], [self.registration.pk])
        self.assertEqual(response.context['new_instances'], [])

    def test_saved_day_returns_existing_rows_with_their_values(self):
        attendance = ALPAttendance.objects.create(
            school=self.school, round=self.round, programme=self.programme, attendance_date=self.day, day_off='No',
        )
        ALPAttendanceChild.objects.create(
            attendance_day=attendance, registration=self.registration, child=self.child,
            attended='No', absence_reason='Sick', absence_reason_other='fever',
        )

        response = self.load(attendance_date=self.day_us)

        self.assertEqual(response.context['new_instances'], [])
        self.assertEqual(len(response.context['instances']), 1)
        record = response.context['instances'][0]
        self.assertEqual(record['registration_id'], self.registration.pk)
        self.assertEqual(record['child_id'], self.child.pk)
        self.assertEqual((record['attended'], record['absence_reason'], record['absence_reason_other']),
                         ('No', 'Sick', 'fever'))
        self.assertContains(response, f'id="status_no_{self.registration.pk}"')

    def test_registration_added_after_the_first_save_is_a_new_instance(self):
        attendance = ALPAttendance.objects.create(
            school=self.school, round=self.round, programme=self.programme, attendance_date=self.day, day_off='No',
        )
        ALPAttendanceChild.objects.create(
            attendance_day=attendance, registration=self.registration, child=self.child, attended='Yes',
        )
        later = self.add_registration(first_name='Later')

        response = self.load()

        self.assertEqual([r['registration_id'] for r in response.context['instances']], [self.registration.pk])
        self.assertEqual([r['registration_id'] for r in response.context['new_instances']], [later.pk])
        self.assertEqual(response.context['new_instances'][0]['attended'], 'Yes')
        self.assertEqual(response.context['new_instances'][0]['child_fullname'], 'Later Ahmad Sayed')
        self.assertContains(response, 'Newly Registered Children')

    def test_saved_row_whose_registration_was_soft_deleted_is_skipped(self):
        attendance = ALPAttendance.objects.create(
            school=self.school, round=self.round, programme=self.programme, attendance_date=self.day, day_off='No',
        )
        gone = self.add_registration(first_name='Gone')
        ALPAttendanceChild.objects.create(attendance_day=attendance, registration=gone, child=gone.child, attended='No')
        ALPAttendanceChild.objects.create(
            attendance_day=attendance, registration=self.registration, child=self.child, attended='Yes',
        )
        ALPRegistration.objects.filter(pk=gone.pk).update(deleted=True)

        response = self.load()

        self.assertEqual([r['registration_id'] for r in response.context['instances']], [self.registration.pk])
        self.assertEqual(response.context['new_instances'], [])

    def test_saved_day_of_another_round_does_not_affect_this_sheet(self):
        other_round = ALPRound.objects.create(name='Round 2025', current_year=False)
        ALPAttendance.objects.create(
            school=self.school, round=other_round, programme=self.programme, attendance_date=self.day, day_off='No',
        )

        response = self.load()

        self.assertEqual([r['registration_id'] for r in response.context['instances']], [self.registration.pk])
        self.assertEqual(response.context['new_instances'], [])

    def test_alp_user_without_school_gets_an_empty_sheet(self):
        User.objects.filter(pk=self.user.pk).update(school=None)

        self.assertEmptySheet(self.load())


# --------------------------------------------------------------------------- children: save

class SaveAttendanceChildrenTests(AttendanceTestCase):
    def setUp(self):
        super().setUp()
        self.registration = self.add_registration(nationality=self.nationality)
        self.child = self.registration.child
        self.url = reverse('alp:save_attendance_children')

    def body(self, children=None, **overrides):
        data = {
            'attendance_date': self.day_iso,
            'round_id': self.round.pk,
            'programme': self.programme.pk,
            'attendance_day_off': 'No',
            'close_reason': '',
            'children_attendance': [child_row(self.registration)] if children is None else children,
        }
        data.update(overrides)
        return data

    def save(self, body):
        return self.post_json('save_attendance_children', body)

    def assertSaveRejected(self, response):
        self.assertEqual(response.status_code, 400)
        payload = response.json()
        self.assertIs(payload['result'], False)
        self.assertTrue(payload['error'])
        self.assertEqual(ALPAttendance.objects.count(), 0)
        self.assertEqual(ALPAttendanceChild.objects.count(), 0)

    # -- access ---------------------------------------------------------------

    def test_get_is_not_allowed(self):
        self.assertEqual(self.client.get(self.url).status_code, 405)

    def test_anonymous_is_redirected_to_login(self):
        self.client.logout()

        response = self.save(self.body())

        self.assertRedirects(response, f'/?next={self.url}', fetch_redirect_response=False)
        self.assertEqual(ALPAttendance.objects.count(), 0)

    def test_superuser_is_forbidden(self):
        self.client.force_login(User.objects.create_superuser('root', 'r@x.com', 'password', school=self.school))

        response = self.save(self.body())

        self.assertEqual(response.status_code, 403)
        self.assertEqual(ALPAttendance.objects.count(), 0)

    def test_user_without_alp_group_is_forbidden(self):
        self.client.force_login(User.objects.create_user('outsider', password='password', school=self.school))

        response = self.save(self.body())

        self.assertEqual(response.status_code, 403)
        self.assertEqual(ALPAttendance.objects.count(), 0)

    def test_alp_user_without_school_gets_400(self):
        User.objects.filter(pk=self.user.pk).update(school=None)

        response = self.save(self.body())

        self.assertEqual(response.status_code, 400)
        self.assertIn(b'No school assigned', response.content)
        self.assertEqual(ALPAttendance.objects.count(), 0)

    # -- payload validation ----------------------------------------------------

    def test_empty_body_is_400(self):
        response = self.client.post(self.url, data='', content_type='application/json')

        self.assertEqual(response.status_code, 400)

    def test_invalid_json_is_400(self):
        response = self.client.post(self.url, data='{not json', content_type='application/json')

        self.assertEqual(response.status_code, 400)

    def test_json_list_is_400(self):
        response = self.save([self.body()])

        self.assertEqual(response.status_code, 400)
        self.assertEqual(ALPAttendance.objects.count(), 0)

    def test_unparsable_date_is_rejected(self):
        for value in ('nope', '2026-13-45', '', None):
            with self.subTest(attendance_date=value):
                self.assertSaveRejected(self.save(self.body(attendance_date=value)))

    def test_missing_date_is_rejected(self):
        body = self.body()
        del body['attendance_date']

        self.assertSaveRejected(self.save(body))

    def test_future_date_is_rejected(self):
        tomorrow = (self.today + timedelta(days=1)).isoformat()

        self.assertSaveRejected(self.save(self.body(attendance_date=tomorrow)))

    def test_empty_round_is_rejected(self):
        self.assertSaveRejected(self.save(self.body(round_id='')))

    def test_empty_programme_is_rejected(self):
        self.assertSaveRejected(self.save(self.body(programme='')))

    def test_non_numeric_round_or_programme_is_rejected(self):
        self.assertSaveRejected(self.save(self.body(round_id='abc')))
        self.assertSaveRejected(self.save(self.body(programme='abc')))

    # -- happy path ------------------------------------------------------------

    def test_success_creates_the_day_and_one_row_per_child(self):
        absent = self.add_registration(first_name='Absent')

        response = self.save(self.body(children=[
            child_row(self.registration, attended='Yes'),
            child_row(absent, attended='No', absence_reason='Sick', absence_reason_other='fever'),
        ]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'result': True})
        attendance = ALPAttendance.objects.get()
        self.assertEqual(
            (attendance.school, attendance.round, attendance.programme, attendance.attendance_date,
             attendance.day_off, attendance.close_reason),
            (self.school, self.round, self.programme, self.day, 'No', None),
        )
        rows = {row.registration_id: row for row in ALPAttendanceChild.objects.all()}
        self.assertEqual(set(rows), {self.registration.pk, absent.pk})
        present_row = rows[self.registration.pk]
        self.assertEqual((present_row.attendance_day, present_row.child, present_row.attended),
                         (attendance, self.child, 'Yes'))
        self.assertIsNone(present_row.absence_reason)
        self.assertEqual(present_row.absence_reason_other, '')
        absent_row = rows[absent.pk]
        self.assertEqual(
            (absent_row.attendance_day, absent_row.child, absent_row.attended,
             absent_row.absence_reason, absent_row.absence_reason_other),
            (attendance, absent.child, 'No', 'Sick', 'fever'),
        )

    def test_us_date_format_is_accepted_on_save(self):
        response = self.save(self.body(attendance_date=self.day_us))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(ALPAttendance.objects.get().attendance_date, self.day)

    def test_close_reason_is_ignored_when_the_day_is_not_off(self):
        response = self.save(self.body(attendance_day_off='No', close_reason='Strike'))

        self.assertEqual(response.status_code, 200)
        attendance = ALPAttendance.objects.get()
        self.assertEqual((attendance.day_off, attendance.close_reason), ('No', None))
        self.assertEqual(ALPAttendanceChild.objects.count(), 1)

    def test_attended_defaults_to_yes_and_clears_absence_fields(self):
        response = self.save(self.body(children=[
            child_row(self.registration, attended='Maybe', absence_reason='Sick', absence_reason_other='ignored'),
        ]))

        self.assertEqual(response.status_code, 200)
        row = ALPAttendanceChild.objects.get()
        self.assertEqual(row.attended, 'Yes')
        self.assertIsNone(row.absence_reason)
        self.assertEqual(row.absence_reason_other, '')

    def test_missing_attended_key_defaults_to_yes(self):
        response = self.save(self.body(children=[
            {'registration_id': self.registration.pk, 'child_id': self.child.pk},
        ]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(ALPAttendanceChild.objects.get().attended, 'Yes')

    def test_invalid_absence_reason_is_stored_as_none(self):
        response = self.save(self.body(children=[
            child_row(self.registration, attended='No', absence_reason='HACKED', absence_reason_other='details'),
        ]))

        self.assertEqual(response.status_code, 200)
        row = ALPAttendanceChild.objects.get()
        self.assertEqual(row.attended, 'No')
        self.assertIsNone(row.absence_reason)
        self.assertEqual(row.absence_reason_other, 'details')

    def test_valid_absence_reasons_are_stored(self):
        for reason in ('Sick', 'No transport', 'Other', 'Unspecified'):
            with self.subTest(absence_reason=reason):
                response = self.save(self.body(children=[child_row(self.registration, 'No', reason)]))

                self.assertEqual(response.status_code, 200)
                self.assertEqual(ALPAttendanceChild.objects.get().absence_reason, reason)

    def test_reposting_the_same_day_updates_in_place(self):
        self.save(self.body(children=[child_row(self.registration, 'No', 'Sick', 'fever')]))
        first_day = ALPAttendance.objects.get()
        first_row = ALPAttendanceChild.objects.get()

        response = self.save(self.body(children=[child_row(self.registration, 'Yes')]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(ALPAttendance.objects.count(), 1)
        self.assertEqual(ALPAttendanceChild.objects.count(), 1)
        row = ALPAttendanceChild.objects.get()
        self.assertEqual(row.pk, first_row.pk)
        self.assertEqual(row.attendance_day_id, first_day.pk)
        self.assertEqual((row.attended, row.absence_reason, row.absence_reason_other), ('Yes', None, ''))

    # -- rows that must be skipped -------------------------------------------

    def test_registration_of_another_school_is_skipped(self):
        foreign = self.add_registration(school=self.other_school_user().school, first_name='Foreign')

        response = self.save(self.body(children=[child_row(foreign, 'No', 'Sick'), child_row(self.registration)]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'result': True})
        self.assertEqual(ALPAttendance.objects.get().school, self.school)
        self.assertEqual(list(ALPAttendanceChild.objects.values_list('registration_id', flat=True)),
                         [self.registration.pk])

    def test_registration_of_another_round_or_programme_is_skipped(self):
        other_round = ALPRound.objects.create(name='Round 2025', current_year=False)
        other_programme = ALPProgram.objects.create(name='ALP Level 2')
        wrong_round = self.add_registration(round_=other_round, first_name='WrongRound')
        wrong_programme = self.add_registration(programme=other_programme, first_name='WrongProgramme')

        response = self.save(self.body(children=[
            child_row(wrong_round), child_row(wrong_programme), child_row(self.registration),
        ]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(ALPAttendanceChild.objects.values_list('registration_id', flat=True)),
                         [self.registration.pk])

    def test_soft_deleted_registration_is_skipped(self):
        deleted = self.add_registration(first_name='Deleted', deleted=True, deleted_by=self.user)

        response = self.save(self.body(children=[child_row(deleted), child_row(self.registration)]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(ALPAttendanceChild.objects.values_list('registration_id', flat=True)),
                         [self.registration.pk])

    def test_child_id_not_matching_the_registration_is_skipped(self):
        stranger = make_child(first_name='Stranger')

        response = self.save(self.body(children=[child_row(self.registration, child_id=stranger.pk)]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(ALPAttendance.objects.count(), 1)
        self.assertEqual(ALPAttendanceChild.objects.count(), 0)

    def test_malformed_child_entries_are_skipped(self):
        response = self.save(self.body(children=[
            'garbage', {'registration_id': 'abc', 'child_id': self.child.pk}, {'child_id': self.child.pk},
            child_row(self.registration),
        ]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(ALPAttendanceChild.objects.count(), 1)

    # -- day off ----------------------------------------------------------------

    def test_day_off_deletes_child_rows_and_stores_close_reason(self):
        self.save(self.body(children=[child_row(self.registration, 'No', 'Sick')]))
        self.assertEqual(ALPAttendanceChild.objects.count(), 1)

        response = self.save(self.body(attendance_day_off='Yes', close_reason='Strike',
                                       children=[child_row(self.registration, 'No', 'Sick')]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'result': True})
        attendance = ALPAttendance.objects.get()
        self.assertEqual((attendance.day_off, attendance.close_reason), ('Yes', 'Strike'))
        self.assertEqual(ALPAttendanceChild.objects.count(), 0)

    def test_day_off_with_close_reason_other_is_stored_as_none(self):
        response = self.save(self.body(attendance_day_off='Yes', close_reason='Other', children=[]))

        self.assertEqual(response.status_code, 200)
        attendance = ALPAttendance.objects.get()
        self.assertEqual((attendance.day_off, attendance.close_reason), ('Yes', None))
        self.assertEqual(ALPAttendanceChild.objects.count(), 0)

    def test_day_off_only_deletes_rows_of_that_day(self):
        previous_day = self.day - timedelta(days=1)
        self.save(self.body(attendance_date=previous_day.isoformat()))
        self.assertEqual(ALPAttendanceChild.objects.count(), 1)

        response = self.save(self.body(attendance_day_off='Yes', close_reason='Public Holiday'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(ALPAttendance.objects.count(), 2)
        self.assertEqual(ALPAttendanceChild.objects.get().attendance_day.attendance_date, previous_day)


# --------------------------------------------------------------------------- teachers: loader

class LoadAttendanceTeachersTests(AttendanceTestCase):
    def setUp(self):
        super().setUp()
        self.teacher = ALPTeacher.objects.create(
            school=self.school, round=self.round, owner=self.user, first_name='Mohamad', last_name='Al Sayed',
        )

    def load(self, attendance_date=None):
        query = {'attendance_date': self.day_iso if attendance_date is None else attendance_date}
        return self.client.get(reverse('alp:load_attendance_teachers'), query)

    def assertEmptySheet(self, response):
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['instances'], [])
        self.assertEqual(response.context['new_instances'], [])

    def test_unsaved_day_lists_school_teachers_as_new_instances(self):
        for date_str in (self.day_iso, self.day_us):
            with self.subTest(attendance_date=date_str):
                response = self.load(date_str)

                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.context['instances'], [])
                self.assertEqual(response.context['new_instances'], [{
                    'teacher_id': self.teacher.pk, 'teacher_fullname': 'Mohamad Al Sayed', 'status': 'Present',
                }])
                self.assertContains(response, 'Mohamad Al Sayed')

    def test_teacher_without_first_name_is_still_listed(self):
        ALPTeacher.objects.filter(pk=self.teacher.pk).update(first_name=None)

        response = self.load()

        self.assertEqual(len(response.context['new_instances']), 1)
        self.assertEqual(response.context['new_instances'][0]['teacher_fullname'], 'Al Sayed')

    def test_teacher_without_any_name_is_still_listed(self):
        ALPTeacher.objects.filter(pk=self.teacher.pk).update(first_name=None, last_name=None)

        response = self.load()

        self.assertEqual(response.context['new_instances'][0]['teacher_id'], self.teacher.pk)
        self.assertEqual(response.context['new_instances'][0]['teacher_fullname'], '')

    def test_other_school_teacher_is_not_listed(self):
        ALPTeacher.objects.create(school=self.other_school_user().school, first_name='Foreign', last_name='Teacher')

        response = self.load()

        self.assertEqual([t['teacher_id'] for t in response.context['new_instances']], [self.teacher.pk])

    def test_saved_day_lists_existing_status(self):
        ALPTeacherAttendance.objects.create(teacher=self.teacher, date=self.day, status='Absent', owner=self.user)

        response = self.load(self.day_us)

        self.assertEqual(response.context['new_instances'], [])
        self.assertEqual(response.context['instances'], [{
            'teacher_id': self.teacher.pk, 'teacher_fullname': 'Mohamad Al Sayed', 'status': 'Absent',
        }])
        self.assertContains(response, f'id="status_no_{self.teacher.pk}"')

    def test_teacher_added_after_the_first_save_is_a_new_instance(self):
        ALPTeacherAttendance.objects.create(teacher=self.teacher, date=self.day, status='Present', owner=self.user)
        later = ALPTeacher.objects.create(school=self.school, first_name='Later', last_name='Teacher')

        response = self.load()

        self.assertEqual([t['teacher_id'] for t in response.context['instances']], [self.teacher.pk])
        self.assertEqual([t['teacher_id'] for t in response.context['new_instances']], [later.pk])

    def test_attendance_rows_without_teacher_are_skipped(self):
        ALPTeacherAttendance.objects.create(teacher=None, date=self.day, status='Absent', owner=self.user)

        response = self.load()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['instances'], [])
        self.assertEqual([t['teacher_id'] for t in response.context['new_instances']], [self.teacher.pk])

    def test_future_missing_or_garbage_date_returns_an_empty_sheet(self):
        tomorrow = (self.today + timedelta(days=1)).isoformat()
        self.assertEmptySheet(self.load(tomorrow))
        self.assertEmptySheet(self.load('garbage'))
        self.assertEmptySheet(self.client.get(reverse('alp:load_attendance_teachers')))

    def test_alp_user_without_school_gets_an_empty_sheet(self):
        User.objects.filter(pk=self.user.pk).update(school=None)

        self.assertEmptySheet(self.load())


# --------------------------------------------------------------------------- teachers: save

class SaveAttendanceTeachersTests(AttendanceTestCase):
    def setUp(self):
        super().setUp()
        self.teacher = ALPTeacher.objects.create(
            school=self.school, round=self.round, owner=self.user, first_name='Mohamad', last_name='Al Sayed',
        )
        self.url = reverse('alp:save_attendance_teachers')

    def body(self, status='Present', teacher=None, **overrides):
        data = {
            'attendance_date': self.day_iso,
            'teachers_attendance': [{'teacher_id': (teacher or self.teacher).pk, 'status': status}],
        }
        data.update(overrides)
        return data

    def save(self, body):
        return self.post_json('save_attendance_teachers', body)

    def assertSaveRejected(self, response):
        self.assertEqual(response.status_code, 400)
        payload = response.json()
        self.assertIs(payload['result'], False)
        self.assertTrue(payload['error'])
        self.assertEqual(ALPTeacherAttendance.objects.count(), 0)

    def test_get_is_not_allowed(self):
        self.assertEqual(self.client.get(self.url).status_code, 405)

    def test_anonymous_is_redirected_to_login(self):
        self.client.logout()

        response = self.save(self.body())

        self.assertRedirects(response, f'/?next={self.url}', fetch_redirect_response=False)

    def test_superuser_and_non_alp_user_are_forbidden(self):
        for user in (User.objects.create_superuser('root', 'r@x.com', 'password', school=self.school),
                     User.objects.create_user('outsider', password='password', school=self.school)):
            with self.subTest(user=user.username):
                self.client.force_login(user)

                self.assertEqual(self.save(self.body()).status_code, 403)
        self.assertEqual(ALPTeacherAttendance.objects.count(), 0)

    def test_alp_user_without_school_gets_400(self):
        User.objects.filter(pk=self.user.pk).update(school=None)

        response = self.save(self.body())

        self.assertEqual(response.status_code, 400)
        self.assertIn(b'No school assigned', response.content)

    def test_empty_invalid_or_list_body_is_400(self):
        self.assertEqual(self.client.post(self.url, data='', content_type='application/json').status_code, 400)
        self.assertEqual(self.client.post(self.url, data='{', content_type='application/json').status_code, 400)
        self.assertEqual(self.save([self.body()]).status_code, 400)
        self.assertEqual(ALPTeacherAttendance.objects.count(), 0)

    def test_unparsable_or_missing_date_is_rejected(self):
        self.assertSaveRejected(self.save(self.body(attendance_date='nope')))
        self.assertSaveRejected(self.save({'teachers_attendance': [{'teacher_id': self.teacher.pk}]}))

    def test_future_date_is_rejected(self):
        tomorrow = (self.today + timedelta(days=1)).isoformat()

        self.assertSaveRejected(self.save(self.body(attendance_date=tomorrow)))

    def test_absent_is_stored_with_the_saving_user_as_owner(self):
        response = self.save(self.body(status='Absent'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'result': True})
        row = ALPTeacherAttendance.objects.get()
        self.assertEqual((row.teacher, row.date, row.status, row.owner), (self.teacher, self.day, 'Absent', self.user))

    def test_us_date_format_is_accepted_on_save(self):
        response = self.save(self.body(attendance_date=self.day_us))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(ALPTeacherAttendance.objects.get().date, self.day)

    def test_invalid_status_is_stored_as_present(self):
        for status in ('HACKED', '', None):
            with self.subTest(status=status):
                response = self.save(self.body(status=status))

                self.assertEqual(response.status_code, 200)
                self.assertEqual(ALPTeacherAttendance.objects.get().status, 'Present')

    def test_teacher_of_another_school_creates_nothing(self):
        foreign = ALPTeacher.objects.create(school=self.other_school_user().school, first_name='Foreign')

        response = self.save(self.body(status='Absent', teacher=foreign))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'result': True})
        self.assertEqual(ALPTeacherAttendance.objects.count(), 0)

    def test_malformed_teacher_entries_are_skipped(self):
        response = self.save(self.body(teachers_attendance=[
            'garbage', {'status': 'Absent'}, {'teacher_id': 'abc', 'status': 'Absent'},
            {'teacher_id': self.teacher.pk, 'status': 'Absent'},
        ]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(ALPTeacherAttendance.objects.count(), 1)

    def test_resave_updates_in_place(self):
        self.save(self.body(status='Absent'))
        first = ALPTeacherAttendance.objects.get()
        second_user = make_alp_school_user('colleague', school=self.school)
        self.client.force_login(second_user)

        response = self.save(self.body(status='Present'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(ALPTeacherAttendance.objects.count(), 1)
        row = ALPTeacherAttendance.objects.get()
        self.assertEqual(row.pk, first.pk)
        self.assertEqual((row.status, row.owner), ('Present', second_user))


# --------------------------------------------------------------------------- unit: filter_by_school

class FilterBySchoolTests(SimpleTestCase):
    """``filter_by_school`` only needs ``school_id`` on the user (no ``school`` attribute)."""

    def _user(self, school_id=42):
        return SimpleNamespace(school_id=school_id)

    def _sql(self, queryset):
        return queryset.query.sql_with_params()

    def test_registration_is_filtered_by_its_school_id(self):
        sql, params = self._sql(filter_by_school(ALPRegistration.objects.all(), self._user()))

        self.assertIn('"alp_alpregistration"."school_id" = %s', sql)
        self.assertEqual(params, (42,))

    def test_teacher_is_filtered_by_its_school_id(self):
        sql, params = self._sql(filter_by_school(ALPTeacher.objects.all(), self._user()))

        self.assertIn('"alp_alpteacher"."school_id" = %s', sql)
        self.assertEqual(params, (42,))

    def test_attendance_is_filtered_by_its_school_id(self):
        sql, params = self._sql(filter_by_school(ALPAttendance.objects.all(), self._user()))

        self.assertIn('"alp_alpattendance"."school_id" = %s', sql)
        self.assertEqual(params, (42,))

    def test_teacher_attendance_is_filtered_through_its_teacher(self):
        sql, params = self._sql(filter_by_school(ALPTeacherAttendance.objects.all(), self._user()))

        self.assertIn('"alp_alpteacher"."school_id" = %s', sql)
        self.assertEqual(params, (42,))

    def test_grading_is_filtered_through_its_registration(self):
        sql, params = self._sql(filter_by_school(ALPGrading.objects.all(), self._user()))

        self.assertIn('"alp_alpregistration"."school_id" = %s', sql)
        self.assertEqual(params, (42,))

    def test_attendance_child_is_filtered_through_its_registration(self):
        sql, params = self._sql(filter_by_school(ALPAttendanceChild.objects.all(), self._user()))

        self.assertIn('"alp_alpregistration"."school_id" = %s', sql)
        self.assertEqual(params, (42,))

    def test_user_without_school_id_gets_an_empty_queryset(self):
        for queryset in (ALPRegistration.objects.all(), ALPTeacher.objects.all(), ALPAttendance.objects.all(),
                         ALPTeacherAttendance.objects.all(), ALPGrading.objects.all(),
                         ALPAttendanceChild.objects.all()):
            with self.subTest(model=queryset.model.__name__):
                self.assertIsInstance(filter_by_school(queryset, self._user(school_id=None)), EmptyQuerySet)

    def test_user_object_without_school_id_attribute_gets_an_empty_queryset(self):
        self.assertIsInstance(filter_by_school(ALPRegistration.objects.all(), SimpleNamespace()), EmptyQuerySet)

    def test_superuser_with_a_school_is_still_filtered(self):
        user = SimpleNamespace(is_superuser=True, school_id=42)

        sql, params = self._sql(filter_by_school(ALPAttendanceChild.objects.all(), user))

        self.assertEqual(params, (42,))

    def test_models_without_a_school_relation_are_returned_unchanged(self):
        sql, params = self._sql(filter_by_school(ALPRound.objects.all(), self._user()))

        self.assertNotIn('school', sql)
        self.assertEqual(params, ())


# --------------------------------------------------------------------------- unit: attendance_date

class AttendanceChildAttendanceDateTests(SimpleTestCase):
    def test_returns_empty_string_without_attendance_day(self):
        self.assertEqual(ALPAttendanceChild(attendance_day=None).attendance_date, '')

    def test_returns_empty_string_when_the_day_has_no_date(self):
        row = ALPAttendanceChild(attendance_day=ALPAttendance(attendance_date=None))

        self.assertEqual(row.attendance_date, '')

    def test_returns_the_day_formatted_as_dd_mm_yyyy(self):
        row = ALPAttendanceChild(attendance_day=ALPAttendance(attendance_date=date(2026, 9, 1)))

        self.assertEqual(row.attendance_date, '01/09/2026')
