# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import json
from collections import Counter

from django.views.generic import (
    DetailView,
    ListView,
    RedirectView,
    UpdateView,
    TemplateView,
    FormView,
    DeleteView,
)
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest, HttpResponseForbidden, HttpResponseRedirect
from django.db.models import Count, F
from django.contrib.postgres.aggregates import ArrayAgg
from django.db import connection
import csv
import io
import zipfile
import codecs
from django.utils.encoding import smart_str
import traceback

from rest_framework import status
from django.db.models import F, Q, OuterRef, Exists, Subquery, IntegerField, Avg, FloatField
from django.db.models.functions import Coalesce, NullIf, Cast
from django.urls import reverse, reverse_lazy
from rest_framework import viewsets, mixins, permissions
from braces.views import GroupRequiredMixin, SuperuserRequiredMixin

from django_filters.views import FilterView
from django_tables2 import MultiTableMixin, RequestConfig, SingleTableView
from django_tables2.export.views import ExportMixin
from fuzzywuzzy import fuzz
from django.shortcuts import redirect, render
import uuid
from django.core.files.base import ContentFile
from django.contrib.auth.decorators import login_required
from student_registration.students.utils import generate_one_unique_id
from student_registration.students.models import Nationality
from student_registration.attendances.models import MSCCAttendanceChild
from student_registration.backends.utils import (
    ExportStorage,
    download_file,
    is_valid_filename,
)

from .filters import (
    MainFilter,
    FullFilter,
    TeacherFilter,
)
from .tables import (
    BootstrapTable,
    MainTable,
    YouthMainTable,
    FullTable,
    PartnerTable,
    TeacherTable,
)
from .models import (
    Round,
    ProvidedServices,
    Registration,
    Teacher,
    PSSService,
    EducationAssessment,
    HealthNutritionService,
    EducationService,
    EducationProgrammeAssessment,
)
from student_registration.backends.models import ExportHistory

from .forms import (
    MainForm,
    ReferralForm,
    TeacherForm,
)
from .serializers import (
    MainSerializer,
    TeacherSerializer,
)

from .utils import *

from student_registration.mscc.templatetags.simple_tags import education_history_model, education_history_programmes
from .tasks import queue_mscc_export, queue_filtered_mscc_export
from student_registration.users.templatetags.custom_tags import has_group


def chart_data(request):
    """Return aggregated MSCC registration data for charts.

    Returns:
        JsonResponse: A list of label/value pairs representing the grouped
        registration counts.
    """
    user = request.user
    metric = request.GET.get('chart', 'nationality')
    qs = Registration.objects.filter(deleted=False)

    if not (user.is_superuser or user.is_staff):
        if user.partner_id:
            qs = qs.filter(partner_id=user.partner_id)
        if user.center_id:
            qs = qs.filter(center_id=user.center_id)

    partner = request.GET.get('partner')
    if partner:
        qs = qs.filter(partner_id=partner)

    governorate = request.GET.get('governorate')
    if governorate:
        qs = qs.filter(center__governorate_id=governorate)

    caza = request.GET.get('caza')
    if caza:
        qs = qs.filter(center__caza_id=caza)

    cadaster = request.GET.get('cadaster')
    if cadaster:
        qs = qs.filter(center__cadaster_id=cadaster)

    programme_type = request.GET.get('programme_type')
    if programme_type:
        qs = qs.filter(education_service__education_program=programme_type)

    start = validate_date(request.GET.get('start'))
    if start:
        qs = qs.filter(created__date__gte=start)

    end = validate_date(request.GET.get('end'))
    if end:
        qs = qs.filter(created__date__lte=end)

    if metric == 'gender':
        data = (
            qs.values(label=F('child__gender'))
            .exclude(child__gender__isnull=True)
            .annotate(value=Count('id'))
            .order_by('label')
        )
    else:
        data = (
            qs.values(label=F('child__nationality__name'))
            .exclude(child__nationality__isnull=True)
            .annotate(value=Count('id'))
            .order_by('label')
        )
    return JsonResponse(list(data), safe=False)


class ProfileView(LoginRequiredMixin,
                  TemplateView):
    template_name = 'mscc/profile.html'

    def get_context_data(self, **kwargs):
        """Build the profile context for the requested registration.

        Args:
            **kwargs: Keyword arguments passed by :class:`TemplateView`.

        Returns:
            dict: Context containing the registration, service metadata and
            whether the child can be enrolled in a new round.
        """
        instance = Registration.objects.get(id=self.kwargs['pk'])
        current_tab = self.request.GET.get('current_tab', 'info')

        rounds_registered = EducationService.objects.filter(
            registration__child_id=instance.child.id,
            registration__deleted=False
        ).values_list('round_id', flat=True)

        # Remove any None values
        rounds_registered = [r for r in rounds_registered if r is not None]

        # Query for available rounds
        available_rounds = Round.objects.filter(current_year=True).exclude(id__in=rounds_registered)

        # Check if any exist
        new_round = available_rounds.exists()

        services = ProvidedServices.objects.filter(registration=instance)
        services_dict = {service.name: service for service in services}

        return {
            'instance': instance,
            'new_round': new_round,
            'current_tab': current_tab,
            'provided_services': services_dict,
        }


class DashboardView(LoginRequiredMixin,
                    TemplateView):
    template_name = 'mscc/dashboard.html'

    def get_context_data(self, **kwargs):
        """Collect contextual data for the dashboard view.

        Args:
            **kwargs: Keyword arguments passed by :class:`TemplateView`.

        Returns:
            dict: Context containing registration counts, center, partner,
            and round collections for dashboard rendering.
        """
        from student_registration.locations.models import Center, Location
        from student_registration.clm.models import PartnerOrganization
        from .models import Round, Registration

        user = self.request.user
        instances = Registration.objects.filter(deleted=False)
        centers = Center.objects.all()
        governorates = Location.objects.filter(type_id=1)
        partners = PartnerOrganization.objects.all()
        rounds = Round.objects.all()

        if not (user.is_superuser or user.is_staff):
            if user.partner_id:
                instances = instances.filter(partner_id=user.partner_id)
                centers = centers.filter(partner_id=user.partner_id)
                partners = partners.filter(id=user.partner_id)
            if user.center_id:
                instances = instances.filter(center_id=user.center_id)
                centers = centers.filter(id=user.center_id)

        return {
            'total': instances.count(),
            'centers': centers,
            'governorates': governorates,
            'partners': partners,
            'rounds': rounds,
        }


