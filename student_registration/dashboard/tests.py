from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from student_registration.locations.models import Center, Location, LocationType
from student_registration.schools.models import PartnerOrganization

User = get_user_model()

class CentersMapTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_superuser(username='testadmin', password='password123', email='test@example.com')
        self.client.login(username='testadmin', password='password123')

        self.partner = PartnerOrganization.objects.create(name="Test Partner")
        self.gov_type = LocationType.objects.create(name="Governorate")
        self.caza_type = LocationType.objects.create(name="Caza")
        self.cad_type = LocationType.objects.create(name="Cadaster")

        self.gov = Location.objects.create(name="Test Gov", type=self.gov_type)
        self.caza = Location.objects.create(name="Test Caza", type=self.caza_type, parent=self.gov)
        self.cad = Location.objects.create(name="Test Cad", type=self.cad_type, parent=self.caza)

        self.center = Center.objects.create(
            name="Test Center",
            partner=self.partner,
            governorate=self.gov,
            caza=self.caza,
            cadaster=self.cad,
            latitude=33.8,
            longitude=35.5,
            is_active=True
        )

    def test_centers_map_view(self):
        response = self.client.get(reverse('dashboard:centers_map'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/centers_map.html')

    def test_centers_geo_data_api(self):
        from student_registration.mscc.models import Teacher
        Teacher.objects.create(first_name="Test", last_name="Teacher", center=self.center)

        response = self.client.get(reverse('dashboard:centers_geo_data'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['name'], "Test Center")
        self.assertEqual(data[0]['latitude'], 33.8)
        self.assertEqual(data[0]['total_teachers'], 1)
        self.assertEqual(data[0]['total_teachers_male'], 0)
        self.assertEqual(data[0]['total_teachers_female'], 0)
        self.assertEqual(data[0]['total_children'], 0)

    def test_centers_geo_data_filter(self):
        other_partner = PartnerOrganization.objects.create(name="Other Partner")
        response = self.client.get(reverse('dashboard:centers_geo_data') + f'?partner_id={other_partner.id}')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 0)

    def test_centers_children_data_api(self):
        response = self.client.get(reverse('dashboard:centers_children_data'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('data', data)
        self.assertIn('pagination', data)
