"""Generate MSCC documents from the same registered child and photograph.

Each workbook row represents one registration. Child and registration IDs
remain in every export so a child registered in several rounds can still be
identified without losing the programme or round of a particular record.
"""

import csv
import datetime
import io
import json
import logging
import re
from collections import Counter, OrderedDict
from dataclasses import dataclass

import xlsxwriter
from django.db import models
from PIL import Image, ImageOps

from student_registration.child.models import Child
from student_registration.mscc.models import Registration


logger = logging.getLogger(__name__)

PHOTO_INCLUDED = 'Photograph included'
PHOTO_MISSING = 'No photograph uploaded'
PHOTO_UNAVAILABLE = 'Photograph unavailable'

# XML 1.0 cannot represent these characters in XLSX or DOCX documents.
_INVALID_XML_CHARACTERS = re.compile(
    '[\x00-\x08\x0b\x0c\x0e-\x1f\ud800-\udfff\ufffe\uffff]'
)


@dataclass(frozen=True)
class ExportColumn:
    key: str
    label: str
    aliases: tuple = ()


@dataclass(frozen=True)
class RegistrationSnapshot:
    values: OrderedDict
    photo_data: bytes | None
    photo_status: str


_REQUIRED_COLUMNS = (
    ExportColumn('registration_id', 'Registration ID', ('id',)),
    ExportColumn('child_id', 'Child ID'),
    ExportColumn('photograph', 'Photograph', ('photo',)),
    ExportColumn('photograph_status', 'Photograph status', ('photo_status',)),
)


def _text(value):
    """Return literal, XML-safe text without inventing values for empty data."""
    if value is None:
        return ''
    if isinstance(value, bool):
        value = 'Yes' if value else 'No'
    elif isinstance(value, (datetime.datetime, datetime.date, datetime.time)):
        value = value.isoformat()
    elif isinstance(value, (dict, list, tuple)):
        value = json.dumps(value, ensure_ascii=False, sort_keys=True, default=str)
    return _INVALID_XML_CHARACTERS.sub('', str(value))


def _model_columns(model, prefix, excluded):
    fields = [field for field in model._meta.concrete_fields if field.name not in excluded]
    labels = [_text(field.verbose_name) for field in fields]
    duplicates = Counter(labels)
    columns = []
    for field, label in zip(fields, labels):
        # Several legacy fields have the same verbose name. Keep each value
        # identifiable while still displaying the familiar registration label.
        if duplicates[label] > 1:
            label = '{} ({})'.format(label, field.name)
        columns.append(ExportColumn(
            '{}__{}'.format(prefix, field.name), label,
            (field.name, '{}.{}'.format(prefix, field.name)),
        ))
        if isinstance(field, models.ForeignKey):
            columns.append(ExportColumn(
                '{}__{}_id'.format(prefix, field.name), '{} ID'.format(label),
                ('{}_id'.format(field.name), '{}.{}_id'.format(prefix, field.name)),
            ))
    return columns


def export_columns(fields=None):
    """Return stable, unambiguous headers, retaining identity and photo columns.

    Optional selectors accept field names, ``child__field`` /
    ``registration__field`` names, or the visible header. Unknown legacy SQL
    selectors do not accidentally fall back to exporting every stored field.
    """
    child_columns = _model_columns(Child, 'child', {'id'})
    registration_columns = _model_columns(Registration, 'registration', {'id', 'child'})
    used_labels = {column.label for column in _REQUIRED_COLUMNS + tuple(child_columns)}
    registration_columns = [
        ExportColumn(
            column.key,
            'Registration {}'.format(column.label) if column.label in used_labels else column.label,
            column.aliases,
        ) for column in registration_columns
    ]
    optional = [
        ExportColumn('child_full_name', 'Child full name', ('child_fullname',)),
        ExportColumn('date_of_birth', 'Date of birth', ('birthday',)),
    ] + child_columns + registration_columns
    if fields:
        if isinstance(fields, str):
            fields = [fields]
        selected = set(fields)
        optional = [column for column in optional if selected.intersection(
            (column.key, column.label) + column.aliases
        )]
    return list(_REQUIRED_COLUMNS) + optional


