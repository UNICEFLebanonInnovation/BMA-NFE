"""Read and management permissions for MSCC exceptional-exam applications."""

from student_registration.users.templatetags.custom_tags import has_group

from .export_access import scoped_registrations, user_can_export
from .models import Registration


def _active(user):
    return bool(user and user.is_authenticated and user.is_active)


def exceptional_exam_registrations(user):
    """Restrict examination applications to the user's assigned child scope."""
    if user_can_export(user):
        return scoped_registrations(user).exclude(child_id=None)
    if _active(user) and has_group(user, 'MSCC') and user.center_id:
        return Registration.objects.filter(
            deleted=False, center_id=user.center_id,
        ).exclude(child_id=None).select_related(
            'child', 'child__governorate', 'child__district', 'center', 'partner', 'round',
        )
    return Registration.objects.none()


def can_manage_exceptional_exam(user, registration):
    """Allow administrators and centre editors to maintain their applications."""
    if not _active(user) or registration.deleted or not registration.child_id:
        return False
    if user.is_staff or user.is_superuser:
        return True
    if not user.center_id or registration.center_id != user.center_id:
        return False
    if has_group(user, 'MSCC_CENTER'):
        return True
    # The base MSCC role also maintains services for its assigned centre.
    # Adding the base role to an analytical/partner account does not make it
    # an editor: those accounts need an explicit centre-editing role.
    return bool(
        has_group(user, 'MSCC')
        and not has_group(user, 'MSCC_UNICEF')
        and not has_group(user, 'MSCC_PARTNER')
    )
