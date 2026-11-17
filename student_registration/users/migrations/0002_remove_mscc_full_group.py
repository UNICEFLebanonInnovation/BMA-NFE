"""Retire a redundant UI role without losing existing model-permission grants."""
from django.conf import settings
from django.db import migrations


def remove_mscc_full_group(apps, schema_editor):
    alias = schema_editor.connection.alias
    Group = apps.get_model('auth', 'Group')
    User = apps.get_model(*settings.AUTH_USER_MODEL.split('.'))
    legacy = Group.objects.using(alias).filter(name='MSCC_FULL').first()
    if legacy is None:
        return

    # The legacy UI role normally has no model permissions. Preserve any
    # deployment-specific grants for its existing members only; do not add
    # those grants to another group or assign a broader replacement role.
    permission_ids = list(legacy.permissions.using(alias).values_list('pk', flat=True))
    if permission_ids:
        DirectPermission = User.user_permissions.through
        member_ids = (User.objects.using(alias).filter(groups=legacy)
                      .order_by().values_list('pk', flat=True).iterator())
        rows = []
        for user_id in member_ids:
            for permission_id in permission_ids:
                rows.append(DirectPermission(user_id=user_id, permission_id=permission_id))
                if len(rows) >= 500:
                    DirectPermission.objects.using(alias).bulk_create(
                        rows, batch_size=500, ignore_conflicts=True)
                    rows = []
        if rows:
            DirectPermission.objects.using(alias).bulk_create(
                rows, batch_size=500, ignore_conflicts=True)

    legacy.delete(using=alias)


class Migration(migrations.Migration):
    dependencies = [('users', '0001_initial')]

    # Removed memberships cannot be reconstructed on rollback. This data
    # cleanup intentionally has no reverse operation.
    operations = [migrations.RunPython(remove_mscc_full_group)]
