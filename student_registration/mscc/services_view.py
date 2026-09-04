# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from django.shortcuts import get_object_or_404

import json

from django.views.generic import ListView, FormView, TemplateView, UpdateView, View
from django.contrib.auth.mixins import LoginRequiredMixin

from student_registration.users.mixins import GroupRequiredMixin, SuperuserRequiredMixin
from django.urls import reverse

from .utils import *
from .services_form import *
from .models import *


class InclusionFormView(LoginRequiredMixin,
                        GroupRequiredMixin,
                        FormView):
    template_name = 'mscc/service_inclusion_form.html'
    form_class = InclusionServiceForm
    success_url = ''
    group_required = [u"MSCC", u"MSCC_CENTER"]

    def get_success_url(self):
        return reverse('mscc:child_profile', kwargs={'pk': self.kwargs['registry']}) + '?current_tab=services'

    def get_context_data(self, **kwargs):
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        kwargs['registry'] = self.kwargs['registry']
        return super(InclusionFormView, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        registry = self.kwargs['registry']
        instance = self.kwargs['pk'] if 'pk' in self.kwargs else None
        data = {}
        if self.request.method == "POST":
            return InclusionServiceForm(self.request.POST, instance=instance, registry=registry, request=self.request)
        else:
            if instance:
                data = to_array(InclusionServiceForm.Meta.fields, get_object_or_404(InclusionService, pk=instance))
                return InclusionServiceForm(data, registry=registry, instance=instance, request=self.request)
            return InclusionServiceForm(registry=registry, instance=instance, request=self.request)

    def form_valid(self, form):
        registry = self.kwargs['registry']
        instance = self.kwargs['pk'] if 'pk' in self.kwargs else None
        form.save(request=self.request, registry=registry, instance=instance)
        return super(InclusionFormView, self).form_valid(form)


class DigitalFormView(LoginRequiredMixin,
                      GroupRequiredMixin,
                      FormView):
    template_name = 'mscc/service_digital_form.html'
    form_class = DigitalServiceForm
    success_url = ''
    group_required = [u"MSCC", u"MSCC_CENTER"]

    def get_success_url(self):
        return reverse('mscc:child_profile', kwargs={'pk': self.kwargs['registry']}) + '?current_tab=services'

    def get_context_data(self, **kwargs):
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        kwargs['registry'] = self.kwargs['registry']
        return super(DigitalFormView, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        registry = self.kwargs['registry']
        instance = self.kwargs['pk'] if 'pk' in self.kwargs else None
        data = {}
        if self.request.method == "POST":
            return DigitalServiceForm(self.request.POST, instance=instance, registry=registry, request=self.request)
        else:
            if instance:
                data = to_array(DigitalServiceForm.Meta.fields, get_object_or_404(DigitalService, pk=instance))
                return DigitalServiceForm(data, registry=registry, instance=instance, request=self.request)
            return DigitalServiceForm(registry=registry, instance=instance, request=self.request)

    def form_valid(self, form):
        registry = self.kwargs['registry']
        instance = self.kwargs['pk'] if 'pk' in self.kwargs else None
        form.save(request=self.request, registry=registry, instance=instance)
        return super(DigitalFormView, self).form_valid(form)


class HealthNutritionFormView(LoginRequiredMixin,
                      GroupRequiredMixin,
                      FormView):
    template_name = 'mscc/service_health_nutrition_form.html'
    form_class = HealthNutritionServiceForm
    success_url = ''
    group_required = [u"MSCC", u"MSCC_CENTER"]

    def get_success_url(self):
        return reverse('mscc:child_profile', kwargs={'pk': self.kwargs['registry']}) + '?current_tab=services'

    def get_context_data(self, **kwargs):
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        kwargs['registry'] = self.kwargs['registry']
        return super(HealthNutritionFormView, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        registry = self.kwargs['registry']
        age = self.kwargs['age']
        instance = self.kwargs['pk'] if 'pk' in self.kwargs else None
        data = {}
        if self.request.method == "POST":
            return HealthNutritionServiceForm(self.request.POST, instance=instance, registry=registry, age=age, request=self.request)
        else:
            if instance:
                data = to_array(HealthNutritionServiceForm.Meta.fields, get_object_or_404(HealthNutritionService, pk=instance))
                return HealthNutritionServiceForm(data, registry=registry, age=age, instance=instance, request=self.request)
            return HealthNutritionServiceForm(registry=registry, age=age, instance=instance, request=self.request)

    def form_valid(self, form):
        registry = self.kwargs['registry']
        instance = self.kwargs['pk'] if 'pk' in self.kwargs else None
        form.save(request=self.request, registry=registry, instance=instance)
        return super(HealthNutritionFormView, self).form_valid(form)


class HealthNutritionReferralFormView(LoginRequiredMixin,
                      GroupRequiredMixin,
                      FormView):
    template_name = 'mscc/service_health_nutrition_referral_form.html'
    form_class = HealthNutritionReferralForm
    success_url = ''
    group_required = [u"MSCC", u"MSCC_CENTER"]

    def get_success_url(self):
        return reverse('mscc:child_profile', kwargs={'pk': self.kwargs['registry']})

    def get_context_data(self, **kwargs):
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        kwargs['registry'] = self.kwargs['registry']
        return super(HealthNutritionReferralFormView, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        registry = self.kwargs['registry']
        instance = self.kwargs['pk'] if 'pk' in self.kwargs else None
        data = {}
        if self.request.method == "POST":
            return HealthNutritionReferralForm(self.request.POST, instance=instance, registry=registry, request=self.request)
        else:
            if instance:
                data = to_array(HealthNutritionReferralForm.Meta.fields, get_object_or_404(HealthNutritionReferral, pk=instance))
                return HealthNutritionReferralForm(data, registry=registry, instance=instance, request=self.request)
            return HealthNutritionReferralForm(registry=registry, instance=instance, request=self.request)

    def form_valid(self, form):
        registry = self.kwargs['registry']
        instance = self.kwargs['pk'] if 'pk' in self.kwargs else None
        form.save(request=self.request, registry=registry, instance=instance)
        return super(HealthNutritionReferralFormView, self).form_valid(form)


class PSSFormView(LoginRequiredMixin,
                      GroupRequiredMixin,
                      FormView):
    template_name = 'mscc/service_pss_form.html'
    form_class = PSSServiceForm
    success_url = ''
    group_required = [u"MSCC", u"MSCC_CENTER"]

    def get_success_url(self):
        return reverse('mscc:child_profile', kwargs={'pk': self.kwargs['registry']}) + '?current_tab=services'

    def get_context_data(self, **kwargs):
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        kwargs['registry'] = self.kwargs['registry']
        return super(PSSFormView, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        registry = self.kwargs['registry']
        instance = self.kwargs['pk'] if 'pk' in self.kwargs else None
        data = {}
        if self.request.method == "POST":
            return PSSServiceForm(self.request.POST, instance=instance, registry=registry, request=self.request)
        else:
            if instance:
                data = to_array(PSSServiceForm.Meta.fields, get_object_or_404(PSSService, pk=instance))
                return PSSServiceForm(data, registry=registry, instance=instance, request=self.request)
            return PSSServiceForm(registry=registry, instance=instance, request=self.request)

    def form_valid(self, form):
        registry = self.kwargs['registry']
        instance = self.kwargs['pk'] if 'pk' in self.kwargs else None
        form.save(request=self.request, registry=registry, instance=instance)
        return super(PSSFormView, self).form_valid(form)


class YouthKitServiceFormView(LoginRequiredMixin,
                      GroupRequiredMixin,
                      FormView):
    template_name = 'mscc/service_youth_kit_form.html'
    form_class = YouthKitServiceForm
    success_url = ''
    group_required = [u"MSCC", u"MSCC_CENTER"]

    def get_success_url(self):
        return reverse('mscc:child_profile', kwargs={'pk': self.kwargs['registry']}) + '?current_tab=services'

    def get_context_data(self, **kwargs):
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        kwargs['registry'] = self.kwargs['registry']
        return super(YouthKitServiceFormView, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        registry = self.kwargs['registry']
        instance = self.kwargs['pk'] if 'pk' in self.kwargs else None
        data = {}
        if self.request.method == "POST":
            return YouthKitServiceForm(self.request.POST, instance=instance, registry=registry, request=self.request)
        else:
            if instance:
                data = to_array(YouthKitServiceForm.Meta.fields, get_object_or_404(YouthKitService, pk=instance))
                return YouthKitServiceForm(data, registry=registry, instance=instance, request=self.request)
            return YouthKitServiceForm(registry=registry, instance=instance, request=self.request)

    def form_valid(self, form):
        registry = self.kwargs['registry']
        instance = self.kwargs['pk'] if 'pk' in self.kwargs else None
        form.save(request=self.request, registry=registry, instance=instance)
        return super(YouthKitServiceFormView, self).form_valid(form)


class YouthServiceMaharatiFormView(LoginRequiredMixin,
                      GroupRequiredMixin,
                      FormView):
    template_name = 'mscc/service_youth_maharati_form.html'
    form_class = YouthServiceMaharatiForm
    success_url = ''
    group_required = [u"MSCC", u"MSCC_CENTER"]

    def get_success_url(self):
        return reverse('mscc:child_profile', kwargs={'pk': self.kwargs['registry']}) + '?current_tab=services'

    def get_context_data(self, **kwargs):
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        kwargs['registry'] = self.kwargs['registry']
        return super(YouthServiceMaharatiFormView, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        registry = self.kwargs['registry']
        instance = self.kwargs['pk'] if 'pk' in self.kwargs else None
        data = {}
        if self.request.method == "POST":
            return YouthServiceMaharatiForm(self.request.POST, instance=instance, registry=registry, request=self.request)
        else:
            if instance:
                service_data = get_object_or_404(YouthService, pk=instance)
                data = service_data.service_values
                return YouthServiceMaharatiForm(data, registry=registry, instance=instance, request=self.request)
            return YouthServiceMaharatiForm(registry=registry, instance=instance, request=self.request)

    def form_valid(self, form):
        registry = self.kwargs['registry']
        instance = self.kwargs['pk'] if 'pk' in self.kwargs else None
        form.save(request=self.request, registry=registry, instance=instance)
        return super(YouthServiceMaharatiFormView, self).form_valid(form)


class YouthServiceGilFormView(LoginRequiredMixin,
                      GroupRequiredMixin,
                      FormView):
    template_name = 'mscc/service_youth_gil_form.html'
    form_class = YouthServiceGilForm
    success_url = ''
    group_required = [u"MSCC", u"MSCC_CENTER"]

    def get_success_url(self):
        return reverse('mscc:child_profile', kwargs={'pk': self.kwargs['registry']}) + '?current_tab=services'

    def get_context_data(self, **kwargs):
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        kwargs['registry'] = self.kwargs['registry']
        return super(YouthServiceGilFormView, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        registry = self.kwargs['registry']
        instance = self.kwargs['pk'] if 'pk' in self.kwargs else None
        data = {}
        if self.request.method == "POST":
            return YouthServiceGilForm(self.request.POST, instance=instance, registry=registry, request=self.request)
        else:
            if instance:
                service_data = get_object_or_404(YouthService, pk=instance)
                data = service_data.service_values
                return YouthServiceGilForm(data, registry=registry, instance=instance, request=self.request)
            return YouthServiceGilForm(registry=registry, instance=instance, request=self.request)

    def form_valid(self, form):
        registry = self.kwargs['registry']
        instance = self.kwargs['pk'] if 'pk' in self.kwargs else None
        form.save(request=self.request, registry=registry, instance=instance)
        return super(YouthServiceGilFormView, self).form_valid(form)


class FollowUpFormView(LoginRequiredMixin,
                       GroupRequiredMixin,
                       FormView):
    template_name = 'mscc/service_follow_up_form.html'
    form_class = FollowUpServiceForm
    success_url = ''
    group_required = [u"MSCC", u"MSCC_CENTER"]

    def get_success_url(self):
        return reverse('mscc:child_profile', kwargs={'pk': self.kwargs['registry']}) + '?current_tab=services'

    def get_context_data(self, **kwargs):
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        kwargs['registry'] = self.kwargs['registry']
        return super(FollowUpFormView, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        registry = self.kwargs['registry']
        instance = self.kwargs['pk'] if 'pk' in self.kwargs else None
        data = {}
        if self.request.method == "POST":
            return FollowUpServiceForm(self.request.POST, instance=instance, registry=registry, request=self.request)
        else:
            if instance:
                data = to_array(FollowUpServiceForm.Meta.fields, get_object_or_404(FollowUpService, pk=instance))
                return FollowUpServiceForm(data, registry=registry, instance=instance, request=self.request)
            return FollowUpServiceForm(registry=registry, instance=instance, request=self.request)

    def form_valid(self, form):
        registry = self.kwargs['registry']
        instance = self.kwargs['pk'] if 'pk' in self.kwargs else None
        form.save(request=self.request, registry=registry, instance=instance)
        return super(FollowUpFormView, self).form_valid(form)


class YouthAssessmentFormView(LoginRequiredMixin,
                       GroupRequiredMixin,
                       FormView):
    template_name = 'mscc/service_youth_assessment_form.html'
    form_class = YouthAssessmentForm
    success_url = ''
    group_required = [u"MSCC", u"MSCC_CENTER"]

    def get_success_url(self):
        return reverse('mscc:child_profile', kwargs={'pk': self.kwargs['registry']}) + '?current_tab=services'

    def get_context_data(self, **kwargs):
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        kwargs['registry'] = self.kwargs['registry']
        return super(YouthAssessmentFormView, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        registry = self.kwargs['registry']
        instance = self.kwargs['pk'] if 'pk' in self.kwargs else None
        data = {}
        if self.request.method == "POST":
            return YouthAssessmentForm(self.request.POST, instance=instance, registry=registry, request=self.request)
        else:
            if instance:
                data = to_array(YouthAssessmentForm.Meta.fields, get_object_or_404(YouthAssessment, pk=instance))
                return YouthAssessmentForm(data, registry=registry, instance=instance, request=self.request)
            return YouthAssessmentForm(registry=registry, instance=instance, request=self.request)

    def form_valid(self, form):
        registry = self.kwargs['registry']
        instance = self.kwargs['pk'] if 'pk' in self.kwargs else None
        form.save(request=self.request, registry=registry, instance=instance)
        return super(YouthAssessmentFormView, self).form_valid(form)


class YouthReferralFormView(LoginRequiredMixin,
                       GroupRequiredMixin,
                       FormView):
    template_name = 'mscc/service_youth_referral_form.html'
    form_class = YouthReferralForm
    success_url = ''
    group_required = [u"MSCC", u"MSCC_CENTER"]

    def get_success_url(self):
        return reverse('mscc:child_profile', kwargs={'pk': self.kwargs['registry']}) + '?current_tab=services'

    def get_context_data(self, **kwargs):
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        kwargs['registry'] = self.kwargs['registry']
        return super(YouthReferralFormView, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        registry = self.kwargs['registry']
        instance = self.kwargs['pk'] if 'pk' in self.kwargs else None
        data = {}
        if self.request.method == "POST":
            return YouthReferralForm(self.request.POST, instance=instance, registry=registry, request=self.request)
        else:
            if instance:
                data = to_array(YouthReferralForm.Meta.fields, get_object_or_404(YouthReferral, pk=instance))
                return YouthReferralForm(data, registry=registry, instance=instance, request=self.request)
            return YouthReferralForm(registry=registry, instance=instance, request=self.request)

    def form_valid(self, form):
        registry = self.kwargs['registry']
        instance = self.kwargs['pk'] if 'pk' in self.kwargs else None
        form.save(request=self.request, registry=registry, instance=instance)
        return super(YouthReferralFormView, self).form_valid(form)


class FollowUpViewAll(LoginRequiredMixin,
                      TemplateView):

    template_name = 'mscc/service_follow_up_all.html'

    def get_context_data(self, **kwargs):
        from student_registration.mscc.templatetags.simple_tags import get_service_all

        registry = self.kwargs['registry']
        instances = get_service_all(registry, 'FollowUpService')

        return {
            'registry': registry,
            'instances': instances
        }


class RecreationalFormView(LoginRequiredMixin,
                           GroupRequiredMixin,
                           FormView):
    template_name = 'mscc/service_recreational_form.html'
    form_class = RecreationalForm
    success_url = ''
    group_required = [u"MSCC", u"MSCC_CENTER"]

    def get_success_url(self):
        return reverse('mscc:child_profile', kwargs={'pk': self.kwargs['registry']}) + '?current_tab=services'

    def get_context_data(self, **kwargs):
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        kwargs['registry'] = self.kwargs['registry']
        return super(RecreationalFormView, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        registry = self.kwargs['registry']
        instance = self.kwargs['pk'] if 'pk' in self.kwargs else None
        data = {}
        if self.request.method == "POST":
            return RecreationalForm(self.request.POST, instance=instance, registry=registry, request=self.request)
        else:
            if instance:
                assessment_data = get_object_or_404(Recreational, pk=instance)
                data = assessment_data.assessment
                return RecreationalForm(data, registry=registry, instance=instance, request=self.request)
            return RecreationalForm(registry=registry, instance=instance, request=self.request)

    def form_valid(self, form):
        registry = self.kwargs['registry']
        instance = self.kwargs['pk'] if 'pk' in self.kwargs else None
        form.save(request=self.request, registry=registry, instance=instance)
        return super(RecreationalFormView, self).form_valid(form)


class LegoServiceFormView(LoginRequiredMixin,
                      GroupRequiredMixin,
                      FormView):
    template_name = 'mscc/service_lego_form.html'
    form_class = LegoServiceForm
    success_url = ''
    group_required = [u"MSCC", u"MSCC_CENTER"]

    def get_success_url(self):
        return reverse('mscc:child_profile', kwargs={'pk': self.kwargs['registry']}) + '?current_tab=services'

    def get_context_data(self, **kwargs):
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        kwargs['registry'] = self.kwargs['registry']
        return super(LegoServiceFormView, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        registry = self.kwargs['registry']
        age = self.kwargs['age']
        instance = self.kwargs['pk'] if 'pk' in self.kwargs else None
        data = {}
        if self.request.method == "POST":
            return LegoServiceForm(self.request.POST, instance=instance, registry=registry, age=age, request=self.request)
        else:
            if instance:
                data = to_array(LegoServiceForm.Meta.fields, get_object_or_404(LegoService, pk=instance))
                return LegoServiceForm(data, registry=registry, age=age, instance=instance, request=self.request)
            return LegoServiceForm(registry=registry, age=age, instance=instance, request=self.request)

    def form_valid(self, form):
        registry = self.kwargs['registry']
        instance = self.kwargs['pk'] if 'pk' in self.kwargs else None
        form.save(request=self.request, registry=registry, instance=instance)
        return super(LegoServiceFormView, self).form_valid(form)

