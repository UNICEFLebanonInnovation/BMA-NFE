"""Background tasks responsible for exporting MSCC data.

The exporters in this module run inside Celery workers but rely on a
thread pool so that multiple export jobs can run concurrently without
blocking other tasks. Because Django database connections are not
thread-safe across threads, helpers such as :func:`_run_with_new_db_connection`
ensure each worker thread opens and closes its own connection safely.

Exports pull from database views (``vw_mscc_child`` and ``vw_mscc_data``),
write either CSV or XLSX payloads, wrap them in a ZIP archive, store the
result via :class:`~student_registration.backends.utils.ExportStorage`, and
notify the requesting user through Firebase push notifications.
"""

from __future__ import absolute_import
import io
import uuid
import csv
import zipfile
import logging
import codecs
import threading

from concurrent.futures import ThreadPoolExecutor

from django.conf import settings
from django.utils.encoding import smart_str
from django.db import connection, close_old_connections
from django.core.files.base import ContentFile
from openpyxl import Workbook

from student_registration.backends.models import ExportHistory
from student_registration.backends.utils import ExportStorage, send_push_to_web
from student_registration.users.templatetags.custom_tags import has_group
from django.urls import reverse

logger = logging.getLogger(__name__)

_executor_lock = threading.Lock()
_export_executor = None


def _get_executor():
    """Return a lazily instantiated thread pool for export jobs.

    A shared ``ThreadPoolExecutor`` keeps export throughput high while
    preventing the creation of unbounded worker threads. The pool size is
    configurable through the ``MSCC_EXPORT_MAX_WORKERS`` Django setting
    (default: ``4``).
    """
    global _export_executor
    if _export_executor is None:
        with _executor_lock:
            if _export_executor is None:
                max_workers = getattr(settings, 'MSCC_EXPORT_MAX_WORKERS', 4)
                _export_executor = ThreadPoolExecutor(
                    max_workers=max_workers,
                    thread_name_prefix='mscc-export'
                )
    return _export_executor


def _run_with_new_db_connection(fn, *args, **kwargs):
    """Execute *fn* ensuring Django DB connections are thread-safe."""
    close_old_connections()
    try:
        return fn(*args, **kwargs)
    finally:
        close_old_connections()


def _generate_mscc_export(export_id, fields=None, file_format='csv'):
    """Produce a full MSCC export and attach it to ``ExportHistory``.

    Parameters mirror those accepted by the synchronous export view: a
    required ``export_id`` that references :class:`ExportHistory`, an optional
    list of ``fields`` to include, and a ``file_format`` indicating CSV or
    XLSX output. The export is wrapped in a ZIP archive before being saved
    and the requesting user (if any) receives a push notification with a
    download link.
    """
    try:
        export = ExportHistory.objects.get(id=export_id)
    except ExportHistory.DoesNotExist:
        logger.error("ExportHistory with id %s does not exist", export_id)
        return
    try:
        user = export.created_by
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM vw_mscc_child")
        mscc_data = cursor.fetchall()
        headers = [col[0] for col in cursor.description]

        selected_headers = headers
        if fields:
            selected_headers = [h for h in headers if h in fields]

        file_ext = file_format or 'csv'

        if file_ext == 'xlsx':
            wb = Workbook()
            ws = wb.active
            ws.append(selected_headers)
            header_indices = [headers.index(h) for h in selected_headers]
            for row in mscc_data:
                ws.append([smart_str(row[i]) for i in header_indices])
            file_content_io = io.BytesIO()
            wb.save(file_content_io)
            data_bytes = file_content_io.getvalue()
        else:
            csv_output = io.StringIO()
            csv_writer = csv.writer(csv_output)
            csv_output.write(codecs.BOM_UTF8.decode('utf-8'))
            csv_writer.writerow(selected_headers)
            header_indices = [headers.index(h) for h in selected_headers]
            for row in mscc_data:
                csv_writer.writerow([smart_str(row[i]) for i in header_indices])
            data_bytes = csv_output.getvalue().encode('utf-8')
            file_ext = 'csv'

        zip_output = io.BytesIO()
        with zipfile.ZipFile(zip_output, 'w') as zf:
            zf.writestr(f'mscc_data.{file_ext}', data_bytes)

        unique_id = str(uuid.uuid4())
        file_name = f'mscc_export_{unique_id}.zip'
        storage = ExportStorage()
        storage.save(file_name, ContentFile(zip_output.getvalue()))
        file_url = reverse('mscc:export_download', args=[file_name])
        export.file_url = file_url
        export.status = 'done'
        export.save()
        if user:
            send_push_to_web(
                user,
                "NFR Sector export ready",
                "Your export is ready to download.",
                data={"type": "mscc_export_ready", "url": file_url},
            )
    except Exception as e:
        logger.exception('Error generating export: %s', e)
        if export:
            export.status = 'failed'
            export.save()
            if export.created_by:
                # Notify the user that the export failed and include the reason
                send_push_to_web(
                    export.created_by,
                    "NFR Sector export failed",
                    str(e),
                    data={"type": "mscc_export_failed", "reason": str(e)},
                )

