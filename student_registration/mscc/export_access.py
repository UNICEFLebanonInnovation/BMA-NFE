"""Shared access and filtering rules for MSCC registration documents."""

from django.core.exceptions import ValidationError
from django.db.models import Q

from student_registration.child.models import Child
from student_registration.users.templatetags.custom_tags import has_group

from .models import Registration


def user_can_export(user):
    """Whether a user has an export role and its required assignment."""
    if not user or not user.is_authenticated or not user.is_active:
        return False
    return bool(
        user.is_staff
        or user.is_superuser
        or has_group(user, 'MSCC_UNICEF')
        or (has_group(user, 'MSCC_PARTNER') and user.partner_id)
        or (has_group(user, 'MSCC_CENTER') and user.center_id)
    )


def scoped_registrations(user):
    """Return all nondeleted registrations within the user's MSCC scope.

    Exports include every authorised round and are independent of list-page
    pagination. All forward relationships used by the document snapshot are
    loaded together with the registration and child.
    """
    related = [
        field.name for field in Registration._meta.fields
        if field.many_to_one
    ]
    related.extend(
        'child__' + field.name for field in Child._meta.fields
        if field.many_to_one
    )
    queryset = Registration.objects.filter(deleted=False).select_related(
        *related
    ).order_by('pk')
    if not user_can_export(user):
        return queryset.none()
    if user.is_staff or user.is_superuser or has_group(user, 'MSCC_UNICEF'):
        return queryset
    if has_group(user, 'MSCC_PARTNER') and user.partner_id:
        return queryset.filter(partner_id=user.partner_id)
    if has_group(user, 'MSCC_CENTER') and user.center_id:
        return queryset.filter(center_id=user.center_id)
    return queryset.none()


def _integer_filter(value, name):
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        raise ValidationError('Invalid %s filter.' % name)
    if parsed <= 0:
        raise ValidationError('Invalid %s filter.' % name)
    return parsed


def filter_registrations(queryset, filters=None):
    """Apply the supported list filters without widening an access scope."""
    filters = filters or {}
    if filters.get('export_scope') == 'all':
        return queryset
    if filters.get('export_scope') == 'filtered':
        queryset = queryset.filter(Q(round__isnull=True) | Q(round__current_year=True))

    for name in (
        'child__first_name', 'child__last_name', 'child__father_name',
        'child__mother_fullname', 'child__unicef_id',
    ):
        value = filters.get(name)
        if value:
            queryset = queryset.filter(**{name + '__icontains': value})

    for name in ('child__gender', 'nfe_programme'):
        value = filters.get(name)
        if value:
            queryset = queryset.filter(**{name: value})

    for name in ('child__nationality', 'partner', 'center'):
        value = filters.get(name)
        if value and str(value).lower() != 'all':
            queryset = queryset.filter(**{name + '_id': _integer_filter(value, name)})

    round_id = filters.get('round')
    if round_id == 'no_round':
        queryset = queryset.filter(round__isnull=True)
    elif round_id and str(round_id).lower() != 'all':
        queryset = queryset.filter(round_id=_integer_filter(round_id, 'round'))

    programme_type = filters.get('programme_type')
    if programme_type:
        queryset = queryset.filter(
            education_service__education_program=programme_type
        ).distinct()
    return queryset
