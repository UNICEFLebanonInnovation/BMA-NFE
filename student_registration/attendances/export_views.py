from __future__ import absolute_import, unicode_literals

import csv
import io
import codecs
import datetime
import logging
import traceback
import uuid

from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.db import connection
from django.http import HttpResponse
from django.urls import reverse
from storages.backends.azure_storage import AzureStorage

from student_registration.backends.models import ExportHistory
from student_registration.users.templatetags.custom_tags import has_group


class ExportStorage(AzureStorage):
    location = "export"


def _normalize_filter(value):
    if value in [None, '', 'none', 'None']:
        return ''
    return value


def _encode_csv_cell(cell):
    if isinstance(cell, bytes):
        return cell.decode('utf-8')
    if isinstance(cell, (datetime.date, datetime.datetime)):
        return cell.strftime('%Y-%m-%d')
    if cell is None:
        return ''
    return str(cell)


def _build_csv_content(headers, rows):
    csv_output = io.StringIO()
    csv_writer = csv.writer(csv_output)

    # BOM for Excel / Arabic support
    csv_output.write(codecs.BOM_UTF8.decode('utf-8'))
    csv_writer.writerow(headers)

    for row in rows:
        csv_writer.writerow([_encode_csv_cell(cell) for cell in row])

    return csv_output.getvalue().encode('utf-8')


def _save_export_file(file_name, content_bytes):
    storage = ExportStorage()
    storage.save(file_name, ContentFile(content_bytes))


@login_required(login_url='/users/login')
def mscc_attendance_export(request, **kwargs):
    try:
        user = request.user
        partner_name = user.partner.name if user.partner else ''

        month = kwargs.get('month')
        year = kwargs.get('year')
        education_program = _normalize_filter(kwargs.get('education_program', ''))
        class_section = _normalize_filter(kwargs.get('class_section', ''))
        partner_id = _normalize_filter(kwargs.get('partner', ''))
        center_id = _normalize_filter(kwargs.get('center', ''))

        cursor = connection.cursor()
        query_params = []
        vw_data_str = "SELECT * FROM vw_mscc_attendance_data WHERE attendance_id > 0"

        if year:
            vw_data_str += " AND EXTRACT(YEAR FROM attendance_date) = %s"
            query_params.append(year)

        if month:
            vw_data_str += " AND EXTRACT(MONTH FROM attendance_date) = %s"
            query_params.append(month)

        if education_program:
            vw_data_str += " AND education_program = %s"
            query_params.append(education_program)

        if class_section:
            vw_data_str += " AND class_section = %s"
            query_params.append(class_section)

        if partner_id:
            vw_data_str += " AND partner_id = %s"
            query_params.append(partner_id)

        if center_id:
            vw_data_str += " AND center_id = %s"
            query_params.append(center_id)

        if not has_group(request.user, 'MSCC_UNICEF'):
            if getattr(request.user, 'partner_id', None):
                vw_data_str += " AND partner_id = %s"
                query_params.append(request.user.partner_id)

            if getattr(request.user, 'center_id', None):
                vw_data_str += " AND center_id = %s"
                query_params.append(request.user.center_id)

        vw_data_str += " ORDER BY attendance_date"

        logging.debug("Executing query: %s", vw_data_str)
        logging.debug("Query params: %s", query_params)

        cursor.execute(vw_data_str, query_params)
        att_data = cursor.fetchall()
        headers = [col[0] for col in cursor.description]

        file_content = _build_csv_content(headers, att_data)
        unique_id = str(uuid.uuid4())
        file_name = "mscc_raw_attendance_data_{}.csv".format(unique_id)

        _save_export_file(file_name, file_content)
        file_url = reverse('mscc:export_download', args=[file_name])

        ExportHistory.objects.create(
            export_type='NFR Sector Raw Attendance',
            created_by=user,
            file_url=file_url,
            status='done',
            partner_name=partner_name
        )

        return HttpResponse(file_name)

    except Exception as e:
        logging.error("An error occurred during mscc_attendance_export")
        logging.error(traceback.format_exc())
        return HttpResponse("An error occurred: " + str(e), status=500)


@login_required(login_url='/users/login')
def mscc_total_attendance_export(request, **kwargs):
    try:
        user = request.user
        partner_name = user.partner.name if user.partner else ''

        month = kwargs.get('month')
        year = kwargs.get('year')
        education_program = _normalize_filter(kwargs.get('education_program', ''))
        class_section = _normalize_filter(kwargs.get('class_section', ''))
        partner_id = _normalize_filter(kwargs.get('partner', ''))
        center_id = _normalize_filter(kwargs.get('center', ''))

        cursor = connection.cursor()
        query_params = []
        vw_data_str = "SELECT * FROM vw_mscc_attendance_absence WHERE center_id > 0"

        if year:
            vw_data_str += " AND attendance_year = %s"
            query_params.append(year)

        if month:
            vw_data_str += " AND attendance_month = %s"
            query_params.append(month)

        if education_program:
            vw_data_str += " AND education_program = %s"
            query_params.append(education_program)

        if class_section:
            vw_data_str += " AND class_section = %s"
            query_params.append(class_section)

        if partner_id:
            vw_data_str += " AND partner_id = %s"
            query_params.append(partner_id)

        if center_id:
            vw_data_str += " AND center_id = %s"
            query_params.append(center_id)

        if not has_group(request.user, 'MSCC_UNICEF'):
            if getattr(request.user, 'partner_id', None):
                vw_data_str += " AND partner_id = %s"
                query_params.append(request.user.partner_id)

            if getattr(request.user, 'center_id', None):
                vw_data_str += " AND center_id = %s"
                query_params.append(request.user.center_id)

        vw_data_str += " ORDER BY child_id"

        logging.debug("Executing query: %s", vw_data_str)
        logging.debug("Query params: %s", query_params)

        cursor.execute(vw_data_str, query_params)
        att_data = cursor.fetchall()
        headers = [col[0] for col in cursor.description]

        file_content = _build_csv_content(headers, att_data)
        unique_id = str(uuid.uuid4())
        file_name = "mscc_total_attendance_data_{}.csv".format(unique_id)

        _save_export_file(file_name, file_content)
        file_url = reverse('mscc:export_download', args=[file_name])

        ExportHistory.objects.create(
            export_type='NFR Sector Total Attendance',
            created_by=user,
            file_url=file_url,
            status='done',
            partner_name=partner_name
        )

        return HttpResponse(file_name)

    except Exception as e:
        logging.error("An error occurred during mscc_total_attendance_export")
        logging.error(traceback.format_exc())
        return HttpResponse("An error occurred: " + str(e), status=500)