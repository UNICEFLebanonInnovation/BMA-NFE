"""Bilingual, parent-filtered form for MSCC exceptional-exam applications."""

from django import forms

from .exceptional_exam_choices import (
    GOVERNORATE_CHOICES, district_choices, town_choices,
)
from .models import ExceptionalExam


SELECT_PROMPT = ('', 'Select an option / اختر خياراً')


def _matching_location_code(location, choices):
    """Use an exact registered location name only when the match is unique."""
    if not location:
        return ''
    names = {
        str(value).strip().casefold()
        for value in (location.name, getattr(location, 'name_en', None)) if value
    }
    matches = [
        code for code, label in choices
        if names.intersection(part.strip().casefold() for part in label.split(' / '))
    ]
    return matches[0] if len(matches) == 1 else ''


class ExceptionalExamForm(forms.ModelForm):
    """Keep residence and examination choices independent of child registration."""

    class Meta:
        model = ExceptionalExam
        fields = (
            'governorate', 'district', 'nearest_town', 'programme', 'grade',
            'math_language', 'language_exam',
        )

    def __init__(self, *args, registration=None, **kwargs):
        super().__init__(*args, **kwargs)
        if registration is not None:
            self.instance.registration = registration
        elif self.instance.registration_id:
            registration = self.instance.registration

        # Stored exam selections always take precedence over the registration
        # address and programme. Selecting an exam residence never rewrites it.
        if not self.is_bound and not self.instance.pk and registration is not None:
            self.initial.setdefault('programme', registration.nfe_programme)
            child = registration.child if registration.child_id else None
            governorate = _matching_location_code(
                child.governorate if child else None, GOVERNORATE_CHOICES,
            )
            self.initial.setdefault('governorate', governorate)
            self.initial.setdefault('district', _matching_location_code(
                child.district if child else None, district_choices(self.initial['governorate']),
            ))

        def selected(name):
            if self.is_bound:
                return self.data.get(self.add_prefix(name), '')
            return self.initial.get(name, '')

        governorate = selected('governorate')
        district = selected('district')
        self.fields['district'].choices = district_choices(governorate)
        self.fields['nearest_town'].choices = town_choices(governorate, district)

        for field in self.fields.values():
            field.required = True
            field.choices = (SELECT_PROMPT,) + tuple(
                choice for choice in field.choices if choice[0] != ''
            )
            field.widget.attrs['class'] = 'form-select'
            field.error_messages.update({
                'required': 'This field is required. / هذا الحقل مطلوب.',
                'invalid_choice': 'Select a valid option. / اختر خياراً صالحاً.',
            })
            field.help_text = 'Required / مطلوب'
        self.fields['district'].help_text = (
            'Select a governorate first. / اختر المحافظة أولاً.'
        )
        self.fields['nearest_town'].help_text = (
            'Select a district first. / اختر القضاء أولاً.'
        )
        self.fields['grade'].help_text = (
            'Grades 2–7 are available for both programmes. / '
            'الصفوف من الثاني إلى السابع متاحة لكلا البرنامجين.'
        )
