from django.test import TestCase
from student_registration.dashboard.exporter_utils import get_model_fields
from student_registration.locations.models import LocationType, Location

class GetModelFieldsTests(TestCase):
    def test_basic_field_types(self):
        """Test with a simple model (LocationType) to verify basic field identification."""
        fields = get_model_fields(LocationType)
        # LocationType has CharField 'name' and 'name_en'.
        # id and id_en are usually internal but CharField.
        # Let's check for 'name' specifically.
        field_ids = [f['id'] for f in fields]
        self.assertIn('name', field_ids)
        self.assertIn('name_en', field_ids)

        name_field = next(f for f in fields if f['id'] == 'name')
        self.assertEqual(name_field['label'], 'Name')
        self.assertEqual(name_field['type'], 'CharField')

    def test_foreign_key_recursion(self):
        """Test with a model having a ForeignKey (Location) to verify 1-level recursion."""
        fields = get_model_fields(Location)
        field_ids = [f['id'] for f in fields]

        # Location has name, name_en, type (FK), latitude (Float), longitude (Float), p_code, parent (TreeFK)
        # get_model_fields filters for CharField, IntegerField, DateField, DateTimeField, BooleanField
        # FloatField is EXCLUDED.

        self.assertIn('name', field_ids)
        self.assertIn('p_code', field_ids)
        self.assertNotIn('latitude', field_ids) # FloatField should be excluded

        # Recursion into 'type' (LocationType)
        self.assertIn('type__name', field_ids)
        self.assertIn('type__name_en', field_ids)

        type_name_field = next(f for f in fields if f['id'] == 'type__name')
        self.assertEqual(type_name_field['label'], 'Type Name')
        self.assertEqual(type_name_field['type'], 'CharField')

        # Recursion into 'parent' (Location) - it's 1 level deep, so it should NOT recurse again from parent
        self.assertIn('parent__name', field_ids)
        # Should NOT have parent__parent__name
        self.assertNotIn('parent__parent__name', field_ids)
