# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, HttpResponse, JsonResponse
from django.utils.timezone import localtime


from .models import ExportHistory


@login_required
def export_history_list(request):
    """
    Return the five most recent exports for the authenticated user.

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

    exports = (
        ExportHistory.objects.filter(created_by=request.user)
        .order_by('-created')[:5]
    )
    data = []
    for export in exports:
        timestamp = localtime(export.created).strftime('%Y-%m-%d %H:%M')
        data.append({'url': export.file_url or '#', 'text': f'MSCC export {timestamp}'})
    return JsonResponse({'exports': data})

