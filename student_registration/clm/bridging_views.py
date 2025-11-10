# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import json
from datetime import datetime

from django.views.generic import ListView, FormView, TemplateView, UpdateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest, HttpResponseForbidden
import io
import csv
import logging
logging.basicConfig(level=logging.ERROR)
import os
import uuid
from django.core.files.storage import default_storage
from storages.backends.azure_storage import AzureStorage
from django.core.files.base import ContentFile
from django.db import connection
import codecs
import logging
import traceback
import datetime
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.detail import SingleObjectMixin
from django.db.models import Q, Sum, Avg, F, Func, When
from django.urls import reverse
from django.shortcuts import render

from rest_framework import status
from rest_framework import viewsets, mixins, permissions
from braces.views import GroupRequiredMixin, SuperuserRequiredMixin

from django_filters.views import FilterView
from django_tables2 import MultiTableMixin, RequestConfig, SingleTableView
from django_tables2.export.views import ExportMixin

from student_registration.outreach.models import Child, OutreachChild
from student_registration.outreach.serializers import ChildSerializer
from student_registration.locations.models import Location
from .filters import (
    BridgingFilter
)
from .tables import (
    BridgingTable
)
from .models import (
    BLN,
    ABLN,
    RS,
    CBECE,
    Assessment,
    Outreach,
    Bridging,
    Inclusion
)
from student_registration.schools.models import (
    School,
    CLMRound,
)
from student_registration.backends.models import ExportHistory
from .bridging_forms import (
    BridgingAssessmentForm,
    BridgingMidAssessmentForm,
    BridgingFollowupForm,
    BridgingServiceForm,
    BridgingForm
)
from .serializers import (
    BLNSerializer,
    ABLNSerializer,
    CBECESerializer,
    BridgingSerializer
)
from .utils import is_allowed_create, is_allowed_edit,  get_outreach_child
from student_registration.users.templatetags.custom_tags import has_group
from student_registration.students.utils import generate_one_unique_id
from student_registration.students.models import Nationality


class CLMView(LoginRequiredMixin,
              GroupRequiredMixin,
              TemplateView):
    template_name = 'pages/home.old.html'

    group_required = [u"CLM"]


def assessment_form(instance_id, stage, enrollment_model, assessment_slug, callback=''):
    try:
        assessment = Assessment.objects.get(slug=assessment_slug)
        return '{form}?d[status]={status}&d[enrollment_id]={enrollment_id}&d[enrollment_model]={enrollment_model}&returnURL={callback}'.format(
            form=assessment.assessment_form,
            status=stage,
            enrollment_model=enrollment_model,
            enrollment_id=instance_id,
            callback=callback
        )
    except Assessment.DoesNotExist:
        return ''


@method_decorator(csrf_exempt, name='dispatch')
class AssessmentSubmission(SingleObjectMixin, View):
    model = RS
    slug_url_kwarg = 'status'

    def post(self, request, *args, **kwargs):

        if 'status' not in request.body and \
            'enrollment_id' not in request.body and \
            'enrollment_model' not in request.body:
            return HttpResponseBadRequest()

        payload = json.loads(request.body.decode('utf-8'))
        status = payload['status']
        enrollment_id = payload['enrollment_id']
        model = payload['enrollment_model']
        static_model_value = payload['static_model_value'] if 'static_model_value' in payload else ''

        if model == 'BLN' or 'BLN_ASSESSMENT/arabic' in payload:
            enrollment = BLN.objects.get(id=int(enrollment_id))
        elif model == 'ABLN' or 'ABLN_ASSESSMENT/arabic' in payload:
            enrollment = ABLN.objects.get(id=int(enrollment_id))
        elif model == 'CBECE':
            enrollment = CBECE.objects.get(id=int(enrollment_id))
        # elif model == 'RS':
        #     enrollment = RS.objects.get(id=int(enrollment_id))
        else:
            enrollment = CBECE.objects.get(id=int(enrollment_id))

        enrollment.status = status
        setattr(enrollment, status, payload)
        enrollment.calculate_score(status)
        enrollment.save()

        return HttpResponse()


class BridgingPage(LoginRequiredMixin,
                   TemplateView):
    template_name = 'clm/index.html'


