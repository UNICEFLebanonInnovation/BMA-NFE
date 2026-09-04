# -*- coding: utf-8 -*-
"""Template context shared by every page."""
from __future__ import absolute_import, unicode_literals

from django.conf import settings


def site_settings(request):
    """Expose deployment-level display settings to templates.

    ``GOOGLE_ANALYTICS_ID`` is empty unless a deployment explicitly opts in,
    so the analytics tag is not shipped with a child-protection system by
    default.
    """
    return {
        'GOOGLE_ANALYTICS_ID': getattr(settings, 'GOOGLE_ANALYTICS_ID', ''),
        'APP_VERSION': getattr(settings, 'APP_VERSION', ''),
    }
