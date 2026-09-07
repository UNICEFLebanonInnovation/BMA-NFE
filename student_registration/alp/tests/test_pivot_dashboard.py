from types import SimpleNamespace

from django.test import SimpleTestCase

from student_registration.alp.views import _alp_pivot_queryset


def _school_filter(queryset):
    """Return the WHERE clause fragment that limits the query to a school."""
    sql, params = queryset.query.sql_with_params()
    where = sql.split(' WHERE ', 1)[1] if ' WHERE ' in sql else ''
    return where, params


class ALPPivotQuerysetTests(SimpleTestCase):
    def test_school_focal_point_is_limited_to_assigned_school(self):
        user = SimpleNamespace(is_superuser=False, is_staff=False, school_id=42)

        where, params = _school_filter(_alp_pivot_queryset(user))

        self.assertIn('"alp_alpregistration"."school_id" = ', where)
        self.assertIn(user.school_id, params)

    def test_school_focal_point_without_school_sees_nothing(self):
        user = SimpleNamespace(is_superuser=False, is_staff=False, school_id=None)

        self.assertTrue(_alp_pivot_queryset(user).query.is_empty())

    def test_staff_user_can_report_across_all_schools(self):
        user = SimpleNamespace(is_superuser=False, is_staff=True, school_id=42)

        where, params = _school_filter(_alp_pivot_queryset(user))

        self.assertNotIn('"alp_alpregistration"."school_id" = ', where)
        self.assertIn('"alp_alpregistration"."deleted"', where)
        self.assertEqual(params, ())

    def test_superuser_can_report_across_all_schools(self):
        user = SimpleNamespace(is_superuser=True, is_staff=True, school_id=None)

        where, params = _school_filter(_alp_pivot_queryset(user))

        self.assertNotIn('"alp_alpregistration"."school_id" = ', where)
        self.assertIn('"alp_alpregistration"."deleted"', where)
        self.assertEqual(params, ())
