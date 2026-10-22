"""Exceptional-exam grades for selected programmes and existing BLN records."""

from django.utils.translation import gettext_lazy as _

from .exceptional_exam_choices import GRADE_CHOICES


BLN_GRADE_BY_PROGRAM = {
    'BLN Level 1': '2',
    'BLN Level 2': '3',
    'BLN Level 3': '4',
}


def programme_grade_choices(programme, education_program=''):
    """Map explicit levels directly; retain the generic BLN service rule."""
    if programme == 'DIRASA':
        return GRADE_CHOICES
    if programme in BLN_GRADE_BY_PROGRAM or programme == 'BLN':
        grade = BLN_GRADE_BY_PROGRAM.get(
            education_program if programme == 'BLN' else programme,
        )
        return tuple(choice for choice in GRADE_CHOICES if choice[0] == grade)
    return ()


def programme_grade_help(programme, education_program=''):
    if programme == 'DIRASA':
        return _('Grades 2–4 are available for DIRASA.')
    if programme in BLN_GRADE_BY_PROGRAM:
        return _('For BLN, the grade is determined by the selected programme level.')
    if programme == 'BLN':
        if education_program not in BLN_GRADE_BY_PROGRAM:
            return _('BLN requires a Program of BLN Level 1, BLN Level 2, or BLN Level 3 in Education Service. Update Education Service first.')
        return _('For BLN, the grade is determined by the Program saved in Education Service.')
    return _('Select a programme first.')


def programme_grade_error(programme, education_program, grade):
    """Return a localized validation error for an ineligible grade, if any."""
    if programme not in ('BLN', 'DIRASA') and programme not in BLN_GRADE_BY_PROGRAM:
        return None
    choices = programme_grade_choices(programme, education_program)
    if programme == 'BLN' and not choices:
        return programme_grade_help(programme, education_program)
    if grade and grade not in dict(choices):
        if programme in BLN_GRADE_BY_PROGRAM:
            return _('Select the grade allowed for the selected BLN programme level.')
        if programme == 'BLN':
            return _('Select the BLN grade allowed by the Program saved in Education Service.')
        return _('Select a valid option.')
    return None