def _field_values(instance, model, prefix, excluded):
    values = OrderedDict()
    for field in model._meta.concrete_fields:
        if field.name in excluded:
            continue
        key = '{}__{}'.format(prefix, field.name)
        value = getattr(instance, field.name, None) if instance is not None else None
        if isinstance(field, models.ForeignKey):
            values[key] = _text(value)
            values['{}__{}_id'.format(prefix, field.name)] = _text(
                getattr(instance, field.attname, None) if instance is not None else None
            )
        elif isinstance(field, models.FileField):
            # Storage names are permanent references; signed storage URLs are
            # neither necessary nor appropriate to retain in a document.
            values[key] = _text(value.name if value else None)
        elif field.choices and instance is not None:
            values[key] = _text(getattr(instance, 'get_{}_display'.format(field.name))())
        elif hasattr(field, 'base_field') and field.base_field.choices and value is not None:
            labels = dict(field.base_field.flatchoices)
            values[key] = '; '.join(_text(labels.get(item, item)) for item in value)
        else:
            values[key] = _text(value)
    return values


def _date_of_birth(child):
    """Use the saved birthday components, including incomplete legacy dates."""
    if child is None:
        return ''
    year = _text(child.birthday_year)
    month = _text(child.birthday_month)
    day = _text(child.birthday_day)
    try:
        return datetime.date(int(year), int(month), int(day)).isoformat()
    except (ValueError, TypeError):
        parts = []
        if year and year != '0':
            parts.append(year)
        if month and month != '0':
            parts.append('month: {}'.format(month))
        if day and day != '0':
            parts.append('day: {}'.format(day))
        return ', '.join(parts)


def _load_photo(child):
    """Read the child's own stored image through local or remote storage."""
    if child is None or not child.photo:
        return None, PHOTO_MISSING
    try:
        with child.photo.open('rb') as source:
            data = source.read()
    except Exception:
        # A storage backend may raise its own network or missing-object errors,
        # rather than OSError. Report this child's image as unavailable without
        # leaking storage URLs or replacing it with another child's picture.
        logger.warning('Photograph unavailable for child ID %s', child.pk)
        return None, PHOTO_UNAVAILABLE
    try:
        with Image.open(io.BytesIO(data)) as image:
            # Apply camera orientation before removing metadata and using
            # the same PNG in both types of document.
            image = ImageOps.exif_transpose(image).convert('RGB')
            image.thumbnail((384, 480), Image.Resampling.LANCZOS)
            destination = io.BytesIO()
            image.save(destination, format='PNG')
            return destination.getvalue(), PHOTO_INCLUDED
    except (OSError, ValueError, SyntaxError, Image.DecompressionBombError):
        logger.warning('Photograph unavailable for child ID %s', child.pk)
        return None, PHOTO_UNAVAILABLE


def registration_snapshot(registration):
    """Read one registration's values and its linked child's photograph once."""
    child = registration.child
    photo_data, photo_status = _load_photo(child)
    values = OrderedDict((
        ('registration_id', _text(registration.pk)),
        ('child_id', _text(registration.child_id)),
        ('photograph', _text(child.photo.name if child and child.photo else None)),
        ('photograph_status', photo_status),
        ('child_full_name', ' '.join(
            _text(getattr(child, name, None)).strip()
            for name in ('first_name', 'father_name', 'last_name')
            if child is not None and getattr(child, name, None)
        ) if child is not None else 'Child record unavailable'),
        ('date_of_birth', _date_of_birth(child)),
    ))
    values.update(_field_values(child, Child, 'child', {'id'}))
    values.update(_field_values(registration, Registration, 'registration', {'id', 'child'}))
    return RegistrationSnapshot(values, photo_data, photo_status)


