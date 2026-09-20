# -*- coding: utf-8 -*-
"""What `field_spec` promises the app about a field.

The app enforces exactly the rules this module exports, so a rule that is not
here is a rule the worker only meets after a push, in an error report, with
the family long gone. These tests pin the export itself rather than a whole
bootstrap, so they need no database.
"""
from __future__ import unicode_literals

from django import forms
from django.core.validators import (
    MaxValueValidator, MinLengthValidator, MinValueValidator, RegexValidator,
)
from django.test import SimpleTestCase

from ..schema import attendance_schema, field_spec

ONLY_LETTERS = RegexValidator(
    regex=r'^[A-Za-zء-يٮ-ۓ\s]+$',
    message='Only alphabetic characters are allowed.',
)


class FieldSpecRuleTests(SimpleTestCase):
    def test_a_regex_validator_reaches_the_app_with_its_message(self):
        """The thirteen name fields on the child registration depend on this."""
        data = field_spec('child_first_name', forms.CharField(required=True, validators=[ONLY_LETTERS]))
        self.assertEqual(data['patterns'], [{
            'pattern': ONLY_LETTERS.regex.pattern,
            'message': 'Only alphabetic characters are allowed.',
        }])
        # Also as a scalar, so an APK already in the field keeps working.
        self.assertEqual(data['pattern'], ONLY_LETTERS.regex.pattern)
        self.assertEqual(data['pattern_message'], 'Only alphabetic characters are allowed.')

    def test_a_regex_fields_own_regex_is_not_duplicated(self):
        data = field_spec('unhcr', forms.RegexField(regex=r'^\d{4}$'))
        self.assertEqual([p['pattern'] for p in data['patterns']], [r'^\d{4}$'])

    def test_bounds_given_as_validators_are_exported(self):
        data = field_spec('n', forms.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(9)]))
        self.assertEqual((data['min_value'], data['max_value']), (1, 9))

    def test_bounds_given_as_arguments_win_over_validators(self):
        data = field_spec('n', forms.IntegerField(min_value=3, max_value=18))
        self.assertEqual((data['min_value'], data['max_value']), (3, 18))

    def test_min_length_is_exported(self):
        data = field_spec('code', forms.CharField(max_length=5, validators=[MinLengthValidator(3)]))
        self.assertEqual((data['min_length'], data['max_length']), (3, 5))

    def test_a_decimal_is_not_typed_as_an_integer(self):
        """DecimalField subclasses IntegerField, so order decides this."""
        data = field_spec('weight', forms.DecimalField(max_digits=5, decimal_places=2, min_value=0, max_value=200))
        self.assertEqual(data['type'], 'decimal')
        self.assertEqual((data['max_digits'], data['decimal_places']), (5, 2))

    def test_an_integer_is_still_an_integer(self):
        self.assertEqual(field_spec('age', forms.IntegerField())['type'], 'number')

    def test_an_opaque_builtin_regex_is_not_shipped(self):
        """A URLValidator's pattern is enormous and not portable to Dart."""
        self.assertNotIn('patterns', field_spec('site', forms.URLField()))

    def test_an_email_keeps_its_type_rather_than_a_pattern(self):
        data = field_spec('email', forms.EmailField())
        self.assertEqual(data['type'], 'email')
        self.assertNotIn('patterns', data)

    def test_a_field_with_no_rules_carries_no_rule_keys(self):
        data = field_spec('note', forms.CharField(required=False))
        for key in ('patterns', 'pattern', 'min_length', 'min_value', 'max_value'):
            self.assertNotIn(key, data, key)


class _Spec(object):
    def __init__(self, kind, module='mscc'):
        self.kind = kind
        self.module = module
        self.key = '%s.attendance_day' % module
        self.label = 'Attendance day'
        self.description = ''


class AttendanceSchemaTests(SimpleTestCase):
    """The rules engine._validate_attendance_common enforces, told to the app."""

    def setUp(self):
        self.child = attendance_schema(_Spec('attendance'))
        self.teacher = attendance_schema(_Spec('teacher_attendance', module='alp'))

    def test_the_sheet_is_no_longer_fieldless(self):
        self.assertEqual([f['name'] for f in self.child['fields']],
                         ['attendance_date', 'attendance_day_off', 'close_reason'])
        self.assertEqual([f['name'] for f in self.child['row_fields']],
                         ['attended', 'absence_reason', 'absence_reason_other'])

    def test_the_date_is_required_and_cannot_be_in_the_future(self):
        date = self.child['fields'][0]
        self.assertTrue(date['required'])
        self.assertEqual(date['max_date'], 'today')

    def test_a_close_reason_is_required_only_on_a_day_off(self):
        rule = self.child['reveals'][0]
        self.assertEqual(rule['show'], ['close_reason'])
        self.assertTrue(rule['require'])
        self.assertFalse(self.child['fields'][2]['required'], 'not required in general')

    def test_an_absence_reason_is_required_only_for_an_absent_child(self):
        reasons, other = self.child['row_reveals']
        self.assertEqual((reasons['when']['in'], reasons['show'], reasons['require']),
                         (['No'], ['absence_reason'], True))
        self.assertEqual((other['when']['in'], other['show'], other['require']),
                         (['Other'], ['absence_reason_other'], True))

    def test_the_reason_lists_are_named_not_inlined(self):
        """So the validator checks the list the roster's own picker offers."""
        self.assertEqual(self.child['fields'][2]['choices_ref'], 'mscc.attendance.close_reason')
        self.assertEqual(self.child['row_fields'][1]['choices_ref'], 'mscc.attendance.absence_reason')

    def test_a_teacher_row_carries_status_and_no_required_flag(self):
        """create_teacher_attendance applies no required check, so nor do we."""
        self.assertEqual([f['name'] for f in self.teacher['row_fields']], ['status'])
        self.assertFalse(self.teacher['row_fields'][0]['required'])
        self.assertEqual([c['value'] for c in self.teacher['row_fields'][0]['choices']], ['Present', 'Absent'])

    def test_a_teacher_sheet_has_no_day_off(self):
        self.assertEqual([f['name'] for f in self.teacher['fields']], ['attendance_date'])
        self.assertEqual(self.teacher['reveals'], [])
        self.assertEqual(self.teacher['row_key'], 'teachers_attendance')
