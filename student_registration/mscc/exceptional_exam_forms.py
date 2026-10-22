"""Translated, parent-filtered form for MSCC exceptional-exam applications."""

from django import forms
from django.utils.translation import gettext_lazy as _, pgettext_lazy

from student_registration.locations.models import Location

from .exceptional_exam_grades import programme_grade_choices, programme_grade_help
from .exceptional_exam_locations import (
    location_label, positive_location_id, town_choices_for_locations,
)
from .models import ExceptionalExam


SELECT_PROMPT = ('', _('Select an option'))


class TranslatedLocationChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return location_label(obj)


class ExceptionalExamForm(forms.ModelForm):
    """Keep residence and examination choices independent of child registration."""

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

        # Stored exam selections always take precedence over the registration
        # address and programme. Selecting an exam residence never rewrites it.
        if not self.is_bound and not self.instance.pk and registration is not None:
            self.initial.setdefault('programme', registration.nfe_programme)
            child = registration.child if registration.child_id else None
            governorate = child.governorate if child and child.governorate_id else None
            district = child.district if child and child.district_id else None
            if governorate and governorate.type_id == 1:
                self.initial.setdefault('governorate', governorate.pk)
                if (district and district.type_id == 2
                        and district.parent_id == governorate.pk):
                    self.initial.setdefault('district', district.pk)

        def selected(name):
            if self.is_bound:
                return self.data.get(self.add_prefix(name), '')
            return self.initial.get(name, '')

        programme = selected('programme')
        # The registration comes from the authorized URL, and its latest saved
        # service is authoritative. Submitted programme levels cannot replace it.
        education_program = registration.education_program if registration and registration.pk else ''

        governorate_id = positive_location_id(selected('governorate'))
        governorate = Location.objects.filter(pk=governorate_id, type_id=1).first()
        district_queryset = Location.objects.none()
        if governorate:
            district_queryset = Location.objects.filter(
                type_id=2, parent_id=governorate.pk,
            ).order_by('name')
        self.fields['district'].queryset = district_queryset
        district_id = positive_location_id(selected('district'))
        district = district_queryset.filter(pk=district_id).first()
        self.fields['nearest_town'].choices = town_choices_for_locations(governorate, district)

        self.grade_choices_by_programme = {
            code: [
                {'id': value, 'text': str(label)}
                for value, label in programme_grade_choices(code, education_program)
            ]
            for code in ('', 'BLN', 'DIRASA')
        }
        self.grade_help_by_programme = {
            code: str(programme_grade_help(code, education_program))
            for code in ('', 'BLN', 'DIRASA')
        }
        grade_choices = programme_grade_choices(programme, education_program)
        self.fields['grade'].choices = grade_choices
        if not self.is_bound and programme == 'BLN' and len(grade_choices) == 1:
            # A service may have changed since the last application. Display
            # the current eligible grade without rewriting the saved answer.
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
        self.fields['district'].help_text = _('Select a governorate first.')
        self.fields['nearest_town'].help_text = _('Select a district first.')
        self.fields['place_of_birth'].help_text = _('Place of birth similar in the Official ID')
        self.fields['grade'].help_text = programme_grade_help(programme, education_program)
        if programme == 'BLN':
            if not grade_choices:
                self.fields['grade'].error_messages['required'] = programme_grade_help(programme, education_program)
            self.fields['grade'].error_messages['invalid_choice'] = (
                _('Select the BLN grade allowed by the Program saved in Education Service.')
                if grade_choices else programme_grade_help(programme, education_program)
            )
