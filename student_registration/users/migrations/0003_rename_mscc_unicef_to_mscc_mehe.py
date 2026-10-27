"""Rename the central MSCC role while retaining members and grants."""
from django.conf import settings
from django.db import migrations


def rename_role(apps, schema_editor, old_name, new_name):
    alias = schema_editor.connection.alias
    Group = apps.get_model('auth', 'Group')
    legacy = Group.objects.using(alias).filter(name=old_name).first()
    if legacy is None:
        return

    destination = Group.objects.using(alias).filter(name=new_name).first()
    if destination is None:
        # Renaming in place retains the group's primary key and M2M rows.
        legacy.name = new_name
        legacy.save(using=alias, update_fields=['name'])
        return

    # Accommodate deployments that have already created the new role. Preserve
    # both groups' grants and members, without duplicating overlapping members.
    destination.permissions.add(*legacy.permissions.using(alias).values_list('pk', flat=True))
    User = apps.get_model(*settings.AUTH_USER_MODEL.split('.'))
    Membership = User.groups.through
    memberships = Membership.objects.using(alias)
    existing = memberships.filter(group_id=destination.pk).values('user_id')
    missing = memberships.filter(group_id=legacy.pk).exclude(user_id__in=existing)
    rows = []
    for user_id in missing.values_list('user_id', flat=True).iterator(chunk_size=500):
        rows.append(Membership(user_id=user_id, group_id=destination.pk))
        if len(rows) == 500:
            memberships.bulk_create(rows, batch_size=500)
            rows = []
    if rows:
        memberships.bulk_create(rows, batch_size=500)
    legacy.delete(using=alias)


def forwards(apps, schema_editor):
    rename_role(apps, schema_editor, 'MSCC_UNICEF', 'MSCC_MEHE')


def backwards(apps, schema_editor):
    # A pre-existing pair of groups cannot be split back into their original
    # memberships; rollback retains their union under the previous role name.
    rename_role(apps, schema_editor, 'MSCC_MEHE', 'MSCC_UNICEF')


class Migration(migrations.Migration):
    dependencies = [('users', '0002_remove_mscc_full_group')]

    operations = [migrations.RunPython(forwards, backwards)]
