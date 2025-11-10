__author__ = 'achamseddine'

from django.core.management.base import BaseCommand

from student_registration.users.tasks import copy_user_email_to_ticket


class Command(BaseCommand):
    help = 'Copy user email to ticket'

    def handle(self, *args, **options):
        copy_user_email_to_ticket()
