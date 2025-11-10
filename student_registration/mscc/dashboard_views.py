# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.views.generic import ListView, TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest, HttpResponseForbidden

from .models import Registration


def children_per_nationality(request):

    return JsonResponse([])
