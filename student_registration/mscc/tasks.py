"""Generate scoped MSCC registration exports in background worker threads."""

from __future__ import absolute_import

import io
import logging
import threading
import uuid
import zipfile
from concurrent.futures import ThreadPoolExecutor

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.core.files.base import ContentFile
from django.db import close_old_connections
from django.urls import reverse

from student_registration.backends.models import ExportHistory
from student_registration.backends.utils import ExportStorage, send_push_to_web

from .document_exports import build_children_csv, build_children_workbook
from .export_access import filter_registrations, scoped_registrations, user_can_export

logger = logging.getLogger(__name__)

_executor_lock = threading.Lock()
_export_executor = None


def _get_executor():
    """Return a shared, bounded thread pool for export jobs."""
    global _export_executor
    if _export_executor is None:
        with _executor_lock:
            if _export_executor is None:
                _export_executor = ThreadPoolExecutor(
                    max_workers=getattr(settings, 'MSCC_EXPORT_MAX_WORKERS', 4),
                    thread_name_prefix='mscc-export',
                )
    return _export_executor


def _run_with_new_db_connection(fn, *args, **kwargs):
    """Open and close database connections within the worker's thread."""
    close_old_connections()
    try:
        return fn(*args, **kwargs)
    finally:
        close_old_connections()


def _notify_export(export, succeeded):
    """Notification failures must not alter an already generated export."""
    if not export.created_by:
        return
    try:
        if succeeded:
            send_push_to_web(
                export.created_by,
                'NFR Sector export ready',
                'Your export is ready to download.',
                data={'type': 'mscc_export_ready', 'url': export.file_url},
            )
        else:
            send_push_to_web(
                export.created_by,
                'NFR Sector export failed',
                'The export could not be generated. Please try again.',
                data={'type': 'mscc_export_failed'},
            )
    except Exception:
        logger.exception('Could not notify the requester for export %s', export.pk)


def _generate_export(export_id, fields=None, filters=None, file_format='csv', wrap_zip=False):
    """Generate documents from the current authorised child records.

    Both export entry points use the same ORM snapshot and photo loader, so
    new address/programme fields and the child's stored photograph are kept
    together without relying on externally maintained database views.
    """
    try:
        export = ExportHistory.objects.select_related('created_by').get(pk=export_id)
    except ExportHistory.DoesNotExist:
        logger.error('ExportHistory with id %s does not exist', export_id)
        return

    try:
        if not user_can_export(export.created_by):
            raise PermissionDenied('An assigned MSCC export role is required.')
        if file_format not in ('csv', 'xlsx'):
            raise ValueError('Unsupported export format.')

        registrations = filter_registrations(
            scoped_registrations(export.created_by), filters
        )
        if file_format == 'xlsx':
            payload = build_children_workbook(registrations, fields=fields)
        else:
            payload = build_children_csv(registrations, fields=fields)

        unique_id = str(uuid.uuid4())
        if wrap_zip:
            output = io.BytesIO()
            with zipfile.ZipFile(output, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
                archive.writestr('mscc_data.%s' % file_format, payload)
            payload = output.getvalue()
            file_name = 'mscc_export_%s.zip' % unique_id
        else:
            file_name = 'out_file_%s.%s' % (unique_id, file_format)

        file_name = ExportStorage().save(file_name, ContentFile(payload))
        export.file_url = reverse('mscc:export_download', args=[file_name])
        export.status = 'done'
        export.save(update_fields=['file_url', 'status', 'modified'])
    except Exception:
        logger.exception('Error generating MSCC export %s', export_id)
        export.status = 'failed'
        export.file_url = ''
        export.save(update_fields=['status', 'file_url', 'modified'])
        _notify_export(export, succeeded=False)
        return

    _notify_export(export, succeeded=True)


def _generate_mscc_export(export_id, fields=None, file_format='csv'):
    """Generate the full authorised registration export in its legacy ZIP wrapper."""
    return _generate_export(
        export_id, fields=fields, file_format=file_format, wrap_zip=True
    )


def _generate_filtered_mscc_export(export_id, filters=None, file_format='csv'):
    """Generate a workbook or CSV for all authorised records or a filtered list."""
    return _generate_export(export_id, filters=filters, file_format=file_format)


def queue_mscc_export(export_id, fields=None, file_format='csv'):
    """Run the MSCC export in a background thread."""
    return _get_executor().submit(
        _run_with_new_db_connection,
        _generate_mscc_export,
        export_id,
        fields,
        file_format,
    )


def queue_filtered_mscc_export(export_id, filters=None, file_format='csv'):
    """Run the filtered MSCC export in a background thread."""
    return _get_executor().submit(
        _run_with_new_db_connection,
        _generate_filtered_mscc_export,
        export_id,
        filters,
        file_format,
    )