def build_children_workbook(registrations, fields=None):
    """Return an XLSX with each photograph contained in its registration row."""
    columns = export_columns(fields)
    destination = io.BytesIO()
    workbook = xlsxwriter.Workbook(destination, {
        'in_memory': True,
        'strings_to_formulas': False,
        'strings_to_urls': False,
    })
    sheet = workbook.add_worksheet('Registered children')
    heading = workbook.add_format({
        'bold': True, 'bg_color': '#164A68', 'font_color': '#FFFFFF',
        'text_wrap': True, 'valign': 'vcenter', 'border': 1,
    })
    body = workbook.add_format({'text_wrap': True, 'valign': 'top'})
    sheet.freeze_panes(1, 2)
    sheet.set_row(0, 42)
    sheet.set_column(0, len(columns) - 1, 24)
    sheet.set_column(0, 1, 15)
    sheet.set_column(2, 2, 20)
    for index, column in enumerate(columns):
        sheet.write_string(0, index, column.label, heading)

    last_row = 0
    for row, registration in enumerate(registrations, start=1):
        if row >= 1048576:
            raise ValueError('The export exceeds the Excel worksheet row limit.')
        last_row = row
        snapshot = registration_snapshot(registration)
        sheet.set_row(row, 108)
        for index, column in enumerate(columns):
            value = snapshot.values.get(column.key, '')
            if column.key == 'photograph':
                value = '' if snapshot.photo_data else snapshot.photo_status
            if len(value) > 32767:
                raise ValueError('A registered value exceeds the Excel cell text limit.')
            # write_string keeps names beginning with '=' or URLs as literal
            # registered values instead of executing formulas or hyperlinks.
            sheet.write_string(row, index, value, body)
        if snapshot.photo_data:
            image_data = io.BytesIO(snapshot.photo_data)
            with Image.open(image_data) as image:
                scale = min(112 / image.width, 136 / image.height, 1)
            sheet.insert_image(row, 2, 'child_{}_registration_{}.png'.format(
                registration.child_id, registration.pk,
            ), {
                'image_data': image_data,
                'x_offset': 4, 'y_offset': 4,
                'x_scale': scale, 'y_scale': scale,
                # Move and size the image with its own row when users sort or
                # filter the workbook. Its full anchor stays inside the row.
                'positioning': 1,
            })
    sheet.autofilter(0, 0, last_row, len(columns) - 1)
    workbook.close()
    return destination.getvalue()


def build_children_csv(registrations, fields=None):
    """Return the same registered values as UTF-8 CSV, with photo references."""
    columns = export_columns(fields)
    destination = io.StringIO(newline='')
    destination.write('\ufeff')
    writer = csv.writer(destination)
    writer.writerow([column.label for column in columns])
    for registration in registrations:
        snapshot = registration_snapshot(registration)
        # CSV has no literal cell type. Escape spreadsheet expression prefixes
        # so opening the file in Excel cannot turn saved text into formulas.
        values = [snapshot.values.get(column.key, '') for column in columns]
        writer.writerow([
            "'" + value if value.lstrip().startswith(('=', '+', '-', '@')) else value
            for value in values
        ])
    return destination.getvalue().encode('utf-8')


