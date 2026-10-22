"""Exceptional-exam grade eligibility based on the selected BLN level."""

from django.utils.translation import gettext_lazy as _

from .exceptional_exam_choices import GRADE_CHOICES


BLN_GRADE_BY_LEVEL = {'1': '2', '2': '3', '3': '4'}


def programme_grade_choices(programme, bln_level=''):
    """Restrict BLN to its selected level and DIRASA to the current grades."""
    if programme == 'DIRASA':
        return GRADE_CHOICES
    if programme == 'BLN':
        grade = BLN_GRADE_BY_LEVEL.get(str(bln_level or ''))
        return tuple(choice for choice in GRADE_CHOICES if choice[0] == grade)
    return ()


def programme_grade_help(programme, bln_level=''):
    if programme == 'DIRASA':
        return _('Grades 2–4 are available for DIRASA.')
    if programme == 'BLN':
        if str(bln_level or '') not in BLN_GRADE_BY_LEVEL:
            return _('Select a BLN level first.')
        return _('For BLN, the grade is determined by the selected BLN level.')
    return _('Select a programme first.')


def programme_grade_error(programme, bln_level, grade):
    """Return a localized validation error for an ineligible grade, if any."""
    if programme not in ('BLN', 'DIRASA'):
        return None
    choices = programme_grade_choices(programme, bln_level)
    if programme == 'BLN' and not choices:
        return programme_grade_help(programme, bln_level)
    if grade and grade not in dict(choices):
        if programme == 'BLN':
            return _('Select the grade allowed for the selected BLN level.')
        return _('Select a valid option.')
    return None
