from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse

from student_registration.users.models import User


class WikiAccessTests(TestCase):
    """Technical documentation is superuser-only on both documentation routes.

    The Markdown route (/dashboard/wiki/) and the HTML guide route
    (/dashboard/guide/) serve mirrored content, so a restriction applied to
    one and not the other leaks the administrator and developer guides.
    """

    RESTRICTED_PAGES = ['admin', 'developer', 'system_details']

    def setUp(self):
        # The sidebar's "Documentation" block only renders for MSCC users, so both
        # accounts need the group for the sidebar assertions to be meaningful.
        mscc_group = Group.objects.create(name='MSCC')
        self.standard_user = User.objects.create_user(
            username='field-officer', password='password'
        )
        self.standard_user.groups.add(mscc_group)
        self.superuser = User.objects.create_superuser(
            username='ministry-admin', password='password', email='admin@example.com'
        )
        self.superuser.groups.add(mscc_group)

    def test_standard_user_cannot_read_technical_wiki_pages(self):
        self.client.force_login(self.standard_user)

        for page in self.RESTRICTED_PAGES:
            with self.subTest(page=page):
                response = self.client.get(reverse('dashboard:wiki_page', args=[page]))

                self.assertEqual(response.status_code, 404)

    def test_standard_user_cannot_read_technical_guide_pages(self):
        self.client.force_login(self.standard_user)

        for page in self.RESTRICTED_PAGES:
            with self.subTest(page=page):
                response = self.client.get(reverse('dashboard:wiki_guide', args=[page]))

                self.assertEqual(response.status_code, 404)

    def test_standard_user_can_read_end_user_manual_on_both_routes(self):
        self.client.force_login(self.standard_user)

        self.assertEqual(
            self.client.get(reverse('dashboard:wiki_page', args=['end_user'])).status_code, 200
        )
        self.assertEqual(
            self.client.get(reverse('dashboard:wiki_guide', args=['end_user'])).status_code, 200
        )

    def test_standard_user_can_read_wiki_index(self):
        self.client.force_login(self.standard_user)

        response = self.client.get(reverse('dashboard:wiki_index'))

        self.assertEqual(response.status_code, 200)

    def test_superuser_can_read_technical_pages_on_both_routes(self):
        self.client.force_login(self.superuser)

        for page in self.RESTRICTED_PAGES:
            with self.subTest(page=page):
                self.assertEqual(
                    self.client.get(reverse('dashboard:wiki_page', args=[page])).status_code, 200
                )
                self.assertEqual(
                    self.client.get(reverse('dashboard:wiki_guide', args=[page])).status_code, 200
                )

    def test_anonymous_user_is_redirected_to_login(self):
        response = self.client.get(reverse('dashboard:wiki_page', args=['end_user']))

        self.assertEqual(response.status_code, 302)

    def test_path_traversal_attempt_is_rejected(self):
        self.client.force_login(self.superuser)

        response = self.client.get('/dashboard/wiki/..%2F..%2Fsettings/')

        self.assertIn(response.status_code, (301, 404))

    def test_technical_wiki_link_hidden_from_standard_user_sidebar(self):
        self.client.force_login(self.standard_user)

        response = self.client.get(reverse('dashboard:wiki_guide', args=['end_user']))

        # The sidebar's documentation block is rendered ...
        self.assertContains(
            response, 'href="{}"'.format(reverse('dashboard:wiki_guide', args=['end_user']))
        )
        # ... but the technical wiki entry is not part of it.
        self.assertNotContains(response, 'href="{}"'.format(reverse('dashboard:wiki_index')))

    def test_technical_wiki_link_shown_to_superuser_sidebar(self):
        self.client.force_login(self.superuser)

        response = self.client.get(reverse('dashboard:wiki_guide', args=['end_user']))

        self.assertContains(response, 'href="{}"'.format(reverse('dashboard:wiki_index')))
