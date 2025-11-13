# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from student_registration.users.templatetags.custom_tags import has_group
from rest_framework import viewsets, mixins, permissions

from django.views.generic import ListView, FormView, TemplateView, UpdateView, View
from django.contrib.auth.mixins import LoginRequiredMixin

from django.db.models import F, Q
from django.shortcuts import render
from braces.views import GroupRequiredMixin, SuperuserRequiredMixin

from django_filters.views import FilterView
from django_tables2 import MultiTableMixin, RequestConfig, SingleTableView
from django_tables2.export.views import ExportMixin

import io
import zipfile
import csv
import codecs
from django.utils.encoding import smart_str
from django.http import HttpResponse
from django.db import connection
import logging
import traceback

from .tables import (
    BootstrapTable,
    CenterTable
)
from .models import (
    Center,
    Location
)
from student_registration.schools.models import PartnerOrganization, School
from student_registration.backends.models import ExportHistory

from .forms import (
    CenterForm
)
from .serializers import (
    LocationSerializer
)
from .filters import (
    CenterFilter
)
from dal import autocomplete
import os
import uuid
from storages.backends.azure_storage import AzureStorage
from django.core.files.base import ContentFile
from django.urls import reverse
from django.contrib.auth.decorators import login_required


class LocationAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Location.objects.none()

        qs = Location.objects.all()
        if self.q:
            qs = Location.objects.filter(
                Q(name__istartswith=self.q) | Q(p_code__istartswith=self.q)
            )
        return qs


class ProfileView(LoginRequiredMixin,
                  TemplateView):
    template_name = 'location/center_profile.html'
    group_required = [u"MSCC"]

    def get_context_data(self, **kwargs):
        center_id = self.kwargs['pk']
        instance = Center.objects.get(id=center_id)
        current_tab = self.request.GET.get('current_tab', 'info')

        return {
            'instance': instance,
            'current_tab': current_tab
        }


