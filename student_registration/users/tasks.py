__author__ = 'achamseddine'

from student_registration.taskapp.celery import app


@app.task
def generate_passwords(group):
    from student_registration.users.models import User

    users = User.objects.filter(is_staff=False, is_superuser=False, groups__name=group)
    for user in users:
        try:
            password = user.username
            if user.phone_number:
                password = password+user.phone_number[:2]
            # if user.email:
            #     password = password+user.email[:2]
            user.update_password(password)
            user.save()
        except Exception as ex:
            pass


@app.task
def assign_groups_to_2nd_shift_schools():
    from student_registration.users.models import User

    users = User.objects.filter(first_name='school')
    for user in users:
        try:
            for group in (1, 4, 8):
                user.groups.add(group)
                user.save()
        except Exception as ex:
            pass


@app.task
def assign_groups_to_2nd_shift_directors():
    from student_registration.users.models import User

    users = User.objects.filter(first_name='director')
    for user in users:
        try:
            for group in (1, 4, 9):
                user.groups.add(group)
                user.save()
        except Exception as ex:
            pass


@app.task
def assign_groups_to_alp_schools():
    from student_registration.users.models import User

    users = User.objects.filter(first_name='alpschl')
    for user in users:
        try:
            for group in (1, 4, 5, 13):
                user.groups.add(group)
                user.save()
        except Exception as ex:
            pass


@app.task
def assign_groups_to_alp_directors():
    from student_registration.users.models import User

    users = User.objects.filter(first_name='alpdirect')
    for user in users:
        try:
            for group in (1, 4, 5, 13, 14):
                user.groups.add(group)
                user.save()
        except Exception as ex:
            pass


@app.task
def generate_tokens(group):
    from rest_framework.authtoken.models import Token
    from student_registration.users.models import User

    users = User.objects.filter(is_staff=False, is_superuser=False, groups__name=group)
    for user in users:
        try:
            try:
                token = Token.objects.get(user_id=user.id)
            except Token.DoesNotExist:
                token = Token.objects.create(user_id=user.id)
        except Exception as ex:
            pass


@app.task
def copy_school_email():
    from student_registration.schools.models import School

    queryset = School.objects.all()

    for school in queryset:
        if not school.email or not school.user_set.all():
            continue
        users = school.user_set.filter(groups__id__exact=8)
        for user in users:
            user.email = school.email
            user.save()
        # school.user_set.update(email=school.email)


@app.task
def copy_user_email_to_ticket():
    from .models import User
    from helpdesk.models import Ticket

    queryset = User.objects.filter(school__isnull=False)
    for line in queryset:
        if not line.school.email:
            continue
        Ticket.objects.filter(submitter_email=line.email).update(submitter_email=line.school.email)
