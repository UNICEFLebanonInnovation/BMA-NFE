# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, HttpResponse, JsonResponse
from django.shortcuts import render
from django.utils import timezone


from .models import ExportHistory


def _format_created(value):
    """Format an export timestamp whether or not USE_TZ is enabled.

    ``timezone.localtime()`` raises on naive datetimes, and this project runs
    with ``USE_TZ = False``, so convert only when the value is aware.
    """
    if value is None:
        return ''
    if timezone.is_aware(value):
        value = timezone.localtime(value)
    return value.strftime('%Y-%m-%d %H:%M')


@login_required
def export_history_list(request):
    """
    Return export history entries for the authenticated user.

    Parameters
    ----------
    request : HttpRequest
        Incoming request containing the authenticated user context.

    Returns
    -------
    JsonResponse
        A JSON payload with an ``exports`` list, each item containing ``url`` and
        ``text`` keys describing the export entry.
    """

    exports = ExportHistory.objects.filter(created_by=request.user).order_by('-created')
    data = []
    for export in exports:
        timestamp = _format_created(export.created)
        label = export.export_type or 'Export'
        data.append({'url': export.file_url or '#', 'text': f'{label} {timestamp}'})
    return JsonResponse({'exports': data})


@login_required
def export_history_page(request):
    """Render the user's export history as a page.

    The notification dropdown only shows the most recent entries; this is the
    destination for its "View all history" link.
    """
    exports = ExportHistory.objects.filter(created_by=request.user).order_by('-created')[:200]
    return render(request, 'backends/export_history.html', {'exports': exports})
