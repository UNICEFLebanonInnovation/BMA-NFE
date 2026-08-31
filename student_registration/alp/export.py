import codecs

from django_tables2.export.views import ExportMixin


class ALPExportMixin(ExportMixin):
    """Make ALP CSV exports open with Arabic text intact in spreadsheet apps."""

    def create_export(self, export_format):
        response = super().create_export(export_format)

        if export_format.lower() == 'csv':
            content = response.content
            if not content.startswith(codecs.BOM_UTF8):
                response.content = codecs.BOM_UTF8 + content
            response['Content-Type'] = 'text/csv; charset=utf-8'

        return response
