import json
from django.test import TestCase, Client
from django.urls import reverse
from student_registration.users.models import User

class SecurityCSRFTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        # Use a client with enforce_csrf=True to properly test CSRF protection
        self.csrf_client = Client(enforce_csrf=True)
        self.csrf_client.login(username='testuser', password='password123')
        self.url = reverse('save_fcm_token')

    def test_save_fcm_token_csrf_required(self):
        """
        Verify that save_fcm_token requires a CSRF token.
        Since we removed @csrf_exempt, a POST request without the CSRF token
        should now return a 403 Forbidden.
        """
        payload = {'token': 'test_token'}
        response = self.csrf_client.post(
            self.url,
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 403)
