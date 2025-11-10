__author__ = 'achamseddine'

from django.core.management.base import BaseCommand

from student_registration.users.tasks import copy_school_email


class Command(BaseCommand):
    help = 'Copy school email to user'

    def handle(self, *args, **options):
        copy_school_email()
