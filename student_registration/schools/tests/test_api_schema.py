"""Keep the school API and the generated API documentation usable."""

from django.contrib.auth import get_user_model
from django.urls import reverse
from drf_spectacular.validation import validate_schema
from rest_framework.test import APITestCase

from student_registration.schools.models import School


class SchoolAPISchemaTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(username='school-api-reader')
        cls.school = School.objects.create(number='API-SCHOOL-001', name='API School')

    def setUp(self):
        self.client.force_authenticate(user=self.user)

    def test_school_list_returns_the_registered_school(self):
        response = self.client.get(reverse('schools-list'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        school = response.data[0]
        self.assertEqual(school['id'], self.school.pk)
        self.assertEqual(school['number'], 'API-SCHOOL-001')
        self.assertEqual(school['name'], 'API School')

    def test_schema_endpoint_returns_valid_openapi_with_school_operations(self):
        response = self.client.get(
            reverse('schema'), HTTP_ACCEPT='application/vnd.oai.openapi+json',
        )

        self.assertEqual(response.status_code, 200)
        schema = response.json()
        validate_schema(schema)
        self.assertIn('get', schema['paths'][reverse('schools-list')])
        properties = schema['components']['schemas']['School']['properties']
        self.assertIn('id', properties)
        self.assertIn('number', properties)
        self.assertIn('name', properties)
