import os
import django
import time

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.test')
django.setup()

from student_registration.attendances.models import CLMAttendance, CLMAttendanceStudent
print([f.name for f in CLMAttendance._meta.get_fields()])