class BridgingListView(LoginRequiredMixin,
                       GroupRequiredMixin,
                       FilterView,
                       ExportMixin,
                       SingleTableView,
                       RequestConfig):
    table_class = BridgingTable
    model = Bridging
    template_name = 'clm/bridging_list.html'
    group_required = [u"CLM_Bridging"]

    filterset_class = BridgingFilter

    def get_queryset(self):
        qs = (
            Bridging.objects.filter(round__current_year=True, deleted=False)
            .select_related(
                "student",
                "student__nationality",
                "round",
                "school",
                "governorate",
                "district",
                "owner",
                "modified_by",
            )
            .order_by(
                "student__first_name",
                "student__father_name",
                "student__last_name",
            )
        )

        if (
            not has_group(self.request.user, "CLM_BRIDGING_ALL")
            and not self.request.user.is_staff
        ):
            if self.request.user.partner:
                qs = qs.filter(partner_id=self.request.user.partner_id)
                if self.request.user.school:
                    qs = qs.filter(school_id=self.request.user.school_id)
            else:
                qs = qs.none()

        return qs


class BridgingAddView(LoginRequiredMixin,
                      GroupRequiredMixin,
                      FormView):
    template_name = 'clm/bridging_form.html'
    form_class = BridgingForm
    success_url = '/clm/bridging-list/'
    group_required = [u"CLM_Bridging"]

    def get_success_url(self):
        if self.request.POST.get('save_add_another', None):
            return '/clm/bridging-add/'
        if self.request.POST.get('save_and_continue', None):
            return '/clm/bridging-edit/' + str(self.request.session.get('instance_id')) + '/'
        if self.request.POST.get('save_and_pretest', None):
            return assessment_form(
                instance_id=self.request.session.get('instance_id'),
                stage='pre_test',
                enrollment_model='Bridging',
                assessment_slug='bridging_pre_test',
                callback=self.request.build_absolute_uri(reverse('clm:bridging_edit',
                                                                 kwargs={
                                                                     'pk': self.request.session.get('instance_id')})))
        return self.success_url

    def get_context_data(self, **kwargs):
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        kwargs['is_allowed_create'] = is_allowed_create('Bridging')
        return super(BridgingAddView, self).get_context_data(**kwargs)

    def get_initial(self):
        initial = super(BridgingAddView, self).get_initial()
        data = {
            'new_registry': self.request.GET.get('new_registry', ''),
            'student_outreached': self.request.GET.get('student_outreached', ''),
            'have_barcode': self.request.GET.get('have_barcode', '')
        }

        if self.request.GET.get('search_model') and self.request.GET.get('enrollment_id'):
            search_model = self.request.GET.get('search_model')
            if search_model == 'BLN':
                instance = BLN.objects.get(id=self.request.GET.get('enrollment_id'))
                data = BLNSerializer(instance).data
                data['student_nationality'] = data['student_nationality_id']
                data['learning_result'] = ''
            elif search_model == 'ABLN':
                instance = ABLN.objects.get(id=self.request.GET.get('enrollment_id'))
                data = ABLNSerializer(instance).data
                data['student_nationality'] = data['student_nationality_id']
                data['learning_result'] = ''
            elif search_model == 'CBECE':
                instance = CBECE.objects.get(id=self.request.GET.get('enrollment_id'))
                data = CBECESerializer(instance).data
                data['student_nationality'] = data['student_nationality_id']
                data['learning_result'] = ''
            else:
                instance = Bridging.objects.get(id=self.request.GET.get('enrollment_id'))
                data = BridgingSerializer(instance).data
                data['student_nationality'] = data['student_nationality_id']
                data['learning_result'] = ''
        else:
            if self.request.GET.get('enrollment_id'):
                instance = Bridging.objects.get(id=self.request.GET.get('enrollment_id'))
                data = BridgingSerializer(instance).data
                data['student_nationality'] = data['student_nationality_id']
                data['learning_result'] = ''

            if self.request.GET.get('child_id'):
                instance = Child.objects.get(id=int(self.request.GET.get('child_id')))
                data = ChildSerializer(instance).data

            if self.request.GET.get('outreach_id'):
                instance = Outreach.objects.get(id=self.request.GET.get('outreach_id'))
                data = BridgingSerializer(instance).data
                data['student_nationality'] = data['student_nationality_id']
                data['learning_result'] = ''

        if data:
            data['new_registry'] = self.request.GET.get('new_registry', 'yes')
            data['student_outreached'] = self.request.GET.get('student_outreached', '')
            data['have_barcode'] = self.request.GET.get('have_barcode', '')
        initial = data

        return initial

    def form_valid(self, form):
        form.save(request=self.request)
        return super(BridgingAddView, self).form_valid(form)

    def get_form(self, form_class=None):
        if self.request.method == "POST":
            return BridgingForm(self.request.POST, self.request.FILES, instance=None, request=self.request)
        else:
            return BridgingForm(None, instance=None, request=self.request, initial=self.get_initial())


