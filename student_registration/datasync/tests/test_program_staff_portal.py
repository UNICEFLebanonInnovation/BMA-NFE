"""The existing NFE teacher portal must handle Compiler ProgramStaff."""
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.messages.storage.fallback import FallbackStorage
from django.test import RequestFactory, TestCase

from student_registration.locations.models import Center
from student_registration.mscc.filters import TeacherFilter
from student_registration.mscc.forms import TeacherForm
from student_registration.mscc.models import Teacher
from student_registration.schools.models import PartnerOrganization


class ProgramStaffPortalTests(TestCase):
    def setUp(self):
        self.center = Center.objects.create(name='Portal centre')
        self.staff = Teacher.objects.create(bma_id='44', bma_source='locations.program_staff',
            center=self.center, facilitator_name='Facilitator ' + 'م' * 180,
            unicef_id='NFE-reference',
            program_staff_details={'programs': ['BLN'], 'subject': ['Education']})
        self.user = get_user_model().objects.create_user(username='portal-editor', is_staff=True)

    def test_imported_full_name_is_visible_and_split_names_are_optional(self):
        form = TeacherForm(instance=self.staff)
        self.assertTrue(form.fields['facilitator_name'].disabled)
        self.assertEqual(form.fields['facilitator_name'].initial, self.staff.facilitator_name)
        for field in ('first_name', 'father_name', 'last_name', 'mother_fullname',
                      'round', 'subjects_provided', 'registration_level', 'trainings', 'extra_coaching'):
            self.assertFalse(form.fields[field].required)

    def test_regular_teacher_keeps_the_existing_required_name_fields(self):
        form = TeacherForm()
        self.assertNotIn('facilitator_name', form.fields)
        for field in ('first_name', 'father_name', 'last_name', 'mother_fullname'):
            self.assertTrue(form.fields[field].required)

    def test_search_matches_the_synced_facilitator_name(self):
        Teacher.objects.create(center=self.center, facilitator_name='Different person')
        result = TeacherFilter({'facilitator_name__icontains': 'facilitator'}, queryset=Teacher.objects.all())
        self.assertEqual(list(result.qs), [self.staff])

    def test_contact_save_preserves_identity_name_and_programme_details(self):
        values = {'center': self.center.pk, 'sex': 'Female', 'primary_phone_number': '70-123456',
            'facilitator_name': 'Forged name', 'bma_id': 'forged-id', 'bma_source': 'mscc.teacher'}
        request = RequestFactory().post('/mscc/teacher-edit/', values)
        request.user = self.user
        request.session = {}
        request._messages = FallbackStorage(request)
        form = TeacherForm(values, instance=self.staff, request=request)
        self.assertTrue(form.is_valid(), form.errors)
        form.save(request, instance=self.staff)
        self.staff.refresh_from_db()
        self.assertEqual(self.staff.primary_phone_number, '70-123456')
        self.assertEqual(self.staff.bma_id, '44')
        self.assertEqual(self.staff.bma_source, 'locations.program_staff')
        self.assertEqual(self.staff.unicef_id, 'NFE-reference')
        self.assertTrue(self.staff.facilitator_name.startswith('Facilitator '))
        self.assertEqual(self.staff.program_staff_details['programs'], ['BLN'])


class TeacherPortalScopeTests(TestCase):
    def setUp(self):
        self.partner = PartnerOrganization.objects.create(name='Portal partner A')
        self.other_partner = PartnerOrganization.objects.create(name='Portal partner B')
        self.center = Center.objects.create(name='A', partner=self.partner)
        self.sibling = Center.objects.create(name='A2', partner=self.partner)
        self.foreign = Center.objects.create(name='B', partner=self.other_partner)
        self.teacher = Teacher.objects.create(center=self.center, bma_id='44',
            bma_source='locations.program_staff', facilitator_name='Scoped teacher')
        self.foreign_teacher = Teacher.objects.create(center=self.foreign, facilitator_name='Foreign teacher')

    def user(self, role, **assignments):
        user = get_user_model().objects.create_user(username=role, **assignments)
        user.groups.add(Group.objects.get_or_create(name=role)[0])
        self.client.force_login(user)
        return user

    def test_centre_user_cannot_open_or_delete_a_foreign_teacher(self):
        self.user('MSCC_CENTER', center=self.center, partner=self.partner)
        self.assertEqual(self.client.get(f'/mscc/teacher-edit/{self.teacher.pk}/').status_code, 200)
        for action in ('teacher-edit', 'teacher-delete'):
            self.assertEqual(self.client.get(f'/mscc/{action}/{self.foreign_teacher.pk}/').status_code, 404)
        self.assertTrue(Teacher.objects.filter(pk=self.foreign_teacher.pk).exists())

    def test_partner_user_cannot_open_a_foreign_partner_teacher(self):
        user = self.user('MSCC_PARTNER', partner=self.partner)
        self.assertEqual(self.client.get(f'/mscc/teacher-edit/{self.foreign_teacher.pk}/').status_code, 404)
        request = RequestFactory().get('/')
        request.user = user
        form = TeacherForm(instance=self.teacher, request=request)
        self.assertEqual(set(form.fields['center'].queryset.values_list('pk', flat=True)), {self.center.pk, self.sibling.pk})

    def test_unassigned_centre_user_gets_no_teachers_or_centre_options(self):
        user = self.user('MSCC_CENTER')
        self.assertEqual(self.client.get(f'/mscc/teacher-edit/{self.teacher.pk}/').status_code, 404)
        request = RequestFactory().get('/')
        request.user = user
        form = TeacherForm(request=request)
        self.assertFalse(form.fields['center'].queryset.exists())

    def test_form_rejects_a_forged_centre_outside_the_assigned_partner(self):
        user = self.user('MSCC_PARTNER', partner=self.partner)
        request = RequestFactory().post('/', {'center': self.foreign.pk, 'primary_phone_number': '70-123456'})
        request.user = user
        form = TeacherForm(request.POST, instance=self.teacher, request=request)
        self.assertFalse(form.is_valid())
        self.assertIn('center', form.errors)
        self.assertEqual(set(form.fields['center'].queryset.values_list('pk', flat=True)), {self.center.pk, self.sibling.pk})

    def test_mehe_user_retains_central_access(self):
        self.user('MSCC_MEHE')
        self.assertEqual(self.client.get(f'/mscc/teacher-edit/{self.foreign_teacher.pk}/').status_code, 200)

    def test_authenticated_account_without_role_gets_403_instead_of_server_error(self):
        user = get_user_model().objects.create_user(username='no-role')
        self.client.force_login(user)
        for url in ('/mscc/teacher-list/', '/mscc/teacher-add/',
                    f'/mscc/teacher-edit/{self.teacher.pk}/', f'/mscc/teacher-delete/{self.teacher.pk}/'):
            self.assertEqual(self.client.get(url).status_code, 403, url)
        self.assertTrue(Teacher.objects.filter(pk=self.teacher.pk).exists())

    def test_unauthenticated_account_is_redirected_to_login(self):
        self.assertEqual(self.client.get(f'/mscc/teacher-edit/{self.teacher.pk}/').status_code, 302)
