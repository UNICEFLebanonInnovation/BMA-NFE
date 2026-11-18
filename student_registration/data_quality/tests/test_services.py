from django.test import TestCase

from student_registration.data_quality.models import (
    AuditAction,
    DataQualityIssue,
    DataQualityRule,
    IssueStatus,
    RuleStatus,
    Severity,
)
from student_registration.data_quality.services import (
    MonitorOnlyIssueService,
    RuleEvaluation,
    RuleNotAvailable,
)
from student_registration.tests.factories import ChildFactory


class MonitorOnlyIssueServiceTests(TestCase):
    def setUp(self):
        self.rule = DataQualityRule.objects.create(
            code="DQ-ID-001",
            version=1,
            name="Identity confirmation matches",
            status=RuleStatus.MONITORING,
            severity=Severity.ERROR,
        )
        self.child = ChildFactory()
        self.service = MonitorOnlyIssueService()

    def failing_evaluation(self):
        return RuleEvaluation(
            rule_code=self.rule.code,
            rule_version=self.rule.version,
            passed=False,
            affected_fields=("individual_case_number", "individual_case_number_confirm"),
            evidence={"comparison": "mismatch"},
            message_code="data_quality.identity_confirmation_mismatch",
        )

    def test_failure_creates_one_open_issue_without_changing_subject(self):
        original_number = self.child.individual_case_number

        issue = self.service.record(
            subject=self.child,
            evaluation=self.failing_evaluation(),
        )

        self.child.refresh_from_db()
        self.assertEqual(self.child.individual_case_number, original_number)
        self.assertEqual(issue.status, IssueStatus.OPEN)
        self.assertEqual(issue.severity, Severity.ERROR)
        self.assertEqual(issue.affected_fields, [
            "individual_case_number",
            "individual_case_number_confirm",
        ])
        self.assertEqual(issue.audit_events.get().action, AuditAction.CREATED)

    def test_repeated_failure_refreshes_existing_issue(self):
        first_issue = self.service.record(
            subject=self.child,
            evaluation=self.failing_evaluation(),
        )
        second_issue = self.service.record(
            subject=self.child,
            evaluation=self.failing_evaluation(),
        )

        self.assertEqual(first_issue.pk, second_issue.pk)
        self.assertEqual(DataQualityIssue.objects.count(), 1)
        self.assertEqual(
            list(second_issue.audit_events.values_list("action", flat=True)),
            [AuditAction.CREATED, AuditAction.DETECTED_AGAIN],
        )

    def test_passing_evaluation_resolves_open_issue(self):
        issue = self.service.record(
            subject=self.child,
            evaluation=self.failing_evaluation(),
        )
        passing = RuleEvaluation(
            rule_code=self.rule.code,
            rule_version=self.rule.version,
            passed=True,
        )

        resolved = self.service.record(subject=self.child, evaluation=passing)

        self.assertEqual(resolved.pk, issue.pk)
        self.assertEqual(resolved.status, IssueStatus.RESOLVED)
        self.assertIsNotNone(resolved.resolved_at)
        self.assertEqual(
            resolved.audit_events.order_by("created_at", "id").last().action,
            AuditAction.RESOLVED,
        )

    def test_new_failure_reopens_resolved_issue(self):
        issue = self.service.record(
            subject=self.child,
            evaluation=self.failing_evaluation(),
        )
        self.service.record(
            subject=self.child,
            evaluation=RuleEvaluation(
                rule_code=self.rule.code,
                rule_version=self.rule.version,
                passed=True,
            ),
        )

        reopened = self.service.record(
            subject=self.child,
            evaluation=self.failing_evaluation(),
        )

        self.assertEqual(reopened.pk, issue.pk)
        self.assertEqual(reopened.status, IssueStatus.OPEN)
        self.assertEqual(
            reopened.audit_events.order_by("created_at", "id").last().action,
            AuditAction.REOPENED,
        )

    def test_draft_rule_cannot_create_issue(self):
        self.rule.status = RuleStatus.DRAFT
        self.rule.save(update_fields=("status",))

        with self.assertRaises(RuleNotAvailable):
            self.service.record(
                subject=self.child,
                evaluation=self.failing_evaluation(),
            )

    def test_unsaved_subject_is_rejected(self):
        child = ChildFactory.build()

        with self.assertRaisesMessage(ValueError, "A saved subject is required"):
            self.service.record(
                subject=child,
                evaluation=self.failing_evaluation(),
            )
