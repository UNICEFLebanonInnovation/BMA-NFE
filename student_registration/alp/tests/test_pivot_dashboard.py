from types import SimpleNamespace

from django.test import SimpleTestCase

from student_registration.alp.views import _alp_pivot_queryset


class ALPPivotQuerysetTests(SimpleTestCase):
    def test_school_focal_point_is_limited_to_assigned_school(self):
        user = SimpleNamespace(is_superuser=False, is_staff=False, school_id=42)
        user.school = SimpleNamespace(pk=user.school_id)

        queryset = _alp_pivot_queryset(user)
        sql, params = queryset.query.sql_with_params()

        self.assertIn('school_id', sql)
        self.assertIn(user.school_id, params)

    def test_staff_user_can_report_across_all_schools(self):
        user = SimpleNamespace(is_superuser=False, is_staff=True, school_id=42)

        queryset = _alp_pivot_queryset(user)
        sql, params = queryset.query.sql_with_params()

        self.assertNotIn('school_id', sql)
        self.assertEqual(params, (False,))

    def test_superuser_can_report_across_all_schools(self):
        user = SimpleNamespace(is_superuser=True, is_staff=True, school_id=None)

        queryset = _alp_pivot_queryset(user)
        sql, params = queryset.query.sql_with_params()

        self.assertNotIn('school_id', sql)
        self.assertEqual(params, (False,))
