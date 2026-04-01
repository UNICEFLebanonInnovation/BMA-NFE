import os
import django
import time
import sys
import django.db

# Setting django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.test')
django.setup()

from student_registration.mscc.utils import update_child_attendance
from student_registration.attendances.models import MSCCAttendance, MSCCAttendanceChild
from student_registration.mscc.models import Registration
from student_registration.students.models import Student
from student_registration.locations.models import Center
from student_registration.child.models import Child

def setup_data():
    from django.db import connection

    # clean up first
    with connection.cursor() as cursor:
        cursor.execute("TRUNCATE TABLE attendances_msccattendancechild CASCADE;")
        cursor.execute("TRUNCATE TABLE attendances_msccattendance CASCADE;")
        cursor.execute("TRUNCATE TABLE mscc_registration CASCADE;")
        cursor.execute("TRUNCATE TABLE child_child CASCADE;")
        cursor.execute("TRUNCATE TABLE locations_center CASCADE;")


    # create some dummy data
    center = Center.objects.create(name="Test Center")

    # Create child and registration
    child = Child.objects.create(first_name="Test", last_name="Child")
    registration = Registration.objects.create(child=child, center=center)

    # Create old and new class sections
    old_class = "A"
    new_class = "B"
    program = "BLN Level 1"

    import datetime

    # Create N attendances
    for i in range(100):
        d = datetime.date(2023, 1, 1) + datetime.timedelta(days=i)

        # Old attendance
        old_att = MSCCAttendance.objects.create(
            center=center,
            attendance_date=d,
            education_program=program,
            class_section=old_class
        )

        MSCCAttendanceChild.objects.create(
            attendance_day=old_att,
            registration=registration,
            child=child
        )

        # New attendance
        if i % 2 == 0:
            MSCCAttendance.objects.create(
                center=center,
                attendance_date=d,
                education_program=program,
                class_section=new_class
            )

    return registration.id, program, old_class, new_class

def run_benchmark():
    reg_id, program, old_class, new_class = setup_data()

    from django.db import connection, reset_queries
    from django.conf import settings

    settings.DEBUG = True
    reset_queries()

    import time
    start = time.time()
    update_child_attendance(reg_id, program, old_class, new_class)
    end = time.time()

    print(f"Time taken: {end - start:.4f} seconds")
    print(f"Queries made: {len(connection.queries)}")

if __name__ == '__main__':
    run_benchmark()
