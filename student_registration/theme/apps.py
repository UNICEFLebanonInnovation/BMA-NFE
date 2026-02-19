from django.apps import AppConfig
from tailwind.apps import TailwindAppConfig


class ThemeConfig(TailwindAppConfig):
    name = "student_registration.theme"
    verbose_name = "Student Registration Tailwind Theme"
    label = "student_registration_theme"
