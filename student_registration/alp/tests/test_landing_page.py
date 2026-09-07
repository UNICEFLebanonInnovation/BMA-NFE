"""Regression tests for the ALP landing page KPIs, trend and export history."""
import json
from datetime import timedelta

from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from student_registration.alp.models import (
    ALPAttendance,
    ALPAttendanceChild,
    ALPProgram,
    ALPRegistration,
    ALPRound,
)
from student_registration.backends.models import ExportHistory
from student_registration.child.models import Child
from student_registration.schools.models import School
from student_registration.students.models import Nationality
from student_registration.users.models import User


def make_alp_user(username, school, **extra):
    """Return a user of the ALP_SCHOOL group attached to ``school``."""
    group, _ = Group.objects.get_or_create(name='ALP_SCHOOL')
    user = User.objects.create_user(username=username, password='password', school=school, **extra)
    user.groups.add(group)
    return user


class LandingPageTestCase(TestCase):
    def setUp(self):
        # ``_current_date`` uses the naive local date when USE_TZ is off.
        self.now = timezone.now()
        self.today = self.now.date()
        self.school_a = School.objects.create(number='A-100', name='Alpha School')
        self.school_b = School.objects.create(number='B-200', name='Beta School')
        self.user = make_alp_user('focal-a', self.school_a)
        self.user_b = make_alp_user('focal-b', self.school_b)
        self.nationality = Nationality.objects.create(pk=1, name='Syrian', name_en='Syrian', code='SY')
        self.alp_round = ALPRound.objects.create(name='Round 2026', current_year=True)
        self.programme = ALPProgram.objects.create(name='Level 1')
        self.client.force_login(self.user)

    def add_registration(self, school, owner, first_name='Lina', days_ago=0):
        """Create an active registration; ``days_ago`` backdates its ``created`` stamp."""
        child = Child.objects.create(
            first_name=first_name, father_name='Ahmad', last_name='Sayed', mother_fullname='Fatima Ali',
            gender='Female', nationality=self.nationality, birthday_year='2014',
            birthday_month='5', birthday_day='10',
        )
        registration = ALPRegistration.objects.create(
            child=child, school=school, round=self.alp_round, programme=self.programme,
            owner=owner, registration_date=self.today,
        )
        if days_ago:
            ALPRegistration.objects.filter(pk=registration.pk).update(created=self.now - timedelta(days=days_ago))
            registration.refresh_from_db()
        return registration

    def add_attendance(self, school, rows, attendance_date=None):
        """Create an attendance day with one child row per ``(registration, attended)``."""
        day = ALPAttendance.objects.create(
            school=school, round=self.alp_round, programme=self.programme,
            attendance_date=attendance_date or self.today, day_off='No',
        )
        for registration, attended in rows:
            ALPAttendanceChild.objects.create(
                attendance_day=day, registration=registration, child=registration.child, attended=attended,
            )
        return day

    def landing(self):
        response = self.client.get(reverse('alp:landing_page'))
        self.assertEqual(response.status_code, 200)
        return response

    def trend(self, response):
        return json.loads(response.context['trend_data'])


class LandingPageKpiTests(LandingPageTestCase):
    def test_kpis_count_registrations_and_attendance_of_the_users_school(self):
        reg_today = self.add_registration(self.school_a, self.user)
        reg_old = self.add_registration(self.school_a, self.user, first_name='Omar', days_ago=10)
        reg_old_2 = self.add_registration(self.school_a, self.user, first_name='Sara', days_ago=10)
        self.add_attendance(self.school_a, [(reg_today, 'Yes'), (reg_old, 'Yes'), (reg_old_2, 'No')])

        response = self.landing()

        self.assertEqual(response.context['kpi_today'], 1)
        self.assertEqual(response.context['kpi_week'], 1)
        self.assertEqual(response.context['kpi_schools'], 1)
        self.assertEqual(response.context['kpi_attendance'], 67)
        self.assertContains(response, '67%')

    def test_trend_covers_the_last_fourteen_days_ending_today(self):
        self.add_registration(self.school_a, self.user)
        self.add_registration(self.school_a, self.user, first_name='Omar', days_ago=10)

        trend = self.trend(self.landing())

        self.assertEqual(len(trend), 14)
        self.assertEqual(trend[0]['date'], (self.today - timedelta(days=13)).isoformat())
        self.assertEqual(trend[-1], {'date': self.today.isoformat(), 'value': 1})
        self.assertEqual(trend[3], {'date': (self.today - timedelta(days=10)).isoformat(), 'value': 1})
        self.assertEqual(sum(point['value'] for point in trend), 2)

    def test_attendance_kpi_only_counts_the_current_month_up_to_today(self):
        registration = self.add_registration(self.school_a, self.user)
        self.add_attendance(self.school_a, [(registration, 'Yes')])
        # Forty days ago is always in a previous month; tomorrow is never counted.
        self.add_attendance(self.school_a, [(registration, 'No')], attendance_date=self.today - timedelta(days=40))
        self.add_attendance(self.school_a, [(registration, 'No')], attendance_date=self.today + timedelta(days=1))

        response = self.landing()

        self.assertEqual(response.context['kpi_attendance'], 100)

    def test_deleted_registrations_are_not_counted(self):
        registration = self.add_registration(self.school_a, self.user)
        ALPRegistration.objects.filter(pk=registration.pk).update(deleted=True, deleted_by=self.user)

        response = self.landing()

        self.assertEqual(response.context['kpi_today'], 0)
        self.assertEqual(response.context['kpi_week'], 0)
        self.assertEqual(response.context['kpi_schools'], 0)
        self.assertEqual(self.trend(response)[-1]['value'], 0)

    def test_kpis_without_any_data_are_zero(self):
        response = self.landing()

        self.assertEqual(response.context['kpi_today'], 0)
        self.assertEqual(response.context['kpi_week'], 0)
        self.assertEqual(response.context['kpi_schools'], 0)
        self.assertEqual(response.context['kpi_attendance'], 0)
        self.assertEqual([point['value'] for point in self.trend(response)], [0] * 14)
        self.assertEqual(response.context['recent_exports'], [])


