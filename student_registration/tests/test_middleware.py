from types import SimpleNamespace

from django.http import HttpResponse
from django.test import RequestFactory, SimpleTestCase, override_settings

from student_registration.middleware import AutoLogout


class AutoLogoutTests(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = AutoLogout(lambda request: HttpResponse())

    def _authenticated_request(self, path):
        request = self.factory.get(path)
        request.user = SimpleNamespace(is_authenticated=True)
        request.session = {}
        return request

    @override_settings(AUTO_LOGOUT_DELAY=30, AUTO_LOGOUT_EXEMPT_PATHS=("/__debug__/",))
    def test_exempt_path_does_not_modify_session(self):
        request = self._authenticated_request("/__debug__/history_sidebar/")

        response = self.middleware(request)

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("last_touch", request.session)

    @override_settings(AUTO_LOGOUT_DELAY=30, AUTO_LOGOUT_EXEMPT_PATHS=("/__debug__/",))
    def test_regular_path_still_updates_last_activity(self):
        request = self._authenticated_request("/dashboard/")

        self.middleware(request)

        self.assertIn("last_touch", request.session)
