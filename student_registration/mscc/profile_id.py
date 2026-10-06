# -*- coding: utf-8 -*-
"""Makani (MSCC) child profile ID cards."""
from __future__ import absolute_import, unicode_literals

from student_registration.backends.profile_ids import (
    ProfileIdProgramme, build_cards_pdf, lookup_name, person_full_name, read_image_field, short_birthday,
)

from .models import Registration

PROFILE_IDS_EXPORT_TYPE = 'Makani Profile IDs'


def registration_profile_id_card(registration):
    """Collect the fields printed on a Makani child's profile ID card.

    Makani children have no place of birth on record, so that line is left blank.
    """
    child = registration.child
    center = registration.center
    return {
        'round': registration.round.name if registration.round else '',
        'id': registration.id,
        'ngo': registration.partner.name if registration.partner else '',
        'full_name': person_full_name(child),
        'birthday': short_birthday(child.birthday_day, child.birthday_month, child.birthday_year) if child else '',
        'place_of_birth': '',
        'nationality': lookup_name(child.nationality) if child else '',
        'governorate': lookup_name(center.governorate) if center else '',
        'physical_difficulties': lookup_name(child.disability) if child and child.disability else 'No',
        'has_picture': bool(child and child.photo),
    }


def registration_profile_picture(registration):
    child = registration.child
    if not child:
        return None
    return read_image_field(child.photo, 'Child {}'.format(child.pk))


def profile_ids_registrations(registration_ids):
    """Registrations to print, in the order the Makani list shows them."""
    return (
        Registration.objects.filter(id__in=registration_ids)
        .select_related('child', 'child__nationality', 'child__disability', 'round', 'partner',
                        'center', 'center__governorate')
        .order_by('child__first_name', 'child__father_name', 'child__last_name')
    )


MAKANI_PROFILE_IDS = ProfileIdProgramme(
    label='Makani',
    export_type=PROFILE_IDS_EXPORT_TYPE,
    download_url_name='mscc:profile_ids_download',
    registrations=profile_ids_registrations,
    card=registration_profile_id_card,
    photo=registration_profile_picture,
)


def build_profile_ids_pdf(registrations):
    """One PDF with a Makani profile ID card per registration, one page each."""
    return build_cards_pdf(
        ((registration_profile_id_card(r), registration_profile_picture(r)) for r in registrations),
        title='Makani profile IDs')
