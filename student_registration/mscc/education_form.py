from __future__ import unicode_literals, absolute_import, division
from datetime import date, datetime

from django.utils.translation import gettext as _
from django import forms
from django.urls import reverse
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db.models import Q

from crispy_forms.helper import FormHelper

from crispy_forms.bootstrap import (
    FormActions,
    InlineCheckboxes
)
from crispy_forms.layout import Layout, Fieldset, Button, Submit, Div, Field, HTML, Reset

from student_registration.mscc.utils import validate_date
from student_registration.mscc.widgets import DatePickerInput
from .models import (
    Registration,
    EducationAssessment,
    EducationService,
    Packages,
    EducationRSService,
    EducationProgrammeAssessment,
    YES_NO,
    Round
)
from student_registration.schools.models import (
    School,
)
from .utils import update_child_attendance


class DiagnosticAssessmentForm(forms.ModelForm):
    # Pre Test
    pre_attended_arabic = forms.ChoiceField(
        label=_("Did the Child Undertake Arabic Language Development Assessment"),
        widget=forms.Select, required=True,
        choices=YES_NO,
    )
    pre_modality_arabic = forms.ChoiceField(
        label=_("Modality"),
        widget=forms.Select,
        required=False,
        choices=EducationAssessment.MODALITY
    )
    pre_arabic_grade = forms.IntegerField(
        label=_('Grade'),
        widget=forms.NumberInput(attrs=({'maxlength': 4, 'placeholder': '0'})),
        min_value=0, required=False,
        initial=0
    )
    pre_attended_language = forms.ChoiceField(
        label=_("Did the Child Undertake Foreign Language Development Assessment"),
        widget=forms.Select, required=True,
        choices=YES_NO,
    )
    pre_modality_language = forms.ChoiceField(
        label=_("Modality"),
        widget=forms.Select,
        required=False,
        choices=EducationAssessment.MODALITY
    )
    pre_language_grade = forms.IntegerField(
        label=_('Grade'),
        widget=forms.NumberInput(attrs=({'maxlength': 4, 'placeholder': '0'})),
        min_value=0, required=False,
        initial=0
    )
    pre_attended_math = forms.ChoiceField(
        label=_("Did the Child Undertake Cognitive Development - Mathematics test"),
        widget=forms.Select, required=True,
        choices=YES_NO,
    )
    pre_modality_math = forms.ChoiceField(
        label=_("Modality"),
        widget=forms.Select,
        required=False,
        choices=EducationAssessment.MODALITY
    )
    pre_math_grade = forms.IntegerField(
        label=_('Grade'),
        widget=forms.NumberInput(attrs=({'maxlength': 4, 'placeholder': '0'})),
        min_value=0, required=False,
        initial=0
    )

    registration_id = forms.CharField(widget=forms.HiddenInput, required=False)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        registry = kwargs.pop('registry', None)
        instance = kwargs.pop('instance', None)

        super(DiagnosticAssessmentForm, self).__init__(*args, **kwargs)

        form_action = reverse('mscc:service_diagnostic_assessment_add', kwargs={'registry': registry})
        if instance:
            form_action = reverse('mscc:service_diagnostic_assessment_edit',
                                  kwargs={'registry': registry, 'pk': instance})
        self.helper = FormHelper()
        self.helper.form_show_labels = True
        self.helper.form_action = form_action
        self.helper.layout = Layout(
            Div(
                Div(
                    HTML('<span class="badge-form badge-pill">1</span>'),
                    Div('pre_attended_arabic', css_class='col-md-6'),
                    Div('pre_modality_arabic', css_class='col-md-3'),
                    Div('pre_arabic_grade', css_class='col-md-2'),
                    css_class='row card-body'
                ),
                Div(
                    HTML('<span class="badge-form badge-pill">2</span>'),
                    Div('pre_attended_language', css_class='col-md-6'),
                    Div('pre_modality_language', css_class='col-md-3'),
                    Div('pre_language_grade', css_class='col-md-2'),
                    css_class='row card-body'
                ),
                Div(
                    HTML('<span class="badge-form badge-pill">3</span>'),
                    Div('pre_attended_math', css_class='col-md-6'),
                    Div('pre_modality_math', css_class='col-md-3'),
                    Div('pre_math_grade', css_class='col-md-2'),
                    css_class='row card-body'
                ),
                FormActions(
                    Submit('save', 'Save',
                           css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-success'),
                    Reset('reset', 'Reset',
                          css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-warning'),
                ),
                css_id='step-1'
            ),
        )

    def save(self, request=None, instance=None, registry=None):

        validated_data = request.POST

        if not instance:
            instance = EducationAssessment.objects.create(registration_id=registry)
        else:
            instance = EducationAssessment.objects.get(id=instance)

        instance.pre_attended_arabic = validated_data.get('pre_attended_arabic')
        instance.pre_modality_arabic = validated_data.get('pre_modality_arabic')
        instance.pre_arabic_grade = int(validated_data.get('pre_arabic_grade'))
        instance.pre_attended_language = validated_data.get('pre_attended_language')
        instance.pre_modality_language = validated_data.get('pre_modality_language')
        instance.pre_language_grade = int(validated_data.get('pre_language_grade'))
        instance.pre_attended_math = validated_data.get('pre_attended_math')
        instance.pre_modality_math = validated_data.get('pre_modality_math')
        instance.pre_math_grade = int(validated_data.get('pre_math_grade'))
        instance.save()

        messages.success(request, _('Your data has been sent successfully to the server'))

        return instance

    def clean(self):
        cleaned_data = super(DiagnosticAssessmentForm, self).clean()

        pre_attended_arabic = cleaned_data.get("pre_attended_arabic")
        pre_modality_arabic = cleaned_data.get("pre_modality_arabic")
        pre_arabic_grade = cleaned_data.get("pre_arabic_grade")
        if pre_attended_arabic and pre_attended_arabic == 'Yes':
            if not pre_modality_arabic:
                self.add_error('pre_modality_arabic', 'This field is required')
            if not pre_arabic_grade:
                self.add_error('pre_arabic_grade', 'This field is required')

        pre_attended_language = cleaned_data.get("pre_attended_language")
        pre_modality_language = cleaned_data.get("pre_modality_language")
        pre_language_grade = cleaned_data.get("pre_language_grade")
        if pre_attended_language and pre_attended_language == 'Yes':
            if not pre_modality_language:
                self.add_error('pre_modality_language', 'This field is required')
            if not pre_language_grade:
                self.add_error('pre_language_grade', 'This field is required')

        pre_attended_math = cleaned_data.get("pre_attended_math")
        pre_modality_math = cleaned_data.get("pre_modality_math")
        pre_math_grade = cleaned_data.get("pre_math_grade")
        if pre_attended_math and pre_attended_math == 'Yes':
            if not pre_modality_math:
                self.add_error('pre_modality_math', 'This field is required')
            if not pre_math_grade:
                self.add_error('pre_math_grade', 'This field is required')

    class Meta:
        model = EducationAssessment
        fields = (
            'pre_attended_arabic',
            'pre_modality_arabic',
            'pre_arabic_grade',
            'pre_attended_language',
            'pre_modality_language',
            'pre_language_grade',
            'pre_attended_math',
            'pre_modality_math',
            'pre_math_grade',
        )


class EducationAssessmentForm(forms.ModelForm):
    participation = forms.ChoiceField(
        label=_("Child Level of participation / Absence"),
        widget=forms.Select, required=True,
        choices=EducationAssessment.PARTICIPATION
    )
    barriers = forms.ChoiceField(
        label=_('The main barriers affecting the child\'s '
                'daily attendance/participation, performance, or causing drop-out'),
        widget=forms.Select, required=False,
        choices=EducationAssessment.BARRIERS
    )
    barriers_other = forms.CharField(
        label=_('Please specify'),
        widget=forms.TextInput(attrs={'placeholder': _('Describe other barriers')}), required=False
    )
    post_test_done = forms.ChoiceField(
        label=_('Did the child undertake the Post tests?'),
        widget=forms.Select, required=True,
        choices=YES_NO
    )
    school_year_completed = forms.ChoiceField(
        label=_('Did the child fully complete the school year?'),
        widget=forms.Select, required=True,
        choices=YES_NO
    )
    # Post test
    post_attended_arabic = forms.ChoiceField(
        label=_("Did the Child Undertake Arabic Language Development Assessment"),
        widget=forms.Select, required=True,
        choices=YES_NO,
    )
    post_modality_arabic = forms.ChoiceField(
        label=_("Modality"),
        widget=forms.Select,
        required=False,
        choices=EducationAssessment.MODALITY
    )
    post_arabic_grade = forms.IntegerField(
        label=_('Grade'),
        widget=forms.NumberInput(attrs=({'maxlength': 4, 'placeholder': '0'})),
        required=False,
        initial=0
    )
    post_attended_language = forms.ChoiceField(
        label=_("Did the Child Undertake Foreign Language Development Assessment"),
        widget=forms.Select, required=True,
        choices=YES_NO,
    )
    post_modality_language = forms.ChoiceField(
        label=_("Modality"),
        widget=forms.Select,
        required=False,
        choices=EducationAssessment.MODALITY
    )
    post_language_grade = forms.IntegerField(
        label=_('Grade'),
        widget=forms.NumberInput(attrs=({'maxlength': 4, 'placeholder': '0'})),
        required=False,
        initial=0
    )
    post_attended_math = forms.ChoiceField(
        label=_("Did the Child Undertake Cognitive Development - Mathematics test"),
        widget=forms.Select, required=True,
        choices=YES_NO,
    )
    post_modality_math = forms.ChoiceField(
        label=_("Modality"),
        widget=forms.Select,
        required=False,
        choices=EducationAssessment.MODALITY
    )
    post_math_grade = forms.IntegerField(
        label=_('Grade'),
        widget=forms.NumberInput(attrs=({'maxlength': 4, 'placeholder': '0'})),
        required=False,
        initial=0
    )

    registration_id = forms.CharField(widget=forms.HiddenInput, required=False)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        registry = kwargs.pop('registry', None)
        instance = kwargs.pop('instance', None)

        super(EducationAssessmentForm, self).__init__(*args, **kwargs)

        form_action = reverse('mscc:service_education_assessment_add', kwargs={'registry': registry})
        if instance:
            form_action = reverse('mscc:service_education_assessment_edit',
                                  kwargs={'registry': registry, 'pk': instance})

        self.helper = FormHelper()
        self.helper.form_show_labels = True
        self.helper.form_action = form_action
        self.helper.layout = Layout(
            Div(
                Div(
                    HTML('<span class="badge-form badge-pill">1</span>'),
                    Div('participation', css_class='col-md-4'),
                    css_class='row card-body'
                ),
                Div(
                    HTML('<span class="badge-form badge-pill">2</span>'),
                    Div('barriers', css_class='col-md-8'),
                    Div('barriers_other', css_class='col-md-3'),
                    css_class='row card-body'
                ),
                Div(
                    HTML('<span class="badge-form badge-pill">3</span>'),
                    Div('post_test_done', css_class='col-md-5'),
                    HTML('<span class="badge-form badge-pill">4</span>'),
                    Div('school_year_completed', css_class='col-md-5'),
                    css_class='row card-body'
                ),
                Div(
                    HTML('<span class="badge-form badge-pill">5</span>'),
                    Div('post_attended_arabic', css_class='col-md-6'),
                    Div('post_modality_arabic', css_class='col-md-3 grd-arabic'),
                    Div('post_arabic_grade', css_class='col-md-2 grd-arabic'),
                    css_class='row grades card-body'
                ),
                Div(
                    HTML('<span class="badge-form badge-pill">6</span>'),
                    Div('post_attended_language', css_class='col-md-6'),
                    Div('post_modality_language', css_class='col-md-3'),
                    Div('post_language_grade', css_class='col-md-2'),
                    css_class='row grades card-body'
                ),
                Div(
                    HTML('<span class="badge-form badge-pill">7</span>'),
                    Div('post_attended_math', css_class='col-md-6'),
                    Div('post_modality_math', css_class='col-md-3'),
                    Div('post_math_grade', css_class='col-md-2'),
                    css_class='row grades card-body'
                ),
                FormActions(
                    Submit('save', 'Save',
                           css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-success'),
                    Reset('reset', 'Reset',
                          css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-warning'),
                ),
                css_id='step-1'
            ),
        )

    def save(self, request=None, instance=None, registry=None):

        validated_data = request.POST

        if not instance:
            instance = EducationAssessment.objects.create(registration_id=registry)
        else:
            instance = EducationAssessment.objects.get(id=instance)

        instance.participation = validated_data.get('participation')
        instance.barriers = validated_data.get('barriers')
        instance.barriers_other = validated_data.get('barriers_other')
        instance.post_test_done = validated_data.get('post_test_done')
        instance.school_year_completed = validated_data.get('school_year_completed')
        instance.post_attended_arabic = validated_data.get('post_attended_arabic')
        instance.post_modality_arabic = validated_data.get('post_modality_arabic')
        instance.post_arabic_grade = int(validated_data.get('post_arabic_grade'))
        instance.post_attended_language = validated_data.get('post_attended_language')
        instance.post_modality_language = validated_data.get('post_modality_language')
        instance.post_language_grade = int(validated_data.get('post_language_grade'))
        instance.post_attended_math = validated_data.get('post_attended_math')
        instance.post_modality_math = validated_data.get('post_modality_math')
        instance.post_math_grade = int(validated_data.get('post_math_grade'))
        instance.save()

        messages.success(request, _('Your data has been sent successfully to the server'))

        return instance

    def clean(self):
        cleaned_data = super(EducationAssessmentForm, self).clean()
        barriers = cleaned_data.get("barriers")
        barriers_other = cleaned_data.get("barriers_other")
        if barriers and barriers == 'Other' and not barriers_other:
            self.add_error('barriers_other', 'This field is required')

        post_test_done = cleaned_data.get("post_test_done")
        if post_test_done and post_test_done == 'Yes':

            post_attended_arabic = cleaned_data.get("post_attended_arabic")
            post_modality_arabic = cleaned_data.get("post_modality_arabic")
            post_arabic_grade = cleaned_data.get("post_arabic_grade")
            if post_attended_arabic and post_attended_arabic == 'Yes':
                if not post_modality_arabic:
                    self.add_error('post_modality_arabic', 'This field is required')
                if not post_arabic_grade:
                    self.add_error('post_arabic_grade', 'This field is required')

            post_attended_language = cleaned_data.get("post_attended_language")
            post_modality_language = cleaned_data.get("post_modality_language")
            post_language_grade = cleaned_data.get("post_language_grade")
            if post_attended_language and post_attended_language == 'Yes':
                if not post_modality_language:
                    self.add_error('post_modality_language', 'This field is required')
                if not post_language_grade:
                    self.add_error('post_language_grade', 'This field is required')

            post_attended_math = cleaned_data.get("post_attended_math")
            post_modality_math = cleaned_data.get("post_modality_math")
            post_math_grade = cleaned_data.get("post_math_grade")
            if post_attended_math and post_attended_math == 'Yes':
                if not post_modality_math:
                    self.add_error('post_modality_math', 'This field is required')
                if not post_math_grade:
                    self.add_error('post_math_grade', 'This field is required')

    class Meta:
        model = EducationAssessment
        fields = (
            'participation',
            'barriers',
            'barriers_other',
            'post_test_done',
            'school_year_completed',
            'post_attended_arabic',
            'post_modality_arabic',
            'post_arabic_grade',
            'post_attended_language',
            'post_modality_language',
            'post_language_grade',
            'post_attended_math',
            'post_modality_math',
            'post_math_grade'
        )


class EducationServiceForm(forms.ModelForm):
    education_status = forms.ChoiceField(
        label=_("Child\'s educational level when registering for the round"),
        widget=forms.Select, required=True,
        choices=EducationService.EDUCATION_STATUS,
    )
    dropout_date = forms.DateField(
        label=_("Please Specify dropout date from school"),
        required=False,
        widget=DatePickerInput(),
        help_text=_('Last date the child attended formal school.')
    )
    round = forms.ModelChoiceField(
        queryset=Round.objects.filter(current_year=True),
        widget=forms.Select,
        label=_('Round'),
        empty_label='-------',
        required=True, to_field_name='id',
    )
    education_program = forms.ChoiceField(
        label=_("Program"),
        widget=forms.Select, required=True,
        choices=EducationService.EDUCATION_PROGRAM,
    )
    catch_up_registered = forms.ChoiceField(
        label=_("Is the child registered in catch-up program"),
        widget=forms.Select, required=False,
        choices=EducationService.CATCH_UP_REGISTERED,
    )
    registration_date = forms.DateField(
        label=_("Date of registration in the round"),
        widget=forms.DateInput(attrs={
            'type': 'date',
        }),
        required=True,
        help_text=_('The date the child joined the current round.')
    )
    class_section = forms.ChoiceField(
        label=_("Class Section"),
        widget=forms.Select,
        required=True,
        choices=EducationService._meta.get_field('class_section').choices,
    )

    registration_id = forms.CharField(widget=forms.HiddenInput, required=False)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        self.registry = kwargs.pop('registry', None)
        instance = kwargs.pop('instance', None)

        super(EducationServiceForm, self).__init__(*args, **kwargs)
        self.fields['registration_date'].widget.attrs['max'] = date.today().strftime('%Y-%m-%d')

        if self.registry:
            self.fields['registration_id'].initial = self.registry

        choices = []

        available_service_names = ()
        if self.registry:
            registry_obj = Registration.objects.select_related('child').filter(id=self.registry).first()
            if registry_obj:
                available_service_names = set(
                    Packages.objects.filter(
                        min_age__lte=registry_obj.child_age,
                        max_age__gte=registry_obj.child_age
                    ).values_list('name', flat=True)
                )
                
        if getattr(registry_obj, 'registration_date', None):
            self.fields['registration_date'].widget.attrs['min'] = (
                registry_obj.registration_date.strftime('%Y-%m-%d')
            )

        for option in available_service_names:
            choices.append((option, option))

        self.fields['education_program'].choices = choices

        display_edu_section = ''

        if self.registry:
            child_id = Registration.objects.filter(id=self.registry).values_list('child_id', flat=True).first()

            if instance:
                try:
                    education_service = EducationService.objects.get(pk=instance)
                    current_round_id = education_service.round_id
                except EducationService.DoesNotExist:
                    current_round_id = None
            else:
                current_round_id = None

            if current_round_id:
                rounds_registered = EducationService.objects.filter(
                    registration__child_id=child_id,
                    registration__deleted=False
                ).exclude(
                    round_id=current_round_id
                ).values_list('round_id', flat=True)
            else:
                rounds_registered = EducationService.objects.filter(
                    registration__child_id=child_id,
                    registration__deleted=False
                ).values_list('round_id', flat=True)

            rounds_registered = [r for r in rounds_registered if r is not None]

            if current_round_id:
                available_rounds = Round.objects.filter(
                    Q(current_year=True) & (
                        ~Q(id__in=rounds_registered) | Q(id=current_round_id)
                    )
                )
            else:
                available_rounds = Round.objects.filter(current_year=True).exclude(id__in=rounds_registered)

            self.fields['round'].queryset = available_rounds

        form_action = reverse('mscc:service_education_add', kwargs={'registry': self.registry})
        if instance:
            form_action = reverse(
                'mscc:service_education_edit',
                kwargs={'registry': self.registry, 'pk': instance}
            )

        self.helper = FormHelper()
        self.helper.form_show_labels = True
        self.helper.form_action = form_action
        self.helper.layout = Layout(
            Div(
                Fieldset(
                    _('Current Educational Status'),
                    Div(
                        Div('education_status', css_class='col-md-6'),
                        Div('dropout_date', css_class='col-md-6'),
                        css_class='row mb-3'
                    ),
                    Div(
                        Div('round', css_class='col-md-6'),
                        css_class='row mb-3'
                    ),
                ),
                Fieldset(
                    _('Program Enrollment Details'),
                    Div(
                        Div('education_program', css_class='col-md-6'),
                        Div('catch_up_registered', css_class='col-md-6'),
                        css_class='row mb-3' + display_edu_section
                    ),
                    Div(
                        Div('class_section', css_class='col-md-6'),
                        Div('registration_date', css_class='col-md-6'),
                        css_class='row mb-3' + display_edu_section
                    ),
                    css_class='mt-4'
                ),
                css_id='step-1'
            ),
            FormActions(
                Submit('save', _('Save Education Data'),
                       css_class='btn btn-primary px-5 fw-bold shadow-sm'),
                HTML(
                    '<a class="btn btn-outline-secondary ms-2" id="cancel-id-cancel" href="/mscc/child-registration-cancel/{}/">Cancel</a>'.format(
                        self.registry)
                ),
                css_class='d-flex justify-content-end border-top pt-4 mt-4'
            ),
        )

    def save(self, request=None, instance=None, registry=None):
        validated_data = request.POST

        if not instance:
            instance = EducationService.objects.create(registration_id=registry)
        else:
            instance = EducationService.objects.get(id=instance)
            old_class_section = instance.class_section
            new_class_section = validated_data.get('class_section')

            if str(old_class_section) != str(new_class_section):
                update_child_attendance(
                    instance.registration.id,
                    instance.education_program,
                    old_class_section,
                    new_class_section
                )

        instance.education_status = validated_data.get('education_status')

        dropout_date_str = validated_data.get('dropout_date')
        if dropout_date_str:
            try:
                instance.dropout_date = validate_date(dropout_date_str)
            except ValidationError as e:
                raise ValidationError("Dropout date error: {}".format(e))

        instance.education_program = validated_data.get('education_program')
        instance.class_section = validated_data.get('class_section')
        instance.round_id = validated_data.get('round')

        registration_date_str = validated_data.get('registration_date')
        if registration_date_str:
            try:
                parsed_registration_date = validate_date(registration_date_str)

                registration_obj = Registration.objects.get(id=registry)



                if parsed_registration_date > date.today():
                    raise ValidationError(
                        "Date of registration in the round cannot be in the future"
                    )

                instance.registration_date = parsed_registration_date

            except ValidationError as e:
                raise ValidationError("Registration date error: {}".format(e))

        instance.save()

        registry = instance.registration
        registry.round_id = instance.round_id
        registry.save()

        messages.success(request, _('Your data has been sent successfully to the server'))

        return instance

    def clean(self):
        cleaned_data = super(EducationServiceForm, self).clean()

        class_section = cleaned_data.get("class_section")
        registration_date = cleaned_data.get("registration_date")
        dropout_date = cleaned_data.get("dropout_date")
        education_status = cleaned_data.get("education_status")

        if not class_section:
            self.add_error("class_section", "This field is required")

        if not registration_date:
            self.add_error("registration_date", "This field is required")
        else:
            if registration_date > date.today():
                self.add_error(
                    "registration_date",
                    "Date of registration in the round cannot be in the future"
                )

            if self.registry:
                try:
                    registration_obj = Registration.objects.get(id=self.registry)

                # IMPORTANT:
                # replace registration_date below with the REAL field name from Registration model
                    main_registration_date = registration_obj.registration_date

                    if main_registration_date and registration_date < main_registration_date:
                        self.add_error(
                            "registration_date",
                            "Date of registration in the round cannot be before Registration date"
                        )

                except Registration.DoesNotExist:
                    self.add_error("registration_date", "Invalid registration")

        if dropout_date:
            try:
                validate_date(dropout_date)
            except ValidationError as e:
                self.add_error("dropout_date", str(e))

        if education_status == 'Currently registered in Formal Education school but not attending' and not dropout_date:
            self.add_error('dropout_date', 'This field is required')

        return cleaned_data

    class Meta:
        model = EducationService
        fields = (
            'registration_id',
            'education_status',
            'dropout_date',
            'round',
            'education_program',
            'class_section',
            'registration_date',
        )


class EducationRSServiceForm(forms.ModelForm):
    school = forms.ModelChoiceField(
        queryset=School.objects.filter(is_bma=True).order_by('name'),
        widget=forms.Select,
        empty_label='-------',
        label=_('Name of public School'),
        required=True,
        to_field_name='id',
    )
    shift = forms.ChoiceField(
        label=_("First or Second shift schools"),
        widget=forms.Select,
        required=False,
        choices=EducationRSService.SCHOOL_SHIFTS
    )
    support_needed = forms.MultipleChoiceField(
        label=_('Needed Support?'),
        choices=EducationRSService.SUPPORT_NEEDED,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    registration_id = forms.CharField(widget=forms.HiddenInput, required=False)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        registry = kwargs.pop('registry', None)
        pk = kwargs.pop('pk', None)

        super(EducationRSServiceForm, self).__init__(*args, **kwargs)

        form_action = reverse('mscc:service_education_rs_add', kwargs={'registry': registry})
        if pk:
            form_action = reverse('mscc:service_education_rs_edit',
                                  kwargs={'registry': registry, 'pk': pk})
        self.helper = FormHelper()
        self.helper.form_show_labels = True
        self.helper.form_action = form_action
        self.helper.layout = Layout(
            Div(
                Div(
                    HTML('<span class="badge-form badge-pill">1</span>'),
                    Div('school', css_class='col-md-6'),
                    HTML('<span class="badge-form badge-pill">2</span>'),
                    Div('shift', css_class='col-md-3'),
                    css_class='row card-body'
                ),
                Div(
                    HTML('<span class="badge-form badge-pill">3</span>'),
                    Div('support_needed', css_class='col-md-3 multiple-choice'),
                    css_class='row card-body'
                ),
                css_id='step-1'
            ),

            FormActions(
                Submit('save', 'Save',
                       css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-success'),
                Reset('reset', 'Reset',
                      css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-warning'),
            ),
        )

    def save(self, request=None, instance=None, registry=None):

        validated_data = request.POST

        if not instance:
            instance = EducationRSService.objects.create(registration_id=registry)
        else:
            instance = EducationRSService.objects.get(id=instance)

        instance.school_id = validated_data.get('school')

        instance.shift = validated_data.get('shift')
        instance.support_needed = validated_data.getlist('support_needed')
        instance.save()
        messages.success(request, _('Your data has been sent successfully to the server'))

        return instance

    class Meta:
        model = EducationRSService
        fields = (
            'school',
            'shift',
            'support_needed',
        )


class EducationGradingForm(forms.ModelForm):
    participation = forms.ChoiceField(
        label=_("Child Level of participation / Absence"),
        widget=forms.Select, required=False,
        choices=EducationAssessment.PARTICIPATION
    )
    barriers = forms.ChoiceField(
        label=_('The main barriers affecting the child\'s '
                'daily attendance/participation, performance, or causing drop-out'),
        widget=forms.Select, required=False,
        choices=EducationAssessment.BARRIERS
    )
    barriers_other = forms.CharField(
        label=_('If Other, Please specify'),
        widget=forms.TextInput, required= False
    )
    post_test_done = forms.ChoiceField(
        label=_('Did the child undertake the Post tests?'),
        widget=forms.Select, required=False,
        choices=YES_NO
    )
    school_year_completed = forms.ChoiceField(
        label=_('Did the child fully complete the school year?'),
        widget=forms.Select, required=False,
        choices=YES_NO
    )

    arabic_grade = forms.IntegerField(
        label=_('Arabic Grade'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        required=False,
        initial=0
    )
    language_grade = forms.IntegerField(
        label=_('Foreign Language Grade'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        required=False,
        initial=0
    )
    english_grade = forms.IntegerField(
        label=_('English Grade'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        required=False,
        initial=0
    )
    french_grade = forms.IntegerField(
        label=_('French Grade'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        required=False,
        initial=0
    )
    math_grade = forms.IntegerField(
        label=_('Mathematics Grade'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        required=False,
        initial=0
    )
    science_grade = forms.IntegerField(
        label=_('Sciences Grade'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        required=False,
        initial=0
    )
    biology_grade = forms.IntegerField(
        label=_('Biology Grade'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        required=False,
        initial=0
    )
    chemistry_grade = forms.IntegerField(
        label=_('Chemistry Grade'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        required=False,
        initial=0
    )
    physics_grade = forms.IntegerField(
        label=_('Physics Grade'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        required=False,
        initial=0
    )
    social_emotional_grade = forms.IntegerField(
        label=_('Social-Emotional Development Grade'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        required=False,
        initial=0
    )
    artistic_grade = forms.IntegerField(
        label=_('Artistic Development Grade'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        required=False,
        initial=0
    )
    psychomotor_grade = forms.IntegerField(
        label=_('Psychomotor Development Grade'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        required=False,
        initial=0
    )
    registration_id = forms.CharField(widget=forms.HiddenInput, required=False)
    programme_type = forms.CharField(widget=forms.HiddenInput, required=False)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        registry = kwargs.pop('registry', None)
        programme_type = kwargs.pop('programme_type', None)
        pre_post = kwargs.pop('pre_post', None)
        instance = kwargs.pop('instance', None)

        super(EducationGradingForm, self).__init__(*args, **kwargs)

        center = getattr(getattr(self.request, 'user', None), 'center', None)
        provide_french_language = getattr(center, 'provide_french_language', None) == "Yes"
        self.provide_french_language = provide_french_language
        self.fields['barriers_other'].required = False

        if self.data.get('barriers') == 'Other':
            self.fields['barriers_other'].required = True
        form_action = reverse('mscc:service_education_grading_add',
                              kwargs={'registry': registry, 'programme_type': programme_type})
        if instance:
            form_action = reverse('mscc:service_education_grading_edit',
                                  kwargs={'registry': registry, 'programme_type': programme_type, 'pre_post': pre_post,
                                          'pk': instance})

        if programme_type:
            self.fields['programme_type'].initial = programme_type

        if programme_type == "BLN Level 1":
            field_init(self.fields['arabic_grade'], 'Arabic Language Development', 68)
            field_init(self.fields['english_grade'], 'English Language Development', 43)
            field_init(self.fields['french_grade'], 'French Language Development', 43)
            field_init(self.fields['math_grade'], 'Mathematics', 22)
            if provide_french_language:
                self.fields['english_grade'].hidden_widget()
                self.fields['english_grade'].required = False
            else:
                self.fields['french_grade'].hidden_widget()
                self.fields['french_grade'].required = False
            self.fields['social_emotional_grade'].hidden_widget()
            self.fields['social_emotional_grade'].required = False
            self.fields['artistic_grade'].hidden_widget()
            self.fields['artistic_grade'].required = False
            self.fields['language_grade'].hidden_widget()
            self.fields['language_grade'].required = False
            self.fields['science_grade'].hidden_widget()
            self.fields['biology_grade'].hidden_widget()
            self.fields['chemistry_grade'].hidden_widget()
            self.fields['physics_grade'].hidden_widget()
            self.fields['psychomotor_grade'].hidden_widget()

        if programme_type == "BLN Level 2":
            field_init(self.fields['arabic_grade'], 'Arabic Language Development', 70)
            field_init(self.fields['english_grade'], 'English Language Development', 65)
            field_init(self.fields['french_grade'], 'French Language Development', 65)
            field_init(self.fields['math_grade'], 'Mathematics', 32)
            if provide_french_language:
                self.fields['english_grade'].hidden_widget()
                self.fields['english_grade'].required = False
            else:
                self.fields['french_grade'].hidden_widget()
                self.fields['french_grade'].required = False
            self.fields['social_emotional_grade'].hidden_widget()
            self.fields['social_emotional_grade'].required = False
            self.fields['artistic_grade'].hidden_widget()
            self.fields['artistic_grade'].required = False
            self.fields['language_grade'].hidden_widget()
            self.fields['language_grade'].required = False
            self.fields['science_grade'].hidden_widget()
            self.fields['biology_grade'].hidden_widget()
            self.fields['chemistry_grade'].hidden_widget()
            self.fields['physics_grade'].hidden_widget()
            self.fields['psychomotor_grade'].hidden_widget()

        if programme_type == "BLN Level 3":
            field_init(self.fields['arabic_grade'], 'Arabic Language Development', 69)
            field_init(self.fields['english_grade'], 'English Language Development', 64)
            field_init(self.fields['french_grade'], 'French Language Development', 59)
            field_init(self.fields['math_grade'], 'Mathematics', 32)
            if provide_french_language:
                self.fields['english_grade'].hidden_widget()
                self.fields['english_grade'].required = False
            else:
                self.fields['french_grade'].hidden_widget()
                self.fields['french_grade'].required = False
            self.fields['social_emotional_grade'].hidden_widget()
            self.fields['social_emotional_grade'].required = False
            self.fields['artistic_grade'].hidden_widget()
            self.fields['artistic_grade'].required = False
            self.fields['language_grade'].hidden_widget()
            self.fields['language_grade'].required = False
            self.fields['science_grade'].hidden_widget()
            self.fields['biology_grade'].hidden_widget()
            self.fields['chemistry_grade'].hidden_widget()
            self.fields['physics_grade'].hidden_widget()
            self.fields['psychomotor_grade'].hidden_widget()

        if programme_type == "CBECE Level 1":
            field_init(self.fields['language_grade'], 'Language Development', 48)
            field_init(self.fields['math_grade'], 'Cognitive Development - Mathematics', 24)
            field_init(self.fields['science_grade'], 'Cognitive Development - Science', 18)
            field_init(self.fields['social_emotional_grade'], 'Social-Emotional Development', 14)
            field_init(self.fields['psychomotor_grade'], 'Psychomotor Development', 20)
            field_init(self.fields['artistic_grade'], 'Artistic Development', 10)
            self.fields['arabic_grade'].hidden_widget()
            self.fields['biology_grade'].hidden_widget()
            self.fields['chemistry_grade'].hidden_widget()
            self.fields['physics_grade'].hidden_widget()
            self.fields['english_grade'].hidden_widget()
            self.fields['french_grade'].hidden_widget()

        if programme_type == "CBECE Level 2":
            field_init(self.fields['arabic_grade'], 'Arabic Language Development', 66)
            field_init(self.fields['language_grade'], 'Foreign Language Development', 66)
            field_init(self.fields['math_grade'], 'Cognitive Development - Mathematics', 48)
            field_init(self.fields['science_grade'], 'Cognitive Development - Science', 38)
            field_init(self.fields['social_emotional_grade'], 'Social-Emotional Development', 40)
            field_init(self.fields['psychomotor_grade'], 'Psychomotor Development', 40)
            field_init(self.fields['artistic_grade'], 'Artistic Development', 16)
            self.fields['biology_grade'].hidden_widget()
            self.fields['chemistry_grade'].hidden_widget()
            self.fields['physics_grade'].hidden_widget()
            self.fields['english_grade'].hidden_widget()
            self.fields['french_grade'].hidden_widget()

        if programme_type == "CBECE Level 3":
            field_init(self.fields['arabic_grade'], 'Arabic Language Development', 74)
            field_init(self.fields['language_grade'], 'Foreign Language Development', 74)
            field_init(self.fields['math_grade'], 'Cognitive Development - Mathematics', 50)
            field_init(self.fields['science_grade'], 'Cognitive Development - Science', 38)
            field_init(self.fields['social_emotional_grade'], 'Social-Emotional Development', 40)
            field_init(self.fields['psychomotor_grade'], 'Psychomotor Development', 42)
            field_init(self.fields['artistic_grade'], 'Artistic Development', 16)
            self.fields['biology_grade'].hidden_widget()
            self.fields['chemistry_grade'].hidden_widget()
            self.fields['physics_grade'].hidden_widget()
            self.fields['english_grade'].hidden_widget()
            self.fields['french_grade'].hidden_widget()

        if programme_type in ["RS Grade 1", "RS Grade 2", "RS Grade 3"]:
            field_init(self.fields['arabic_grade'], 'Arabic Language', 20)
            field_init(self.fields['language_grade'], 'Foreign Language', 20)
            field_init(self.fields['math_grade'], 'Mathematics', 20)
            field_init(self.fields['science_grade'], 'Science', 20)

            self.fields['biology_grade'].hidden_widget()
            self.fields['chemistry_grade'].hidden_widget()
            self.fields['physics_grade'].hidden_widget()
            self.fields['social_emotional_grade'].hidden_widget()
            self.fields['psychomotor_grade'].hidden_widget()
            self.fields['artistic_grade'].hidden_widget()
            self.fields['english_grade'].hidden_widget()
            self.fields['french_grade'].hidden_widget()

        display_post_fields_css = 'd-none'
        display_pre_fields_css = ''
        badge_css = 'badge-form'
        grade_field_css = ''
        ctr = 0
        if pre_post == 'post':
            ctr = 4
            badge_css = 'badge-form-2'
            grade_field_css = 'grade-field'
            display_post_fields_css = ''
            display_pre_fields_css = ' d-none'
            self.fields['participation'].required = True
            self.fields['barriers'].required = True
            self.fields['post_test_done'].required = True
            self.fields['school_year_completed'].required = True

        self.helper = FormHelper()
        self.helper.form_show_labels = True
        self.helper.form_action = form_action

        if programme_type in ["BLN Level 1", "BLN Level 2", "BLN Level 3"]:
            language_field = 'french_grade' if provide_french_language else 'english_grade'
            self.helper.layout = Layout(
                Div(
                    Div(
                        HTML('<span class="badge-form badge-pill">1</span>'),
                        Div('participation', css_class='col-md-4'),
                        css_class='row card-body ' + display_post_fields_css
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">2</span>'),
                        Div('barriers', css_class='col-md-8'),
                        Div('barriers_other', css_class='col-md-3'),
                        css_class='row card-body ' + display_post_fields_css
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">3</span>'),
                        Div('post_test_done', css_class='col-md-5'),
                        HTML('<span class="badge-form badge-pill">4</span>'),
                        Div('school_year_completed', css_class='col-md-5'),
                        css_class='row card-body ' + display_post_fields_css
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">' + str(1 + ctr) + '</span>'),
                        Div('arabic_grade', css_class='col-md-4'),
                        HTML('<span class="badge-form badge-pill">' + str(2 + ctr) + '</span>'),
                        Div(language_field, css_class='col-md-4'),
                        css_class='row card-body ' + grade_field_css + display_pre_fields_css
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">' + str(3 + ctr) + '</span>'),
                        Div('math_grade', css_class='col-md-4'),
                        css_class='row card-body ' + grade_field_css + display_pre_fields_css
                    ),
                    FormActions(
                        Submit('save', 'Save',
                               css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-success'),
                        Reset('reset', 'Reset',
                              css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-warning'),
                    ),
                    css_id='step-1'
                ),
            )

        if programme_type in ["CBECE Level 1"]:
            self.helper.layout = Layout(
                Div(
                    Div(
                        HTML('<span class="badge-form badge-pill">1</span>'),
                        Div('participation', css_class='col-md-4'),
                        css_class='row card-body ' + display_post_fields_css
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">2</span>'),
                        Div('barriers', css_class='col-md-8'),
                        Div('barriers_other', css_class='col-md-3'),
                        css_class='row card-body ' + display_post_fields_css
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">3</span>'),
                        Div('post_test_done', css_class='col-md-5'),
                        HTML('<span class="badge-form badge-pill">4</span>'),
                        Div('school_year_completed', css_class='col-md-5'),
                        css_class='row card-body ' + display_post_fields_css
                    ),
                    Div(
                        HTML('<span class="' + badge_css + ' badge-pill">' + str(1 + ctr) + '</span>'),
                        Div('language_grade', css_class='col-md-4'),
                        HTML('<span class="' + badge_css + ' badge-pill">' + str(2 + ctr) + '</span>'),
                        Div('math_grade', css_class='col-md-4'),
                        css_class='row card-body ' + grade_field_css + display_pre_fields_css
                    ),
                    Div(
                        HTML('<span class="' + badge_css + ' badge-pill">' + str(3 + ctr) + '</span>'),
                        Div('science_grade', css_class='col-md-4'),
                        HTML('<span class="' + badge_css + ' badge-pill">' + str(4 + ctr) + '</span>'),
                        Div('psychomotor_grade', css_class='col-md-4'),
                        css_class='row card-body ' + grade_field_css + display_pre_fields_css
                    ),
                    Div(
                        HTML('<span class="' + badge_css + ' badge-pill">' + str(5 + ctr) + '</span>'),
                        Div('social_emotional_grade', css_class='col-md-4'),
                        HTML('<span class="' + badge_css + ' badge-pill">' + str(6 + ctr) + '</span>'),
                        Div('artistic_grade', css_class='col-md-4'),
                        css_class='row card-body ' + grade_field_css + display_pre_fields_css
                    ),
                    FormActions(
                        Submit('save', 'Save',
                               css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-success'),
                        Reset('reset', 'Reset',
                              css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-warning'),
                    ),
                    css_id='step-1'
                ),
            )

        if programme_type in ["CBECE Level 2", "CBECE Level 3"]:
            self.helper.layout = Layout(
                Div(
                    Div(
                        HTML('<span class="badge-form badge-pill">1</span>'),
                        Div('participation', css_class='col-md-4'),
                        css_class='row card-body ' + display_post_fields_css
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">2</span>'),
                        Div('barriers', css_class='col-md-8'),
                        Div('barriers_other', css_class='col-md-3'),
                        css_class='row card-body ' + display_post_fields_css
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">3</span>'),
                        Div('post_test_done', css_class='col-md-5'),
                        HTML('<span class="badge-form badge-pill">4</span>'),
                        Div('school_year_completed', css_class='col-md-5'),
                        css_class='row card-body ' + display_post_fields_css
                    ),
                    Div(
                        HTML('<span class="' + badge_css + ' badge-pill">' + str(1 + ctr) + '</span>'),
                        Div('arabic_grade', css_class='col-md-4'),
                        HTML('<span class="' + badge_css + ' badge-pill">' + str(2 + ctr) + '</span>'),
                        Div('language_grade', css_class='col-md-4'),
                        css_class='row card-body ' + grade_field_css + display_pre_fields_css
                    ),
                    Div(
                        HTML('<span class="' + badge_css + ' badge-pill">' + str(3 + ctr) + '</span>'),
                        Div('math_grade', css_class='col-md-4'),
                        HTML('<span class="' + badge_css + ' badge-pill">' + str(4 + ctr) + '</span>'),
                        Div('science_grade', css_class='col-md-4'),
                        css_class='row card-body ' + grade_field_css + display_pre_fields_css
                    ),
                    Div(
                        HTML('<span class="' + badge_css + ' badge-pill">' + str(5 + ctr) + '</span>'),
                        Div('psychomotor_grade', css_class='col-md-4'),
                        HTML('<span class="' + badge_css + ' badge-pill">' + str(6 + ctr) + '</span>'),
                        Div('social_emotional_grade', css_class='col-md-4'),
                        css_class='row card-body ' + grade_field_css + display_pre_fields_css
                    ),
                    Div(
                        HTML('<span class="' + badge_css + ' badge-pill">' + str(7 + ctr) + '</span>'),
                        Div('artistic_grade', css_class='col-md-4'),
                        css_class='row card-body ' + grade_field_css + display_pre_fields_css
                    ),
                    FormActions(
                        Submit('save', 'Save',
                               css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-success'),
                        Reset('reset', 'Reset',
                              css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-warning'),
                    ),
                    css_id='step-1'
                ),
            )

        if programme_type in ["RS Grade 1", "RS Grade 2", "RS Grade 3"]:
            self.helper.layout = Layout(
                Div(
                    Div(
                        HTML('<span class="badge-form badge-pill">1</span>'),
                        Div('participation', css_class='col-md-4'),
                        css_class='row card-body ' + display_post_fields_css
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">2</span>'),
                        Div('barriers', css_class='col-md-8'),
                        Div('barriers_other', css_class='col-md-3'),
                        css_class='row card-body ' + display_post_fields_css
                    ),
                    Div(
                        HTML('<span class="badge-form-2 badge-pill">3</span>'),
                        Div('post_test_done', css_class='col-md-5'),
                        HTML('<span class="badge-form-2 badge-pill">4</span>'),
                        Div('school_year_completed', css_class='col-md-5'),
                        css_class='row card-body ' + display_post_fields_css
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">' + str(1 + ctr) + '</span>'),
                        Div('arabic_grade', css_class='col-md-4'),
                        HTML('<span class="badge-form badge-pill">' + str(2 + ctr) + '</span>'),
                        Div('language_grade', css_class='col-md-4'),
                        css_class='row card-body ' + grade_field_css + display_pre_fields_css
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">' + str(3 + ctr) + '</span>'),
                        Div('math_grade', css_class='col-md-4'),
                        HTML('<span class="badge-form badge-pill">' + str(4 + ctr) + '</span>'),
                        Div('science_grade', css_class='col-md-4'),
                        css_class='row card-body ' + grade_field_css + display_pre_fields_css
                    ),
                    FormActions(
                        Submit('save', 'Save',
                               css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-success'),
                        Reset('reset', 'Reset',
                              css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-warning'),
                    ),
                    css_id='step-1'
                ),
            )

    def save(self, request=None, instance=None, registry=None, programme_type=None, pre_post=None):

        if not instance:
            instance = EducationProgrammeAssessment.objects.create(registration_id=registry)
            instance.pre_test = request.POST
        else:
            instance = EducationProgrammeAssessment.objects.get(id=instance)
            if pre_post == "pre":
                instance.pre_test = request.POST
            if pre_post == "post":
                instance.post_test = request.POST

        instance.programme_type = programme_type
        instance.save()

        messages.success(request, _('Your data has been sent successfully to the server'))

        return instance

    def clean(self):

        cleaned_data = super(EducationGradingForm, self).clean()
        programme_type = cleaned_data.get("programme_type")

        # Validation thresholds for each programme type
        thresholds = {
            "BLN Level 1": {
                "arabic_grade": 68,
                "english_grade": 43,
                "french_grade": 43,
                "math_grade": 22,
                "social_emotional_grade": 24,
                "artistic_grade": 10,
            },
            "BLN Level 2": {
                "arabic_grade": 70,
                "english_grade": 65,
                "french_grade": 65,
                "math_grade": 32,
                "social_emotional_grade": 24,
                "artistic_grade": 10,
            },
            "BLN Level 3": {
                "arabic_grade": 69,
                "english_grade": 64,
                "french_grade": 59,
                "math_grade": 32,
                "social_emotional_grade": 24,
                "artistic_grade": 10,
            },
            "CBECE Level 1": {
                "language_grade": 48,
                "math_grade": 24,
                "science_grade": 18,
                "social_emotional_grade": 14,
                "psychomotor_grade": 20,
                "artistic_grade": 10,
            },
            "CBECE Level 2": {
                "arabic_grade": 66,
                "language_grade": 66,
                "math_grade": 48,
                "science_grade": 38,
                "social_emotional_grade": 40,
                "psychomotor_grade": 40,
                "artistic_grade": 16,
            },
            "CBECE Level 3": {
                "arabic_grade": 74,
                "language_grade": 74,
                "math_grade": 50,
                "science_grade": 38,
                "social_emotional_grade": 40,
                "psychomotor_grade": 42,
                "artistic_grade": 16,
            },
            "RS Grade 1": {
                "arabic_grade": 20,
                "language_grade": 20,
                "math_grade": 20,
                "science_grade": 20,
            },
            "RS Grade 2": {
                "arabic_grade": 20,
                "language_grade": 20,
                "math_grade": 20,
                "science_grade": 20,
            },
            "RS Grade 3": {
                "arabic_grade": 20,
                "language_grade": 20,
                "math_grade": 20,
                "science_grade": 20,
            },
        }

        if programme_type in thresholds:
            programme_thresholds = thresholds[programme_type]

            # Iterate through the thresholds to validate each field
            for field, max_value in programme_thresholds.items():
                field_value = cleaned_data.get(field)
                if field_value is not None and field_value > max_value:
                    self.add_error(field, "This value is greater than " + str(max_value))

        return cleaned_data

    class Meta:
        model = EducationProgrammeAssessment
        fields = (
            'programme_type',
        )


class YouthScoringForm(forms.ModelForm):
    participation = forms.ChoiceField(
        label=_("Child Level of participation / Absence"),
        widget=forms.Select, required=False,
        choices=EducationAssessment.PARTICIPATION
    )
    barriers = forms.ChoiceField(
        label=_('The main barriers affecting the child\'s '
                'daily attendance/participation, performance, or causing drop-out'),
        widget=forms.Select, required=False,
        choices=EducationAssessment.BARRIERS
    )
    barriers_other = forms.CharField(
        label=_('If Other, Please specify'),
        widget=forms.TextInput, required=False
    )
    post_test_done = forms.ChoiceField(
        label=_('Did the child undertake the Post tests?'),
        widget=forms.Select, required=False,
        choices=YES_NO
    )
    school_year_completed = forms.ChoiceField(
        label=_('Did the child fully complete the school year?'),
        widget=forms.Select, required=False,
        choices=YES_NO
    )

    arabic_grade = forms.IntegerField(
        label=_('Arabic'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        required=False,
        initial=0
    )
    language_grade = forms.IntegerField(
        label=_('Foreign Language'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        required=False,
        initial=0
    )
    math_grade = forms.IntegerField(
        label=_('Mathematics'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        required=False,
        initial=0
    )
    life_skills = forms.IntegerField(
        label=_('Life Skills'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        required=False,
        initial=0
    )
    english_development = forms.IntegerField(
        label=_('English Development'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        required=False,
        initial=0
    )
    financial_development = forms.IntegerField(
        label=_('Financial Literacy Development'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        required=False,
        initial=0
    )
    it_development = forms.IntegerField(
        label=_('IT Development'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        required=False,
        initial=0
    )
    registration_id = forms.CharField(widget=forms.HiddenInput, required=False)
    programme_type = forms.CharField(widget=forms.HiddenInput, required=False)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        registry = kwargs.pop('registry', None)
        programme_type = kwargs.pop('programme_type', None)
        pre_post = kwargs.pop('pre_post', 'pre')
        instance = kwargs.pop('instance', None)

        super(YouthScoringForm, self).__init__(*args, **kwargs)

        form_action = reverse('mscc:service_youth_scoring_add',
                              kwargs={'registry': registry, 'programme_type': programme_type})
        if instance:
            form_action = reverse('mscc:service_youth_scoring_edit',
                                  kwargs={'registry': registry, 'programme_type': programme_type, 'pre_post': pre_post,
                                          'pk': instance})

        if programme_type:
            self.fields['programme_type'].initial = programme_type
            if self.data:
                self.data = self.data.copy()
                self.data['programme_type'] = programme_type

        if programme_type == "YBLN Level 1":
            field_init(self.fields['arabic_grade'], 'Arabic Language Development', 12)
            field_init(self.fields['language_grade'], 'Foreign Language Development', 0)
            field_init(self.fields['math_grade'], 'Mathematics', 15)
            field_init(self.fields['life_skills'], 'Life Skills Development', 12)
            self.fields['english_development'].hidden_widget()
            self.fields['financial_development'].hidden_widget()
            self.fields['it_development'].hidden_widget()

        if programme_type == "YBLN Level 2":
            field_init(self.fields['arabic_grade'], 'Arabic Language Development', 12)
            field_init(self.fields['language_grade'], 'Foreign Language Development', 12)
            field_init(self.fields['math_grade'], 'Mathematics', 21)
            field_init(self.fields['life_skills'], 'Life Skills Development', 12)
            self.fields['english_development'].hidden_widget()
            self.fields['financial_development'].hidden_widget()
            self.fields['it_development'].hidden_widget()

        if programme_type in ["YFS Level 1", "YFS Level 2", "YFS Level 1 - RS Grade 9", "YFS Level 2 - RS Grade 9"]:
            field_init(self.fields['english_development'], 'English Development', 100)
            field_init(self.fields['financial_development'], 'Financial Literacy Development', 100)
            field_init(self.fields['it_development'], 'IT Development', 100)
            self.fields['arabic_grade'].hidden_widget()
            self.fields['language_grade'].hidden_widget()
            self.fields['math_grade'].hidden_widget()
            self.fields['life_skills'].hidden_widget()

        display_post_fields_css = 'd-none'
        display_pre_fields_css = ''
        badge_css = 'badge-form'
        grade_field_css = ''
        ctr = 0
        if pre_post == 'post':
            ctr = 4
            badge_css = 'badge-form-2'
            grade_field_css = 'grade-field'
            display_post_fields_css = ''
            display_pre_fields_css = ' d-none'
            self.fields['participation'].required = True
            self.fields['barriers'].required = True
            self.fields['post_test_done'].required = True
            self.fields['school_year_completed'].required = True

        self.helper = FormHelper()
        self.helper.form_show_labels = True
        self.helper.form_action = form_action

        if programme_type in ["YBLN Level 1", "YBLN Level 2"]:
            self.helper.layout = Layout(
                Div(
                    Div(
                        HTML('<span class="badge-form badge-pill">1</span>'),
                        Div('participation', css_class='col-md-4'),
                        css_class='row card-body ' + display_post_fields_css
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">2</span>'),
                        Div('barriers', css_class='col-md-8'),
                        Div('barriers_other', css_class='col-md-3'),
                        css_class='row card-body ' + display_post_fields_css
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">3</span>'),
                        Div('post_test_done', css_class='col-md-5'),
                        HTML('<span class="badge-form badge-pill">4</span>'),
                        Div('school_year_completed', css_class='col-md-5'),
                        css_class='row card-body ' + display_post_fields_css
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">' + str(1 + ctr) + '</span>'),
                        Div('arabic_grade', css_class='col-md-4'),
                        HTML('<span class="badge-form badge-pill">' + str(2 + ctr) + '</span>'),
                        Div('language_grade', css_class='col-md-4'),
                        css_class='row card-body ' + grade_field_css + display_pre_fields_css
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">' + str(3 + ctr) + '</span>'),
                        Div('math_grade', css_class='col-md-4'),
                        HTML('<span class="badge-form badge-pill">' + str(4 + ctr) + '</span>'),
                        Div('life_skills', css_class='col-md-4'),
                        css_class='row card-body ' + grade_field_css + display_pre_fields_css
                    ),
                    FormActions(
                        Submit('save', 'Save',
                               css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-success'),
                        Reset('reset', 'Reset',
                              css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-warning'),
                    ),
                    css_id='step-1'
                ),
            )

        if programme_type in ["YFS Level 1", "YFS Level 2", "YFS Level 1 - RS Grade 9", "YFS Level 2 - RS Grade 9"]:
            self.helper.layout = Layout(
                Div(
                    Div(
                        HTML('<span class="badge-form badge-pill">1</span>'),
                        Div('participation', css_class='col-md-4'),
                        css_class='row card-body ' + display_post_fields_css
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">2</span>'),
                        Div('barriers', css_class='col-md-8'),
                        Div('barriers_other', css_class='col-md-3'),
                        css_class='row card-body ' + display_post_fields_css
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">3</span>'),
                        Div('post_test_done', css_class='col-md-5'),
                        HTML('<span class="badge-form badge-pill">4</span>'),
                        Div('school_year_completed', css_class='col-md-5'),
                        css_class='row card-body ' + display_post_fields_css
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">' + str(1 + ctr) + '</span>'),
                        Div('english_development', css_class='col-md-4'),
                        HTML('<span class="badge-form badge-pill">' + str(2 + ctr) + '</span>'),
                        Div('financial_development', css_class='col-md-4'),
                        css_class='row card-body ' + grade_field_css + display_pre_fields_css
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">' + str(3 + ctr) + '</span>'),
                        Div('it_development', css_class='col-md-4'),
                        css_class='row card-body ' + grade_field_css + display_pre_fields_css
                    ),
                    FormActions(
                        Submit('save', 'Save',
                               css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-success'),
                        Reset('reset', 'Reset',
                              css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-warning'),
                    ),
                    css_id='step-1'
                ),
            )

    def save(self, request=None, instance=None, registry=None, programme_type=None, pre_post=None):
        if not instance:
            instance = EducationProgrammeAssessment.objects.create(registration_id=registry)
            instance.pre_test = request.POST
        else:
            instance = EducationProgrammeAssessment.objects.get(id=instance)
            if pre_post == "pre":
                instance.pre_test = request.POST
            if pre_post == "post":
                instance.post_test = request.POST

        instance.programme_type = programme_type
        instance.save()

        messages.success(request, _('Your data has been sent successfully to the server'))

        return instance

    def clean(self):
        cleaned_data = super(YouthScoringForm, self).clean()
        programme_type = cleaned_data.get("programme_type") or self.initial.get("programme_type")
        thresholds = {
            "YBLN Level 1": {
                "arabic_grade": 12,
                "language_grade": 0,
                "math_grade": 15,
                "life_skills": 12,
            },
            "YBLN Level 2": {
                "arabic_grade": 12,
                "language_grade": 12,
                "math_grade": 21,
                "life_skills": 12,
            },
            "YFS Level 1": {
                "english_development": 100,
                "financial_development": 100,
                "it_development": 100,
            },
            "YFS Level 2": {
                "english_development": 100,
                "financial_development": 100,
                "it_development": 100,
            },
            "YFS Level 1 - RS Grade 9": {
                "english_development": 100,
                "financial_development": 100,
                "it_development": 100,
            },
            "YFS Level 2 - RS Grade 9": {
                "english_development": 100,
                "financial_development": 100,
                "it_development": 100,
            }
        }

        if programme_type in thresholds:
            programme_thresholds = thresholds[programme_type]

            for field, max_value in programme_thresholds.items():
                field_value = cleaned_data.get(field)
                if field_value is not None and field_value > max_value:
                    self.add_error(field, "This value is greater than {}".format(max_value))

        return cleaned_data

    class Meta:
        model = EducationProgrammeAssessment
        fields = (
            'programme_type',
        )


class EducationSchoolGradingForm(forms.ModelForm):
    arabic_grade = forms.IntegerField(
        widget=forms.NumberInput(attrs=({'maxlength': 4, 'max': 100})),
        required=False,
        label="Arabic Language",
        initial=0
    )
    language_grade = forms.IntegerField(
        widget=forms.NumberInput(attrs=({'maxlength': 4, 'max': 100})),
        required=False,
        label="Foreign Language",
        initial=0
    )
    math_grade = forms.IntegerField(
        widget=forms.NumberInput(attrs=({'maxlength': 4, 'max': 100})),
        required=False,
        label="Mathematics",
        initial=0
    )
    biology_grade = forms.IntegerField(
        widget=forms.NumberInput(attrs=({'maxlength': 4, 'max': 100})),
        required=False,
        label="Biology",
        initial=0
    )
    chemistry_grade = forms.IntegerField(
        widget=forms.NumberInput(attrs=({'maxlength': 4, 'max': 100})),
        required=False,
        label="Chemistry",
        initial=0
    )
    physics_grade = forms.IntegerField(
        widget=forms.NumberInput(attrs=({'maxlength': 4, 'max': 100})),
        required=False,
        label="Physics",
        initial=0
    )
    science_grade = forms.IntegerField(
        widget=forms.NumberInput(attrs=({'maxlength': 4, 'max': 100})),
        required=False,
        label="Science",
        initial=0
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        registry = kwargs.pop('registry', None)
        programme_type = kwargs.pop('programme_type', None)
        instance = kwargs.pop('instance', None)

        super(EducationSchoolGradingForm, self).__init__(*args, **kwargs)

        form_action = reverse('mscc:service_school_grading',
                              kwargs={'registry': registry, 'programme_type': programme_type, 'pk': instance})

        if programme_type in ["RS Grade 7", "RS Grade 8", "RS Grade 9", "YFS Level 1 - RS Grade 9", "YFS Level 2 - RS Grade 9"]:
            field_init(self.fields['arabic_grade'], 'Arabic Language', 20)
            field_init(self.fields['language_grade'], 'Foreign Language', 20)
            field_init(self.fields['math_grade'], 'Mathematics', 20)
            field_init(self.fields['biology_grade'], 'Biology', 20)
            field_init(self.fields['chemistry_grade'], 'Chemistry', 20)
            field_init(self.fields['physics_grade'], 'Physics', 20)
            self.fields['science_grade'].hidden_widget()

        if programme_type in ["RS Grade 1", "RS Grade 2", "RS Grade 3", "RS Grade 4", "RS Grade 5", "RS Grade 6"]:
            field_init(self.fields['arabic_grade'], 'Arabic Language', 20)
            field_init(self.fields['language_grade'], 'Foreign Language', 20)
            field_init(self.fields['math_grade'], 'Mathematics', 20)
            field_init(self.fields['science_grade'], 'Science', 20)

            self.fields['biology_grade'].hidden_widget()
            self.fields['chemistry_grade'].hidden_widget()
            self.fields['physics_grade'].hidden_widget()

        self.helper = FormHelper()
        self.helper.form_show_labels = True
        self.helper.form_action = form_action

        if programme_type in ["RS Grade 7", "RS Grade 8", "RS Grade 9", "YFS Level 1 - RS Grade 9", "YFS Level 2 - RS Grade 9"]:
            self.helper.layout = Layout(
                Div(
                    Div(
                        HTML('<span class="badge-form badge-pill">1</span>'),
                        Div('arabic_grade', css_class='col-md-4'),
                        HTML('<span class="badge-form badge-pill">2</span>'),
                        Div('language_grade', css_class='col-md-4'),
                        css_class='row card-body'
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">3</span>'),
                        Div('math_grade', css_class='col-md-4'),
                        HTML('<span class="badge-form badge-pill">4</span>'),
                        Div('biology_grade', css_class='col-md-4'),
                        css_class='row card-body'
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">5</span>'),
                        Div('chemistry_grade', css_class='col-md-4'),
                        HTML('<span class="badge-form badge-pill">6</span>'),
                        Div('physics_grade', css_class='col-md-4'),
                        css_class='row card-body'
                    ),

                    FormActions(
                        Submit('save', 'Save',
                               css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-success'),
                        Reset('reset', 'Reset',
                              css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-warning'),
                    ),
                    css_id='step-1'
                ),
            )

        if programme_type in ["RS Grade 1", "RS Grade 2", "RS Grade 3", "RS Grade 4", "RS Grade 5", "RS Grade 6"]:
            self.helper.layout = Layout(
                Div(
                    Div(
                        HTML('<span class="badge-form badge-pill">1</span>'),
                        Div('arabic_grade', css_class='col-md-4'),
                        HTML('<span class="badge-form badge-pill">2</span>'),
                        Div('language_grade', css_class='col-md-4'),
                        css_class='row card-body'
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">3</span>'),
                        Div('math_grade', css_class='col-md-4'),
                        HTML('<span class="badge-form badge-pill">4</span>'),
                        Div('science_grade', css_class='col-md-4'),
                        css_class='row card-body'
                    ),
                    FormActions(
                        Submit('save', 'Save',
                               css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-success'),
                        Reset('reset', 'Reset',
                              css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-warning'),
                    ),
                    css_id='step-1'
                ),
            )

    def save(self, request=None, instance=None):
        instance = EducationProgrammeAssessment.objects.get(id=instance)
        instance.school_test = request.POST
        instance.save()

        messages.success(request, _('Your data has been sent successfully to the server'))

        return instance

    def clean(self):
        cleaned_data = super(EducationSchoolGradingForm, self).clean()
        arabic_grade = cleaned_data.get("arabic_grade")
        language_grade = cleaned_data.get("language_grade")
        math_grade = cleaned_data.get("math_grade")
        biology_grade = cleaned_data.get("biology_grade")
        chemistry_grade = cleaned_data.get("chemistry_grade")
        physics_grade = cleaned_data.get("physics_grade")
        science_grade = cleaned_data.get("science_grade")

        if arabic_grade and arabic_grade > 20:
            self.add_error('arabic_grade', 'This value is greater that 20')
        if language_grade and language_grade > 20:
            self.add_error('language_grade', 'This value is greater that 20')
        if math_grade and math_grade > 20:
            self.add_error('math_grade', 'This value is greater that 20')
        if biology_grade and biology_grade > 20:
            self.add_error('biology_grade', 'This value is greater that 20')
        if chemistry_grade and chemistry_grade > 20:
            self.add_error('chemistry_grade', 'This value is greater that 20')
        if physics_grade and physics_grade > 20:
            self.add_error('physics_grade', 'This value is greater that 20')
        if science_grade and science_grade > 20:
            self.add_error('science_grade', 'This value is greater that 20')

    class Meta:
        model = EducationProgrammeAssessment
        fields = ()


def field_init(field, label_name, max_number):
    field.label = "{} / {}".format(label_name, str(max_number))
    field.widget.attrs['max'] = max_number
    field.required = True
