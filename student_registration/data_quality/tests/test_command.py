from io import StringIO

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from student_registration.data_quality.models import DataQualityRun, RunStatus
from student_registration.tests.factories import ChildFactory


class AuditDataQualityCommandTests(TestCase):
    def test_audit_single_child_completes_monitor_only_run(self):
        child = ChildFactory()
        output = StringIO()

        call_command(
            "audit_data_quality",
            model="child",
            record_id=child.pk,
            stdout=output,
        )

        quality_run = DataQualityRun.objects.get()
        self.assertEqual(quality_run.status, RunStatus.COMPLETED)
        self.assertTrue(quality_run.monitor_only)
        self.assertEqual(quality_run.records_checked, 1)
        self.assertEqual(quality_run.rules_evaluated, 8)
        self.assertIn("monitor only", output.getvalue())

    def test_unknown_record_is_rejected_without_creating_run(self):
        with self.assertRaisesMessage(CommandError, "does not exist"):
            call_command(
                "audit_data_quality",
                model="child",
                record_id=999999,
            )

        self.assertFalse(DataQualityRun.objects.exists())
