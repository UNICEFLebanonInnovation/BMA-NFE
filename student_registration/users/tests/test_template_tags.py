from types import SimpleNamespace

from django.test import SimpleTestCase

from student_registration.users.templatetags.custom_tags import active_route


class ActiveRouteTests(SimpleTestCase):
    @staticmethod
    def request(namespace, url_name):
        return SimpleNamespace(
            resolver_match=SimpleNamespace(
                app_name=namespace,
                url_name=url_name,
            )
        )

    def test_exact_route_match_is_active(self):
        request = self.request("alp", "school_profile")

        self.assertEqual(active_route(request, "alp", "school_profile"), "active")

    def test_partial_route_match_is_not_active(self):
        request = self.request("alp", "dashboard_school")

        self.assertEqual(active_route(request, "alp", "school_profile"), "")

    def test_matching_name_in_another_namespace_is_not_active(self):
        request = self.request("alp", "pivot_dashboard")

        self.assertEqual(active_route(request, "dashboard", "pivot_dashboard"), "")

    def test_missing_resolver_match_is_not_active(self):
        self.assertEqual(active_route(SimpleNamespace(), "alp", "school_profile"), "")
