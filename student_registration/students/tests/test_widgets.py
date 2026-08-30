from django.forms.widgets import ClearableFileInput
from django.test import SimpleTestCase

from student_registration.students.widgets import CustomClearableFileInput


class CustomClearableFileInputTests(SimpleTestCase):
    def test_uses_students_template(self):
        widget = CustomClearableFileInput()

        self.assertIsInstance(widget, ClearableFileInput)
        self.assertEqual(widget.template_name, 'students/clearable_file_input.html')
