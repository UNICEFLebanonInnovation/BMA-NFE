# from django.http import HttpResponse
# from django.template import loader
# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals
from django.http import HttpResponseForbidden, JsonResponse
from django.db.models import OuterRef, Subquery, F
from django.views.generic import ListView, TemplateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
import logging

logger = logging.getLogger(__name__)

from student_registration.mscc.models import (
    PACKAGE_TYPES,
    Round,
    EducationService,
    Registration,
    EducationProgrammeAssessment,
)
from student_registration.schools.models import PartnerOrganization
from student_registration.locations.models import Center, Location


class ChartBuilderView(LoginRequiredMixin, TemplateView):
    """Interactive page for end users to create D3 charts."""

    template_name = 'dashboard/chart_builder.html'

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        context.update(
            {
                "package_types": PACKAGE_TYPES,
                "partners": PartnerOrganization.objects.all(),
                "rounds": Round.objects.all(),
                "centers": Center.objects.all(),
                "governorates": Location.objects.filter(type_id=1),
                "cazas": Location.objects.filter(type_id=2),
                "cadasters": Location.objects.filter(type_id=3),
                "programme_types": EducationService.EDUCATION_PROGRAM,
            }
        )
        return context

class PivotDashboardView(LoginRequiredMixin, TemplateView):
    """Display a PivotTable.js dashboard for MSCC registrations."""

    template_name = 'dashboard/pivot_dashboard.html'


def pivot_data(request):
    """Return minimal MSCC registration data for the pivot table."""
    if not request.user.is_authenticated:
        return HttpResponseForbidden()

    latest_prog_type = (
        EducationProgrammeAssessment.objects.filter(
            registration=OuterRef("pk")
        )
        .order_by("-id")
        .values_list("programme_type", flat=True)[:1]
    )

    qs = (
        Registration.objects.filter(deleted=False)
        .annotate(
            programme_type=Subquery(latest_prog_type),
            center_name=F("center__name"),
            partner_name=F("center__partner__name"),
            round_name=F("round__name"),
            round_year=F("round__year"),
            governorate=F("center__governorate__name"),
            caza=F("center__caza__name"),
            district=F("center__cadaster__name"),
            gender=F("child__gender"),
            nationality=F("child__nationality__name"),
            package_type=F("type"),
        )
    )

    data = [
        {
            "center": getattr(row, "center_name", "") or "",
            "partner": getattr(row, "partner_name", "") or "",
            "governorate": getattr(row, "governorate", "") or "",
            "caza": getattr(row, "caza", "") or "",
            "district": getattr(row, "district", "") or "",
            "gender": getattr(row, "gender", "") or "",
            "nationality": getattr(row, "nationality", "") or "",
            "package_type": getattr(row, "package_type", "") or "",
            "round": getattr(row, "round_name", "") or "",
            "round_year": getattr(row, "round_year", "") or "",
            "programme_type": getattr(row, "programme_type", "") or "",
        }
        for row in qs
    ]

    return JsonResponse(data, safe=False)

