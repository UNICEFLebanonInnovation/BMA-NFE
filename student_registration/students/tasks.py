__author__ = 'achamseddine'

from django.db.models import Q
from student_registration.taskapp.celery import app
from student_registration.students.utils import generate_id


@app.task
def generate_2ndshift_unique_number(offset=0):
    from student_registration.enrollments.models import Enrollment
    limit = offset + 50000
    registrations = Enrollment.objects.all()[offset:limit]
    for registry in registrations:
        student = registry.student
        try:
            student.number = generate_id(student.first_name, student.father_name, student.last_name,
                                         student.mother_fullname, student.sex,
                                         student.birthday_day, student.birthday_month, student.birthday_year)

            student.number_part1 = generate_id(student.first_name, student.father_name, student.last_name,
                                               student.mother_fullname, student.sex,
                                               '', '', '')

            student.number_part2 = generate_id(student.first_name, student.father_name, student.last_name,
                                               '', '',
                                               student.birthday_day, student.birthday_month, student.birthday_year)
            student.save()
        except Exception as ex:
            continue


@app.task
def generate_alp_unique_number():
    from student_registration.alp.models import Outreach

    registrations = Outreach.objects.all()
    for registry in registrations:
        student = registry.student
        try:
            student.number = generate_id(student.first_name, student.father_name, student.last_name,
                                         student.mother_fullname, student.sex,
                                         student.birthday_day, student.birthday_month, student.birthday_year)

            student.number_part1 = generate_id(student.first_name, student.father_name, student.last_name,
                                               student.mother_fullname, student.sex,
                                               '', '', '')

            student.number_part2 = generate_id(student.first_name, student.father_name, student.last_name,
                                               '', '',
                                               student.birthday_day, student.birthday_month, student.birthday_year)
            student.save()
        except Exception as ex:
            continue


@app.task
def disable_duplicate_enrolments(offset=None, school_number=None):
    from student_registration.enrollments.models import Enrollment
    registrations = []
    queryset = Enrollment.objects.all()
    if offset:
        limit = offset + 50000
        registrations = queryset.order_by('-id', 'student__number', 'school__number')[offset:limit]
    elif school_number:
        registrations = queryset.filter(school__number=school_number).order_by('-id', 'student__number', 'school__number')

    students = {}
    students2 = {}
    duplicates = []

    for registry in registrations:
        student = registry.student
        if student.number not in students:
            students[student.number] = registry
        else:
            duplicates.append(registry)

        if student.number_part1:
            if student.number_part1 not in students2:
                students2[student.number_part1] = registry
            else:
                duplicates.append(registry)



    for registry in duplicates:
        registry.deleted = True
        registry.save()



@app.task
def disable_duplicate_outreaches(school_number=None):
    from student_registration.alp.models import Outreach, ALPRound
    alp_round = ALPRound.objects.get(current_round=True)
    registrations = Outreach.objects.filter(alp_round=alp_round).order_by('-id')
    if school_number:
        registrations = registrations.filter(school__number=school_number)

    students = {}
    students2 = {}
    duplicates = []

    for registry in registrations:

        student = registry.student
        if student.number not in students:
            students[student.number] = registry
        else:
            duplicates.append(registry)

        if student.number_part1 not in students2:
            students2[student.number_part1] = registry
        else:
            duplicates.append(registry)


    for registry in duplicates:
        registry.deleted = True
        registry.save()



@app.task
def cleanup_registry_duplications(registry_type='alp'):
    from student_registration.alp.models import Outreach
    from student_registration.enrollments.models import Enrollment

    model = Outreach if registry_type == 'alp' else Enrollment

    registrations = model.objects.filter(deleted=True)
    registrations.delete()


@app.task
def cleanup_duplications():
    from .models import Student

    registrations = Student.objects.filter(
        student_enrollment__isnull=True,
        alp_enrollment__isnull=True,
    )
    registrations.delete()


@app.task
def move_data_from_registry_to_students(registry_type='alp'):
    from student_registration.alp.models import Outreach
    from student_registration.enrollments.models import Enrollment

    model = Outreach if registry_type == 'alp' else Enrollment
    registrations = model.objects.all()

    for registry in registrations:
        student = registry.student
        student.registered_in_unhcr = registry.registered_in_unhcr
        student.save()