class LandingPageScopingTests(LandingPageTestCase):
    def test_other_schools_rows_are_not_counted(self):
        reg_a = self.add_registration(self.school_a, self.user)
        reg_b = self.add_registration(self.school_b, self.user_b, first_name='Sara')
        self.add_attendance(self.school_a, [(reg_a, 'Yes')])
        self.add_attendance(self.school_b, [(reg_b, 'No')])

        response = self.landing()

        self.assertEqual(response.context['kpi_today'], 1)
        self.assertEqual(response.context['kpi_week'], 1)
        self.assertEqual(response.context['kpi_schools'], 1)
        self.assertEqual(response.context['kpi_attendance'], 100)
        self.assertEqual(self.trend(response)[-1]['value'], 1)

    def test_alp_user_without_a_school_gets_zero_kpis(self):
        reg_a = self.add_registration(self.school_a, self.user)
        self.add_attendance(self.school_a, [(reg_a, 'Yes')])
        self.add_registration(None, self.user, first_name='Orphan')
        lost = make_alp_user('lost', None)
        self.client.force_login(lost)

        response = self.landing()

        self.assertEqual(response.context['kpi_today'], 0)
        self.assertEqual(response.context['kpi_week'], 0)
        self.assertEqual(response.context['kpi_schools'], 0)
        self.assertEqual(response.context['kpi_attendance'], 0)
        self.assertEqual([point['value'] for point in self.trend(response)], [0] * 14)

    def test_superuser_counts_both_schools(self):
        reg_a = self.add_registration(self.school_a, self.user)
        reg_b = self.add_registration(self.school_b, self.user_b, first_name='Sara')
        self.add_attendance(self.school_a, [(reg_a, 'Yes')])
        self.add_attendance(self.school_b, [(reg_b, 'No')])
        superuser = User.objects.create_superuser('root', 'root@example.org', 'password')
        self.client.force_login(superuser)

        response = self.landing()

        self.assertEqual(response.context['kpi_today'], 2)
        self.assertEqual(response.context['kpi_week'], 2)
        self.assertEqual(response.context['kpi_schools'], 2)
        self.assertEqual(response.context['kpi_attendance'], 50)
        self.assertEqual(self.trend(response)[-1]['value'], 2)

    def test_anonymous_user_is_redirected_to_login(self):
        self.client.logout()

        response = self.client.get(reverse('alp:landing_page'))

        self.assertEqual(response.status_code, 302)
        self.assertIn('next=', response['Location'])

    def test_user_without_alp_group_is_forbidden(self):
        outsider = User.objects.create_user(username='outsider', password='password', school=self.school_a)
        self.client.force_login(outsider)

        response = self.client.get(reverse('alp:landing_page'))

        self.assertEqual(response.status_code, 403)


class LandingPageExportHistoryTests(LandingPageTestCase):
    def test_export_of_another_user_is_not_listed(self):
        ExportHistory.objects.create(
            export_type='ALP Registrations', created_by=self.user_b, file_url='https://example.org/x.csv',
            status='done',
        )

        response = self.landing()

        self.assertEqual(response.context['recent_exports'], [])
        self.assertNotContains(response, 'https://example.org/x.csv')
        self.assertContains(response, 'No recent export history.')

    def test_own_export_is_listed_with_file_url_and_created_display(self):
        export = ExportHistory.objects.create(
            export_type='ALP Registrations', created_by=self.user, file_url='https://example.org/mine.csv',
            status='done',
        )
        created = export.created
        if timezone.is_aware(created):
            created = timezone.localtime(created)

        response = self.landing()

        self.assertEqual(response.context['recent_exports'], [{
            'export_type': 'ALP Registrations',
            'created_display': created.strftime('%Y-%m-%d %H:%M'),
            'status': 'done',
            'file_url': 'https://example.org/mine.csv',
        }])
        self.assertContains(response, 'href="https://example.org/mine.csv"')

    def test_export_without_file_url_links_to_hash(self):
        ExportHistory.objects.create(export_type='ALP Registrations', created_by=self.user, file_url=None)

        response = self.landing()

        self.assertEqual(len(response.context['recent_exports']), 1)
        self.assertEqual(response.context['recent_exports'][0]['file_url'], '#')
        self.assertEqual(response.context['recent_exports'][0]['status'], 'pending')

    def test_only_alp_exports_are_listed(self):
        ExportHistory.objects.create(
            export_type='School List', created_by=self.user, file_url='https://example.org/s.csv',
        )
        ExportHistory.objects.create(
            export_type='ALP Teachers', created_by=self.user, file_url='https://example.org/t.csv',
        )

        response = self.landing()

        self.assertEqual(
            [export['export_type'] for export in response.context['recent_exports']],
            ['ALP Teachers'],
        )
