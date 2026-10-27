"""Retiring MSCC_FULL must preserve role scopes and existing edit access."""
from importlib import import_module
from types import SimpleNamespace

from django.apps import apps
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.db import connection
from django.test import RequestFactory, TestCase
from django.urls import reverse

from student_registration.child.models import Child
from student_registration.locations.models import Center
from student_registration.schools.models import PartnerOrganization
from student_registration.students.models import IDType
from student_registration.mscc.models import Registration, Round
from student_registration.mscc.tables import FullTable, MainTable, PartnerTable, YouthMainTable
from student_registration.mscc.views import MainListView


class MsccRoleAccessTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.groups = {name: Group.objects.create(name=name) for name in
                      ('MSCC', 'MSCC_CENTER', 'MSCC_PARTNER', 'MSCC_UNICEF', 'MSCC_FULL')}
        cls.partner_a = PartnerOrganization.objects.create(name='Role QA partner A')
        cls.partner_b = PartnerOrganization.objects.create(name='Role QA partner B')
        cls.center_a = Center.objects.create(name='Role QA centre A', partner=cls.partner_a)
        cls.center_b = Center.objects.create(name='Role QA centre B', partner=cls.partner_a)
        cls.center_c = Center.objects.create(name='Role QA centre C', partner=cls.partner_b)
        cls.current = Round.objects.create(name='Role QA current', current_year=True)
        cls.old = Round.objects.create(name='Role QA past', current_year=False)
        id_type = IDType.objects.create(name='Role QA ID')
        child = Child.objects.create(first_name='Role QA', last_name='Child', father_name='Parent', id_type=id_type,
                                     birthday_year='2015', birthday_month='1', birthday_day='1')
        cls.registration = Registration.objects.create(child=child, center=cls.center_a,
            partner=cls.partner_a, round=cls.current)
        cls.other_center = Registration.objects.create(child=child, center=cls.center_b,
            partner=cls.partner_a, round=cls.current)
        cls.other_partner = Registration.objects.create(child=child, center=cls.center_c,
            partner=cls.partner_b, round=cls.current)
        Registration.objects.create(child=child, center=cls.center_a, partner=cls.partner_a, round=cls.old)
        Registration.objects.create(child=child, center=cls.center_a, partner=cls.partner_a,
                                    round=cls.current, deleted=True)

    def user(self, name, roles=(), **assignments):
        user = get_user_model().objects.create(username=name, **assignments)
        user.groups.add(*(self.groups[role] for role in roles))
        return user

    def view(self, user):
        request = RequestFactory().get(reverse('mscc:list'))
        request.user = user
        view = MainListView()
        view.setup(request)
        return view

    def test_centre_user_without_full_stays_in_the_assigned_centre(self):
        user = self.user('centre', ('MSCC','MSCC_CENTER'), center=self.center_a, partner=self.partner_a)
        view = self.view(user)
        self.assertQuerySetEqual(view.get_queryset(), [self.registration], ordered=False)
        self.assertIs(view.get_table_class(), MainTable)

    def test_partner_user_without_full_stays_in_the_assigned_partner(self):
        user = self.user('partner', ('MSCC','MSCC_PARTNER'), partner=self.partner_a)
        view = self.view(user)
        self.assertQuerySetEqual(view.get_queryset(), [self.registration,self.other_center], ordered=False)
        self.assertIs(view.get_table_class(), PartnerTable)

    def test_unicef_user_without_full_sees_current_records_across_partners(self):
        user = self.user('unicef', ('MSCC','MSCC_UNICEF'))
        view = self.view(user)
        self.assertQuerySetEqual(view.get_queryset(),
                                [self.registration,self.other_center,self.other_partner], ordered=False)
        self.assertIs(view.get_table_class(), FullTable)

    def test_module_membership_or_legacy_group_does_not_grant_a_data_scope(self):
        for name,roles in [('base',('MSCC',)), ('legacy',('MSCC','MSCC_FULL'))]:
            with self.subTest(roles=roles):
                view = self.view(self.user(name,roles))
                self.assertFalse(view.get_queryset().exists())
                self.assertIs(view.get_table_class(), YouthMainTable)

    def test_unassigned_centre_and_partner_users_do_not_see_other_records(self):
        for role in ('MSCC_CENTER','MSCC_PARTNER'):
            with self.subTest(role=role):
                self.assertFalse(self.view(self.user(role,('MSCC',role))).get_queryset().exists())

    def test_superuser_access_does_not_require_the_retired_group(self):
        user = self.user('super',is_superuser=True,is_staff=True)
        self.assertEqual(self.view(user).get_queryset().count(),3)
        self.assertIs(self.view(user).get_table_class(),FullTable)

    def test_centre_registration_button_no_longer_requires_full(self):
        user = self.user('entry',('MSCC','MSCC_CENTER'),center=self.center_a,partner=self.partner_a)
        self.client.force_login(user)
        response = self.client.get(reverse('mscc:list'))
        self.assertContains(response,'data-bs-target="#child-registration-modal"')

    def test_registration_button_still_requires_centre_role_and_assignments(self):
        cases = [('missing-center',('MSCC','MSCC_CENTER'),{'partner':self.partner_a}),
                 ('missing-partner',('MSCC','MSCC_CENTER'),{'center':self.center_a}),
                 ('partner-viewer',('MSCC','MSCC_PARTNER'),{'partner':self.partner_a})]
        for name,roles,assignments in cases:
            with self.subTest(name=name):
                self.client.force_login(self.user(name,roles,**assignments))
                response = self.client.get(reverse('mscc:list'))
                self.assertEqual(response.status_code,200)
                self.assertNotContains(response,'data-bs-target="#child-registration-modal"')

    def test_existing_new_round_roles_can_see_and_open_the_action_without_full(self):
        for role in ('MSCC','MSCC_CENTER'):
            with self.subTest(role=role):
                user = self.user('round-'+role,(role,),center=self.center_a,partner=self.partner_a)
                self.client.force_login(user)
                profile = self.client.get(reverse('mscc:child_profile',kwargs={'pk':self.registration.pk}))
                self.assertContains(profile,'data-bs-target="#newRoundModal"')
                self.assertContains(profile,'id="new-round-confirm"')
                form = self.client.get(reverse('mscc:new_round',kwargs={'pk':self.registration.pk}))
                self.assertEqual(form.status_code,200)

    def test_viewer_groups_alone_do_not_enable_new_round(self):
        for role in ('MSCC_PARTNER','MSCC_UNICEF','MSCC_FULL'):
            with self.subTest(role=role):
                user = self.user('viewer-'+role,(role,),partner=self.partner_a)
                self.client.force_login(user)
                profile = self.client.get(reverse('mscc:child_profile',kwargs={'pk':self.registration.pk}))
                self.assertEqual(profile.status_code,200)
                self.assertNotContains(profile,'data-bs-target="#newRoundModal"')
                self.assertNotContains(profile,'id="new-round-confirm"')
                form = self.client.get(reverse('mscc:new_round',kwargs={'pk':self.registration.pk}))
                self.assertEqual(form.status_code,403)

    def test_anonymous_new_round_request_redirects_to_login(self):
        response = self.client.get(reverse('mscc:new_round',kwargs={'pk':self.registration.pk}))
        self.assertEqual(response.status_code,302)
        self.assertIn('next=',response.url)

    def test_missing_module_or_legacy_only_membership_cannot_open_the_list(self):
        for name,roles in [('no-roles',()),('legacy-only',('MSCC_FULL',))]:
            with self.subTest(roles=roles):
                self.client.force_login(self.user(name,roles))
                self.assertEqual(self.client.get(reverse('mscc:list')).status_code,403)

    def test_anonymous_list_request_redirects_to_login(self):
        response = self.client.get(reverse('mscc:list'))
        self.assertEqual(response.status_code,302)
        self.assertIn('next=',response.url)