def build_examination_card(registration):
    """Return an editable Word card populated from one current snapshot."""
    from docx import Document
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.shared import Inches, Mm, Pt

    snapshot = registration_snapshot(registration)
    values = snapshot.values
    document = Document()
    section = document.sections[0]
    section.page_width = Mm(210)
    section.page_height = Mm(297)
    section.top_margin = Inches(0.55)
    section.bottom_margin = Inches(0.55)
    section.left_margin = Inches(0.65)
    section.right_margin = Inches(0.65)
    document.styles['Normal'].font.name = 'Arial'
    document.styles['Normal'].font.size = Pt(10)
    document.styles['Normal'].paragraph_format.space_after = Pt(4)

    title = document.add_heading('Examination Card', 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    subtitle = document.add_paragraph('MSCC / Makani')
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    header = document.add_table(rows=1, cols=2)
    header.autofit = False
    header.columns[0].width = Inches(4.9)
    header.columns[1].width = Inches(1.3)
    identity = header.cell(0, 0)
    identity.paragraphs[0].add_run(values['child_full_name'] or 'Child name not recorded').bold = True
    identity.add_paragraph('Child ID: {}'.format(values['child_id']))
    identity.add_paragraph('Registration ID: {}'.format(values['registration_id']))
    identity.add_paragraph('UNIQUE ID: {}'.format(values['child__unicef_id'] or 'Not recorded'))
    photo = header.cell(0, 1).paragraphs[0]
    photo.alignment = WD_ALIGN_PARAGRAPH.CENTER
    if snapshot.photo_data:
        with Image.open(io.BytesIO(snapshot.photo_data)) as image:
            scale = min(1.15 / image.width, 1.4 / image.height)
            width, height = image.width * scale, image.height * scale
        photo.add_run().add_picture(
            io.BytesIO(snapshot.photo_data), width=Inches(width), height=Inches(height),
        )
    else:
        photo.add_run(snapshot.photo_status)

    document.add_paragraph()
    details = (
        ('First name', 'child__first_name'),
        ('Father name', 'child__father_name'),
        ('Last name', 'child__last_name'),
        ('Mother full name', 'child__mother_fullname'),
        ('Date of birth', 'date_of_birth'),
        ('Gender', 'child__gender'),
        ('Nationality', 'child__nationality'),
        ('Other nationality', 'child__nationality_other'),
        ('Disability / special need', 'child__disability'),
        ('Other disability', 'child__disability_other'),
        ('Formal Education unique student ID', 'child__fe_unique_id'),
        ('Type of NFE Programme', 'registration__nfe_programme'),
        ('Caregiver phone number', 'child__first_phone_number'),
        ('Governorate (محافظة)', 'child__governorate'),
        ('District/Caza (قضاء)', 'child__district'),
        ('Municipality (بلدية)', 'child__municipality'),
        ('Village (قرية)', 'child__village'),
        ('Street (شارع)', 'child__street'),
        ('Building/Camp (مبنى/مخيم)', 'child__building_camp'),
        ('Cadaster (منطقة عقارية)', 'child__cadaster'),
        ('Center', 'registration__center'),
        ('Partner', 'registration__partner'),
        ('Round', 'registration__round'),
        ('Registration date', 'registration__registration_date'),
    )
    table = document.add_table(rows=0, cols=2)
    table.style = 'Table Grid'
    for label, key in details:
        if key in ('child__nationality_other', 'child__disability_other') and not values.get(key):
            continue
        cells = table.add_row().cells
        cells[0].text = label
        value = values.get(key)
        if not value and key in ('child__governorate', 'child__district', 'child__cadaster'):
            value = values.get('{}_legacy'.format(key))
        cells[1].text = value or 'Not recorded'
        cells[0].paragraphs[0].runs[0].bold = True
    if values.get('child__address') and not any(values.get('child__{}'.format(field)) for field in (
        'governorate', 'district', 'municipality', 'village', 'street', 'building_camp', 'cadaster'
    )):
        cells = table.add_row().cells
        cells[0].text = 'Residential address (legacy)'
        cells[1].text = values['child__address']
        cells[0].paragraphs[0].runs[0].bold = True
    document.core_properties.title = 'Examination card - Child {}'.format(values['child_id'])
    document.core_properties.subject = 'MSCC / Makani registration {}'.format(values['registration_id'])
    destination = io.BytesIO()
    document.save(destination)
    return destination.getvalue()