class DashboardCustomView(LoginRequiredMixin,
                    TemplateView):
    template_name = 'mscc/dashboard_d3.html'

    def get_context_data(self, **kwargs):
        """Collect contextual data for the D3 dashboard view.

        Args:
            **kwargs: Keyword arguments passed by :class:`TemplateView`.

        Returns:
            dict: Context containing registration, center, partner and round
            collections for dashboard rendering.
        """
        from student_registration.locations.models import Center, Location
        from student_registration.clm.models import PartnerOrganization
        from .models import Round

        user = self.request.user
        instances = Registration.objects.filter(deleted=False)
        centers = Center.objects.all()
        governorates = Location.objects.filter(type_id=1)
        partners = PartnerOrganization.objects.all()
        rounds = Round.objects.all()

        if not (user.is_superuser or user.is_staff):
            if user.partner_id:
                instances = instances.filter(partner_id=user.partner_id)
                centers = centers.filter(partner_id=user.partner_id)
                partners = partners.filter(id=user.partner_id)
            if user.center_id:
                instances = instances.filter(center_id=user.center_id)
                centers = centers.filter(id=user.center_id)

        # Children registered in more than one round
        moved_qs = (
            instances.values(
                'child__first_name',
                'child__father_name',
                'child__last_name',
            )
            .annotate(
                rounds=ArrayAgg('round__name', distinct=True),
                programmes=ArrayAgg('education_service__education_program', distinct=True),
                num_rounds=Count('round', distinct=True),
            )
            .filter(num_rounds__gt=1)
        )

        moved_children = [
            {
                'name': f"{row['child__first_name']} {row['child__father_name']} {row['child__last_name']}",
                'rounds': [r for r in row['rounds'] if r],
                'programmes': [p for p in row['programmes'] if p],
            }
            for row in moved_qs
        ]

        return {
            'total': instances.count(),
            'centers': centers,
            'governorates': governorates,
            'partners': partners,
            'rounds': rounds,
            'moved_children': moved_children,
        }


class DashboardDataView(LoginRequiredMixin, View):
    """Return aggregated data for dashboard charts."""

    def get(self, request):
        from django.db.models import Count
        from .models import (
            Registration,
            YouthKitService,
            PSSService,
            Referral,
        )
        user = request.user
        cash_support_programmes = Registration.CASH_SUPPORT_PROGRAMMES

        qs = Registration.objects.filter(deleted=False)

        if not (user.is_superuser or user.is_staff):
            if user.partner_id:
                qs = qs.filter(partner_id=user.partner_id)
            if user.center_id:
                qs = qs.filter(center_id=user.center_id)

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
            qs = qs.filter(partner_id__in=partners)

        def aggregate(queryset, field):
            results = queryset.values(field).annotate(total=Count('id')).order_by(field)
            data = []
            for row in results:
                name = row.get(field) or 'N/A'
                data.append({'name': name, 'y': row['total']})
            return data

        pss_qs = PSSService.objects.filter(registration__in=qs)
        ys_qs = YouthKitService.objects.filter(registration__in=qs)
        ref_qs = Referral.objects.filter(registration__in=qs)

        data = {
            'children_per_gender': aggregate(qs, 'child__gender'),
            'children_per_status': aggregate(qs, 'child__marital_status'),
            'children_per_programme': aggregate(qs, 'type'),
            'children_per_nationality': aggregate(qs, 'child__nationality__name'),
            'children_per_source': aggregate(qs, 'source_of_identification'),
            'children_per_disability': aggregate(qs, 'child__disability__name'),
            'children_per_vulnerability': aggregate(pss_qs, 'child_vulnerability'),
            'children_referred_formal_education': aggregate(ref_qs, 'referred_formal_education'),
        }

        programme_counts = Counter()
        for programmes in qs.values_list('cash_support_programmes', flat=True):
            if programmes:
                programme_counts.update(programmes)

        cash = []
        for value, _ in cash_support_programmes:
            if value:
                cash.append({'name': value, 'y': programme_counts.get(value, 0)})
        data['children_cash_support'] = cash

        data['children_volunteering'] = aggregate(ys_qs, 'participate_volunteering')

        # Number of unique children per round
        per_round = (
            qs.values('round__name')
            .annotate(total=Count('child', distinct=True))
            .order_by('round__name')
        )
        round_names = [row.get('round__name') or 'N/A' for row in per_round]
        per_round_dict = {name: row['total'] for name, row in zip(round_names, per_round)}
        data['children_per_round'] = [
            {'name': name, 'y': per_round_dict[name]}
            for name in round_names
        ]

        # Children registered in more than one round
        multi_round_children = list(
            qs.values('child')
            .annotate(round_count=Count('round', distinct=True))
            .filter(round_count__gt=1)
            .values_list('child', flat=True)
        )
        moved_per_round = (
            qs.filter(child__in=multi_round_children)
            .values('round__name')
            .annotate(total=Count('child', distinct=True))
            .order_by('round__name')
        )
        moved_dict = {row.get('round__name') or 'N/A': row['total'] for row in moved_per_round}

        data['children_moved_rounds'] = {
            'categories': round_names,
            'moved': [moved_dict.get(name, 0) for name in round_names],
            'new': [per_round_dict[name] - moved_dict.get(name, 0) for name in round_names],
        }

        return JsonResponse(data, safe=False)


