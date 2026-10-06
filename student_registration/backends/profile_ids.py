# -*- coding: utf-8 -*-
"""Child profile ID cards shared by the Dirasa (Bridging) and Makani (MSCC) programmes.

A programme describes how to turn its registrations into card data and photos
(:class:`ProfileIdProgramme`). This module renders the cards to a PDF, one A5
landscape page per child, runs the bulk generation in the background and
notifies the requesting user with a web push when the file is ready.
"""
from __future__ import absolute_import, unicode_literals

import io
import logging
import uuid
from pathlib import Path

from arabic_reshaper import ArabicReshaper
from arabic_reshaper.ligatures import LIGATURES
from bidi import get_display
from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.http import HttpResponse
from django.urls import reverse
from reportlab.lib.pagesizes import A5, landscape
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from .models import ExportHistory
from .utils import ExportStorage, download_file, is_valid_filename, send_push_to_web

logger = logging.getLogger(__name__)

SUBTITLE = 'الامتحان الاستثنائي لطلاب التعليم الغير نظامي'

PROFILE_IDS_READY = 'profile_ids_ready'
PROFILE_IDS_FAILED = 'profile_ids_failed'

# DejaVu Sans ships Arabic presentation forms, so one font covers both scripts.
FONTS_DIR = Path(__file__).resolve().parents[1] / 'static' / 'fonts'
FONT_REGULAR = 'DejaVuSans'
FONT_BOLD = 'DejaVuSans-Bold'

PAGE_SIZE = landscape(A5)
MARGIN = 8 * mm
PHOTO_WIDTH = 45 * mm
PHOTO_HEIGHT = 40 * mm
PHOTO_COLOR = (0x44 / 255.0, 0x72 / 255.0, 0xC4 / 255.0)
LINE_SPACING = 1.75


# --------------------------------------------------------------------------- card data helpers

def first_non_empty(*values):
    for value in values:
        if value:
            return value
    return ''


def date_part(value):
    """Birthday day/month/year are stored as strings and default to 0 when unknown."""
    value = str(value or '').strip()
    return '' if value == '0' else value


def short_birthday(day, month, year):
    """``d/m/yy`` as printed on the card, or '' when any part is unknown."""
    day, month, year = date_part(day), date_part(month), date_part(year)
    if day and month and year:
        return '{}/{}/{}'.format(day, month, year[-2:])
    return ''


def person_full_name(person):
    if not person:
        return ''
    return ' '.join(part for part in (person.first_name, person.father_name, person.last_name) if part)


def lookup_name(obj):
    """English name of a lookup row (nationality, location, disability), falling back to the Arabic one."""
    if not obj:
        return ''
    return first_non_empty(getattr(obj, 'name_en', ''), getattr(obj, 'name', ''))


def read_image_field(field, owner=''):
    """Raw bytes of an uploaded image, or None when missing or unreadable."""
    if not field:
        return None
    try:
        with field.open('rb') as fh:
            return fh.read()
    except Exception:
        logger.warning('Could not read profile picture of %s', owner, exc_info=True)
        return None


def card_lines(card):
    """The text lines of a card, top to bottom, as (text, font, size)."""
    return [
        (card['round'], FONT_BOLD, 16),
        (SUBTITLE, FONT_BOLD, 9),
        ('ID: {}'.format(card['id']), FONT_BOLD, 13),
        ('NGO: {}'.format(card['ngo']), FONT_BOLD, 13),
        ('الاسم الثلاثي: {}'.format(card['full_name']), FONT_BOLD, 13),
        ('Date of Birth: {}'.format(card['birthday']), FONT_BOLD, 13),
        ('Place of Birth: {}'.format(card['place_of_birth']), FONT_BOLD, 13),
        ('Nationality: {}'.format(card['nationality']), FONT_BOLD, 13),
        ('Governorate: {}'.format(card['governorate']), FONT_BOLD, 13),
        ('Physical difficulties: {}'.format(card['physical_difficulties']), FONT_BOLD, 13),
    ]