class CenterFormView(LoginRequiredMixin,
                      GroupRequiredMixin,
                      FormView):
    template_name ='location/center_form.html'
    form_class = CenterForm
    success_url = ''
    group_required = [u"MSCC", u"MSCC_CENTER"]

    def get_success_url(self):
        pk = self.kwargs.get('pk')
        if pk is not None:
            return reverse('locations:center_profile', kwargs={'pk': pk})
        else:
            return reverse('mscc:list')

    def get_context_data(self, **kwargs):
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        return super(CenterFormView, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        pk = self.kwargs['pk'] if 'pk' in self.kwargs else None

        if self.request.method == "POST":
            return CenterForm(self.request.POST, pk=pk,  request=self.request)
        else:
            if pk:
                instance = Center.objects.get(id=pk)
                return CenterForm(instance=instance, pk=pk, request=self.request)
            return CenterForm( pk=pk, request=self.request)

    def form_valid(self, form):
        instance = self.kwargs['pk'] if 'pk' in self.kwargs else None
        form.save(request=self.request,  instance=instance)
        return super(CenterFormView, self).form_valid(form)


class CenterListView(LoginRequiredMixin,
                   GroupRequiredMixin,
                   FilterView,
                   ExportMixin,
                   SingleTableView,
                   RequestConfig):
    table_class = CenterTable
    model = Center
    template_name = 'location/center_list.html'
    table = BootstrapTable(Center.objects.all(), order_by='id')
    group_required = [u"MSCC", u"MSCC_PARTNER"]
    filterset_class = CenterFilter

    def get_queryset(self):
        user = self.request.user
        center_id = user.center_id
        partner_id = user.partner_id
        if has_group(user, 'MSCC_UNICEF'):
            return Center.objects.order_by('-id')
        elif has_group(user, 'MSCC_PARTNER') and partner_id:
            return Center.objects.filter(partner__id=partner_id).order_by('-id')
        elif has_group(user, 'MSCC_CENTER') and center_id:
            return Center.objects.filter(id=center_id).order_by('-id')

        return Center.objects.none()


def export_data(request):
    try:
        cursor = connection.cursor()
        user = request.user
        center_id = user.center_id
        partner_id = user.partner_id

        center_name = request.GET.get('center_name', '')
        center_type = request.GET.get('center_type', '')
        center_governorate = request.GET.get('center_governorate', '')


        vw_center_data_str = "SELECT * FROM vw_center_data WHERE center_id > 0"

        if has_group(user, 'MSCC_UNICEF'):
            vw_center_data_str += ""  # UNICEF has no extra filter
        elif has_group(user, 'MSCC_PARTNER') and partner_id:
            vw_center_data_str += " AND partner_id = {}".format(partner_id)
        elif has_group(user, 'MSCC_CENTER') and center_id:
            vw_center_data_str += " AND center_id = {}".format(center_id)
        else:
            vw_center_data_str += " AND center_id = 0"  # Dummy condition for safety

        if center_name:
            vw_center_data_str += " AND center_name LIKE '%{}%'".format(center_name)
        if center_type:
            vw_center_data_str += " AND center_type LIKE '%{}%'".format(center_type)
        if center_governorate:
            vw_center_data_str += " AND governorate_id = {}".format(center_governorate)

        cursor.execute(vw_center_data_str)
        data = cursor.fetchall()
        headers = [col[0] for col in cursor.description]

        zip_output = io.BytesIO()
        with zipfile.ZipFile(zip_output, 'w') as zf:
            # Create CSV for center data
            csv_center_output = io.StringIO()
            csv_writer = csv.writer(csv_center_output)

            csv_center_output.write(codecs.BOM_UTF8.decode('utf-8'))
            csv_writer.writerow(headers)

            for row in data:
                csv_writer.writerow([smart_str(cell) for cell in row])

            zf.writestr('center_data.csv', csv_center_output.getvalue())

            center_ids = [row[0] for row in data]
            if center_ids:
                staff_data_str = "SELECT * FROM vw_center_program_staff WHERE center_id IN ({})".format(
                    ','.join(map(str, center_ids)))
                cursor.execute(staff_data_str)
                staff_data = cursor.fetchall()
                staff_headers = [col[0] for col in cursor.description]

                # Create CSV for staff data
                csv_staff_output = io.StringIO()
                csv_writer = csv.writer(csv_staff_output)

                # Add BOM for staff data CSV
                csv_staff_output.write(codecs.BOM_UTF8.decode('utf-8'))
                csv_writer.writerow(staff_headers)

                for row in staff_data:
                    csv_writer.writerow([smart_str(cell) for cell in row])

                zf.writestr('staff_data.csv', csv_staff_output.getvalue())

        response = HttpResponse(zip_output.getvalue(), content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename=exported_data.zip'

        return response

    except Exception as e:
        logging.error("An error occurred during the export process:")
        logging.error(traceback.format_exc())

        return HttpResponse("An error occurred: " + str(e), status=500)


class ExportStorage(AzureStorage):
    """Azure storage backend dedicated for exported files."""
    location = "export"


@login_required(login_url='/users/login')
def export_center_background(request):
    try:
        cursor = connection.cursor()
        user = request.user
        center_id = user.center_id
        partner_id = 0
        partner_name = ''
        if user.partner_id:
            partner_id = user.partner_id
            partner_name = user.partner.name

        center_name = request.GET.get('center_name', '')
        center_type = request.GET.get('center_type', '')
        center_governorate = request.GET.get('center_governorate', '')


        vw_center_data_str = "SELECT * FROM vw_center_data WHERE center_id > 0"

        if has_group(user, 'MSCC_UNICEF'):
            vw_center_data_str += ""  # UNICEF has no extra filter
        elif has_group(user, 'MSCC_PARTNER') and partner_id:
            vw_center_data_str += " AND partner_id = {}".format(partner_id)
        elif has_group(user, 'MSCC_CENTER') and center_id:
            vw_center_data_str += " AND center_id = {}".format(center_id)
        else:
            vw_center_data_str += " AND center_id = 0"  # Dummy condition for safety

        if center_name:
            vw_center_data_str += " AND center_name LIKE '%{}%'".format(center_name)
        if center_type:
            vw_center_data_str += " AND center_type LIKE '%{}%'".format(center_type)
        if center_governorate:
            vw_center_data_str += " AND governorate_id = {}".format(center_governorate)

        cursor.execute(vw_center_data_str)
        data = cursor.fetchall()
        headers = [col[0] for col in cursor.description]

        zip_output = io.BytesIO()
        with zipfile.ZipFile(zip_output, 'w') as zf:
            # Create CSV for center data
            csv_center_output = io.StringIO()
            csv_writer = csv.writer(csv_center_output)

            csv_center_output.write(codecs.BOM_UTF8.decode('utf-8'))
            csv_writer.writerow(headers)

            for row in data:
                csv_writer.writerow([smart_str(cell) for cell in row])

            zf.writestr('center_data.csv', csv_center_output.getvalue())

            center_ids = [row[0] for row in data]
            if center_ids:
                staff_data_str = "SELECT * FROM vw_center_program_staff WHERE center_id IN ({})".format(
                    ','.join(map(str, center_ids)))
                cursor.execute(staff_data_str)
                staff_data = cursor.fetchall()
                staff_headers = [col[0] for col in cursor.description]

                # Create CSV for staff data
                csv_staff_output = io.StringIO()
                csv_writer = csv.writer(csv_staff_output)

                # Add BOM for staff data CSV
                csv_staff_output.write(codecs.BOM_UTF8.decode('utf-8'))
                csv_writer.writerow(staff_headers)

                for row in staff_data:
                    csv_writer.writerow([smart_str(cell) for cell in row])

                zf.writestr('staff_data.csv', csv_staff_output.getvalue())

        unique_id = str(uuid.uuid4())
        file_name = "out_file_{}.zip".format(unique_id)
        file_path = os.path.join('export', file_name)

        # default_storage.save(file_path, ContentFile(zip_output.getvalue()))
        storage = ExportStorage()
        storage.save(file_name, ContentFile(zip_output.getvalue()))

        file_url = reverse('mscc:export_download', args=[file_name])

        ExportHistory.objects.create(
            export_type='Center List',
            created_by=user,
            file_url=file_url,
            status='done',
            partner_name=partner_name
        )
        return HttpResponse(file_name)

    except Exception as e:
        logging.error("An error occurred during the export process:")
        logging.error(traceback.format_exc())

        return HttpResponse("An error occurred: " + str(e), status=500)


###################### API VIEWS #############################

class LocationViewSet(mixins.RetrieveModelMixin,
                      mixins.ListModelMixin,
                      mixins.CreateModelMixin,
                      mixins.UpdateModelMixin,
                      viewsets.GenericViewSet):

    model = Location
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        if self.request.method in ["PATCH", "POST", "PUT"]:
            return self.queryset


def load_districts(request):
    id_governorate = request.GET.get('id_governorate')
    cities = Location.objects.filter(parent_id=id_governorate).order_by('name')
    return render(request, 'clm/city_dropdown_list_options.html', {'cities': cities})


def load_cadasters(request):
    id_district = request.GET.get('id_district')
    cities = Location.objects.filter(parent_id=id_district).order_by('name')
    return render(request, 'clm/cadaster_dropdown_list_options.html', {'cities': cities})


def load_schools(request):
    id_governorate = request.GET.get('id_governorate')
    schools = School.objects.filter(location_id=id_governorate).order_by('name')
    return render(request, 'clm/school_dropdown_list_options.html', {'schools': schools})
