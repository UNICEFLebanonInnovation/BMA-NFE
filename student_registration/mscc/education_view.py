# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.views.generic import ListView, FormView, TemplateView, UpdateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from braces.views import GroupRequiredMixin, SuperuserRequiredMixin
from django.urls import reverse

from dal import autocomplete
from student_registration.schools.models import School

from .education_form import *
from .utils import *


class SchoolAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = School.objects.filter(is_bma=True).order_by('name')
        if self.q:
            qs = qs.filter(name__icontains=self.q)
        return qs


class EducationServiceFormView(LoginRequiredMixin,
                                  GroupRequiredMixin,
                                  FormView):
    template_name = 'mscc/service_education_service_form.html'
    form_class = EducationServiceForm
    success_url = ''
    group_required = [u"MSCC", u"MSCC_CENTER"]

    def get_success_url(self):
        return reverse('mscc:child_profile', kwargs={'pk': self.kwargs['registry']}) + '?current_tab=services'

    def get_context_data(self, **kwargs):
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        kwargs['registry'] = self.kwargs['registry']
        return super(EducationServiceFormView, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        registry = self.kwargs['registry']
        instance = self.kwargs['pk'] if 'pk' in self.kwargs else None
        data = {}
        if self.request.method == "POST":
            return EducationServiceForm(self.request.POST, instance=instance, registry=registry,
                                        request=self.request)
        else:
            if instance:
                data = to_array(EducationServiceForm.Meta.fields, EducationService.objects.get(id=instance))
                return EducationServiceForm(data, registry=registry, instance=instance, request=self.request)
            return EducationServiceForm(registry=registry, instance=instance, request=self.request)

    def form_valid(self, form):
        registry = self.kwargs['registry']
        instance = self.kwargs['pk'] if 'pk' in self.kwargs else None
        form.save(request=self.request, registry=registry, instance=instance)
        return super(EducationServiceFormView, self).form_valid(form)


class EducationRSServiceFormView(LoginRequiredMixin,
                                 GroupRequiredMixin,
                                 FormView):
    template_name = 'mscc/service_education_rs_service_form.html'
    form_class = EducationRSServiceForm
    success_url = ''
    group_required = [u"MSCC", u"MSCC_CENTER"]

    def get_success_url(self):
        return reverse('mscc:child_profile', kwargs={'pk': self.kwargs['registry']}) + '?current_tab=services'

    def get_context_data(self, **kwargs):
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        kwargs['registry'] = self.kwargs['registry']
        return super(EducationRSServiceFormView, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        registry = self.kwargs['registry']
        pk = self.kwargs['pk'] if 'pk' in self.kwargs else None

        if self.request.method == "POST":
            return EducationRSServiceForm(self.request.POST, pk=pk, registry=registry, request=self.request)
        else:
            if pk:
                instance = EducationRSService.objects.get(id=pk)
                return EducationRSServiceForm(instance=instance, registry=registry, pk=pk, request=self.request)
            return EducationRSServiceForm(registry=registry, pk=pk, request=self.request)

    def form_valid(self, form):
        registry = self.kwargs['registry']
        instance = self.kwargs['pk'] if 'pk' in self.kwargs else None
        form.save(request=self.request, registry=registry, instance=instance)
        return super(EducationRSServiceFormView, self).form_valid(form)


class EducationGradingFormView(LoginRequiredMixin,
                               GroupRequiredMixin,
                               FormView):
    template_name = 'mscc/service_education_grading_form.html'
    form_class = EducationGradingForm
    success_url = ''
    group_required = [u"MSCC", u"MSCC_CENTER"]

    def get_success_url(self):
        return reverse('mscc:child_profile', kwargs={'pk': self.kwargs['registry']}) + '?current_tab=services'

    def get_context_data(self, **kwargs):
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        kwargs['registry'] = self.kwargs['registry']
        kwargs['programme_type'] = self.kwargs['programme_type']
        kwargs['pre_post'] = self.kwargs['pre_post'] if 'pre_post' in self.kwargs else None
        return super(EducationGradingFormView, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        registry = self.kwargs['registry']
        programme_type = self.kwargs['programme_type']
        pre_post = self.kwargs['pre_post'] if 'pre_post' in self.kwargs else None
        instance = self.kwargs['pk'] if 'pk' in self.kwargs else None
        data = {}
        if self.request.method == "POST":
            return EducationGradingForm(self.request.POST, instance=instance, registry=registry,
                                        programme_type=programme_type,pre_post=pre_post, request=self.request)
        else:
            if instance:
                grade_data = EducationProgrammeAssessment.objects.get(id=instance)
                if pre_post == 'pre':
                    data = grade_data.pre_test
                if pre_post == 'post':
                    data = grade_data.post_test
                return EducationGradingForm(data, registry=registry, programme_type=programme_type,pre_post=pre_post, instance=instance, request=self.request)
            return EducationGradingForm(registry=registry, programme_type=programme_type, pre_post=pre_post, instance=instance, request=self.request)

    def form_valid(self, form):
        registry = self.kwargs['registry']
        programme_type = self.kwargs['programme_type']
        pre_post = self.kwargs['pre_post'] if 'pre_post' in self.kwargs else None
        instance = self.kwargs['pk'] if 'pk' in self.kwargs else None
        form.save(request=self.request, registry=registry,  programme_type=programme_type, pre_post=pre_post,
                  instance=instance)
        return super(EducationGradingFormView, self).form_valid(form)


class YouthScoringFormView(LoginRequiredMixin,
                           GroupRequiredMixin,
                           FormView):
    template_name = 'mscc/service_youth_scoring_form.html'
    form_class = YouthScoringForm
    success_url = ''
    group_required = [u"MSCC", u"MSCC_CENTER"]

    def get_success_url(self):
        return reverse('mscc:child_profile', kwargs={'pk': self.kwargs['registry']}) + '?current_tab=services'

    def get_context_data(self, **kwargs):
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        kwargs['registry'] = self.kwargs['registry']
        kwargs['programme_type'] = self.kwargs['programme_type']
        kwargs['pre_post'] = self.kwargs['pre_post'] if 'pre_post' in self.kwargs else 'pre'
        return super(YouthScoringFormView, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        registry = self.kwargs['registry']
        programme_type = self.kwargs['programme_type']
        pre_post = self.kwargs['pre_post'] if 'pre_post' in self.kwargs else None
        instance = self.kwargs['pk'] if 'pk' in self.kwargs else None
        data = {}
        if self.request.method == "POST":
            return YouthScoringForm(self.request.POST, instance=instance, registry=registry,
                                    programme_type=programme_type, pre_post=pre_post, request=self.request)
        else:
            if instance:
                grade_data = EducationProgrammeAssessment.objects.get(id=instance)
                if pre_post == 'pre':
                    data = grade_data.pre_test
                if pre_post == 'post':
                    data = grade_data.post_test
                return YouthScoringForm(data, registry=registry, programme_type=programme_type,pre_post=pre_post,
                                        instance=instance, request=self.request)
            return YouthScoringForm(registry=registry, programme_type=programme_type, pre_post=pre_post,
                                    instance=instance, request=self.request)

    def form_valid(self, form):
        registry = self.kwargs['registry']
        programme_type = self.kwargs['programme_type']
        pre_post = self.kwargs['pre_post'] if 'pre_post' in self.kwargs else None
        instance = self.kwargs['pk'] if 'pk' in self.kwargs else None
        form.save(request=self.request, registry=registry,  programme_type=programme_type, pre_post=pre_post,
                  instance=instance)
        return super(YouthScoringFormView, self).form_valid(form)


class EducationSchoolGradingFormView(LoginRequiredMixin,
                                     GroupRequiredMixin,
                                     FormView):
    template_name = 'mscc/service_school_grading_form.html'
    form_class = EducationSchoolGradingForm
    success_url = ''
    group_required = [u"MSCC", u"MSCC_CENTER"]

    def get_success_url(self):
        return reverse('mscc:child_profile', kwargs={'pk': self.kwargs['registry']}) + '?current_tab=services'

    def get_context_data(self, **kwargs):
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        kwargs['registry'] = self.kwargs['registry']
        kwargs['programme_type'] = self.kwargs['programme_type']
        return super(EducationSchoolGradingFormView, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        registry = self.kwargs['registry']
        programme_type = self.kwargs['programme_type']
        instance = self.kwargs['pk'] if 'pk' in self.kwargs else None
        if self.request.method == "POST":
            return EducationSchoolGradingForm(self.request.POST, instance=instance, registry=registry,
                                              programme_type=programme_type, request=self.request)
        else:
            grade_data = EducationProgrammeAssessment.objects.get(id=instance)
            data = grade_data.school_test
            return EducationSchoolGradingForm(data, registry=registry, programme_type=programme_type, instance=instance, request=self.request)

    def form_valid(self, form):
        registry = self.kwargs['registry']
        instance = self.kwargs['pk'] if 'pk' in self.kwargs else None
        form.save(request=self.request, instance=instance)
        return super(EducationSchoolGradingFormView, self).form_valid(form)
