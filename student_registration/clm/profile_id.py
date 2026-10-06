# -*- coding: utf-8 -*-
"""Dirasa (Bridging) child profile ID cards."""
from __future__ import absolute_import, unicode_literals

from student_registration.backends.profile_ids import (
    ProfileIdProgramme, build_cards_pdf, lookup_name, person_full_name, read_image_field, short_birthday,
)

from .models import Bridging

PROFILE_IDS_EXPORT_TYPE = 'Bridging Profile IDs'


def bridging_profile_id_card(bridging):
    """Collect the fields printed on a child's Dirasa profile ID card."""
    student = bridging.student
    return {
        'round': bridging.round.name if bridging.round else '',
        'id': bridging.id,
        'ngo': bridging.partner.name if bridging.partner else '',
        'full_name': person_full_name(student),
        'birthday': short_birthday(student.birthday_day, student.birthday_month, student.birthday_year)
        if student else '',
        'place_of_birth': (student.place_of_birth or '') if student else '',
        'nationality': lookup_name(student.nationality) if student else '',
        'governorate': lookup_name(bridging.governorate),
        'physical_difficulties': lookup_name(bridging.disability) if bridging.disability else 'No',
        'has_picture': bool(bridging.profile_picture),
    }


def bridging_profile_picture(bridging):
    return read_image_field(bridging.profile_picture, 'Bridging {}'.format(bridging.pk))


def profile_ids_registrations(registration_ids):
    """Registrations to print, in the order the Dirasa list shows them."""
    return (
        Bridging.objects.filter(id__in=registration_ids)
        .select_related('student', 'student__nationality', 'round', 'partner', 'governorate', 'disability')
        .order_by('student__first_name', 'student__father_name', 'student__last_name')
    )


BRIDGING_PROFILE_IDS = ProfileIdProgramme(
    label='Dirasa',
    export_type=PROFILE_IDS_EXPORT_TYPE,
    download_url_name='clm:bridging_profile_ids_download',
    registrations=profile_ids_registrations,
    card=bridging_profile_id_card,
    photo=bridging_profile_picture,
)


def build_profile_ids_pdf(registrations):
    """One PDF with a Dirasa profile ID card per registration, one page each."""
    return build_cards_pdf(((bridging_profile_id_card(b), bridging_profile_picture(b)) for b in registrations),
                           title='Dirasa profile IDs')
