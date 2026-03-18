

from functools import wraps
from django.shortcuts import render
from django.http import HttpResponseForbidden
from student_registration.users.templatetags.custom_tags import has_group


def mscc_access_required(view_func):
    """
    Decorator to ensure MSCC roles are correctly configured with a Center or Partner.
    Redirects to an error page with a message to contact the admin if configuration is missing.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            return view_func(request, *args, **kwargs)

        if user.is_superuser or user.is_staff:
            return view_func(request, *args, **kwargs)

        # Role-based configuration checks
        if has_group(user, 'MSCC_CENTER'):
            if not user.center or not user.partner:
                return render(request, 'error.html', {'missing_info': 'center'}, status=403)

        if has_group(user, 'MSCC_PARTNER'):
            if not user.partner:
                return render(request, 'error.html', {'missing_info': 'partner'}, status=403)

        return view_func(request, *args, **kwargs)
    return _wrapped_view


class MSCCAccessMixin(object):
    """
    Mixin to ensure MSCC roles are correctly configured with a Center or Partner.
    Redirects to an error page with a message to contact the admin if configuration is missing.
    """

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            return super(MSCCAccessMixin, self).dispatch(request, *args, **kwargs)

        if user.is_superuser or user.is_staff:
            return super(MSCCAccessMixin, self).dispatch(request, *args, **kwargs)

        # Role-based configuration checks
        if has_group(user, 'MSCC_CENTER'):
            if not user.center or not user.partner:
                return render(request, 'error.html', {'missing_info': 'center'}, status=403)

        if has_group(user, 'MSCC_PARTNER'):
            if not user.partner:
                return render(request, 'error.html', {'missing_info': 'partner'}, status=403)

        return super(MSCCAccessMixin, self).dispatch(request, *args, **kwargs)


def get_default_export_formats():
    from import_export.admin import base_formats
    """
    Return available export formats.
    """
    return (
        base_formats.XLS,
        base_formats.XLSX,
        base_formats.JSON
    )
