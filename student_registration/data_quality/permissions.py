from django.contrib.auth.models import Group, Permission

from .constants import DATA_QUALITY_REVIEWER_GROUP

REVIEWER_PERMISSION_CODENAMES = (
    "view_dataqualityrule",
    "view_dataqualityrun",
    "view_dataqualityissue",
    "change_dataqualityissue",
    "view_dataqualityauditevent",
    "run_data_quality_checks",
    "review_data_quality_issue",
    "view_cross_partner_evidence",
)


def ensure_reviewer_group(**kwargs):
    """Create the reviewer group and attach only data-quality permissions."""

    group, _ = Group.objects.get_or_create(name=DATA_QUALITY_REVIEWER_GROUP)
    permissions = Permission.objects.filter(
        content_type__app_label="data_quality",
        codename__in=REVIEWER_PERMISSION_CODENAMES,
    )
    group.permissions.set(permissions)


def can_review_data_quality(user):
    return bool(
        user
        and user.is_authenticated
        and (
            user.is_superuser
            or user.has_perm("data_quality.review_data_quality_issue")
        )
    )


def can_view_cross_partner_evidence(user):
    return bool(
        user
        and user.is_authenticated
        and (
            user.is_superuser
            or user.has_perm("data_quality.view_cross_partner_evidence")
        )
    )
