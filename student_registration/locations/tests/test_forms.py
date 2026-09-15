from django.test import SimpleTestCase

from student_registration.locations.forms import CenterForm


class CenterFormTests(SimpleTestCase):
    def test_nearby_phcc_name_is_optional(self):
        self.assertFalse(CenterForm().fields['neaby_phcc'].required)