# --------------------------------------------------------------------------- PDF rendering

_reshaper = None


def register_fonts():
    if FONT_BOLD not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(TTFont(FONT_REGULAR, str(FONTS_DIR / 'DejaVuSans.ttf')))
        pdfmetrics.registerFont(TTFont(FONT_BOLD, str(FONTS_DIR / 'DejaVuSans-Bold.ttf')))


def _reshaper_for_font():
    """A reshaper that only emits ligature glyphs the bundled font can draw.

    arabic_reshaper enables ligatures such as "الله" (U+FDF2) by default, which
    DejaVu Sans lacks and would print as a missing-glyph box.
    """
    global _reshaper
    if _reshaper is None:
        register_fonts()
        glyphs = pdfmetrics.getFont(FONT_BOLD).face.charToGlyph
        configuration = {'delete_harakat': False, 'support_ligatures': True}
        for name, (_, forms) in LIGATURES:
            configuration[name] = all(ord(char) in glyphs for form in forms for char in form)
        _reshaper = ArabicReshaper(configuration=configuration)
    return _reshaper


def shape_text(text):
    """Join Arabic letters and reorder right-to-left runs so the PDF shows them correctly.

    Latin-only text comes back unchanged.
    """
    text = '' if text is None else str(text)
    return get_display(_reshaper_for_font().reshape(text))


def _fit_font_size(pdf, text, font, size, max_width, minimum=7):
    while size > minimum and pdf.stringWidth(text, font, size) > max_width:
        size -= 1
    return size


def draw_card(pdf, card, photo_bytes=None):
    """Draw one profile ID card on the current page of ``pdf``."""
    width, height = PAGE_SIZE

    pdf.setLineWidth(0.8)
    pdf.setStrokeColorRGB(0, 0, 0)
    pdf.rect(MARGIN / 2, MARGIN / 2, width - MARGIN, height - MARGIN)

    photo_x = MARGIN
    photo_y = height - MARGIN - PHOTO_HEIGHT
    pdf.setFillColorRGB(*PHOTO_COLOR)
    pdf.rect(photo_x, photo_y, PHOTO_WIDTH, PHOTO_HEIGHT, stroke=0, fill=1)
    drawn = False
    if photo_bytes:
        try:
            pdf.drawImage(ImageReader(io.BytesIO(photo_bytes)), photo_x, photo_y, PHOTO_WIDTH, PHOTO_HEIGHT,
                          preserveAspectRatio=True, anchor='c', mask='auto')
            drawn = True
        except Exception:
            logger.warning('Could not draw profile picture for card %s', card['id'], exc_info=True)
    if not drawn:
        pdf.setFillColorRGB(1, 1, 1)
        pdf.setFont(FONT_REGULAR, 9)
        pdf.drawCentredString(photo_x + PHOTO_WIDTH / 2, photo_y + PHOTO_HEIGHT / 2 - 3, 'picture')

    pdf.setFillColorRGB(0, 0, 0)
    centre = width / 2
    cursor = height - MARGIN - 20 * mm
    for text, font, size in card_lines(card):
        shaped = shape_text(text)
        # Lines level with the photo must not run into it.
        beside_photo = cursor > photo_y
        max_width = (width - 2 * (PHOTO_WIDTH + MARGIN + 4 * mm)) if beside_photo else (width - 2 * MARGIN)
        size = _fit_font_size(pdf, shaped, font, size, max_width)
        pdf.setFont(font, size)
        pdf.drawCentredString(centre, cursor, shaped)
        cursor -= max(size, 12) * LINE_SPACING


