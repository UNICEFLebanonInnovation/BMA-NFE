"""Exceptional-exam grades for the three selectable BLN programme levels."""

from django.utils.translation import gettext_lazy as _

from .exceptional_exam_choices import GRADE_CHOICES


BLN_GRADE_BY_PROGRAM = {
    'BLN Level 1': '2',
    'BLN Level 2': '3',
    'BLN Level 3': '4',
}


def programme_grade_choices(programme):
    """Offer only the grade linked to the selected programme level."""
    grade = BLN_GRADE_BY_PROGRAM.get(programme)
    return tuple(choice for choice in GRADE_CHOICES if choice[0] == grade)


def programme_grade_help(programme):
    if programme in BLN_GRADE_BY_PROGRAM:
        return _('For BLN, the grade is determined by the selected programme level.')
    return _('Select a programme first.')


def programme_grade_error(programme, grade):
    """Return a localized validation error for an ineligible grade, if any."""
    if programme not in BLN_GRADE_BY_PROGRAM:
        return None
    choices = programme_grade_choices(programme)
    if grade and grade not in dict(choices):
        return _('Select the grade allowed for the selected BLN programme level.')
    return None
