import os
import django
import time

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.test")
django.setup()

from student_registration.mscc.utils import create_attendance
from student_registration.attendances.models import MSCCAttendance, MSCCAttendanceChild
from student_registration.locations.models import Center
from student_registration.child.models import Child
from student_registration.mscc.models import Registration

# Create center, children, registrations
MSCCAttendanceChild.objects.all().delete()
MSCCAttendance.objects.all().delete()
Registration.objects.all().delete()
Child.objects.all().delete()
Center.objects.all().delete()
center = Center.objects.create(name="Test Center")
children_data = []
for i in range(100):
    child = Child.objects.create(first_name=f"Child {i}", last_name="Test")
    reg = Registration.objects.create(child=child, center=center)
    children_data.append({
        'child_id': child.id,
        'registration_id': reg.id,
        'attended': 'Yes',
        'absence_reason': '',
        'absence_reason_other': ''
    })

data = {
    "round_id": 1,
    "education_program": "Program A",
    "class_section": "Section A",
    "attendance_date": "01/01/2023",
    "attendance_day_off": "no",
    "close_reason": "",
    "children_attendance": children_data
}

# Run once to measure create
start = time.time()
create_attendance(data, center.id)
create_time = time.time() - start

# Run again to measure update
start = time.time()
create_attendance(data, center.id)
update_time = time.time() - start

print(f"Create Time: {create_time:.4f}s")
print(f"Update Time: {update_time:.4f}s")
