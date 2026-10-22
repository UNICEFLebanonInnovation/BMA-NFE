"""Translated, parent-filtered form for MSCC exceptional-exam applications."""

from django import forms
from django.utils.translation import gettext_lazy as _, pgettext_lazy

from student_registration.locations.models import Location

from .exceptional_exam_choices import COUNTRY_OF_BIRTH_CHOICES, PROGRAMME_CHOICES
from .exceptional_exam_grades import (
    BLN_GRADE_BY_PROGRAM, programme_grade_choices, programme_grade_help,
)
from .exceptional_exam_locations import (
    location_label, registered_village_code, town_choices_for_locations,
)
from .models import ExceptionalExam


SELECT_PROMPT = ('', _('Select an option'))


class TranslatedLocationChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return location_label(obj)


class ExceptionalExamForm(forms.ModelForm):
    """Copy read-only registration details and validate the exam answers."""

    REGISTRATION_FIELDS = (
        'programme', 'governorate', 'district', 'nearest_town',
        'country_of_birth', 'place_of_birth',
    )

    governorate = TranslatedLocationChoiceField(
        queryset=Location.objects.filter(type_id=1).order_by('name'),
        label=pgettext_lazy('exceptional_exam', 'Governorate'), empty_label=SELECT_PROMPT[1],
    )
    district = TranslatedLocationChoiceField(
        queryset=Location.objects.none(), label=_('District/Caza'),
        empty_label=SELECT_PROMPT[1],
    )

    class Meta:
        model = ExceptionalExam
        fields = (
            'governorate', 'district', 'nearest_town', 'country_of_birth',
            'place_of_birth', 'programme', 'grade', 'math_language',
            'language_exam',
        )

    def __init__(self, *args, registration=None, **kwargs):
        super().__init__(*args, **kwargs)
        if registration is not None:
            self.instance.registration = registration
        elif self.instance.registration_id:
            registration = self.instance.registration

        child = registration.child if registration is not None and registration.child_id else None
        governorate = child.governorate if child and child.governorate_id else None
        district = child.district if child and child.district_id else None
        if not governorate or governorate.type_id != 1:
            governorate = None
        if not (governorate and district and district.type_id == 2
                and district.parent_id == governorate.pk):
            district = None
        self.registration_residence_valid = bool(governorate and district)
        self.registration_residence_help = _(
            "Update the governorate and district in the child's registration first."
        )
        self.registration_details_help = _(
            "Complete the required programme, address, and birth details in the child's registration first."
        )
        for name, location in (('governorate', governorate), ('district', district)):
            self.initial[name] = location.pk if location else None
            self.fields[name].queryset = (
                Location.objects.filter(pk=location.pk) if location else Location.objects.none()
            )
        self.fields['nearest_town'].choices = town_choices_for_locations(governorate, district)

        # These values always come from the authorized registration, even on
        # edit or when posted data and supplied initial values claim otherwise.
        programme = registration.nfe_programme if registration is not None else ''
        programme = programme if programme in BLN_GRADE_BY_PROGRAM else ''
        country = (getattr(child, 'country_of_birth', '') or '') if child else ''
        country = country if country in dict(COUNTRY_OF_BIRTH_CHOICES) else ''
        birthplace = (getattr(child, 'place_of_birth', '') or '').strip() if child else ''
        village = registered_village_code(
            governorate, district, child.village if child else '',
        )
        self.initial.update({
            'programme': programme,
            'nearest_town': village,
            'country_of_birth': country,
            'place_of_birth': birthplace,
        })
        for name in self.REGISTRATION_FIELDS:
            self.fields[name].disabled = True
        self.registration_details_valid = bool(
            self.registration_residence_valid and village and programme and country
            and birthplace and len(birthplace) <= self.fields['place_of_birth'].max_length
        )
        programme_codes = ('',) + tuple(code for code, _ in PROGRAMME_CHOICES)

        self.grade_choices_by_programme = {
            code: [
                {'id': value, 'text': str(label)}
                for value, label in programme_grade_choices(code)
            ]
            for code in programme_codes
        }
        self.grade_help_by_programme = {
            code: str(programme_grade_help(code))
            for code in programme_codes
        }
        self.grade_help_by_programme[''] = str(self.registration_details_help)
        grade_choices = programme_grade_choices(programme)
        self.fields['grade'].choices = grade_choices
        if not self.is_bound and len(grade_choices) == 1:
            # Display the eligible grade without rewriting the saved answer.
            self.initial['grade'] = grade_choices[0][0]

        for field in self.fields.values():
            field.required = True
            if not isinstance(field, forms.ChoiceField):
                # Free-text entries such as the place of birth.
                field.widget.attrs['class'] = 'form-control'
                field.widget.attrs.setdefault('autocomplete', 'off')
                field.error_messages['required'] = _('This field is required.')
                field.help_text = _('Required')
                continue
            if not isinstance(field, forms.ModelChoiceField):
                field.choices = (SELECT_PROMPT,) + tuple(
                    choice for choice in field.choices if choice[0] != ''
                )
            field.widget.attrs['class'] = 'form-select'
            field.error_messages.update({
                'required': _('This field is required.'),
                'invalid_choice': _('Select a valid option.'),
            })
            field.help_text = _('Required')
        for name in self.REGISTRATION_FIELDS:
            self.fields[name].help_text = _("From the child's registration.")
            self.fields[name].error_messages['required'] = self.registration_details_help
            self.fields[name].error_messages['invalid_choice'] = self.registration_details_help
        self.fields['place_of_birth'].error_messages['max_length'] = self.registration_details_help
        self.fields['place_of_birth'].help_text = _('Place of birth similar in the Official ID')
        self.fields['grade'].help_text = (
            programme_grade_help(programme) if programme else self.registration_details_help
        )
        if programme in BLN_GRADE_BY_PROGRAM:
            self.fields['grade'].error_messages['invalid_choice'] = _(
                'Select the grade allowed for the selected BLN programme level.'
            )
        else:
            self.fields['grade'].error_messages['required'] = self.registration_details_help
            self.fields['grade'].error_messages['invalid_choice'] = self.registration_details_help
