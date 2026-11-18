# Generated manually for the initial data-quality application.

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


def create_reviewer_group(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Group.objects.get_or_create(name="DATA_QUALITY_REVIEWER")


def remove_reviewer_group(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Group.objects.filter(name="DATA_QUALITY_REVIEWER").delete()


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("contenttypes", "0002_remove_content_type_name"),
    ]

    operations = [
        migrations.CreateModel(
            name="DataQualityRule",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("code", models.CharField(max_length=64)),
                ("version", models.PositiveIntegerField(default=1)),
                ("name", models.CharField(max_length=200)),
                ("description", models.TextField(blank=True)),
                ("status", models.CharField(choices=[("draft", "Draft"), ("monitoring", "Monitoring"), ("active_warning", "Active warning"), ("active_blocking", "Active blocking"), ("disabled", "Disabled")], db_index=True, default="draft", max_length=32)),
                ("severity", models.CharField(choices=[("info", "Information"), ("warning", "Warning"), ("error", "Error")], default="warning", max_length=16)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "ordering": ("code", "-version"),
                "permissions": [("run_data_quality_checks", "Can run data quality checks")],
            },
        ),
        migrations.CreateModel(
            name="DataQualityRun",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("status", models.CharField(choices=[("running", "Running"), ("completed", "Completed"), ("failed", "Failed")], db_index=True, default="running", max_length=16)),
                ("monitor_only", models.BooleanField(default=True, editable=False)),
                ("scope", models.JSONField(blank=True, default=dict)),
                ("started_at", models.DateTimeField(auto_now_add=True)),
                ("finished_at", models.DateTimeField(blank=True, null=True)),
                ("records_checked", models.PositiveIntegerField(default=0)),
                ("rules_evaluated", models.PositiveIntegerField(default=0)),
                ("failures_found", models.PositiveIntegerField(default=0)),
                ("error_message", models.TextField(blank=True)),
                ("triggered_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="data_quality_runs", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ("-started_at",)},
        ),
        migrations.CreateModel(
            name="DataQualityIssue",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("rule_version", models.PositiveIntegerField()),
                ("object_id", models.PositiveBigIntegerField()),
                ("subject_label", models.CharField(blank=True, max_length=255)),
                ("status", models.CharField(choices=[("open", "Open"), ("in_review", "In review"), ("resolved", "Resolved"), ("dismissed", "Dismissed")], db_index=True, default="open", max_length=16)),
                ("severity", models.CharField(choices=[("info", "Information"), ("warning", "Warning"), ("error", "Error")], max_length=16)),
                ("affected_fields", models.JSONField(blank=True, default=list)),
                ("evidence", models.JSONField(blank=True, default=dict)),
                ("message_code", models.CharField(max_length=128)),
                ("message_params", models.JSONField(blank=True, default=dict)),
                ("first_detected_at", models.DateTimeField(auto_now_add=True)),
                ("last_detected_at", models.DateTimeField(auto_now=True)),
                ("resolved_at", models.DateTimeField(blank=True, null=True)),
                ("resolution_note", models.TextField(blank=True)),
                ("content_type", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="contenttypes.contenttype")),
                ("rule", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="issues", to="data_quality.dataqualityrule")),
                ("run", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="issues", to="data_quality.dataqualityrun")),
            ],
            options={
                "ordering": ("-last_detected_at",),
                "permissions": [("review_data_quality_issue", "Can review data quality issues"), ("view_cross_partner_evidence", "Can view cross-partner evidence")],
            },
        ),
        migrations.CreateModel(
            name="DataQualityAuditEvent",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("action", models.CharField(choices=[("created", "Created"), ("reopened", "Reopened"), ("detected_again", "Detected again"), ("review_started", "Review started"), ("resolved", "Resolved"), ("dismissed", "Dismissed")], max_length=32)),
                ("metadata", models.JSONField(blank=True, default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("actor", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="data_quality_audit_events", to=settings.AUTH_USER_MODEL)),
                ("issue", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="audit_events", to="data_quality.dataqualityissue")),
            ],
            options={"ordering": ("created_at", "id")},
        ),
        migrations.AddConstraint(
            model_name="dataqualityrule",
            constraint=models.UniqueConstraint(fields=("code", "version"), name="unique_data_quality_rule_version"),
        ),
        migrations.AddIndex(
            model_name="dataqualityissue",
            index=models.Index(fields=["content_type", "object_id", "status"], name="dq_issue_subject_status_idx"),
        ),
        migrations.AddConstraint(
            model_name="dataqualityissue",
            constraint=models.UniqueConstraint(fields=("content_type", "object_id", "rule", "rule_version"), name="unique_quality_issue_subject_rule"),
        ),
        migrations.RunPython(create_reviewer_group, remove_reviewer_group),
    ]
