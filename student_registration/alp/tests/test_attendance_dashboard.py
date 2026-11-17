from datetime import datetime
from types import SimpleNamespace
from unittest.mock import patch

from django.test import SimpleTestCase, override_settings

from student_registration.alp.views import _alp_attendance_queryset, _current_date


class CurrentDateTests(SimpleTestCase):
    @override_settings(USE_TZ=False)
    @patch('student_registration.alp.views.timezone.localdate')
    @patch('student_registration.alp.views.timezone.now')
    def test_naive_datetime_does_not_get_localized(self, now, localdate):
        now.return_value = datetime(2026, 8, 30, 13, 57, 32)

        self.assertEqual(_current_date(), datetime(2026, 8, 30).date())
        localdate.assert_not_called()


class ALPAttendanceDashboardQuerysetTests(SimpleTestCase):
    def test_school_user_is_limited_to_assigned_school(self):
        user = SimpleNamespace(is_superuser=False, school_id=42)

        queryset = _alp_attendance_queryset(user)
        sql, params = queryset.query.sql_with_params()

        self.assertIn('school_id', sql)
        self.assertIn(user.school_id, params)

    def test_superuser_can_report_across_all_schools(self):
        user = SimpleNamespace(is_superuser=True, school_id=None)

        queryset = _alp_attendance_queryset(user)
        sql, params = queryset.query.sql_with_params()

        self.assertNotIn('school_id', sql)
        self.assertEqual(params, ())

    def test_staff_user_can_report_across_all_schools(self):
        user = SimpleNamespace(
            is_superuser=False, is_staff=True, school_id=42
        )

        queryset = _alp_attendance_queryset(user)
        sql, params = queryset.query.sql_with_params()

        self.assertNotIn('school_id', sql)
        self.assertEqual(params, ())
