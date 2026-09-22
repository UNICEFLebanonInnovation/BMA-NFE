"""Pure-Python contracts for QA test support constants."""

import unittest

from student_registration.tests.constants import DATA_QUALITY_REVIEWER_GROUP


class TestSupportContractTests(unittest.TestCase):
    def test_reviewer_group_name_is_stable(self):
        self.assertEqual(DATA_QUALITY_REVIEWER_GROUP, "DATA_QUALITY_REVIEWER")
