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

        return {}
