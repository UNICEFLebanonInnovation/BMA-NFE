__author__ = 'achamseddine'

from django.core.management.base import BaseCommand

from student_registration.users.tasks import generate_passwords


class Command(BaseCommand):
    help = 'Generate Users password'

    def add_arguments(self, parser):
        parser.add_argument('group', nargs='+', type=str)

    def handle(self, *args, **options):
        for group in options['group']:
            generate_passwords(group)