def _generate_filtered_mscc_export(export_id, filters=None, file_format='csv'):
    """Generate an MSCC export with optional filtering and notify the user.

    Parameters are used to filter the SQL query. Results are written as a
    single CSV/XLSX file stored in Azure storage. A push notification
    containing the download URL is sent to the requesting user when done.
    """
    export = ExportHistory.objects.get(id=export_id)
    try:
        user = export.created_by
        cursor = connection.cursor()
        center_id = user.center_id
        partner_id = user.partner_id or 0
        filters = filters or {}
        round_id = filters.get('round')

        query_params = []

        if not round_id or round_id == 'All':
            vw_mscc_data_str = "SELECT * FROM vw_mscc_data WHERE id > 0"
        elif round_id == "no_round":
            vw_mscc_data_str = "SELECT * FROM vw_mscc_data_no_round WHERE id > 0"
        else:
            vw_mscc_data_str = "SELECT * FROM vw_mscc_data WHERE round_id = %s"
            query_params.append(round_id)

        if has_group(user, 'MSCC_UNICEF'):
            vw_mscc_data_str += " AND id > 0"
        elif has_group(user, 'MSCC_PARTNER') and partner_id:
            vw_mscc_data_str += " AND partner_id = %s"
            query_params.append(partner_id)
        elif has_group(user, 'MSCC_CENTER') and center_id:
            vw_mscc_data_str += " AND center_id = %s"
            query_params.append(center_id)
        else:
            vw_mscc_data_str += " AND id = 0"

        # Apply additional filters from the UI
        if filters.get('child__first_name'):
            vw_mscc_data_str += " AND child_first_name ILIKE %s"
            query_params.append(f"%{filters['child__first_name']}%")
        if filters.get('child__last_name'):
            vw_mscc_data_str += " AND child_last_name ILIKE %s"
            query_params.append(f"%{filters['child__last_name']}%")
        if filters.get('child__father_name'):
            vw_mscc_data_str += " AND child_father_name ILIKE %s"
            query_params.append(f"%{filters['child__father_name']}%")
        if filters.get('child__mother_fullname'):
            vw_mscc_data_str += " AND child_mother_fullname = %s"
            query_params.append(filters['child__mother_fullname'])
        if filters.get('child__nationality'):
            vw_mscc_data_str += " AND child_nationality_id = %s"
            query_params.append(filters['child__nationality'])
        if filters.get('child__gender'):
            vw_mscc_data_str += " AND child_gender = %s"
            query_params.append(filters['child__gender'])
        if filters.get('child__unicef_id'):
            vw_mscc_data_str += " AND unicef_id LIKE %s"
            query_params.append(f"%{filters['child__unicef_id']}%")
        if filters.get('programme_type'):
            vw_mscc_data_str += " AND education_program = %s"
            query_params.append(filters['programme_type'])

        cursor.execute(vw_mscc_data_str, query_params)
        mscc_data = cursor.fetchall()
        headers = [col[0] for col in cursor.description]

        file_ext = file_format or 'csv'
        if file_ext == 'xlsx':
            wb = Workbook()
            ws = wb.active
            ws.append(headers)
            for row in mscc_data:
                ws.append([smart_str(cell) for cell in row])
            file_content_io = io.BytesIO()
            wb.save(file_content_io)
            data_bytes = file_content_io.getvalue()
        else:
            csv_mscc_output = io.StringIO()
            csv_writer = csv.writer(csv_mscc_output)
            csv_mscc_output.write(codecs.BOM_UTF8.decode('utf-8'))
            csv_writer.writerow(headers)
            for row in mscc_data:
                encoded_row = [smart_str(cell) for cell in row]
                csv_writer.writerow(encoded_row)
            data_bytes = csv_mscc_output.getvalue().encode('utf-8')
            file_ext = 'csv'

        unique_id = str(uuid.uuid4())
        file_name = f"out_file_{unique_id}.{file_ext}"
        storage = ExportStorage()
        storage.save(file_name, ContentFile(data_bytes))
        file_url = reverse('mscc:export_download', args=[file_name])
        export.file_url = file_url
        export.status = 'done'
        export.save()
        if user:
            send_push_to_web(
                user,
                "NFR Sector export ready",
                "Your export is ready to download.",
                data={"type": "mscc_export_ready", "url": file_url},
            )
    except Exception as e:  # pragma: no cover - logged for debugging purposes
        logger.exception('Error generating export: %s', e)
        export.status = 'failed'
        export.save()
        if export.created_by:
            send_push_to_web(
                export.created_by,
                "NFR Sector export failed",
                str(e),
                data={"type": "mscc_export_failed", "reason": str(e)},
            )


def queue_mscc_export(export_id, fields=None, file_format='csv'):
    """Run the MSCC export in a background thread."""
    executor = _get_executor()
    return executor.submit(
        _run_with_new_db_connection,
        _generate_mscc_export,
        export_id,
        fields,
        file_format,
    )


def queue_filtered_mscc_export(export_id, filters=None, file_format='csv'):
    """Run the filtered MSCC export in a background thread."""
    executor = _get_executor()
    return executor.submit(
        _run_with_new_db_connection,
        _generate_filtered_mscc_export,
        export_id,
        filters,
        file_format,
    )
