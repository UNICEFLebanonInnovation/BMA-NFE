import os

from django.contrib.auth.models import Group
from django.test import TestCase, override_settings
from django.urls import reverse

from student_registration.dashboard.manual_views import (
    MANUAL_LANGUAGES, MANUAL_MODULES, manual_file_path, manual_markdown_path, manual_module_for,
)
from student_registration.users.models import User


class ManualFilesTests(TestCase):
    """The committed manual files exist for every module, language and format."""

    def test_markdown_sources_exist(self):
        for module in MANUAL_MODULES:
            for language in MANUAL_LANGUAGES:
                with self.subTest(module=module, language=language):
                    self.assertTrue(os.path.isfile(manual_markdown_path(module, language)))

    def test_word_and_pdf_files_exist(self):
        for module in MANUAL_MODULES:
            for language in MANUAL_LANGUAGES:
                for fmt in ('docx', 'pdf'):
                    with self.subTest(module=module, language=language, fmt=fmt):
                        self.assertTrue(os.path.isfile(manual_file_path(module, language, fmt)))


class ManualModuleRuleTests(TestCase):
    def test_alp_school_users_get_the_alp_manual(self):
        user = User.objects.create_user(username='focal-point', password='password')
        user.groups.add(Group.objects.get_or_create(name='ALP_SCHOOL')[0])

        self.assertEqual(manual_module_for(user), 'alp')

    def test_other_users_get_the_nfe_manual(self):
        user = User.objects.create_user(username='center-user', password='password')
        user.groups.add(Group.objects.get_or_create(name='MSCC_CENTER')[0])

        self.assertEqual(manual_module_for(user), 'nfe')


@override_settings(LANGUAGE_CODE='en')
class UserManualViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='center-user', password='password')
        self.alp_user = User.objects.create_user(username='focal-point', password='password')
        self.alp_user.groups.add(Group.objects.get_or_create(name='ALP_SCHOOL')[0])

    def test_anonymous_user_is_redirected_to_login(self):
        response = self.client.get(reverse('dashboard:user_manual'))

        self.assertEqual(response.status_code, 302)

    def test_nfe_user_sees_the_nfe_manual_with_screenshots(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse('dashboard:user_manual'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['module'], 'nfe')
        self.assertContains(response, 'NFE Module')
        self.assertContains(response, reverse('dashboard:user_manual_screenshot', args=['en', '00_login_empty.png']))
        self.assertContains(response, reverse('dashboard:user_manual_download', args=['nfe', 'en', 'pdf']))
        self.assertContains(response, reverse('dashboard:user_manual_download', args=['nfe', 'en', 'docx']))
        self.assertNotContains(response, '../screenshots/')

    def test_alp_user_sees_the_alp_manual_by_default(self):
        self.client.force_login(self.alp_user)

        response = self.client.get(reverse('dashboard:user_manual'))

        self.assertEqual(response.context['module'], 'alp')
        self.assertContains(response, 'ALP Module')

    def test_any_user_can_open_the_other_module_manual(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse('dashboard:user_manual_module', args=['alp']))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['module'], 'alp')

    def test_manual_follows_the_interface_language(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse('dashboard:user_manual'), HTTP_ACCEPT_LANGUAGE='ar')

        self.assertEqual(response.context['language'], 'ar')
        self.assertTrue(response.context['is_rtl'])
        self.assertContains(response, 'dir="rtl"')
        self.assertContains(response, reverse('dashboard:user_manual_screenshot', args=['ar', '00_login_empty.png']))

    def test_sidebar_links_to_the_manual(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse('dashboard:user_manual'))

        self.assertContains(response, 'href="%s"' % reverse('dashboard:user_manual'))


class ManualFileRoutesTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='center-user', password='password')

    def test_screenshot_requires_login(self):
        response = self.client.get(reverse('dashboard:user_manual_screenshot', args=['en', '00_login_empty.png']))

        self.assertEqual(response.status_code, 302)

    def test_screenshot_is_served_to_signed_in_users(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse('dashboard:user_manual_screenshot', args=['en', '00_login_empty.png']))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'image/png')
        self.assertTrue(b''.join(response.streaming_content).startswith(b'\x89PNG'))

    def test_unknown_screenshot_is_a_404(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse('dashboard:user_manual_screenshot', args=['en', 'does-not-exist.png']))

        self.assertEqual(response.status_code, 404)

    def test_path_traversal_is_not_routed(self):
        self.client.force_login(self.user)

        response = self.client.get('/dashboard/manual/screenshot/en/../../wiki/index.md')

        self.assertEqual(response.status_code, 404)

    def test_downloads_are_sent_as_attachments(self):
        self.client.force_login(self.user)

        for fmt, content_type in (('pdf', 'application/pdf'),
                                  ('docx', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')):
            with self.subTest(fmt=fmt):
                response = self.client.get(reverse('dashboard:user_manual_download', args=['alp', 'ar', fmt]))

                self.assertEqual(response.status_code, 200)
                self.assertEqual(response['Content-Type'], content_type)
                self.assertIn('attachment', response['Content-Disposition'])
                self.assertIn('ALP_User_Manual_AR.%s' % fmt, response['Content-Disposition'])
                self.assertGreater(len(b''.join(response.streaming_content)), 100000)

    def test_download_requires_login(self):
        response = self.client.get(reverse('dashboard:user_manual_download', args=['nfe', 'en', 'pdf']))

        self.assertEqual(response.status_code, 302)


@override_settings(LANGUAGE_CODE='en')
class AdminManualAccessTests(TestCase):
    """The admin panel manual is reserved for staff and superusers."""

    def setUp(self):
        self.user = User.objects.create_user(username='center-user', password='password')
        self.staff = User.objects.create_user(username='staff-user', password='password', is_staff=True)

    def test_ordinary_user_does_not_see_the_admin_manual_tab(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse('dashboard:user_manual'))

        self.assertNotContains(response, reverse('dashboard:user_manual_module', args=['admin']))

    def test_ordinary_user_cannot_open_or_download_the_admin_manual(self):
        self.client.force_login(self.user)

        self.assertEqual(self.client.get(reverse('dashboard:user_manual_module', args=['admin'])).status_code, 404)
        download = reverse('dashboard:user_manual_download', args=['admin', 'en', 'pdf'])
        self.assertEqual(self.client.get(download).status_code, 404)

    def test_staff_user_can_read_the_admin_manual(self):
        self.client.force_login(self.staff)

        response = self.client.get(reverse('dashboard:user_manual_module', args=['admin']))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['module'], 'admin')
        self.assertContains(response, 'Admin Panel')
        self.assertContains(response, reverse('dashboard:user_manual_screenshot', args=['en', 'adm_01_dashboard.png']))
        self.assertContains(response, reverse('dashboard:user_manual_module', args=['admin']))

    def test_staff_user_still_lands_on_the_nfe_manual_by_default(self):
        self.client.force_login(self.staff)

        response = self.client.get(reverse('dashboard:user_manual'))

        self.assertEqual(response.context['module'], 'nfe')
