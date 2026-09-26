"""Database-backed contract tests for the shared QA factories."""

from django.test import TestCase

from student_registration.tests.constants import DATA_QUALITY_REVIEWER_GROUP
from student_registration.tests.factories import DataQualityReviewerFactory, RegistrationFactory


class DataQualityReviewerFactoryTests(TestCase):
    def test_reviewer_is_created_in_dedicated_group(self):
        reviewer = DataQualityReviewerFactory()

        self.assertTrue(
            reviewer.groups.filter(name=DATA_QUALITY_REVIEWER_GROUP).exists()
        )
        self.assertTrue(reviewer.check_password("test-password"))


class RegistrationFactoryTests(TestCase):
    def test_registration_relationships_use_the_same_partner(self):
        registration = RegistrationFactory()

        self.assertEqual(registration.center.partner, registration.partner)
        self.assertEqual(registration.owner.partner, registration.partner)
        self.assertIsNotNone(registration.child)
        self.assertIsNotNone(registration.round)