def build_cards_pdf(cards, title='Profile IDs'):
    """One PDF from ``(card, photo_bytes)`` pairs, each card on its own A5 landscape page."""
    register_fonts()
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=PAGE_SIZE)
    pdf.setTitle(title)
    pdf.setAuthor('BMA')

    count = 0
    for card, photo_bytes in cards:
        draw_card(pdf, card, photo_bytes)
        pdf.showPage()
        count += 1

    if count == 0:
        pdf.setFont(FONT_REGULAR, 12)
        pdf.drawCentredString(PAGE_SIZE[0] / 2, PAGE_SIZE[1] / 2, 'No children to generate.')
        pdf.showPage()

    pdf.save()
    return buffer.getvalue()


# --------------------------------------------------------------------------- programmes and the background job

class ProfileIdProgramme(object):
    """How one programme feeds the shared profile ID generator.

    ``registrations(ids)`` returns the registrations to print in display order,
    ``card(registration)`` the card data and ``photo(registration)`` the photo
    bytes (or None).
    """

    def __init__(self, label, export_type, download_url_name, registrations, card, photo):
        self.label = label
        self.export_type = export_type
        self.download_url_name = download_url_name
        self.registrations = registrations
        self.card = card
        self.photo = photo

    def build_pdf(self, registrations):
        return build_cards_pdf(((self.card(registration), self.photo(registration)) for registration in registrations),
                               title='{} profile IDs'.format(self.label))


def generate_profile_ids(export_id, programme, registration_ids):
    """Build the profile IDs PDF, store it, record it on the export and notify its owner.

    Returns the download URL, or None when the export is missing or generation failed.
    """
    try:
        export = ExportHistory.objects.get(id=export_id)
    except ExportHistory.DoesNotExist:
        logger.error('ExportHistory with id %s does not exist', export_id)
        return None

    user = export.created_by
    try:
        pdf_bytes = programme.build_pdf(programme.registrations(registration_ids))

        file_name = 'profile_ids_{}.pdf'.format(uuid.uuid4())
        ExportStorage().save(file_name, ContentFile(pdf_bytes))
        file_url = reverse(programme.download_url_name, args=[file_name])

        export.file_url = file_url
        export.status = ExportHistory.STATUS.done
        export.save()

        if user:
            send_push_to_web(
                user,
                '{} profile IDs ready'.format(programme.label),
                'The PDF with {} profile ID card(s) is ready to download.'.format(len(registration_ids)),
                data={'type': PROFILE_IDS_READY, 'label': programme.label, 'url': file_url, 'export_id': export.id},
            )
        return file_url
    except Exception as exc:
        logger.exception('Error generating %s profile IDs for export %s: %s', programme.label, export_id, exc)
        export.status = ExportHistory.STATUS.failed
        export.save()
        if user:
            send_push_to_web(
                user,
                '{} profile IDs failed'.format(programme.label),
                str(exc),
                data={'type': PROFILE_IDS_FAILED, 'label': programme.label, 'reason': str(exc),
                      'export_id': export.id},
            )
        return None


def queue_profile_ids(export_id, programme, registration_ids):
    """Generate the profile IDs PDF in the background (same pool as the Makani exports)."""
    from student_registration.mscc.tasks import _get_executor, _run_with_new_db_connection

    return _get_executor().submit(
        _run_with_new_db_connection,
        generate_profile_ids,
        export_id,
        programme,
        list(registration_ids),
    )


def start_profile_ids_export(request, programme, registration_ids):
    """Record the export and queue it; returns the JSON-ready status payload."""
    export = ExportHistory.objects.create(
        export_type=programme.export_type,
        created_by=request.user,
        partner_name=request.user.partner.name if request.user.partner else '',
        file_format='pdf',
        fields={'count': len(registration_ids), 'filters': request.GET.dict()},
    )
    queue_profile_ids(export.id, programme, registration_ids)
    return {'status': 'started', 'export_id': export.id, 'count': len(registration_ids)}


@login_required(login_url='/users/login')
def profile_ids_download(request, file_name):
    if is_valid_filename(file_name, 'pdf'):
        return download_file(file_name, 'profile_ids.pdf', content_type='application/pdf')
    return HttpResponse("Invalid file.", status=400)
