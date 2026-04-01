from django.test import SimpleTestCase

from student_registration.locations.utils import to_array

class DummyObject:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

class ToArrayTests(SimpleTestCase):
    def test_to_array_happy_path(self):
        obj = DummyObject(name="Test", age=30, active=True)
        result = to_array(["name", "age"], obj)
        self.assertEqual(result, {"name": "Test", "age": 30})

    def test_to_array_missing_fields(self):
        obj = DummyObject(name="Test")
        result = to_array(["name", "missing"], obj)
        self.assertEqual(result, {"name": "Test"})

    def test_to_array_empty_fields(self):
        obj = DummyObject(name="Test")
        result = to_array([], obj)
        self.assertEqual(result, {})

    def test_to_array_no_attributes(self):
        obj = object()
        result = to_array(["name", "age"], obj)
        self.assertEqual(result, {})

    def test_to_array_none_object(self):
        result = to_array(["name"], None)
        self.assertEqual(result, {})
