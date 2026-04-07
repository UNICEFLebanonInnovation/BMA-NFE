# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.views.generic import ListView, TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.db.models import Count, Q
from django.db.models.functions import ExtractYear

from .models import Registration, Teacher
from student_registration.students.models import Training


def children_per_nationality(request):

    return JsonResponse([])

class TeacherDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'mscc/teacher_dashboard.html'

    def get_context_data(self, **kwargs):
        from student_registration.locations.models import Center, Location
        from student_registration.clm.models import PartnerOrganization
        from .models import Round

        user = self.request.user
        centers = Center.objects.all()
        governorates = Location.objects.filter(type_id=1)
        partners = PartnerOrganization.objects.all()
        rounds = Round.objects.all()

        if not (user.is_superuser or user.is_staff):
            if user.partner_id:
                centers = centers.filter(partner_id=user.partner_id)
                partners = partners.filter(id=user.partner_id)
            if user.center_id:
                centers = centers.filter(id=user.center_id)

        return {
            'centers': centers,
            'governorates': governorates,
            'partners': partners,
            'rounds': rounds,
        }


class TeacherDashboardDataView(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user
        qs = Teacher.objects.all()

        if not (user.is_superuser or user.is_staff):
            if user.partner_id:
                qs = qs.filter(center__partner_id=user.partner_id)
            if user.center_id:
                qs = qs.filter(center_id=user.center_id)

        # Apply Filters
        centers = request.GET.getlist('centers')
        if centers:
            qs = qs.filter(center_id__in=centers)
        rounds = request.GET.getlist('rounds')
        if rounds:
            qs = qs.filter(round_id__in=rounds)
        governorates = request.GET.getlist('governorates')
        if governorates:
            qs = qs.filter(center__governorate_id__in=governorates)
        partners = request.GET.getlist('partners')
        if partners:
            qs = qs.filter(center__partner_id__in=partners)

        # Basic indicators
        total_teachers = qs.count()

        # Gender
        gender_data = list(qs.values('sex').annotate(count=Count('id')).order_by('sex'))
        gender_formatted = [{'name': item['sex'] if item['sex'] else 'Unknown', 'value': item['count']} for item in gender_data]

        # Nationality
        nationality_data = list(qs.values('nationality__name').annotate(count=Count('id')).order_by('nationality__name'))
        nationality_formatted = [{'name': item['nationality__name'] if item['nationality__name'] else 'Unknown', 'value': item['count']} for item in nationality_data]

        # By Center
        center_data = list(qs.values('center__name').annotate(count=Count('id')).order_by('center__name'))
        center_formatted = [{'name': item['center__name'] if item['center__name'] else 'Unknown', 'value': item['count']} for item in center_data]

        # Per academic year (round)
        round_data = list(qs.values('round__name').annotate(count=Count('id')).order_by('round__name'))
        round_formatted = [{'name': item['round__name'] if item['round__name'] else 'Unknown', 'value': item['count']} for item in round_data]

        # Teacher assignment
        assignment_data = list(qs.values('teacher_assignment').annotate(count=Count('id')).order_by('teacher_assignment'))
        assignment_formatted = [{'name': item['teacher_assignment'] if item['teacher_assignment'] else 'Unknown', 'value': item['count']} for item in assignment_data]

        # Subjects provided (ArrayField, we might need a workaround for counting)
        # Using a simple python side counter since ArrayField aggregation is complex in some DBs
        subjects_counter = {}
        for teacher in qs.filter(subjects_provided__isnull=False):
            if teacher.subjects_provided:
                for subject in teacher.subjects_provided:
                    if subject:
                        subjects_counter[subject] = subjects_counter.get(subject, 0) + 1
        subjects_formatted = [{'name': k, 'value': v} for k, v in sorted(subjects_counter.items(), key=lambda item: item[1], reverse=True)]

        # Training (ManyToMany)
        training_data = list(qs.values('trainings__name').annotate(count=Count('id')).order_by('trainings__name'))
        training_formatted = [{'name': item['trainings__name'] if item['trainings__name'] else 'None', 'value': item['count']} for item in training_data]

        # Training frequency
        frequency_data = list(qs.values('training_sessions_attended').annotate(count=Count('id')).order_by('training_sessions_attended'))
        frequency_formatted = [{'name': str(item['training_sessions_attended']) if item['training_sessions_attended'] is not None else 'Unknown', 'value': item['count']} for item in frequency_data]

        # Training date of completion
        completion_date_data = list(qs.filter(training_date_of_completion__isnull=False).annotate(year=ExtractYear('training_date_of_completion')).values('year').annotate(count=Count('id')).order_by('year'))
        completion_date_formatted = [{'name': str(item['year']) if item['year'] else 'Unknown', 'value': item['count']} for item in completion_date_data]

        return JsonResponse({
            'total_teachers': total_teachers,
            'gender': gender_formatted,
            'nationality': nationality_formatted,
            'center': center_formatted,
            'round': round_formatted,
            'assignment': assignment_formatted,
            'subjects': subjects_formatted,
            'trainings': training_formatted,
            'training_frequency': frequency_formatted,
            'training_completion_year': completion_date_formatted,
        })
