from django.test import TestCase
from django.urls import reverse

from student_registration.dashboard.views import WIKI_HTML_PAGES, wiki_page_is_visible_to
from student_registration.users.models import User


TECHNICAL_PAGES = [page for page, _label, _section in WIKI_HTML_PAGES if page != 'end_user']

#: Technical pages that also exist as Markdown under ``docs/wiki/``. The
#: numbered developer guides are HTML only, so the Markdown route has nothing
#: to serve for them either way.
TECHNICAL_MARKDOWN_PAGES = ['index', 'admin', 'developer', 'system_details']


class DocumentationAccessRuleTests(TestCase):
    """The rule itself: user guidelines for all, technical docs for superusers."""

    def test_end_user_manual_is_visible_to_everyone(self):
        user = User(username='field-worker', is_superuser=False)

        self.assertTrue(wiki_page_is_visible_to(user, 'end_user'))

    def test_technical_pages_are_hidden_from_ordinary_users(self):
        user = User(username='field-worker', is_superuser=False)

        for page in TECHNICAL_PAGES:
            with self.subTest(page=page):
                self.assertFalse(wiki_page_is_visible_to(user, page))

    def test_superuser_sees_every_page(self):
        user = User(username='root', is_superuser=True)

        for page, _label, _section in WIKI_HTML_PAGES:
            with self.subTest(page=page):
                self.assertTrue(wiki_page_is_visible_to(user, page))


class GuideRouteAccessTests(TestCase):
    """``/dashboard/guide/<page>/`` serves docs/wiki_html/."""

    def setUp(self):
        self.user = User.objects.create_user(username='field-worker', password='password')
        self.superuser = User.objects.create_superuser(
            username='root', password='password', email='root@example.com'
        )

    def test_anonymous_user_is_redirected_to_login(self):
        response = self.client.get(reverse('dashboard:wiki_guide', args=['end_user']))

        self.assertEqual(response.status_code, 302)

    def test_ordinary_user_can_read_the_user_guide(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse('dashboard:wiki_guide', args=['end_user']))

        self.assertEqual(response.status_code, 200)

    def test_ordinary_user_cannot_read_technical_guides(self):
        self.client.force_login(self.user)

        for page in TECHNICAL_PAGES:
            with self.subTest(page=page):
                response = self.client.get(reverse('dashboard:wiki_guide', args=[page]))
                self.assertEqual(response.status_code, 404)

    def test_superuser_can_read_technical_guides(self):
        self.client.force_login(self.superuser)

        for page in TECHNICAL_PAGES:
            with self.subTest(page=page):
                response = self.client.get(reverse('dashboard:wiki_guide', args=[page]))
                self.assertEqual(response.status_code, 200)


class WikiRouteAccessTests(TestCase):
    """``/dashboard/wiki/<page>/`` serves the same content from docs/wiki/."""

    def setUp(self):
        self.user = User.objects.create_user(username='field-worker', password='password')
        self.superuser = User.objects.create_superuser(
            username='root', password='password', email='root@example.com'
        )

    def test_anonymous_user_is_redirected_to_login(self):
        response = self.client.get(reverse('dashboard:wiki_page', args=['end_user']))

        self.assertEqual(response.status_code, 302)

    def test_ordinary_user_can_read_the_user_guide(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse('dashboard:wiki_page', args=['end_user']))

        self.assertEqual(response.status_code, 200)

    def test_ordinary_user_cannot_read_technical_markdown_pages(self):
        self.client.force_login(self.user)

        for page in TECHNICAL_MARKDOWN_PAGES:
            with self.subTest(page=page):
                response = self.client.get(reverse('dashboard:wiki_page', args=[page]))
                self.assertEqual(response.status_code, 404)

    def test_ordinary_user_cannot_reach_the_wiki_index(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse('dashboard:wiki_index'))

        self.assertEqual(response.status_code, 404)

    def test_superuser_can_read_technical_markdown_pages(self):
        self.client.force_login(self.superuser)

        for page in TECHNICAL_MARKDOWN_PAGES:
            with self.subTest(page=page):
                response = self.client.get(reverse('dashboard:wiki_page', args=[page]))
                self.assertEqual(response.status_code, 200)

    def test_page_name_with_path_traversal_is_rejected(self):
        self.client.force_login(self.superuser)

        response = self.client.get('/dashboard/wiki/..%2Fdeployment/')

        self.assertIn(response.status_code, (404, 400))
