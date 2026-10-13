"""Exceptional-exam grade eligibility based on the registered child's age."""

from datetime import date

from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .exceptional_exam_choices import GRADE_CHOICES


BLN_GRADE_BY_AGE = {
    7: '2', 8: '2', 9: '3', 10: '4', 11: '5', 12: '6', 13: '6', 14: '6',
}


def completed_age(child, on_date=None):
    """Return completed years only for a complete, valid, non-future birth date.

    Child.age assumes that stored date components are valid. Examination
    eligibility must also handle incomplete and historical registration data.
    """
    if child is None:
        return None
    values = tuple(
        str(getattr(child, name, '') or '').strip()
        for name in ('birthday_year', 'birthday_month', 'birthday_day')
    )
    if not all(value.isdecimal() for value in values):
        return None
    try:
        birthday = date(*(int(value) for value in values))
    except (ValueError, OverflowError):
        return None
    if on_date is not None:
        today = on_date
    else:
        now = timezone.now()
        today = timezone.localdate(now) if timezone.is_aware(now) else now.date()
    if birthday > today:
        return None
    return today.year - birthday.year - (
        (today.month, today.day) < (birthday.month, birthday.day)
    )


def programme_grade_choices(programme, child, on_date=None):
    """Use the saved child's birthday, never submitted age or child fields."""
    if programme == 'DIRASA':
        return GRADE_CHOICES
    if programme == 'BLN':
        grade = BLN_GRADE_BY_AGE.get(completed_age(child, on_date))
        return tuple(choice for choice in GRADE_CHOICES if choice[0] == grade)
    return ()


def programme_grade_help(programme, child, on_date=None):
    if programme == 'DIRASA':
        return _('Grades 2–7 are available for DIRASA.')
    if programme == 'BLN':
        age = completed_age(child, on_date)
        if age is None:
            return _("BLN requires a complete, valid date of birth. Update the child's registration first.")
        if age not in BLN_GRADE_BY_AGE:
            return _('BLN is available for children aged 7–14.')
        return _("For BLN, the grade is determined by the child's current age.")
    return _('Select a programme first.')


def programme_grade_error(programme, child, grade, on_date=None):
    """Return a localized validation error for an ineligible grade, if any."""
    if not grade or programme not in ('BLN', 'DIRASA'):
        return None
    choices = programme_grade_choices(programme, child, on_date)
    if programme == 'BLN' and not choices:
        return programme_grade_help(programme, child, on_date)
    if grade and grade not in dict(choices):
        if programme == 'BLN':
            return _("Select the BLN grade allowed for the child's age.")
        return _('Select a valid option.')
    return None
