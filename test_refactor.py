import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.test')
django.setup()

from student_registration.mscc.models import EducationProgrammeGrading
print("Django works")
