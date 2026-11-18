from django.db import IntegrityError, transaction
from django.test import TestCase

from student_registration.data_quality.models import (
    DataQualityRule,
    DataQualityRun,
    RuleStatus,
    RunStatus,
)


class DataQualityRuleTests(TestCase):
    def test_rule_code_and_version_are_unique_together(self):
        DataQualityRule.objects.create(
            code="DQ-TEST-001",
            version=1,
            name="Test rule",
            status=RuleStatus.MONITORING,
        )

        with self.assertRaises(IntegrityError), transaction.atomic():
            DataQualityRule.objects.create(
                code="DQ-TEST-001",
                version=1,
                name="Duplicate version",
                status=RuleStatus.MONITORING,
            )

        newer_rule = DataQualityRule.objects.create(
            code="DQ-TEST-001",
            version=2,
            name="New version",
            status=RuleStatus.MONITORING,
        )
        self.assertEqual(str(newer_rule), "DQ-TEST-001 v2")


class DataQualityRunTests(TestCase):
    def test_complete_records_monitoring_statistics(self):
        quality_run = DataQualityRun.objects.create(scope={"model": "child"})

        quality_run.complete(
            records_checked=3,
            rules_evaluated=9,
            failures_found=2,
        )

        self.assertTrue(quality_run.monitor_only)
        self.assertEqual(quality_run.status, RunStatus.COMPLETED)
        self.assertEqual(quality_run.records_checked, 3)
        self.assertEqual(quality_run.rules_evaluated, 9)
        self.assertEqual(quality_run.failures_found, 2)
        self.assertIsNotNone(quality_run.finished_at)

    def test_fail_records_error_without_raising_it_again(self):
        quality_run = DataQualityRun.objects.create()

        quality_run.fail("Rule execution failed")

        self.assertEqual(quality_run.status, RunStatus.FAILED)
        self.assertEqual(quality_run.error_message, "Rule execution failed")
        self.assertIsNotNone(quality_run.finished_at)
