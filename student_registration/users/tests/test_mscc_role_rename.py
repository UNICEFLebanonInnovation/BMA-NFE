"""Existing accounts retain the same central role when its name changes."""
from importlib import import_module
from types import SimpleNamespace

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import TestCase


class MsccRoleRenameTests(TestCase):
    def setUp(self):
        self.migration = import_module(
            'student_registration.users.migrations.0003_rename_mscc_unicef_to_mscc_mehe')
        # Exercise the migration with historical models, as migrate does.
        self.apps = MigrationExecutor(connection).loader.project_state(
            [('users', '0002_remove_mscc_full_group')]).apps
        self.schema_editor = SimpleNamespace(connection=connection)
        self.permission = Permission.objects.get(
            content_type__app_label='mscc', codename='view_registration')
        self.other_permission = Permission.objects.get(
            content_type__app_label='mscc', codename='view_teacher')

    def rename(self):
        self.migration.forwards(self.apps, self.schema_editor)

    def user(self, username, *groups):
        user = get_user_model().objects.create_user(username=username)
        user.groups.add(*groups)
        return user

    def test_missing_legacy_group_is_safe_and_does_not_create_a_role(self):
        self.rename()
        self.rename()
        self.assertFalse(Group.objects.filter(name__in=['MSCC_UNICEF', 'MSCC_MEHE']).exists())

    def test_rename_keeps_group_id_members_grants_and_unrelated_memberships(self):
        old = Group.objects.create(name='MSCC_UNICEF')
        old.permissions.add(self.permission)
        base = Group.objects.create(name='MSCC')
        member = self.user('central-member', old, base)
        outsider = self.user('outsider', base)
        before = get_user_model().objects.filter(pk=member.pk).values().get()
        self.rename()
        self.assertFalse(Group.objects.filter(name='MSCC_UNICEF').exists())
        renamed = Group.objects.get(name='MSCC_MEHE')
        self.assertEqual(renamed.pk, old.pk)
        self.assertEqual(set(member.groups.values_list('name', flat=True)), {'MSCC', 'MSCC_MEHE'})
        self.assertEqual(get_user_model().objects.filter(pk=member.pk).values().get(), before)
        self.assertTrue(get_user_model().objects.get(pk=member.pk).has_perm('mscc.view_registration'))
        self.assertFalse(get_user_model().objects.get(pk=outsider.pk).has_perm('mscc.view_registration'))
        self.assertQuerySetEqual(renamed.permissions.all(), [self.permission])

    def test_preexisting_destination_merges_members_and_grants_without_duplicates(self):
        old = Group.objects.create(name='MSCC_UNICEF')
        new = Group.objects.create(name='MSCC_MEHE')
        old.permissions.add(self.permission, self.other_permission)
        new.permissions.add(self.other_permission)
        old_member = self.user('old-member', old)
        new_member = self.user('new-member', new)
        shared = self.user('shared-member', old, new)
        outsider = self.user('outsider')
        self.rename()
        self.rename()
        self.assertEqual(Group.objects.get(name='MSCC_MEHE').pk, new.pk)
        self.assertFalse(Group.objects.filter(pk=old.pk).exists())
        self.assertSetEqual(set(new.user_set.values_list('pk', flat=True)),
                            {old_member.pk, new_member.pk, shared.pk})
        for member in (old_member, new_member, shared):
            self.assertEqual(member.groups.filter(name='MSCC_MEHE').count(), 1)
        self.assertSetEqual(set(new.permissions.values_list('pk', flat=True)),
                            {self.permission.pk, self.other_permission.pk})
        self.assertFalse(outsider.groups.exists())
        self.assertFalse(outsider.has_perm('mscc.view_registration'))

    def test_existing_destination_is_unchanged_without_the_legacy_role(self):
        new = Group.objects.create(name='MSCC_MEHE')
        new.permissions.add(self.permission)
        member = self.user('current-member', new)
        self.rename()
        self.assertEqual(Group.objects.get(name='MSCC_MEHE').pk, new.pk)
        self.assertQuerySetEqual(member.groups.all(), [new])
        self.assertQuerySetEqual(new.permissions.all(), [self.permission])

    def test_empty_legacy_group_is_renamed(self):
        old = Group.objects.create(name='MSCC_UNICEF')
        self.rename()
        self.assertEqual(Group.objects.get(name='MSCC_MEHE').pk, old.pk)

    def test_renaming_twice_keeps_one_group_and_one_membership(self):
        old = Group.objects.create(name='MSCC_UNICEF')
        member = self.user('member', old)
        self.rename()
        self.rename()
        self.assertEqual(Group.objects.filter(name='MSCC_MEHE').count(), 1)
        self.assertEqual(member.groups.count(), 1)

    def test_reverse_retains_members_and_grants(self):
        old = Group.objects.create(name='MSCC_UNICEF')
        old.permissions.add(self.permission)
        member = self.user('member', old)
        self.rename()
        self.migration.backwards(self.apps, self.schema_editor)
        self.assertEqual(Group.objects.get(name='MSCC_UNICEF').pk, old.pk)
        self.assertQuerySetEqual(member.groups.all(), [old])
        self.assertQuerySetEqual(old.permissions.all(), [self.permission])
        self.assertFalse(Group.objects.filter(name='MSCC_MEHE').exists())