class BridgingEditView(LoginRequiredMixin,
                       GroupRequiredMixin,
                       FormView):
    template_name = 'clm/bridging_form.html'
    form_class = BridgingForm
    success_url = '/clm/bridging-list/'
    group_required = [u"CLM_Bridging"]

    def get_success_url(self):
        if self.request.POST.get('save_add_another', None):
            return '/clm/bridging-add/'
        if self.request.POST.get('save_and_continue', None):
            return '/clm/bridging-edit/' + str(self.request.session.get('instance_id')) + '/'
        if self.request.POST.get('save_and_pretest', None):
            return assessment_form(
                instance_id=self.request.session.get('instance_id'),
                stage='pre_test',
                enrollment_model='Bridging',
                assessment_slug='bridging_pre_test',
                callback=self.request.build_absolute_uri(reverse('clm:bridging_edit',
                                                                 kwargs={
                                                                     'pk': self.request.session.get('instance_id')})))
        return self.success_url

    def get_context_data(self, **kwargs):
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        kwargs['is_allowed_edit'] = is_allowed_edit('Bridging')
        return super(BridgingEditView, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        instance = Bridging.objects.get(id=self.kwargs['pk'])
        if self.request.method == "POST":
            return BridgingForm(self.request.POST, self.request.FILES, instance=instance, request=self.request)
        else:
            data = BridgingSerializer(instance).data
            data['student_nationality'] = data['student_nationality_id']
            if 'pre_test' in data:
                p_test = data['pre_test']
                if p_test:

                    if "Bridging_ASSESSMENT/arabic_alphabet_knowledge" in p_test:
                        data['arabic_alphabet_knowledge'] = p_test["Bridging_ASSESSMENT/arabic_alphabet_knowledge"]
                    if "Bridging_ASSESSMENT/arabic_familiar_words" in p_test:
                        data['arabic_familiar_words'] = p_test["Bridging_ASSESSMENT/arabic_familiar_words"]
                    if "Bridging_ASSESSMENT/arabic_reading_comprehension" in p_test:
                        data['arabic_reading_comprehension'] = p_test["Bridging_ASSESSMENT/arabic_reading_comprehension"]

                    if "Bridging_ASSESSMENT/english_alphabet_knowledge" in p_test:
                        data['english_alphabet_knowledge'] = p_test["Bridging_ASSESSMENT/english_alphabet_knowledge"]
                    if "Bridging_ASSESSMENT/english_familiar_words" in p_test:
                        data['english_familiar_words'] = p_test["Bridging_ASSESSMENT/english_familiar_words"]
                    if "Bridging_ASSESSMENT/english_reading_comprehension" in p_test:
                        data['english_reading_comprehension'] = p_test["Bridging_ASSESSMENT/english_reading_comprehension"]


                    if "Bridging_ASSESSMENT/french_alphabet_knowledge" in p_test:
                        data['french_alphabet_knowledge'] = p_test["Bridging_ASSESSMENT/french_alphabet_knowledge"]
                    if "Bridging_ASSESSMENT/french_familiar_words" in p_test:
                        data['french_familiar_words'] = p_test["Bridging_ASSESSMENT/french_familiar_words"]
                    if "Bridging_ASSESSMENT/french_reading_comprehension" in p_test:
                        data['french_reading_comprehension'] = p_test["Bridging_ASSESSMENT/french_reading_comprehension"]

                    if "Bridging_ASSESSMENT/math" in p_test:
                        data['math'] = p_test["Bridging_ASSESSMENT/math"]

                    if "Bridging_ASSESSMENT/exam1" in p_test:
                        data['exam1'] = p_test["Bridging_ASSESSMENT/exam1"]

            return BridgingForm(data, instance=instance, request=self.request)

    def form_valid(self, form):
        instance = Bridging.objects.get(id=self.kwargs['pk'])
        form.save(request=self.request, instance=instance)
        return super(BridgingEditView, self).form_valid(form)


class ExportStorage(AzureStorage):
    """Azure storage backend dedicated for exported files."""
    location = "export"

@login_required(login_url='/users/login')
def bridging_export_data(request, **kwargs):
    try:
        cursor = connection.cursor()
        user = request.user
        partner_name = user.partner.name if user.partner else ''

        round_id = request.GET.get('round', None)

        vw_bridging_data = 'SELECT * FROM vw_bridging_data WHERE id > 0'
        query_params = []

        if round_id:
            vw_bridging_data += " AND round_id = %s"
            query_params.append(round_id)

        clm_bridging_all = has_group(request.user, 'CLM_BRIDGING_ALL')
        is_staff = request.user.is_staff

        if not clm_bridging_all and not is_staff and request.user.partner:
            school_id = 0
            partner_id = request.user.partner_id

            vw_bridging_data += " AND partner_id = %s"
            query_params.append(partner_id)

            if request.user.school:
                school_id = request.user.school.id
            if school_id > 0:
                vw_bridging_data += " AND school_id = %s"
                query_params.append(school_id)

        elif not clm_bridging_all and not is_staff and not request.user.partner:
            vw_bridging_data += " AND id = 0 "

        vw_bridging_data += " ORDER BY student_first_name, student_fathername, last_name "

        cursor.execute(vw_bridging_data, query_params)
        bridging_data = cursor.fetchall()

        logging.debug("Executing query: %s", vw_bridging_data)
        logging.debug("Query params: %s", str(query_params))

        headers = [col[0] for col in cursor.description]

        # Create CSV
        csv_output = io.StringIO()
        csv_writer = csv.writer(csv_output)

        # Add BOM for Arabic text
        csv_output.write(codecs.BOM_UTF8.decode('utf-8'))
        csv_writer.writerow(headers)  # Write headers

        for row in bridging_data:
            encoded_row = []
            for cell in row:
                if isinstance(cell, (str, bytes)):  # Handle string and bytes
                    encoded_row.append(cell.decode('utf-8') if isinstance(cell, bytes) else cell)
                elif isinstance(cell, (datetime.date, datetime.datetime)):  # Convert date/datetime objects to string
                    encoded_row.append(cell.strftime('%Y-%m-%d'))
                else:  # Convert other data types to string
                    encoded_row.append(str(cell))
            csv_writer.writerow(encoded_row)

        unique_id = str(uuid.uuid4())
        file_name = "bridging_{}.csv".format(unique_id)
        file_path = os.path.join('export', file_name)

        # Save file
        # default_storage.save(file_path, ContentFile(csv_output.getvalue().encode('utf-8')))

        storage = ExportStorage()
        storage.save(file_name, ContentFile(csv_output.getvalue().encode('utf-8')))
        file_url = reverse('mscc:export_download', args=[file_name])

        # Store export history
        ExportHistory.objects.create(
            export_type='Bridging List',
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


@login_required(login_url='/users/login')
def bridging_school_export(request, **kwargs):
    try:
        cursor = connection.cursor()
        user = request.user
        partner_name = user.partner.name if user.partner else ''

        school_id = int(kwargs.get('school_id'))

        clm_bridging_all = has_group(request.user, 'CLM_BRIDGING_ALL')
        is_staff = request.user.is_staff

        vw_bridging_data = 'SELECT * FROM vw_bridging_data WHERE id > 0'
        query_params = []

        if not clm_bridging_all and not is_staff and request.user.partner:
            partner_id = request.user.partner_id
            vw_bridging_data += " AND partner_id = %s"
            query_params.append(partner_id)

        elif not clm_bridging_all and not is_staff and not request.user.partner:
            vw_bridging_data += " AND id = 0"

        if school_id > 0:
            vw_bridging_data += " AND school_id = %s"
            query_params.append(school_id)

        vw_bridging_data += " ORDER BY student_first_name, student_fathername, last_name"

        cursor.execute(vw_bridging_data, query_params)
        bridging_data = cursor.fetchall()

        logging.debug("Executing query: %s", vw_bridging_data)
        logging.debug("Query params: %s", str(query_params))

        headers = [col[0] for col in cursor.description]

        csv_output = io.StringIO()
        csv_writer = csv.writer(csv_output)

        csv_output.write(codecs.BOM_UTF8.decode('utf-8'))
        csv_writer.writerow(headers)

        for row in bridging_data:
            encoded_row = []
            for cell in row:
                if isinstance(cell, (str, bytes)):  # Handle string and bytes
                    encoded_row.append(cell.decode('utf-8') if isinstance(cell, bytes) else cell)
                elif isinstance(cell, (datetime.date, datetime.datetime)):  # Convert date/datetime objects to string
                    encoded_row.append(cell.strftime('%Y-%m-%d'))
                else:  # Convert other data types to string
                    encoded_row.append(str(cell))
                # Local 2.7
                # if isinstance(cell, str) or isinstance(cell, unicode):  # Handle Unicode strings
                #     encoded_row.append(force_str(cell).encode('utf-8'))
                # elif isinstance(cell, (datetime.date, datetime.datetime)):  # Convert date/datetime objects to string
                #     encoded_row.append(cell.strftime('%Y-%m-%d'))
                # else:  # Convert other data types to string
                #     encoded_row.append(str(cell).encode('utf-8'))
            csv_writer.writerow(encoded_row)

        unique_id = str(uuid.uuid4())
        file_name = "bridging_school_{}.csv".format(unique_id)
        file_path = os.path.join('export', file_name)


        # default_storage.save(file_path, ContentFile(csv_output.getvalue().encode('utf-8')))

        storage = ExportStorage()
        storage.save(file_name, ContentFile(csv_output.getvalue().encode('utf-8')))
        file_url = reverse('mscc:export_download', args=[file_name])

        # Store export history
        ExportHistory.objects.create(
            export_type='School List - Bridging',
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



class BridgingAttendanceReport(LoginRequiredMixin,
                   TemplateView):

    template_name = 'clm/bridging_attendance_report.html'
    rounds = CLMRound.objects.filter(current_year=True).all()

    def get_context_data(self, **kwargs):
        context = super(BridgingAttendanceReport, self).get_context_data(**kwargs)
        context['rounds'] = CLMRound.objects.filter(current_year=True).all()
        return context



class BridgingPostAssessmentView(LoginRequiredMixin,
                            GroupRequiredMixin,
                            FormView):
    template_name = 'clm/bridging_post_assessment.html'
    form_class = BridgingAssessmentForm
    success_url = '/clm/bridging-list/'
    group_required = [u"CLM_Bridging"]

    def get_context_data(self, **kwargs):
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        return super(BridgingPostAssessmentView, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        form_class = self.get_form_class()
        instance = Bridging.objects.get(id=self.kwargs['pk'])

        if self.request.method == "POST":
            return form_class(self.request.POST, instance=instance, request=self.request)

        else:
            data = BridgingSerializer(instance).data
            if 'post_test' in data:
                p_test = data['post_test']
                if p_test:
                    if "Bridging_ASSESSMENT/arabic_alphabet_knowledge" in p_test:
                        data['arabic_alphabet_knowledge'] = p_test["Bridging_ASSESSMENT/arabic_alphabet_knowledge"]
                    if "Bridging_ASSESSMENT/arabic_familiar_words" in p_test:
                        data['arabic_familiar_words'] = p_test["Bridging_ASSESSMENT/arabic_familiar_words"]
                    if "Bridging_ASSESSMENT/arabic_reading_comprehension" in p_test:
                        data['arabic_reading_comprehension'] = p_test[
                            "Bridging_ASSESSMENT/arabic_reading_comprehension"]

                    if "Bridging_ASSESSMENT/english_alphabet_knowledge" in p_test:
                        data['english_alphabet_knowledge'] = p_test["Bridging_ASSESSMENT/english_alphabet_knowledge"]
                    if "Bridging_ASSESSMENT/english_familiar_words" in p_test:
                        data['english_familiar_words'] = p_test["Bridging_ASSESSMENT/english_familiar_words"]
                    if "Bridging_ASSESSMENT/english_reading_comprehension" in p_test:
                        data['english_reading_comprehension'] = p_test[
                            "Bridging_ASSESSMENT/english_reading_comprehension"]

                    if "Bridging_ASSESSMENT/french_alphabet_knowledge" in p_test:
                        data['french_alphabet_knowledge'] = p_test["Bridging_ASSESSMENT/french_alphabet_knowledge"]
                    if "Bridging_ASSESSMENT/french_familiar_words" in p_test:
                        data['french_familiar_words'] = p_test["Bridging_ASSESSMENT/french_familiar_words"]
                    if "Bridging_ASSESSMENT/french_reading_comprehension" in p_test:
                        data['french_reading_comprehension'] = p_test[
                            "Bridging_ASSESSMENT/french_reading_comprehension"]

                    if "Bridging_ASSESSMENT/math" in p_test:
                        data['math'] = p_test["Bridging_ASSESSMENT/math"]

                    if "Bridging_ASSESSMENT/exam3" in p_test:
                        data['exam3'] = p_test["Bridging_ASSESSMENT/exam3"]

                    # if "Bridging_ASSESSMENT/artistic" in p_test:
                    #     data['artistic'] = p_test["Bridging_ASSESSMENT/artistic"]
                    # if "Bridging_ASSESSMENT/social_emotional" in p_test:
                    #     data['social_emotional'] = p_test["Bridging_ASSESSMENT/social_emotional"]

            return form_class(data, instance=instance, request=self.request)

    def form_valid(self, form):
        instance = Bridging.objects.get(id=self.kwargs['pk'])
        form.save(request=self.request, instance=instance)
        return super(BridgingPostAssessmentView, self).form_valid(form)


class BridgingMidAssessmentView(LoginRequiredMixin,
                            GroupRequiredMixin,
                            FormView):
    template_name = 'clm/bridging_mid_assessment.html'
    form_class = BridgingMidAssessmentForm
    success_url = '/clm/bridging-list/'
    group_required = [u"CLM_Bridging"]

    def get_context_data(self, **kwargs):
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        kwargs['number'] = self.kwargs['number'] if 'number' in self.kwargs else None
        return super(BridgingMidAssessmentView, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        form_class = self.get_form_class()
        instance = Bridging.objects.get(id=self.kwargs['pk'])
        number = int(self.kwargs.get('number', 1))

        if self.request.method == "POST":
            return form_class(self.request.POST, instance=instance,number=number, request=self.request)
        else:
            data = BridgingSerializer(instance).data
            p_test = ''
            if number == 1 and 'mid_test1' in data:
                p_test = data['mid_test1']
            elif number == 2 and 'mid_test2' in data:
                p_test = data['mid_test2']

            if p_test:
                if "Bridging_ASSESSMENT/mid_test_done" in p_test:
                    data['mid_test_done'] = p_test["Bridging_ASSESSMENT/mid_test_done"]

                if "Bridging_ASSESSMENT/arabic_alphabet_knowledge" in p_test:
                    data['arabic_alphabet_knowledge'] = p_test["Bridging_ASSESSMENT/arabic_alphabet_knowledge"]
                if "Bridging_ASSESSMENT/arabic_familiar_words" in p_test:
                    data['arabic_familiar_words'] = p_test["Bridging_ASSESSMENT/arabic_familiar_words"]
                if "Bridging_ASSESSMENT/arabic_reading_comprehension" in p_test:
                    data['arabic_reading_comprehension'] = p_test[
                        "Bridging_ASSESSMENT/arabic_reading_comprehension"]

                if "Bridging_ASSESSMENT/english_alphabet_knowledge" in p_test:
                    data['english_alphabet_knowledge'] = p_test["Bridging_ASSESSMENT/english_alphabet_knowledge"]
                if "Bridging_ASSESSMENT/english_familiar_words" in p_test:
                    data['english_familiar_words'] = p_test["Bridging_ASSESSMENT/english_familiar_words"]
                if "Bridging_ASSESSMENT/english_reading_comprehension" in p_test:
                    data['english_reading_comprehension'] = p_test[
                        "Bridging_ASSESSMENT/english_reading_comprehension"]

                if "Bridging_ASSESSMENT/french_alphabet_knowledge" in p_test:
                    data['french_alphabet_knowledge'] = p_test["Bridging_ASSESSMENT/french_alphabet_knowledge"]
                if "Bridging_ASSESSMENT/french_familiar_words" in p_test:
                    data['french_familiar_words'] = p_test["Bridging_ASSESSMENT/french_familiar_words"]
                if "Bridging_ASSESSMENT/french_reading_comprehension" in p_test:
                    data['french_reading_comprehension'] = p_test[
                        "Bridging_ASSESSMENT/french_reading_comprehension"]

                if "Bridging_ASSESSMENT/math" in p_test:
                    data['math'] = p_test["Bridging_ASSESSMENT/math"]

                if "Bridging_ASSESSMENT/exam2" in p_test:
                    data['exam2'] = p_test["Bridging_ASSESSMENT/exam2"]

            return form_class(data, instance=instance, number=number, request=self.request)

    def form_valid(self, form):
        instance = Bridging.objects.get(id=self.kwargs['pk'])
        number = self.kwargs['number'] if 'number' in self.kwargs else None
        form.save(request=self.request, number=number, instance=instance)
        return super(BridgingMidAssessmentView, self).form_valid(form)


class BridgingFollowupView(LoginRequiredMixin,
                            GroupRequiredMixin,
                            FormView):
    template_name = 'clm/bridging_followup.html'
    form_class = BridgingFollowupForm
    success_url = '/clm/bridging-list/'
    group_required = [u"CLM_Bridging"]

    def get_context_data(self, **kwargs):
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        return super(BridgingFollowupView, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        form_class = self.get_form_class()
        instance = Bridging.objects.get(id=self.kwargs['pk'])

        if self.request.method == "POST":
            return form_class(self.request.POST, instance=instance, request=self.request)

        else:
            data = BridgingSerializer(instance).data
            return form_class(data, instance=instance, request=self.request)

    def form_valid(self, form):
        instance = Bridging.objects.get(id=self.kwargs['pk'])
        form.save(request=self.request, instance=instance)
        return super(BridgingFollowupView, self).form_valid(form)


class BridgingServiceView(LoginRequiredMixin,
                            GroupRequiredMixin,
                            FormView):
    template_name = 'clm/bridging_service.html'
    form_class = BridgingServiceForm
    success_url = '/clm/bridging-list/'
    group_required = [u"CLM_Bridging"]

    def get_context_data(self, **kwargs):
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        return super(BridgingServiceView, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        form_class = self.get_form_class()
        instance = Bridging.objects.get(id=self.kwargs['pk'])

        if self.request.method == "POST":
            return form_class(self.request.POST, instance=instance, request=self.request)

        else:
            data = BridgingSerializer(instance).data
            return form_class(data, instance=instance, request=self.request)

    def form_valid(self, form):
        instance = Bridging.objects.get(id=self.kwargs['pk'])
        form.save(request=self.request, instance=instance)
        return super(BridgingServiceView, self).form_valid(form)


####################### API VIEWS #############################


class BridgingViewSet(mixins.RetrieveModelMixin,
                 mixins.ListModelMixin,
                 mixins.CreateModelMixin,
                 mixins.UpdateModelMixin,
                 viewsets.GenericViewSet):
    model = Bridging
    queryset = Bridging.objects.all()
    serializer_class = BridgingSerializer
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

# def BridgingDeleteView(request, pk):
#     if request.user.is_authenticated:
#         try:
#             registration =  Bridging.objects.get(pk=pk)
#             registration.delete()
#             result = {"isSuccessful": True}
#         except Bridging.DoesNotExist:
#             result = {"isSuccessful": False}
#     else:
#         result = {"isSuccessful": False}
#     return JsonResponse(result)


def bridging_mark_delete_view(request, pk):
    if request.user.is_authenticated:
        try:
            registration = Bridging.objects.get(id=pk)
            registration.deleted = True
            registration.save()
            result = {"isSuccessful": True}
        except Bridging.DoesNotExist:
            result = {"isSuccessful": False}
    else:
        result = {"isSuccessful": False}
    return JsonResponse(result)


def load_districts(request):
    cities = []
    if request.GET.get('id_governorate'):
        id_governorate = request.GET.get('id_governorate')
        cities = Location.objects.filter(parent_id=id_governorate).order_by('name')
    return render(request, 'clm/city_dropdown_list_options.html', {'cities': cities})


def load_cadasters(request):
    cities = []
    if request.GET.get('id_district'):
        id_district = request.GET.get('id_district')
        cities = Location.objects.filter(parent_id=id_district).order_by('name')
    return render(request, 'clm/cadaster_dropdown_list_options.html', {'cities': cities})


def load_schools(request):
    schools = []
    if request.GET.get('id_governorate'):
        id_governorate = request.GET.get('id_governorate')
        schools = School.objects.filter(location_id=id_governorate).order_by('name')
    return render(request, 'clm/school_dropdown_list_options.html', {'schools': schools})


def search_clm_child(request):
    # from django.db.models.functions import Concat
    # from django.db.models import Value

    clm_type = request.GET.get('clm_type', 'BLN')
    term = request.GET.get('term', 0)
    terms = request.GET.get('term', 0)
    model = Bridging
    if clm_type == 'RS':
        model = RS
    elif clm_type == 'ABLN':
        model = ABLN
    elif clm_type == 'CBECE':
        model = CBECE
    elif clm_type == 'Outreach':
        model = Outreach
    elif clm_type == 'Bridging':
        model = Bridging
    elif clm_type == 'Inclusion':
        model = Inclusion

    search_model = clm_type

    qs = {}
    qs = clm_child_list(model, term, terms, search_model)

    if clm_type == 'Bridging' and len(qs) == 0:
        model = BLN
        search_model = 'BLN'
        qs = clm_child_list(model, term, terms, search_model)
        if len(list(qs)) == 0:
            model = ABLN
            search_model = 'ABLN'
            qs = clm_child_list(model, term, terms, search_model)
            if len(qs) == 0:
                model = CBECE
                search_model = 'CBECE'
                qs = clm_child_list(model, term, terms, search_model)

    return JsonResponse({'result': json.dumps(list(qs))})


def clm_child_list(model, term, terms, search_model):
    from django.db.models.functions import Concat
    from django.db.models import Value
    from django.db.models import CharField
    qs = {}
    if terms:
        if len(terms.split()) > 1:

            # .filter(partner=request.user.partner_id) \

            qs = model.objects.annotate(fullname=Concat('student__first_name', Value(' '),
                                                        'student__father_name', Value(' '),
                                                        'student__last_name')) \
                .filter(fullname__icontains=terms, deleted=False) \
                .values('id', 'student__first_name', 'student__father_name',
                        'student__last_name', 'student__mother_fullname',
                        'student__sex', 'student__birthday_day', 'student__birthday_month',
                        'student__birthday_year', 'round__name', 'internal_number').distinct().annotate(search_model=Value(search_model, output_field=CharField()))

        else:
            # for term in terms:
            # .filter(partner=request.user.partner_id)
            qs = model.objects.filter(deleted=False)\
                .filter(
                Q(student__first_name__contains=term) |
                Q(student__father_name__contains=term) |
                Q(student__last_name__contains=term) |
                Q(student__id_number__startswith=term) |
                Q(student__number__startswith=term) |
                Q(internal_number__startswith=term)
            ).values('id', 'student__first_name', 'student__father_name',
                     'student__last_name', 'student__mother_fullname',
                     'student__sex', 'student__birthday_day', 'student__birthday_month',
                     'student__birthday_year', 'round__name', 'internal_number').distinct().annotate(search_model=Value(search_model, output_field=CharField()))

    return qs


def search_kobo_outreach_child(request):
    from django.db.models.functions import Concat
    from django.db.models import Value

    term = request.GET.get('term', 0)
    terms = request.GET.get('term', 0)
    qs = {}
    if terms:
        if len(terms.split()) > 1:

            qs = OutreachChild.objects.annotate(fullname=Concat('first_name', Value(' '),
                                                        'outreach_caregiver__father_name', Value(' '),
                                                        'outreach_caregiver__last_name')) \
                .filter(fullname__icontains=terms) \
                .values('id', 'first_name', 'outreach_caregiver__father_name',
                        'outreach_caregiver__last_name', 'outreach_caregiver__mother_full_name',
                        'outreach_caregiver__caregiver_first_name','outreach_caregiver__caregiver_father_name',
                        'outreach_caregiver__caregiver_last_name',
                        'outreach_caregiver__caregiver_mother_name', 'outreach_caregiver__caregiver_dob',
                        'gender', 'birthday_day', 'birthday_month','birthday_year').distinct()

        else:
            qs = OutreachChild.objects \
                .filter(
                Q(first_name=term) |
                Q(outreach_caregiver__father_name=term) |
                Q(outreach_caregiver__last_name=term)
            ).values('id', 'first_name', 'outreach_caregiver__father_name',
                        'outreach_caregiver__last_name', 'outreach_caregiver__mother_full_name',
                        'outreach_caregiver__caregiver_first_name','outreach_caregiver__caregiver_father_name',
                        'outreach_caregiver__caregiver_last_name',
                        'outreach_caregiver__caregiver_mother_name', 'outreach_caregiver__caregiver_dob',
                        'gender', 'birthday_day', 'birthday_month','birthday_year').distinct()

    return JsonResponse({'result': json.dumps(list(qs))})


def outreach_child(request):
    outreach_id = request.GET.get('outreach_id')
    result = get_outreach_child(outreach_id)
    return JsonResponse(result)


def search_clm_duplicate_unicef_id(request):
    body_unicode = request.body.decode('utf-8')
    if body_unicode:
        body = json.loads(body_unicode)

        round_id = body.get('round_id')
        first_name = body.get('student_first_name')
        father_name = body.get('student_father_name')
        last_name = body.get('student_last_name')
        mother_fullname = body.get('student_mother_fullname')
        sex = body.get('student_sex')
        day = body.get('student_birthday_day')
        month = body.get('student_birthday_month')
        year = body.get('student_birthday_year')
        nationality_id = body.get('student_nationality')
        registration_id = body.get('registration_id')

        try:
            nationality = Nationality.objects.get(id=nationality_id).name_en
        except Nationality.DoesNotExist:
            nationality = ''

        birthdate = '{0}-{1}-{2}'.format(year, month, day)
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
            qs = Bridging.objects.filter(
                round_id=round_id,
                student__unicef_id=unicef_id,
                deleted=False
            )
            if registration_id:
                qs = qs.exclude(pk=registration_id)
            qs = qs.values('partner__name').first()

            if qs and 'partner__name' in qs:
                return JsonResponse({'result': qs['partner__name']})

    return JsonResponse({'result': ''})


import sys
if sys.version_info[0] >= 3:
    unicode = str

@login_required(login_url='/users/login')
def bridging_export_all(request, **kwargs):
    try:
        cursor = connection.cursor()
        query = 'SELECT * FROM vw_bridging_extract WHERE id > 0'
        cursor.execute(query)
        data = cursor.fetchall()
        headers = [col[0] for col in cursor.description]

        # Create CSV in memory
        csv_output = io.StringIO()
        csv_output.write(u'\ufeff')  # UTF-8 BOM for Arabic Excel support
        writer = csv.writer(csv_output)

        writer.writerow(headers)
        for row in data:
            encoded_row = []
            for cell in row:
                if isinstance(cell, (datetime.date, datetime.datetime)):
                    encoded_row.append(cell.strftime('%Y-%m-%d'))
                elif isinstance(cell, bytes):
                    # Decode byte strings safely
                    encoded_row.append(cell.decode('utf-8', errors='replace'))
                elif cell is None:
                    encoded_row.append('')
                else:
                    encoded_row.append(unicode(cell))  # Ensure proper Unicode text
            writer.writerow(encoded_row)

        # Prepare downloadable response
        file_name = "bridging_{}.csv".format(uuid.uuid4().hex)
        response = HttpResponse(csv_output.getvalue().encode('utf-8'), content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="{}"'.format(file_name)
        return response

    except Exception as e:
        logging.error("Export failed: %s", traceback.format_exc())
        return HttpResponse("An error occurred: " + str(e), status=500)