class RetireMsccFullMigrationTests(TestCase):
    def retire(self):
        migration = import_module('student_registration.users.migrations.0002_remove_mscc_full_group')
        migration.remove_mscc_full_group(apps,SimpleNamespace(connection=connection))

    def test_absent_group_is_safe_and_idempotent(self):
        other = Group.objects.create(name='MSCC_CENTER')
        self.retire()
        self.retire()
        self.assertTrue(Group.objects.filter(pk=other.pk).exists())

    def test_removal_preserves_users_assignments_and_other_roles(self):
        legacy = Group.objects.create(name='MSCC_FULL')
        center_role = Group.objects.create(name='MSCC_CENTER')
        partner = PartnerOrganization.objects.create(name='Role migration partner')
        center = Center.objects.create(name='Role migration centre',partner=partner)
        user = get_user_model().objects.create(username='legacy-member',center=center,partner=partner)
        user.groups.add(legacy,center_role)
        self.retire()
        self.assertFalse(Group.objects.filter(name='MSCC_FULL').exists())
        user.refresh_from_db()
        self.assertEqual((user.center_id,user.partner_id),(center.pk,partner.pk))
        self.assertEqual(list(user.groups.values_list('name',flat=True)),['MSCC_CENTER'])

    def test_existing_model_permissions_are_preserved_only_for_existing_members(self):
        legacy = Group.objects.create(name='MSCC_FULL')
        permission = Permission.objects.get(content_type__app_label='mscc',codename='view_registration')
        legacy.permissions.add(permission)
        member = get_user_model().objects.create(username='member')
        member.groups.add(legacy)
        already_direct = get_user_model().objects.create(username='direct')
        already_direct.groups.add(legacy)
        already_direct.user_permissions.add(permission)
        outsider = get_user_model().objects.create(username='outsider')
        other_group = Group.objects.create(name='MSCC')
        outsider.groups.add(other_group)
        self.assertTrue(member.has_perm('mscc.view_registration'))
        self.retire()
        self.retire()
        for user in (member,already_direct):
            reloaded = get_user_model().objects.get(pk=user.pk)
            self.assertTrue(reloaded.has_perm('mscc.view_registration'))
            self.assertEqual(reloaded.user_permissions.filter(pk=permission.pk).count(),1)
            self.assertFalse(reloaded.groups.exists())
        self.assertFalse(get_user_model().objects.get(pk=outsider.pk).has_perm('mscc.view_registration'))
        self.assertFalse(other_group.permissions.exists())

    def test_legacy_only_member_is_not_assigned_a_broader_replacement_role(self):
        legacy = Group.objects.create(name='MSCC_FULL')
        user = get_user_model().objects.create(username='legacy-only')
        user.groups.add(legacy)
        self.retire()
        self.assertTrue(get_user_model().objects.filter(pk=user.pk).exists())
        self.assertFalse(user.groups.exists())
        self.assertFalse(user.user_permissions.exists())
