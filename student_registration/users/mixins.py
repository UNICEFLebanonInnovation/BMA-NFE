# -*- coding: utf-8 -*-
"""Access-control mixins for class-based views.

These replace the equivalents from ``django-braces``, whose
``handle_no_permission(request)`` signature is incompatible with Django 5's
``AccessMixin.handle_no_permission(self)``. When a view combined braces'
``GroupRequiredMixin`` with Django's ``LoginRequiredMixin``, Django's version
won the MRO and every permission denial raised ``TypeError`` — so users without
the required group saw a 500 crash page instead of "not allowed".

The mixins below keep the ``group_required`` API used across the project and
behave the way the rest of Django does: anonymous users are redirected to the
login page (keeping the URL they asked for), authenticated users who lack the
permission get a 403 rendered from ``templates/403.html``.
"""
from __future__ import absolute_import, unicode_literals

from django.contrib.auth.mixins import AccessMixin
from django.core.exceptions import ImproperlyConfigured


class GroupRequiredMixin(AccessMixin):
    """Allow access only to members of ``group_required``.

    ``group_required`` may be a single group name or a list/tuple of names;
    membership in any one of them grants access. Superusers always pass.
    """

    group_required = None
    raise_exception = True  # authenticated-but-denied -> 403, not a login loop

    def get_group_required(self):
        if self.group_required is None or not isinstance(self.group_required, (list, tuple, str)):
            raise ImproperlyConfigured(
                '{0} requires the `group_required` attribute to be set to a '
                'string, list or tuple.'.format(self.__class__.__name__)
            )
        if isinstance(self.group_required, str):
            return (self.group_required,)
        return self.group_required

    def check_membership(self, groups):
        """Return True when the current user belongs to any of ``groups``."""
        user = self.request.user
        if user.is_superuser:
            return True
        user_groups = user.groups.values_list('name', flat=True)
        return bool(set(groups) & set(user_groups))

    def dispatch(self, request, *args, **kwargs):
        self.request = request
        if not request.user.is_authenticated:
            # Anonymous: send them to the login page and back here afterwards.
            self.raise_exception = False
            return self.handle_no_permission()
        if not self.check_membership(self.get_group_required()):
            self.raise_exception = True
            return self.handle_no_permission()
        return super(GroupRequiredMixin, self).dispatch(request, *args, **kwargs)


class SuperuserRequiredMixin(AccessMixin):
    """Allow access only to superusers, with the same 403/redirect behaviour."""

    raise_exception = True

    def dispatch(self, request, *args, **kwargs):
        self.request = request
        if not request.user.is_authenticated:
            self.raise_exception = False
            return self.handle_no_permission()
        if not request.user.is_superuser:
            self.raise_exception = True
            return self.handle_no_permission()
        return super(SuperuserRequiredMixin, self).dispatch(request, *args, **kwargs)
