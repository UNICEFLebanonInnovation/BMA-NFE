# -*- coding: utf-8 -*-
"""Role → capability mapping shared by the login profile and the push engine.

The rules mirror ``group_required`` on the web views (see
``docs/ACCESS_CONTROL.md``); the app hides what a user cannot do and the
server re-checks every write.
"""
from __future__ import unicode_literals

from django.utils import timezone

from student_registration.users.templatetags.custom_tags import has_group

MSCC_GROUPS = ('MSCC', 'MSCC_CENTER', 'MSCC_PARTNER', 'MSCC_UNICEF', 'MSCC_FULL')
CLM_GROUPS = ('CLM_Bridging', 'CLM_BRIDGING_ALL', 'CLM_ATTENDANCE', 'CLM_TEACHER')


def any_group(user, groups):
    return any(has_group(user, g) for g in groups)


def is_mscc_unicef(user):
    return has_group(user, 'MSCC_UNICEF') or user.is_staff


def mscc_can_register(user):
    if has_group(user, 'MSCC'):
        return True
    return has_group(user, 'MSCC_CENTER') and bool(user.partner_id)


def mscc_can_edit(user):
    return has_group(user, 'MSCC') or has_group(user, 'MSCC_CENTER')


def mscc_can_attend(user):
    return any_group(user, ('MSCC', 'MSCC_UNICEF', 'MSCC_CENTER', 'MSCC_PARTNER'))


def mscc_can_manage_teachers(user):
    return any_group(user, ('MSCC', 'MSCC_CENTER', 'MSCC_PARTNER', 'MSCC_UNICEF'))


def alp_enabled(user):
    return has_group(user, 'ALP_SCHOOL')


def alp_can_write(user):
    # ALPEditPermissionMixin: superusers are read-only; school users manage data.
    return alp_enabled(user) and not user.is_superuser and bool(user.school_id)


def clm_enabled(user):
    return any_group(user, CLM_GROUPS)


def clm_can_register(user):
    return has_group(user, 'CLM_Bridging')


def clm_can_attend(user):
    return has_group(user, 'CLM_ATTENDANCE') or has_group(user, 'CLM_Bridging')


def clm_can_manage_teachers(user):
    return has_group(user, 'CLM_TEACHER') or has_group(user, 'CLM_BRIDGING_ALL')


def module_capabilities(user):
    return {
        'mscc': {
            'enabled': any_group(user, MSCC_GROUPS),
            'can_register': mscc_can_register(user),
            'can_edit': mscc_can_edit(user),
            'can_attend': mscc_can_attend(user),
            'can_manage_teachers': mscc_can_manage_teachers(user),
            'scope': 'all' if is_mscc_unicef(user)
            else 'partner' if has_group(user, 'MSCC_PARTNER') and user.partner_id
            else 'center' if user.center_id else 'none',
        },
        'alp': {
            'enabled': alp_enabled(user),
            'can_register': alp_can_write(user),
            'can_edit': alp_can_write(user),
            'can_attend': alp_can_write(user),
            'can_manage_teachers': alp_can_write(user),
            'scope': 'school' if user.school_id else 'none',
        },
        'clm': {
            'enabled': clm_enabled(user),
            'can_register': clm_can_register(user),
            'can_edit': clm_can_register(user),
            'can_attend': clm_can_attend(user),
            'can_manage_teachers': clm_can_manage_teachers(user),
            'scope': 'all' if has_group(user, 'CLM_BRIDGING_ALL') or user.is_staff
            else 'school' if user.school_id else 'partner' if user.partner_id else 'none',
        },
    }


def _ref(obj, extra=()):
    if obj is None:
        return None
    data = {'id': obj.pk, 'name': str(obj)}
    for attr in extra:
        data[attr] = getattr(obj, attr, None)
    return data


def user_profile(user):
    """Profile block returned by login and ``/me/``."""
    partner = user.partner
    center = user.center
    school = user.school
    return {
        'id': user.pk,
        'username': user.username,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'email': user.email,
        'is_staff': user.is_staff,
        'is_superuser': user.is_superuser,
        'groups': sorted(user.groups.values_list('name', flat=True)),
        'partner': _ref(partner, ('short_name',)),
        'center': _ref(center, ('partner_id',)),
        'school': _ref(school, ('number',)),
        'schools': [_ref(s, ('number',)) for s in user.schools.all()],
        'modules': module_capabilities(user),
        'server_time': timezone.now().isoformat(),
    }
