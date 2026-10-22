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
            'place_of_birth', 'programme', 'bln_level', 'grade', 'math_language',
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
            if self.initial.get('programme') == 'BLN':
                # A prior age-derived examination grade does not establish the
                # child's enrolled level. Only an exact saved service does.
                levels = {'BLN Level 1': '1', 'BLN Level 2': '2', 'BLN Level 3': '3'}
                level = levels.get(registration.education_program)
                if level:
                    self.initial.setdefault('bln_level', level)
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
        if self.is_bound and programme == 'DIRASA':
            # Ignore a stale or malicious BLN level when applying for DIRASA.
            # Copy the input so the request's original data remains intact.
            self.data = self.data.copy()
            self.data[self.add_prefix('bln_level')] = ''
        bln_level = selected('bln_level')

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

        programmes_and_levels = {
            '': ('', ''),
            'BLN': ('BLN', ''),
            'BLN:1': ('BLN', '1'),
            'BLN:2': ('BLN', '2'),
            'BLN:3': ('BLN', '3'),
            'DIRASA': ('DIRASA', ''),
        }
        self.grade_choices_by_programme = {
            key: [
                {'id': value, 'text': str(label)}
                for value, label in programme_grade_choices(code, level)
            ]
            for key, (code, level) in programmes_and_levels.items()
        }
        self.grade_help_by_programme = {
            key: str(programme_grade_help(code, level))
            for key, (code, level) in programmes_and_levels.items()
        }
        grade_choices = programme_grade_choices(programme, bln_level)
        self.fields['grade'].choices = grade_choices
        if not self.is_bound and programme == 'BLN' and len(grade_choices) == 1:
            # Showing the grade for an explicit level does not change the
            # stored examination application until it is saved.
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
        self.fields['bln_level'].required = programme == 'BLN'
        self.fields['bln_level'].help_text = _('Required for BLN.')
        self.fields['grade'].help_text = programme_grade_help(programme, bln_level)
        if programme == 'BLN':
            if not grade_choices:
                self.fields['grade'].error_messages['required'] = programme_grade_help(programme, bln_level)
            self.fields['grade'].error_messages['invalid_choice'] = (
                _('Select the grade allowed for the selected BLN level.')
                if grade_choices else programme_grade_help(programme, bln_level)
            )
