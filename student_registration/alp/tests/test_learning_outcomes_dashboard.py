from datetime import datetime, timedelta
from types import SimpleNamespace

from django.test import SimpleTestCase

from student_registration.alp.views import build_learning_outcome_data


class LearningOutcomeDashboardTests(SimpleTestCase):
    def setUp(self):
        self.arabic = SimpleNamespace(
            id=1, material='Arabic', min_grade=0, max_grade=20
        )
        self.math = SimpleNamespace(
            id=2, material='Math', min_grade=10, max_grade=30
        )

    def grading(self, registration_id, created, data):
        return SimpleNamespace(
            registration_id=registration_id,
            created=created,
            grading_data=data,
        )

    def test_uses_latest_assessment_and_reports_improvement(self):
        first_date = datetime(2026, 1, 1)
        gradings = [
            self.grading(1, first_date, {'1': 8, '2': 18}),
            self.grading(1, first_date + timedelta(days=30), {'1': 16, '2': 26}),
            self.grading(2, first_date, {'1': 10, '2': 20}),
        ]

        result = build_learning_outcome_data(
            gradings, [self.arabic, self.math]
        )

        self.assertEqual(result['assessed_children'], 2)
        self.assertEqual(result['children_with_follow_up'], 1)
        self.assertEqual(result['improved_children'], 1)
        self.assertEqual(result['average_achievement'], 65.0)
        self.assertEqual(
            result['performance_bands'],
            [
                {'name': 'On track', 'y': 1},
                {'name': 'Developing', 'y': 1},
                {'name': 'Needs support', 'y': 0},
            ],
        )
        self.assertEqual(
            result['subjects'],
            [{'name': 'Arabic', 'y': 65.0}, {'name': 'Math', 'y': 65.0}],
        )

    def test_ignores_invalid_scores_and_handles_no_assessments(self):
        result = build_learning_outcome_data(
            [self.grading(1, datetime(2026, 1, 1), {'1': 'not a score'})],
            [self.arabic],
        )

        self.assertEqual(result['assessed_children'], 0)
        self.assertIsNone(result['average_achievement'])
        self.assertEqual(result['subjects'], [])

    def test_clamps_scores_outside_configured_range(self):
        result = build_learning_outcome_data(
            [self.grading(1, datetime(2026, 1, 1), {'1': 50, '2': 0})],
            [self.arabic, self.math],
        )

        self.assertEqual(result['average_achievement'], 50.0)
        self.assertEqual(
            result['subjects'],
            [{'name': 'Arabic', 'y': 100.0}, {'name': 'Math', 'y': 0.0}],
        )
