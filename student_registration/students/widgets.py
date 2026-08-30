"""Reusable form widgets for the students application."""

from django.forms.widgets import ClearableFileInput


class CustomClearableFileInput(ClearableFileInput):
    """Render file inputs with the project's current-file display template."""

    template_name = 'students/clearable_file_input.html'