class MainAddView(LoginRequiredMixin,
                  GroupRequiredMixin,
                  FormView):
    template_name = 'mscc/main_form.html'
    form_class = MainForm
    success_url = reverse_lazy('mscc:list')
    group_required = [u"MSCC", u"MSCC_CENTER"]

    def dispatch(self, request, *args, **kwargs):
        if has_group(request.user, 'MSCC_CENTER') and not request.user.partner:
            return redirect('mscc:list')
        return super(MainAddView, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('mscc:child_profile', kwargs={'pk': self.request.session.get('instance_id')})

    def get_context_data(self, **kwargs):
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        return super(MainAddView, self).get_context_data(**kwargs)

    def get_initial(self):
        initial = super(MainAddView, self).get_initial()
        data = {
            'type': self.request.GET.get('type', ''),
        }
        initial = data

        return initial

    def form_valid(self, form):
        form.save(self.request)
        return super(MainAddView, self).form_valid(form)

    def get_form(self, form_class=None):
        if self.request.method == "POST":
            return MainForm(self.request.POST, instance=None, request=self.request)
        else:
            return MainForm(None, instance=None, request=self.request, initial=self.get_initial())


class MainEditView(LoginRequiredMixin,
                   GroupRequiredMixin,
                   FormView):
    template_name = 'mscc/main_form.html'
    form_class = MainForm
    success_url = reverse_lazy('mscc:list')
    group_required = [u"MSCC", u"MSCC_CENTER"]

    def get_success_url(self):
        return reverse('mscc:child_profile', kwargs={'pk': self.request.session.get('instance_id')})

    def get_context_data(self, **kwargs):
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        return super(MainEditView, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        instance = Registration.objects.get(id=self.kwargs['pk'])
        if self.request.method == "POST":
            return MainForm(self.request.POST, instance=instance, request=self.request)
        else:
            data = MainSerializer(instance).data
            data['child_nationality'] = data['child_nationality_id'] if 'child_nationality_id' in data else ''
            data['child_disability'] = data['child_disability_id'] if 'child_disability_id' in data else ''
            data['main_caregiver_nationality'] = data['main_caregiver_nationality_id']if 'main_caregiver_nationality_id' in data else ''
            data['father_educational_level'] = data['father_educational_level_id']if 'father_educational_level_id' in data else ''
            data['mother_educational_level'] = data['mother_educational_level_id']if 'mother_educational_level_id' in data else ''
            data['id_type'] = data['id_type_id']if 'id_type_id' in data else ''
            return MainForm(data, instance=instance, request=self.request)

    def form_valid(self, form):
        instance = Registration.objects.get(id=self.kwargs['pk'])
        form.save(request=self.request, instance=instance)
        return super(MainEditView, self).form_valid(form)


class NewRoundView(LoginRequiredMixin,
                   GroupRequiredMixin,
                   TemplateView):

    group_required = [u"MSCC", u"MSCC_CENTER"]
    template_name = 'mscc/new_round.html'

    def get_context_data(self, **kwargs):
        registry = kwargs.get('pk')
        return {
            'registry': registry
        }


class NewRoundRedirectView(LoginRequiredMixin, RedirectView):
    permanent = False

    def get_redirect_url(self):

        registry = self.request.GET.get('registry')

        if self.request.GET.get('new_round_confirmation', None) == 'confirmed':
            import copy
            registration = Registration.objects.get(id=registry)
            new_registration = copy.copy(registration)
            new_registration.pk = None
            new_registration.round = None
            new_registration.owner = self.request.user
            new_registration.modified_by = self.request.user
            if self.request.user.center:
                new_registration.center = self.request.user.center
            if self.request.user.partner:
                new_registration.partner = self.request.user.partner
            new_registration.save()

            return reverse('mscc:service_education_add', kwargs={'registry': new_registration.id})

        return reverse('mscc:new_round', kwargs={'registry': registry})


def main_mark_delete_view(request, pk):
    if request.user.is_authenticated:
        try:
            registration = Registration.objects.get(id=pk)
            registration.deleted = True
            registration.deleted_by = request.user
            registration.save()
            result = {"isSuccessful": True}
        except Registration.DoesNotExist:
            result = {"isSuccessful": False}
    else:
        result = {"isSuccessful": False}
    return JsonResponse(result)


class MainListView(LoginRequiredMixin,
                   GroupRequiredMixin,
                   FilterView,
                   ExportMixin,
                   SingleTableView,
                   RequestConfig):

    table_class = MainTable
    model = Registration
    template_name = 'mscc/list.html'
    table = BootstrapTable(Registration.objects.all(), order_by='id')
    group_required = [u"MSCC"]

    filterset_class = MainFilter

    def get_queryset(self):
        user = self.request.user
        center_id = user.center_id
        partner_id = user.partner_id

        qs = (Registration.objects
              .select_related(
            'child',
            'child__nationality',
            'partner',
            'center',
            'center__governorate',
            'center__caza',
            'center__cadaster',
            'owner',
            'modified_by',
            'round',
        )
              .prefetch_related('education_service')
              .filter(deleted=False))

        previous_registration = Registration.objects.filter(
            child_id=OuterRef('child_id'),
            created__lt=OuterRef('created'),
        )

        absent_days = (
            MSCCAttendanceChild.objects
                .filter(registration_id=OuterRef('pk'), attended='No')
                .values('registration')
                .annotate(count=Count('id'))
                .values('count')
        )

        qs = qs.annotate(
            has_previous=Exists(previous_registration),
            _total_absent_days=Coalesce(Subquery(absent_days, output_field=IntegerField()), 0),
        )

        round_filter = Q(round__isnull=True) | Q(round__current_year=True)

        if has_group(user, 'MSCC_UNICEF'):
            return qs.filter(round_filter).order_by('-id')

        elif has_group(user, 'MSCC_PARTNER') and partner_id:
            return qs.filter(round_filter, partner=partner_id).order_by('-id')

        elif has_group(user, 'MSCC_CENTER') and center_id:
            return qs.filter(round_filter, center=center_id).order_by('-id')

        return Registration.objects.none()

    def get_table_class(self):

        """
        Return the class to use for the table.
        """
        if has_group(self.request.user, 'MSCC_UNICEF'):
            return FullTable
        elif has_group(self.request.user, 'MSCC_PARTNER'):
            return PartnerTable
        elif has_group(self.request.user, 'MSCC_CENTER'):
            return self.table_class

        if not has_group(self.request.user, 'MSCC_FULL'):
            return YouthMainTable
        return self.table_class

    def get_filterset_class(self):
        if has_group(self.request.user, 'MSCC_UNICEF'):
            return FullFilter
        elif has_group(self.request.user, 'MSCC_PARTNER'):
            return self.filterset_class
        elif has_group(self.request.user, 'MSCC_CENTER'):
            return self.filterset_class

        return self.filterset_class


class MainViewSet(mixins.RetrieveModelMixin,
                  mixins.ListModelMixin,
                  mixins.CreateModelMixin,
                  mixins.UpdateModelMixin,
                  viewsets.GenericViewSet):
    model = Registration
    queryset = Registration.objects.all()
    serializer_class = MainSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        from datetime import datetime

        qs = self.queryset
        if self.request.GET.get('creation_date', None):
            return self.queryset.filter(
                created__gte=datetime.strptime(self.request.GET.get('creation_date', None), '%Y-%m-%d')).order_by(
                'created')

        if self.request.GET.get('school', None):
            return self.queryset.filter(school_id=self.request.GET.get('school', None))

        return qs

    def delete(self, request, *args, **kwargs):
        instance = self.model.objects.get(id=kwargs['pk'])
        instance.delete()
        return JsonResponse({'status': status.HTTP_200_OK})


def main_registration_cancel_view(request, pk):
    if request.user.is_authenticated:
        try:
            registration = Registration.objects.get(id=pk)
            registration.deleted = True
            registration.save()
            return redirect('mscc:list')
        except Registration.DoesNotExist:
            result = {"isSuccessful": False}
    else:
        result = {"isSuccessful": False}
    return JsonResponse(result)



class ReferralFormView(LoginRequiredMixin,
                       GroupRequiredMixin,
                       FormView):
    template_name = 'mscc/referral_form.html'
    form_class = ReferralForm
    success_url = reverse_lazy('mscc:list')
    group_required = [u"MSCC", u"MSCC_CENTER"]

    def get_success_url(self):
        return reverse('mscc:child_profile', kwargs={'pk': self.kwargs['registry']}) + '?current_tab=services'

    def get_context_data(self, **kwargs):
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        kwargs['registry'] = self.kwargs['registry']
        return super(ReferralFormView, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        registry = self.kwargs['registry']
        pk = self.kwargs['pk'] if 'pk' in self.kwargs else None

        if self.request.method == "POST":
            return ReferralForm(self.request.POST, pk=pk, registry=registry, request=self.request)
        else:
            if pk:
                instance = Referral.objects.get(id=pk)

                return ReferralForm(instance=instance, registry=registry, pk=pk, request=self.request)
            return ReferralForm(registry=registry, pk=pk, request=self.request)

    def form_valid(self, form):
        registry = self.kwargs['registry']
        instance = self.kwargs['pk'] if 'pk' in self.kwargs else None
        form.save(request=self.request, registry=registry, instance=instance)
        return super(ReferralFormView, self).form_valid(form)


def child_duplication_check(request):
    body_unicode = request.body.decode('utf-8')
    if body_unicode:
        body = json.loads(body_unicode)

        birthday_year = body.get('birthday_year')
        birthday_month = body.get('birthday_month')
        birthday_day = body.get('birthday_day')
        first_name = body.get('first_name')
        father_name = body.get('father_name')
        last_name = body.get('last_name')
        mother_fullname = body.get('mother_fullname')
        sex = body.get('sex')
        nationality_id = body.get('nationality')
        registration_id = body.get('registration_id')

        try:
            nationality = Nationality.objects.get(id=nationality_id).name_en
        except Nationality.DoesNotExist:
            nationality = ''

        birthdate = '{0}-{1}-{2}'.format(birthday_year, birthday_month, birthday_day)
        unicef_id = generate_one_unique_id(
            '0',
            first_name,
            father_name,
            last_name,
            mother_fullname,
            birthdate,
            nationality,
            sex
        )

        if unicef_id:
            qs = Registration.objects.filter(
                child__unicef_id=unicef_id,
                deleted=False
            )
            if registration_id:
                qs = qs.exclude(pk=registration_id)
            qs = qs.values(
                'id',
                'center__name',
                'child__first_name',
                'child__father_name',
                'child__last_name',
                'child__mother_fullname',
                'child__birthday_day',
                'child__birthday_month',
                'child__birthday_year',
                'child__gender',
                'child__nationality__name'
            )
            return JsonResponse({'result': list(qs)})

    return JsonResponse({'result': []})


def quick_search(request):
    from django.db.models.functions import Concat
    from django.db.models import Value

    term = request.GET.get('term', 0).strip()
    terms = request.GET.get('term', 0).strip()
    qs = {}

    if terms:
        user = request.user
        if user.is_authenticated:
            center_id = user.center_id
            partner_id = user.partner_id

            if has_group(user, 'MSCC_UNICEF'):
                qs= Registration.objects.filter(
                    Q(round__isnull=True) | Q(round__current_year=True),
                    deleted=False
                ).order_by('-id')
            elif has_group(user, 'MSCC_PARTNER') and partner_id:
                qs= Registration.objects.filter(
                    Q(round__isnull=True) | Q(round__current_year=True),
                    deleted=False, partner=partner_id
                ).order_by('-id')
            elif has_group(user, 'MSCC_CENTER') and center_id:
                qs= Registration.objects.filter(
                    Q(round__isnull=True) | Q(round__current_year=True),
                    deleted=False, center=center_id
                ).order_by('-id')
            else:
                qs = Registration.objects.none()

            if len(terms.split()) > 1:
                qs = qs.annotate(fullname=Concat('child__first_name', Value(' '), 'child__father_name',
                                                 Value(' '), 'child__last_name')) \
                    .filter(fullname__icontains=terms) \
                    .values('id', 'child__first_name', 'child__last_name',
                            'child__father_name', 'child__mother_fullname').distinct()

            else:
                # for term in terms:
                qs = qs.filter(
                    Q(child__first_name__icontains=term) |
                    Q(child__last_name__icontains=term))\
                    .values('id', 'child__first_name', 'child__last_name',
                            'child__father_name', 'child__mother_fullname').distinct()
        else:
            return JsonResponse({'error': 'User not authenticated'}, status=401)

    return JsonResponse({'result': json.dumps(list(qs))})


class TeacherListView(LoginRequiredMixin,
                  GroupRequiredMixin,
                  FilterView,
                  ExportMixin,
                  SingleTableView,
                  RequestConfig):
    table_class = TeacherTable
    model = Teacher
    template_name = 'mscc/teacher_list.html'
    table = TeacherTable(Teacher.objects.none(), order_by='id')
    group_required = [u"MSCC", u"MSCC_CENTER", u"MSCC_PARTNER", u"MSCC_UNICEF"]
    filterset_class = TeacherFilter

    def get_queryset(self):
        base_queryset = Teacher.objects.select_related('round', 'center')
        user = self.request.user

        if has_group(user, 'MSCC_UNICEF') or user.is_staff:
            return base_queryset

        center_id = user.center_id if user.center_id else 0
        partner_id = user.partner_id if user.partner_id else 0

        if center_id:
            return base_queryset.filter(center_id=center_id)
        if partner_id:
            return base_queryset.filter(center__partner_id=partner_id)

        return base_queryset.none()


class TeacherAddView(LoginRequiredMixin,
                 GroupRequiredMixin,
                 FormView):
    template_name = 'mscc/teacher_form.html'
    form_class = TeacherForm
    success_url = reverse_lazy('mscc:teacher_list')
    group_required = [u"MSCC", u"MSCC_CENTER", u"MSCC_PARTNER", u"MSCC_UNICEF"]

    def get_success_url(self):
        if self.request.POST.get('save_add_another', None):
            return reverse_lazy('mscc:teacher_add')
        if self.request.POST.get('save_and_continue', None):
            # return '/mscc/teacher-edit/' + str(self.request.session.get('instance_id')) + '/'
            return reverse('mscc:teacher_edit', kwargs={'pk': self.request.session.get('instance_id')})
        return self.success_url

    def get_context_data(self, **kwargs):
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        return super(TeacherAddView, self).get_context_data(**kwargs)

    def form_valid(self, form):
        form.save(self.request)
        return super(TeacherAddView, self).form_valid(form)

    def get_form(self, form_class=None):
        if self.request.method == "POST":
            return TeacherForm(self.request.POST, self.request.FILES, instance=None, request=self.request)
        return TeacherForm(None, instance=None, request=self.request)


class TeacherEditView(LoginRequiredMixin,
                  GroupRequiredMixin,
                  FormView):
    template_name = 'mscc/teacher_form.html'
    form_class = TeacherForm
    success_url = reverse_lazy('mscc:teacher_list')
    group_required = [u"MSCC", u"MSCC_CENTER", u"MSCC_PARTNER", u"MSCC_UNICEF"]

    def get_success_url(self):
        if self.request.POST.get('save_add_another', None):
            return reverse_lazy('mscc:teacher_add')
        if self.request.POST.get('save_and_continue', None):
            # return '/mscc/teacher-edit/' + str(self.request.session.get('instance_id')) + '/'
            return reverse('mscc:teacher_edit', kwargs={'pk': self.request.session.get('instance_id')})
        return self.success_url

    def get_form(self, form_class=None):
        instance = Teacher.objects.get(id=self.kwargs['pk'])
        if self.request.method == "POST":
            return TeacherForm(self.request.POST, self.request.FILES, instance=instance, request=self.request)
        data = TeacherSerializer(instance).data
        return TeacherForm(data, instance=instance, request=self.request)

    def form_valid(self, form):
        instance = Teacher.objects.get(id=self.kwargs['pk'])
        form.save(request=self.request, instance=instance)
        return super(TeacherEditView, self).form_valid(form)


class TeacherDeleteView(LoginRequiredMixin, GroupRequiredMixin, DeleteView):
    model = Teacher
    success_url = reverse_lazy('mscc:teacher_list')
    group_required = [u"MSCC", u"MSCC_CENTER", u"MSCC_PARTNER", u"MSCC_UNICEF"]

    def get_object(self):
        from django.shortcuts import get_object_or_404
        return get_object_or_404(Teacher, pk=self.kwargs['pk'])

    def get(self, request, *args, **kwargs):
        obj = self.get_object()
        obj.delete()
        return HttpResponseRedirect(self.success_url)


class TeacherViewSet(mixins.RetrieveModelMixin,
                 mixins.ListModelMixin,
                 mixins.CreateModelMixin,
                 mixins.UpdateModelMixin,
                 viewsets.GenericViewSet):
    model = Teacher
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        queryset = Teacher.objects.all()

        if has_group(user, 'MSCC_UNICEF') or user.is_staff:
            return queryset

        center_id = user.center_id if user.center_id else 0
        partner_id = user.partner_id if user.partner_id else 0

        if center_id:
            return queryset.filter(center_id=center_id)
        if partner_id:
            return queryset.filter(center__partner_id=partner_id)

        return queryset.none()

    def delete(self, request, *args, **kwargs):
        instance = self.model.objects.get(id=kwargs['pk'])
        instance.delete()
        return JsonResponse({'status': status.HTTP_200_OK})


class ProgrammeDetails(LoginRequiredMixin,
                       TemplateView):

    template_name = 'mscc/programme_details.html'

    def get_context_data(self, **kwargs):

        programme_id = self.request.GET.get('programme_id')
        programme_type = self.request.GET.get('programme_type')

        instance = education_history_model(programme_id, programme_type)

        return {
            'instance': instance,
            'programme_type': programme_type
        }


class ChildProfilePreview(LoginRequiredMixin, TemplateView):
    template_name = 'mscc/child_profile_preview.html'

    def get_context_data(self, **kwargs):
        context = super(ChildProfilePreview, self).get_context_data(**kwargs)

        registry_id = self.request.GET.get('registry_id')

        if not registry_id:
            context['error'] = 'No id provided.'
            return context

        try:
            instance = Registration.objects.get(id=registry_id)
        except Registration.DoesNotExist:
            context['error'] = 'Registration with id' + str(registry_id) + ' not found.'
            return context
        except ValueError:
            context['error'] = 'Invalid registry_id ' + str(registry_id)
            return context

        context['instance'] = instance
        return context


@login_required(login_url='/users/login')
def export_list_background(request):
    user = request.user
    filters = request.GET.dict()
    file_format = request.GET.get('format', 'csv')

    export_record = ExportHistory.objects.create(
        export_type='NFR Sector List',
        created_by=user,
        partner_name=user.partner.name if user.partner else '',
        file_format=file_format,
        fields=filters
    )
    queue_filtered_mscc_export(
        export_record.id,
        filters=filters,
        file_format=file_format
    )
    return JsonResponse({'status': 'started'})


def export_child_list_background(request):
    try:
        cursor = connection.cursor()

        vw_mscc_data_str = "SELECT * FROM vw_mscc_child "
        cursor.execute(vw_mscc_data_str)
        mscc_data = cursor.fetchall()
        headers = [col[0] for col in cursor.description]

        zip_output = io.BytesIO()
        with zipfile.ZipFile(zip_output, 'w') as zf:
            # Create CSV for vw_mscc_data
            csv_mscc_output = io.StringIO()
            csv_writer = csv.writer(csv_mscc_output)

            # Add BOM to handle Arabic text correctly
            csv_mscc_output.write(codecs.BOM_UTF8.decode('utf-8'))
            csv_writer.writerow(headers)  # Write headers

            for row in mscc_data:
                encoded_row = [smart_str(cell) for cell in row]
                csv_writer.writerow(encoded_row)

            # Add CSV to ZIP
            zf.writestr('mscc_data.csv', csv_mscc_output.getvalue())

        unique_id = str(uuid.uuid4())
        file_name = "out_file_{}.zip".format(unique_id)
        storage = ExportStorage()
        storage.save(file_name, ContentFile(zip_output.getvalue()))

        return HttpResponse(file_name)

    except Exception as e:
        logging.error("An error occurred during the export process:")
        logging.error(traceback.format_exc())

        return HttpResponse("An error occurred: " + str(e), status=500)


@login_required(login_url='/users/login')
def export_list_async(request):
    fields = None
    file_format = 'csv'
    if request.method == 'POST':
        try:
            payload = json.loads(request.body.decode('utf-8'))
        except (ValueError, AttributeError):
            payload = request.POST
        if isinstance(payload, dict):
            file_format = payload.get('format', 'csv')
            fields = payload.get('fields') or None
        else:
            file_format = payload.get('format', 'csv') if payload else 'csv'
    else:
        file_format = request.GET.get('format', 'csv')
    export_record = ExportHistory.objects.create(
        export_type='NFR Sector List',
        created_by=request.user,
        partner_name=request.user.partner.name if request.user.partner else '',
        fields=fields,
        file_format=file_format,
    )
    queue_mscc_export(export_record.id, fields, file_format)
    return JsonResponse({'status': 'started'})


@login_required(login_url='/users/login')
def get_file(request, file_name):
    if is_valid_filename(file_name, 'zip'):
        return download_file(file_name, 'output_file.zip')
    return HttpResponse("Invalid file.")


@login_required(login_url='/users/login')
def get_file_csv(request, file_name):
    if is_valid_filename(file_name, 'csv'):
        return download_file(file_name, 'exported_data.csv', content_type='text/csv')
    return HttpResponse("Invalid file.", status=400)


class WellbeingDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'mscc/wellbeing_dashboard.html'

    def get_context_data(self, **kwargs):
        from student_registration.locations.models import Center, Location
        from student_registration.clm.models import PartnerOrganization

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


class WellbeingDashboardDataView(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user
        qs = Registration.objects.filter(deleted=False)

        if not (user.is_superuser or user.is_staff):
            if user.partner_id:
                qs = qs.filter(partner_id=user.partner_id)
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
            qs = qs.filter(partner_id__in=partners)

        total_registrations = qs.count() or 1

        # 1. Socio-Economic Data
        labor_participation = (
            qs.values(name=F('have_labour'))
            .annotate(y=Count('id'))
            .order_by('-y')
        )
        labor_participation = [
            {'name': item['name'] or 'Unknown', 'y': item['y']}
            for item in labor_participation
        ]

        labor_income = (
            qs.exclude(have_labour='No')
            .values('labour_type', 'labour_weekly_income')
            .annotate(count=Count('id'))
            .order_by('labour_type', 'labour_weekly_income')
        )
        labor_income_matrix = [
            {
                'type': item['labour_type'] or 'Other',
                'income': item['labour_weekly_income'] or 'Unknown',
                'count': item['count']
            }
            for item in labor_income
        ]

        cash_counts = Counter()
        for programs in qs.values_list('cash_support_programmes', flat=True):
            if programs:
                cash_counts.update(programs)
        cash_support = [
            {'name': name, 'y': count}
            for name, count in cash_counts.items()
        ]

        # 2. Wellbeing & Family (PSS)
        pss_qs = PSSService.objects.filter(registration__in=qs)
        living_arrangements = (
            pss_qs.values(name=F('child_living_arrangement'))
            .annotate(y=Count('id'))
            .order_by('-y')
        )
        living_arrangements = [
            {'name': item['name'] or 'N/A', 'y': item['y']}
            for item in living_arrangements
        ]

        birth_reg = (
            pss_qs.values(name=F('child_registered'))
            .annotate(y=Count('id'))
            .order_by('-y')
        )
        birth_reg = [
            {'name': item['name'] or 'Unknown', 'y': item['y']}
            for item in birth_reg
        ]

        vulnerabilities = (
            pss_qs.values(name=F('child_vulnerability'))
            .annotate(y=Count('id'))
            .order_by('-y')
        )
        vulnerabilities = [
            {'name': item['name'] or 'None Identified', 'y': item['y']}
            for item in vulnerabilities
        ]

        pss_indicators = {
            'caregiver_distress': pss_qs.filter(caregivers_distress='Yes').count(),
            'child_distress': pss_qs.filter(child_distress='Yes').count(),
            'protection_concern': pss_qs.exclude(child_protection_concern__in=['', None]).count(),
        }

        # 3. Education
        edu_qs = EducationService.objects.filter(registration__in=qs)
        edu_status = (
            edu_qs.values(name=F('education_status'))
            .annotate(y=Count('id'))
            .order_by('-y')
        )
        edu_status = [
            {'name': item['name'] or 'Unknown', 'y': item['y']}
            for item in edu_status
        ]

        assess_qs = EducationAssessment.objects.filter(registration__in=qs)
        avg_improvement = assess_qs.aggregate(
            arabic=Avg(Cast(F('post_arabic_grade') - F('pre_arabic_grade'), FloatField()) / NullIf(Cast(F('pre_arabic_grade'), FloatField()), 0.0) * 100),
            math=Avg(Cast(F('post_math_grade') - F('pre_math_grade'), FloatField()) / NullIf(Cast(F('pre_math_grade'), FloatField()), 0.0) * 100),
            language=Avg(Cast(F('post_language_grade') - F('pre_language_grade'), FloatField()) / NullIf(Cast(F('pre_language_grade'), FloatField()), 0.0) * 100),
        )

        # 4. Impact Analysis & KPIs
        # Attendance logic (simplified: use the annotated property if possible or aggregate)
        # For performance, let's just get the average of the annotated _total_absent_days if we were in a ListView,
        # but here we need a raw count.
        total_absences = MSCCAttendanceChild.objects.filter(registration__in=qs, attended='No').count()
        # We don't have total_attendance_days easily without another join.
        # Let's assume a standard 100 days for rate display or just show raw absences if needed.
        # Actually, let's try to get a better proxy.
        total_possible_days = MSCCAttendanceChild.objects.filter(registration__in=qs).count() or 1
        avg_attendance_rate = ((total_possible_days - total_absences) / total_possible_days) * 100

        labor_rate = (qs.exclude(have_labour='No').count() / total_registrations) * 100
        overall_improvement = (
            (avg_improvement['arabic'] or 0) +
            (avg_improvement['math'] or 0) +
            (avg_improvement['language'] or 0)
        ) / 3

        protection_rate = (pss_indicators['protection_concern'] / total_registrations) * 100

        # Barriers
        barriers = (
            assess_qs.values(name=F('barriers'))
            .annotate(y=Count('id'))
            .order_by('-y')
        )
        barriers = [
            {'name': item['name'] or 'No barriers', 'y': item['y']}
            for item in barriers
        ]

        # Impact: Attendance vs Improvement
        # High attendance (>90%) vs Low attendance (<90%)
        # This requires per-registration attendance calculation.
        # For a simplified view, let's look at children with labor vs without labor impact on attendance.
        labor_yes_qs = qs.exclude(have_labour='No')
        labor_no_qs = qs.filter(have_labour='No')

        def get_attendance_rate(sub_qs):
            absences = MSCCAttendanceChild.objects.filter(registration__in=sub_qs, attended='No').count()
            total = MSCCAttendanceChild.objects.filter(registration__in=sub_qs).count() or 1
            return round(((total - absences) / total) * 100, 1)

        labor_impact_attendance = {
            'with_labor': get_attendance_rate(labor_yes_qs),
            'without_labor': get_attendance_rate(labor_no_qs)
        }

        # New Education Grading Analysis
        programme_assessments = EducationProgrammeAssessment.objects.filter(registration__in=qs).values(
            'programme_type', 'pre_test', 'post_test'
        )

        improvements = {}
        for p in programme_assessments:
            ptype = p.get('programme_type') or 'Unknown'
            pre = p.get('pre_test') or {}
            post = p.get('post_test') or {}

            if ptype not in improvements:
                improvements[ptype] = {}

            for key in post.keys():
                if key.endswith('_grade') or key in ['life_skills', 'english_development', 'financial_development', 'it_development']:
                    try:
                        post_val = float(post[key])
                        pre_val = float(pre.get(key, 0))
                        if pre_val > 0:
                            imp = ((post_val - pre_val) / pre_val) * 100
                            if key not in improvements[ptype]:
                                improvements[ptype][key] = []
                            improvements[ptype][key].append(imp)
                    except (ValueError, TypeError):
                        pass

        programme_improvements = []
        all_nfe_improvements = []
        for ptype, metrics in improvements.items():
            for metric, vals in metrics.items():
                if vals:
                    imp_val = round(sum(vals) / len(vals), 1)
                    programme_improvements.append({
                        'programme': ptype,
                        'material': metric.replace('_grade', '').replace('_', ' ').title(),
                        'improvement': imp_val
                    })
                    all_nfe_improvements.extend(vals)

        avg_nfe_grade = 0
        if all_nfe_improvements:
            avg_nfe_grade = sum(all_nfe_improvements) / len(all_nfe_improvements)

        # Impact: Attendance on Improvement
        # Children with 0 absences vs children with > 5 absences
        no_absences_ids = (
            MSCCAttendanceChild.objects.filter(registration__in=qs)
            .values('registration')
            .annotate(absences=Count('id', filter=Q(attended='No')))
            .filter(absences=0)
            .values_list('registration', flat=True)
        )
        high_absences_ids = (
            MSCCAttendanceChild.objects.filter(registration__in=qs)
            .values('registration')
            .annotate(absences=Count('id', filter=Q(attended='No')))
            .filter(absences__gt=5)
            .values_list('registration', flat=True)
        )

        def get_avg_imp(ids):
            agg = EducationAssessment.objects.filter(registration_id__in=ids).aggregate(
                avg=Avg(
                    (Cast(F('post_arabic_grade') - F('pre_arabic_grade'), FloatField()) / NullIf(Cast(F('pre_arabic_grade'), FloatField()), 0.0) * 100 +
                     Cast(F('post_math_grade') - F('pre_math_grade'), FloatField()) / NullIf(Cast(F('pre_math_grade'), FloatField()), 0.0) * 100 +
                     Cast(F('post_language_grade') - F('pre_language_grade'), FloatField()) / NullIf(Cast(F('pre_language_grade'), FloatField()), 0.0) * 100) / 3
                )
            )
            return round(agg['avg'] or 0, 1)

        attendance_impact_improvement = {
            'high_attendance': get_avg_imp(no_absences_ids),
            'low_attendance': get_avg_imp(high_absences_ids)
        }

        # NEW CORRELATION: Psychological distress vs attendance rates
        distressed_ids = pss_qs.filter(
            Q(caregivers_distress='Yes') | Q(child_distress='Yes')
        ).values_list('registration_id', flat=True)

        not_distressed_ids = pss_qs.exclude(
            Q(caregivers_distress='Yes') | Q(child_distress='Yes')
        ).values_list('registration_id', flat=True)

        distress_impact_attendance = {
            'with_distress': get_attendance_rate(qs.filter(id__in=distressed_ids)),
            'without_distress': get_attendance_rate(qs.filter(id__in=not_distressed_ids))
        }

        # NEW CORRELATION: Cash support programs vs child labor
        cash_support_yes_ids = qs.exclude(Q(cash_support_programmes__isnull=True) | Q(cash_support_programmes=[])).values_list('id', flat=True)
        cash_support_no_ids = qs.filter(Q(cash_support_programmes__isnull=True) | Q(cash_support_programmes=[])).values_list('id', flat=True)

        def get_labor_rate(sub_qs):
            total = sub_qs.count() or 1
            labor = sub_qs.exclude(have_labour='No').count()
            return round((labor / total) * 100, 1)

        cash_impact_labor = {
            'with_cash_support': get_labor_rate(qs.filter(id__in=cash_support_yes_ids)),
            'without_cash_support': get_labor_rate(qs.filter(id__in=cash_support_no_ids))
        }

        # NEW INDICATOR: NFE to FE transition
        # Count referrals with 'Progress to FE'
        nfe_to_fe_count = Referral.objects.filter(
            registration__in=qs,
            recommended_learning_path='Progress to FE'
        ).count()

        # NEW INDICATOR: Monitor children grades and transition between NFE platforms
        # E.g. other pathways or transition rates between NFE platforms
        nfe_transitions = (
            Referral.objects.filter(registration__in=qs)
            .exclude(recommended_learning_path__in=[None, '', 'Progress to FE', 'Drop out'])
            .values(name=F('recommended_learning_path'))
            .annotate(y=Count('id'))
            .order_by('-y')
        )
        nfe_transitions = [
            {'name': item['name'] or 'Unknown', 'y': item['y']}
            for item in nfe_transitions
        ]

        # NEW INDICATOR: Dropout rate based on attendance (< 45 days)
        # 1. Total registrations that could drop out
        # 2. Number of children whose attended days < 45
        attended_counts = MSCCAttendanceChild.objects.filter(registration__in=qs, attended='Yes').values('registration').annotate(attended_days=Count('id'))

        # Determine dropout based on < 45 attended days
        dropped_out_registrations = [
            item['registration'] for item in attended_counts if item['attended_days'] < 45
        ]

        # Registrations with 0 attendance could also be dropouts depending on how you look at it,
        # but let's just count those with < 45 days or no attendance at all.
        registrations_with_attendance = MSCCAttendanceChild.objects.filter(registration__in=qs).values_list('registration', flat=True).distinct()
        no_attendance_registrations = qs.exclude(id__in=registrations_with_attendance).values_list('id', flat=True)

        total_dropouts = len(dropped_out_registrations) + len(no_attendance_registrations)

        avg_dropout_rate = 0
        if total_registrations > 0:
            avg_dropout_rate = (total_dropouts / total_registrations) * 100

        data = {
            'kpis': {
                'avg_attendance': round(avg_attendance_rate, 1),
                'labor_rate': round(labor_rate, 1),
                'avg_improvement': round(overall_improvement, 1),
                'protection_concerns': round(protection_rate, 1),
            },
            'socio_economic': {
                'labor_participation': labor_participation,
                'labor_income': labor_income_matrix,
                'cash_support': cash_support,
            },
            'wellbeing': {
                'living_arrangements': living_arrangements,
                'birth_registration': birth_reg,
                'vulnerabilities': vulnerabilities,
                'pss_indicators': pss_indicators,
            },
            'education': {
                'status': edu_status,
                'improvement': [
                    {'name': 'Arabic', 'value': round(avg_improvement['arabic'] or 0, 1)},
                    {'name': 'Math', 'value': round(avg_improvement['math'] or 0, 1)},
                    {'name': 'Language', 'value': round(avg_improvement['language'] or 0, 1)},
                ],
                'programme_improvements': programme_improvements,
            },
            'impact': {
                'barriers': barriers,
                'attendance_impact_improvement': attendance_impact_improvement,
                'labor_impact_attendance': labor_impact_attendance,
                'distress_impact_attendance': distress_impact_attendance,
                'cash_impact_labor': cash_impact_labor,
            },
            'transitions': {
                'nfe_to_fe': nfe_to_fe_count,
                'nfe_platforms': nfe_transitions,
                'dropout_rate': round(avg_dropout_rate, 1),
                'avg_nfe_grade': round(avg_nfe_grade, 1)
            }
        }

        return JsonResponse(data, safe=False)
