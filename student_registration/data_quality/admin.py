from django.contrib import admin

from .models import (
    DataQualityAuditEvent,
    DataQualityIssue,
    DataQualityRule,
    DataQualityRun,
)


@admin.register(DataQualityRule)
class DataQualityRuleAdmin(admin.ModelAdmin):
    list_display = ("code", "version", "name", "status", "severity", "updated_at")
    list_filter = ("status", "severity")
    search_fields = ("code", "name", "description")


@admin.register(DataQualityRun)
class DataQualityRunAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "status",
        "monitor_only",
        "records_checked",
        "failures_found",
        "started_at",
        "finished_at",
    )
    list_filter = ("status", "monitor_only")
    readonly_fields = ("started_at", "finished_at")


@admin.register(DataQualityIssue)
class DataQualityIssueAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "rule",
        "subject_label",
        "status",
        "severity",
        "last_detected_at",
    )
    list_filter = ("status", "severity", "rule")
    search_fields = ("subject_label", "message_code", "rule__code")
    readonly_fields = ("first_detected_at", "last_detected_at")


@admin.register(DataQualityAuditEvent)
class DataQualityAuditEventAdmin(admin.ModelAdmin):
    list_display = ("id", "issue", "action", "actor", "created_at")
    list_filter = ("action",)
    readonly_fields = ("issue", "action", "actor", "metadata", "created_at")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
