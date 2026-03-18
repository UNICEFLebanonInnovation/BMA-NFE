from django.db.models import F
from django.db import connection
from openpyxl import Workbook
import csv
import io
import uuid
import codecs
import zipfile
import logging
from django.core.files.base import ContentFile
from django.urls import reverse
from django.utils.encoding import smart_str
from student_registration.backends.utils import ExportStorage, send_push_to_web
from student_registration.backends.models import ExportHistory

logger = logging.getLogger(__name__)

def _generate_advanced_export(export_id, base_model_name, fields=None, filters=None, file_format='csv'):
    from student_registration.mscc.models import Registration, Teacher
    from student_registration.locations.models import Center

    try:
        export = ExportHistory.objects.get(id=export_id)
    except ExportHistory.DoesNotExist:
        logger.error("ExportHistory with id %s does not exist", export_id)
        return

    try:
        user = export.created_by

        # 1. Determine base model
        if base_model_name == 'registration':
            qs = Registration.objects.filter(deleted=False)
            if not (user.is_superuser or user.is_staff):
                if user.partner_id:
                    qs = qs.filter(partner_id=user.partner_id)
                if user.center_id:
                    qs = qs.filter(center_id=user.center_id)
        elif base_model_name == 'center':
            qs = Center.objects.all()
            if not (user.is_superuser or user.is_staff):
                if user.partner_id:
                    qs = qs.filter(partner_id=user.partner_id)
                if user.center_id:
                    qs = qs.filter(id=user.center_id)
        elif base_model_name == 'teacher':
            qs = Teacher.objects.all()
            if not (user.is_superuser or user.is_staff):
                if user.partner_id:
                    qs = qs.filter(center__partner_id=user.partner_id)
                if user.center_id:
                    qs = qs.filter(center_id=user.center_id)
        else:
            raise ValueError(f"Unknown base model: {base_model_name}")

        # Apply user filters if any (basic implementation, extend as needed)
        if filters:
            if 'center_id' in filters and filters['center_id']:
                if base_model_name == 'center':
                    qs = qs.filter(id__in=filters['center_id'])
                else:
                    qs = qs.filter(center_id__in=filters['center_id'])
            if 'partner_id' in filters and filters['partner_id']:
                if base_model_name == 'center':
                    qs = qs.filter(partner_id__in=filters['partner_id'])
                elif base_model_name == 'teacher':
                    qs = qs.filter(center__partner_id__in=filters['partner_id'])
                else:
                    qs = qs.filter(partner_id__in=filters['partner_id'])
            if 'round_id' in filters and filters['round_id']:
                if base_model_name == 'registration':
                    qs = qs.filter(round_id__in=filters['round_id'])
                elif base_model_name == 'teacher':
                    qs = qs.filter(round_id__in=filters['round_id'])

        # 2. Select Fields
        if not fields:
            # Default fields if none selected
            fields = ['id']

        data = qs.values_list(*fields)
        headers = fields

        # 3. Write to file
        file_ext = file_format or 'csv'
        if file_ext == 'xlsx':
            wb = Workbook()
            ws = wb.active
            ws.append(headers)
            for row in data:
                ws.append([smart_str(cell) if cell is not None else '' for cell in row])
            file_content_io = io.BytesIO()
            wb.save(file_content_io)
            data_bytes = file_content_io.getvalue()
        else:
            csv_output = io.StringIO()
            csv_writer = csv.writer(csv_output)
            csv_output.write(codecs.BOM_UTF8.decode('utf-8'))
            csv_writer.writerow(headers)
            for row in data:
                encoded_row = [smart_str(cell) if cell is not None else '' for cell in row]
                csv_writer.writerow(encoded_row)
            data_bytes = csv_output.getvalue().encode('utf-8')
            file_ext = 'csv'

        zip_output = io.BytesIO()
        with zipfile.ZipFile(zip_output, 'w') as zf:
            zf.writestr(f'advanced_export_{base_model_name}.{file_ext}', data_bytes)

        unique_id = str(uuid.uuid4())
        file_name = f'advanced_export_{unique_id}.zip'
        storage = ExportStorage()
        storage.save(file_name, ContentFile(zip_output.getvalue()))
        file_url = reverse('backends:export_download', args=[file_name]) # Or mscc:export_download depending on existing setup
        export.file_url = file_url
        export.status = 'done'
        export.save()
        if user:
            send_push_to_web(
                user,
                "Advanced Export Ready",
                f"Your advanced export for {base_model_name} is ready.",
                data={"type": "advanced_export_ready", "url": file_url},
            )

    except Exception as e:
        logger.exception('Error generating advanced export: %s', e)
        if export:
            export.status = 'failed'
            export.save()
            if export.created_by:
                send_push_to_web(
                    export.created_by,
                    "Advanced Export Failed",
                    str(e),
                    data={"type": "advanced_export_failed", "reason": str(e)},
                )
