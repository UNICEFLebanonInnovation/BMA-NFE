import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
django.setup()

from student_registration.mscc.models import Registration

r = Registration.objects.filter(education_service__isnull=False).first()
if r:
    from django.urls import reverse
    print(reverse('mscc:child_profile', args=[r.id]))
