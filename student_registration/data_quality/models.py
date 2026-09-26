from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class RuleStatus(models.TextChoices):
    DRAFT = "draft", _("Draft")
    MONITORING = "monitoring", _("Monitoring")
    ACTIVE_WARNING = "active_warning", _("Active warning")
    ACTIVE_BLOCKING = "active_blocking", _("Active blocking")
    DISABLED = "disabled", _("Disabled")


class Severity(models.TextChoices):
    INFO = "info", _("Information")
    WARNING = "warning", _("Warning")
    ERROR = "error", _("Error")


class DataQualityRule(models.Model):
    """Versioned metadata for a deterministic data-quality rule."""

    code = models.CharField(max_length=64)
    version = models.PositiveIntegerField(default=1)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(
        max_length=32,
        choices=RuleStatus.choices,
        default=RuleStatus.DRAFT,
        db_index=True,
    )
    severity = models.CharField(
        max_length=16,
        choices=Severity.choices,
        default=Severity.WARNING,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("code", "-version")
        constraints = [
            models.UniqueConstraint(
                fields=("code", "version"),
                name="unique_data_quality_rule_version",
            )
        ]
        permissions = [
            ("run_data_quality_checks", "Can run data quality checks"),
        ]

    def __str__(self):
        return f"{self.code} v{self.version}"


class RunStatus(models.TextChoices):
    RUNNING = "running", _("Running")
    COMPLETED = "completed", _("Completed")
    FAILED = "failed", _("Failed")


class DataQualityRun(models.Model):
    """Audit record for one monitor-only evaluation operation."""

    status = models.CharField(
        max_length=16,
        choices=RunStatus.choices,
        default=RunStatus.RUNNING,
        db_index=True,
    )
    monitor_only = models.BooleanField(default=True, editable=False)
    scope = models.JSONField(default=dict, blank=True)
    triggered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="data_quality_runs",
    )
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    records_checked = models.PositiveIntegerField(default=0)
    rules_evaluated = models.PositiveIntegerField(default=0)
    failures_found = models.PositiveIntegerField(default=0)
    error_message = models.TextField(blank=True)

    class Meta:
        ordering = ("-started_at",)

    def complete(self, *, records_checked, rules_evaluated, failures_found):
        self.status = RunStatus.COMPLETED
        self.finished_at = timezone.now()
        self.records_checked = records_checked
        self.rules_evaluated = rules_evaluated
        self.failures_found = failures_found
        self.error_message = ""
        self.save(
            update_fields=(
                "status",
                "finished_at",
                "records_checked",
                "rules_evaluated",
                "failures_found",
                "error_message",
            )
        )

    def fail(self, error_message):
        self.status = RunStatus.FAILED
        self.finished_at = timezone.now()
        self.error_message = str(error_message)
        self.save(update_fields=("status", "finished_at", "error_message"))


class IssueStatus(models.TextChoices):
    OPEN = "open", _("Open")
    IN_REVIEW = "in_review", _("In review")
    RESOLVED = "resolved", _("Resolved")
    DISMISSED = "dismissed", _("Dismissed")


class DataQualityIssue(models.Model):
    """A monitor-only rule finding attached to an arbitrary domain record."""

    rule = models.ForeignKey(
        DataQualityRule,
        on_delete=models.PROTECT,
        related_name="issues",
    )
    rule_version = models.PositiveIntegerField()
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveBigIntegerField()
    subject = GenericForeignKey("content_type", "object_id")
    subject_label = models.CharField(max_length=255, blank=True)
    run = models.ForeignKey(
        DataQualityRun,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="issues",
    )
    status = models.CharField(
        max_length=16,
        choices=IssueStatus.choices,
        default=IssueStatus.OPEN,
        db_index=True,
    )
    severity = models.CharField(max_length=16, choices=Severity.choices)
    affected_fields = models.JSONField(default=list, blank=True)
    evidence = models.JSONField(default=dict, blank=True)
    message_code = models.CharField(max_length=128)
    message_params = models.JSONField(default=dict, blank=True)
    first_detected_at = models.DateTimeField(auto_now_add=True)
    last_detected_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolution_note = models.TextField(blank=True)

    class Meta:
        ordering = ("-last_detected_at",)
        indexes = [
            models.Index(
                fields=("content_type", "object_id", "status"),
                name="dq_issue_subject_status_idx",
            )
        ]
        constraints = [
            models.UniqueConstraint(
                fields=("content_type", "object_id", "rule", "rule_version"),
                name="unique_quality_issue_subject_rule",
            )
        ]
        permissions = [
            ("review_data_quality_issue", "Can review data quality issues"),
            ("view_cross_partner_evidence", "Can view cross-partner evidence"),
        ]

    def __str__(self):
        return f"{self.rule} on {self.subject_label or self.object_id}"


class AuditAction(models.TextChoices):
    CREATED = "created", _("Created")
    REOPENED = "reopened", _("Reopened")
    DETECTED_AGAIN = "detected_again", _("Detected again")
    REVIEW_STARTED = "review_started", _("Review started")
    RESOLVED = "resolved", _("Resolved")
    DISMISSED = "dismissed", _("Dismissed")


class DataQualityAuditEvent(models.Model):
    """Append-only audit event for issue creation and review activity."""

    issue = models.ForeignKey(
        DataQualityIssue,
        on_delete=models.CASCADE,
        related_name="audit_events",
    )
    action = models.CharField(max_length=32, choices=AuditAction.choices)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="data_quality_audit_events",
    )
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("created_at", "id")

    def __str__(self):
        return f"{self.issue_id}: {self.action}"
