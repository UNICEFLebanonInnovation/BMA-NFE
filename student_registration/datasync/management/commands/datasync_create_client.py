# -*- coding: utf-8 -*-
"""Create (or rotate the token of) the Compiler's service account.

The token this prints is what goes into the Compiler's ``DATASYNC_TARGET_TOKEN``
setting. It is shown once; run the command again with ``--rotate`` to issue a
new one if it is ever lost or leaked.
"""

from __future__ import unicode_literals, absolute_import, division

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand
from rest_framework.authtoken.models import Token

from student_registration.datasync.permissions import sync_client_group


class Command(BaseCommand):
    help = (
        "Create the service account the Compiler uses to push MSCC data, "
        "and print its API token."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            default='compiler-sync',
            help='Username of the service account (default: compiler-sync).',
        )
        parser.add_argument(
            '--rotate',
            action='store_true',
            help='Issue a new token, invalidating the current one.',
        )

    def handle(self, *args, **options):
        """Ensure the account, its group membership and its token exist."""
        username = options['username']
        group_name = sync_client_group()

        user_model = get_user_model()
        user, created = user_model.objects.get_or_create(
            username=username,
            defaults={'is_active': True, 'is_staff': False},
        )
        if created:
            # No password: this account authenticates by token only.
            user.set_unusable_password()
            user.save()
            self.stdout.write(self.style.SUCCESS(
                'Created service account "{}".'.format(username)
            ))
        else:
            self.stdout.write('Service account "{}" already exists.'.format(username))

        group, group_created = Group.objects.get_or_create(name=group_name)
        if group_created:
            self.stdout.write(self.style.SUCCESS('Created group "{}".'.format(group_name)))
        user.groups.add(group)

        if options['rotate']:
            Token.objects.filter(user=user).delete()
            self.stdout.write(self.style.WARNING('Previous token revoked.'))

        token, token_created = Token.objects.get_or_create(user=user)
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(
            'Token: {}'.format(token.key)
        ))
        self.stdout.write(
            'Set this as DATASYNC_TARGET_TOKEN in the Compiler, '
            'together with DATASYNC_TARGET_URL pointing at /api/sync/events/.'
        )
        if not token_created and not options['rotate']:
            self.stdout.write(
                'This is the existing token; re-run with --rotate to replace it.'
            )
