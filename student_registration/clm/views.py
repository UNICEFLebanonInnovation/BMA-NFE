# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.views.generic import ListView, FormView, TemplateView, UpdateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
import logging


logging.basicConfig(level=logging.ERROR)


class DashboardView(LoginRequiredMixin,
                    TemplateView):
    template_name = 'clm/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Use default PowerBI link for admins
        default_dashboard_url = 'https://app.powerbi.com/view?r=eyJrIjoiOTExNDAyZjUtN2NhNS00MTBiLWE2MWMtMzVmMDBiYTE4NTQ1IiwidCI6Ijc3NDEwMTk1LTE0ZTEtNGZiOC05MDRiLWFiMTg5MjAyMzY2NyIsImMiOjh9'

        if user.is_superuser or user.is_staff:
            context['dashboard_url'] = default_dashboard_url
        elif user.partner_id and user.partner and user.partner.dashboard_url:
            context['dashboard_url'] = user.partner.dashboard_url
        else:
            context['dashboard_url'] = None

        return context
