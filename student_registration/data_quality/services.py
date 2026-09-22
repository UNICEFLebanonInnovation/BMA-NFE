from dataclasses import dataclass, field

from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.utils import timezone

from .models import (
    AuditAction,
    DataQualityAuditEvent,
    DataQualityIssue,
    DataQualityRule,
    IssueStatus,
    RuleStatus,
)


@dataclass(frozen=True)
class RuleEvaluation:
    """Structured, serializable result returned by a deterministic rule."""

    rule_code: str
    rule_version: int
    passed: bool
    affected_fields: tuple = ()
    evidence: dict = field(default_factory=dict)
    message_code: str = ""
    message_params: dict = field(default_factory=dict)


class RuleNotAvailable(LookupError):
    """Raised when an evaluation has no active rule metadata."""


class MonitorOnlyIssueService:
    """Persist rule results without blocking or changing the subject record."""

    executable_statuses = (
        RuleStatus.MONITORING,
        RuleStatus.ACTIVE_WARNING,
        RuleStatus.ACTIVE_BLOCKING,
    )

    def _get_rule(self, evaluation):
        try:
            return DataQualityRule.objects.get(
                code=evaluation.rule_code,
                version=evaluation.rule_version,
                status__in=self.executable_statuses,
            )
        except DataQualityRule.DoesNotExist as error:
            raise RuleNotAvailable(
                f"Rule {evaluation.rule_code} v{evaluation.rule_version} is not available"
            ) from error

    @transaction.atomic
    def record(self, *, subject, evaluation, run=None, actor=None):
        """Create, refresh, reopen, or resolve one monitor-only finding."""

        if subject.pk is None:
            raise ValueError("A saved subject is required for data-quality evaluation")

        rule = self._get_rule(evaluation)
        content_type = ContentType.objects.get_for_model(
            subject,
            for_concrete_model=False,
        )
        lookup = {
            "content_type": content_type,
            "object_id": subject.pk,
            "rule": rule,
            "rule_version": evaluation.rule_version,
        }

        if evaluation.passed:
            issue = DataQualityIssue.objects.filter(**lookup).first()
            if issue and issue.status in (IssueStatus.OPEN, IssueStatus.IN_REVIEW):
                issue.status = IssueStatus.RESOLVED
                issue.resolved_at = timezone.now()
                issue.resolution_note = "Resolved by a subsequent monitor-only evaluation."
                issue.run = run
                issue.save(
                    update_fields=(
                        "status",
                        "resolved_at",
                        "resolution_note",
                        "run",
                        "last_detected_at",
                    )
                )
                DataQualityAuditEvent.objects.create(
                    issue=issue,
                    action=AuditAction.RESOLVED,
                    actor=actor,
                    metadata={"automatic": True},
                )
            return issue

        defaults = {
            "subject_label": str(subject)[:255],
            "run": run,
            "severity": rule.severity,
            "affected_fields": list(evaluation.affected_fields),
            "evidence": evaluation.evidence,
            "message_code": evaluation.message_code,
            "message_params": evaluation.message_params,
            "resolved_at": None,
            "resolution_note": "",
        }
        issue, created = DataQualityIssue.objects.get_or_create(
            **lookup,
            defaults={**defaults, "status": IssueStatus.OPEN},
        )
        action = AuditAction.CREATED
        if not created:
            action = AuditAction.DETECTED_AGAIN
            if issue.status in (IssueStatus.RESOLVED, IssueStatus.DISMISSED):
                issue.status = IssueStatus.OPEN
                action = AuditAction.REOPENED
            for attribute, value in defaults.items():
                setattr(issue, attribute, value)
            issue.save()

        DataQualityAuditEvent.objects.create(
            issue=issue,
            action=action,
            actor=actor,
            metadata={"run_id": run.pk if run else None},
        )
        return issue
