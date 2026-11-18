from django.contrib.auth.models import Group
from django.test import TestCase

from student_registration.data_quality.constants import DATA_QUALITY_REVIEWER_GROUP
from student_registration.data_quality.permissions import (
    can_review_data_quality,
    can_view_cross_partner_evidence,
    ensure_reviewer_group,
)
from student_registration.tests.factories import UserFactory


class DataQualityReviewerPermissionTests(TestCase):
    def setUp(self):
        ensure_reviewer_group()
        self.group = Group.objects.get(name=DATA_QUALITY_REVIEWER_GROUP)

    def test_reviewer_group_receives_review_and_cross_partner_permissions(self):
        reviewer = UserFactory()
        reviewer.groups.add(self.group)

        self.assertTrue(can_review_data_quality(reviewer))
        self.assertTrue(can_view_cross_partner_evidence(reviewer))

    def test_ordinary_authenticated_user_cannot_review_or_view_cross_partner_data(self):
        user = UserFactory()

        self.assertFalse(can_review_data_quality(user))
        self.assertFalse(can_view_cross_partner_evidence(user))

    def test_superuser_can_review_and_view_cross_partner_data(self):
        superuser = UserFactory(is_superuser=True, is_staff=True)

        self.assertTrue(can_review_data_quality(superuser))
        self.assertTrue(can_view_cross_partner_evidence(superuser))
