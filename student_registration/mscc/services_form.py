from __future__ import unicode_literals, absolute_import, division

from django.utils.translation import gettext as _
from django import forms
from django.urls import reverse
from django.contrib import messages
from django.core.exceptions import ValidationError

from crispy_forms.helper import FormHelper

from crispy_forms.bootstrap import (
    FormActions,
    InlineCheckboxes
)
from crispy_forms.layout import Layout, Fieldset, Button, Submit, Div, Field, HTML, Reset

from .utils import update_service, validate_date, TrimmedDateField
from .models import (
    PSSService,
    InclusionService,
    DigitalService,
    HealthNutritionService,
    HealthNutritionReferral,
    YouthKitService,
    YouthService,
    FollowUpService,
    YouthAssessment,
    YouthReferral,
    Recreational,
    LegoService,
    YES_NO,
    AGREE_DISAGREE
)


class PSSServiceForm(forms.ModelForm):

    child_registered = forms.ChoiceField(
        label=_("Is the child registered/ have birth registration?"),
        widget=forms.Select, required=True,
        choices=YES_NO
    )

    child_living_arrangement = forms.ChoiceField(
        widget=forms.Select, required=False,
        choices=PSSService.LIVING_ARRANGEMENT,
        label=_("What is the child's living arrangement?")
    )
    child_vulnerability = forms.ChoiceField(
        widget=forms.Select, required=True,
        choices=PSSService.CHILD_VULNERABILITY,
        label=_("Visible and known vulnerabilites of the child")
    )
    child_out_school_reasons = forms.ChoiceField(
        widget=forms.Select, required=True,
        choices=PSSService.OUT_SCHOOL_REASONS,
        label=_("Reasons for a child being out of school")
    )
    caregivers_distress = forms.ChoiceField(
        widget=forms.Select, required=True,
        choices=YES_NO,
        label=_('Do you feel distressed and anxious?')
    )
    caregivers_additional_parenting = forms.ChoiceField(
        widget=forms.Select, required=False,
        choices=YES_NO,
        label=_('If yes, would you like any additional parenting or psychosocial support?')
    )
    child_distress = forms.ChoiceField(
        widget=forms.Select, required=True,
        choices=YES_NO,
        label=_('Are any of the children in your HH experiencing any '
                       'signs of distress or negative mental health symptoms ?')
    )
    child_additional_parenting = forms.ChoiceField(
        widget=forms.Select, required=False,
        choices=YES_NO,
        label=_('If yes, do you need additional support '
                       'for taking care or better dealing with your children?')
    )
    child_know_seek_help = forms.ChoiceField(
        widget=forms.Select, required=True,
        choices=YES_NO,
        label=_('Does the child know where to seek help or support in case he is exposed to violence, abuse, or exploitation?')
    )

    child_protection_concern = forms.ChoiceField(
        widget=forms.Select, required=True,
        choices=PSSService.PROTECTION_CONCERN,
        label=_('Does the facilitator identify any child protection concern or has the caregiver expressed any of the below signs on their children?')

    )

    registration_id = forms.CharField(widget=forms.HiddenInput, required=False)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        registry = kwargs.pop('registry', None)
        instance = kwargs.pop('instance', None)

        super(PSSServiceForm, self).__init__(*args, **kwargs)

        form_action = reverse('mscc:service_pss_add', kwargs={'registry': registry})
        if instance:
            form_action = reverse('mscc:service_pss_edit', kwargs={'registry': registry, 'pk': instance})

        self.helper = FormHelper()
        self.helper.form_show_labels = True
        self.helper.form_action = form_action
        self.helper.layout = Layout(
            Div(
                Div(
                    HTML('<span class="badge-form badge-pill">1</span>'),
                    Div('child_registered', css_class='col-md-5'),
                    HTML('<span class="badge-form badge-pill">2</span>'),
                    Div('child_living_arrangement', css_class='col-md-6'),
                    css_class='row card-body'
                ),
                Div(
                    HTML('<span class="badge-form badge-pill">3</span>'),
                    Div('child_vulnerability', css_class='col-md-5'),
                    HTML('<span class="badge-form badge-pill">4</span>'),
                    Div('child_out_school_reasons', css_class='col-md-6'),
                    css_class='row card-body'
                ),
                css_id='step-1'
            ),
            Div(
                Div(
                    HTML('<span class="badge-form badge-pill">1</span>'),
                    Div('caregivers_distress', css_class='col-md-5'),
                    Div('caregivers_additional_parenting', css_class='col-md-6'),
                    css_class='row card-body'
                ),
                Div(
                    HTML('<span class="badge-form badge-pill">2</span>'),
                    Div('child_distress', css_class='col-md-5'),
                    Div('child_additional_parenting', css_class='col-md-6'),
                    css_class='row card-body'
                ),
                Div(
                    HTML('<span class="badge-form badge-pill">3</span>'),
                    Div('child_know_seek_help', css_class='col-md-5'),
                    HTML('<span class="badge-form badge-pill">4</span>'),
                    Div('child_protection_concern', css_class='col-md-6'),
                    css_class='row card-body'
                ),
                FormActions(
                    Submit('save', 'Save',
                           css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-success'),
                    Reset('reset', 'Reset',
                          css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-warning'),
                ),
                css_id='step-2'
            )
        )

    def save(self, request=None, instance=None, registry=None):
        validated_data = request.POST

        if not instance:
            instance = PSSService.objects.create(registration_id=registry)
        else:
            instance = PSSService.objects.get(id=instance)
        instance.child_registered = validated_data.get('child_registered')
        instance.child_living_arrangement = validated_data.get('child_living_arrangement')
        instance.child_vulnerability = validated_data.get('child_vulnerability')
        instance.child_out_school_reasons = validated_data.get('child_out_school_reasons')
        instance.caregivers_distress = validated_data.get('caregivers_distress')
        instance.caregivers_additional_parenting = validated_data.get('caregivers_additional_parenting')
        instance.child_distress = validated_data.get('child_distress')
        instance.child_additional_parenting = validated_data.get('child_additional_parenting')
        instance.child_know_seek_help = validated_data.get('child_know_seek_help')
        instance.child_protection_concern = validated_data.get('child_protection_concern')
        instance.modified_by = request.user
        instance.save()

        messages.success(request, _('Your data has been sent successfully to the server'))

        update_service(registry_id=registry, service_name='PSS', service_id=instance.id)

        return instance

    def clean(self):
        cleaned_data = super(PSSServiceForm, self).clean()
        caregivers_distress = cleaned_data.get("caregivers_distress")
        caregivers_additional_parenting = cleaned_data.get("caregivers_additional_parenting")
        if caregivers_distress and caregivers_distress == 'Yes' and not caregivers_additional_parenting:
            self.add_error('caregivers_additional_parenting', 'This field is required')

        child_distress = cleaned_data.get("child_distress")
        child_additional_parenting = cleaned_data.get("child_additional_parenting")
        if child_distress and child_distress == 'Yes' and not child_additional_parenting:
            self.add_error('child_additional_parenting', 'This field is required')

    class Meta:
        model = PSSService
        fields = (
            'child_registered',
            'child_living_arrangement',
            'child_vulnerability',
            'child_out_school_reasons',
            'caregivers_distress',
            'caregivers_additional_parenting',
            'child_distress',
            'child_additional_parenting',
            'child_know_seek_help',
            'child_protection_concern'
        )


class InclusionServiceForm(forms.ModelForm):

    dropout = forms.ChoiceField(
        label=_("Dropout"),
        widget=forms.Select, required=True,
        choices=YES_NO
    )
    parental_engagement = forms.ChoiceField(
        widget=forms.Select, required=True,
        choices=InclusionService.PARENTAL_ENGAGEMENT,
        label=_('Parental Engagement Curriculum')
    )
    registration_id = forms.CharField(widget=forms.HiddenInput, required=False)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        registry = kwargs.pop('registry', None)
        instance = kwargs.pop('instance', None)

        super(InclusionServiceForm, self).__init__(*args, **kwargs)

        form_action = reverse('mscc:service_inclusion_add', kwargs={'registry': registry})
        if instance:
            form_action = reverse('mscc:service_inclusion_edit', kwargs={'registry': registry, 'pk': instance})

        self.helper = FormHelper()
        self.helper.form_show_labels = True
        self.helper.form_action = form_action
        self.helper.layout = Layout(
            Div(
                Div(
                    HTML('<span class="badge-form badge-pill">1</span>'),
                    Div('dropout', css_class='col-md-4'),
                    HTML('<span class="badge-form badge-pill">2</span>'),
                    Div('parental_engagement', css_class='col-md-4'),
                    css_class='row card-body'
                ),
                css_id='step-1'
            ),
            FormActions(
                Submit('save', 'Save',
                       css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-success'),
                Reset('reset', 'Reset',
                      css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-warning'),
            )
        )

    def save(self, request=None, instance=None, registry=None):

        validated_data = request.POST

        if not instance:
            instance = InclusionService.objects.create(registration_id=registry)
        else:
            instance = InclusionService.objects.get(id=instance)

        instance.dropout = validated_data.get('dropout')
        instance.parental_engagement = validated_data.get('parental_engagement')
        # instance.modified_by = request.user
        instance.save()

        messages.success(request, _('Your data has been sent successfully to the server'))

        update_service(registry_id=registry, service_name='Inclusion', service_id=instance.id)

        return instance

    class Meta:
        model = InclusionService
        fields = (
            'dropout',
            'parental_engagement',
        )


class DigitalServiceForm(forms.ModelForm):

    using_akelius = forms.ChoiceField(
        label=_("Is the child using Akelius?"),
        widget=forms.Select, required=True,
        choices=YES_NO
    )
    akelius_sessions_number = forms.IntegerField(
        label=_('Number of sessions per week'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        required=False,
        min_value=0
    )
    akelius_access = forms.ChoiceField(
        widget=forms.Select, required=False,
        choices=DigitalService.ACCESS,
        label=_('Access during')
    )
    akelius_child_equipped = forms.ChoiceField(
        widget=forms.Select, required=False,
        choices=DigitalService.YES_NO_OCCASIONALLY,
        label=_('Is the child equipped at home to access the platforms (Based on Child and parents'' confirmation)')
    )
    akelius_change_literacy = forms.ChoiceField(
        widget=forms.Select, required=False,
        choices=DigitalService.NOTICING_CHANGE,
        label=_('As a teacher, are you noticing a change in motivation & output about Literacy')
    )
    akelius_change_math = forms.ChoiceField(
        widget=forms.Select, required=False,
        choices=DigitalService.NOTICING_CHANGE,
        label=_('As a teacher, are you noticing a change in motivation & output about Math')
    )
    akelius_change_learning = forms.ChoiceField(
        widget=forms.Select, required=False,
        choices=DigitalService.NOTICING_CHANGE,
        label=_('As a teacher, are you noticing a change in attitude towards learning')
    )
    using_lp = forms.ChoiceField(
        label=_("Is the child using Learning Passport?"),
        widget=forms.Select, required=True,
        choices=YES_NO
    )
    lp_sessions_number = forms.IntegerField(
        label=_('Number of sessions per week'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        required=False,
        min_value=0
    )
    lp_access = forms.ChoiceField(
        widget=forms.Select, required=False,
        choices=DigitalService.ACCESS,
        label=_('Access during')
    )
    lp_child_equipped = forms.ChoiceField(
        widget=forms.Select, required=False,
        choices=DigitalService.YES_NO_OCCASIONALLY,
        label=_('Is the child equipped at home to access the platforms (Based on Child and parents'' confirmation)')
    )
    lp_change_literacy = forms.ChoiceField(
        widget=forms.Select, required=False,
        choices=DigitalService.NOTICING_CHANGE,
        label=_('As a teacher, are you noticing a change in motivation & output about Literacy')
    )
    lp_change_math = forms.ChoiceField(
        widget=forms.Select, required=False,
        choices=DigitalService.NOTICING_CHANGE,
        label=_('As a teacher, are you noticing a change in motivation & output about Math')
    )
    lp_change_learning = forms.ChoiceField(
        widget=forms.Select, required=False,
        choices=DigitalService.NOTICING_CHANGE,
        label=_('As a teacher, are you noticing a change in attitude towards learning')
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        registry = kwargs.pop('registry', None)
        instance = kwargs.pop('instance', None)

        super(DigitalServiceForm, self).__init__(*args, **kwargs)

        form_action = reverse('mscc:service_digital_add', kwargs={'registry': registry})
        if instance:
            form_action = reverse('mscc:service_digital_edit', kwargs={'registry': registry, 'pk': instance})

        self.helper = FormHelper()
        self.helper.form_show_labels = True
        self.helper.form_action = form_action
        self.helper.layout = Layout(
            Div(
                Div(
                    HTML('<span class="badge-form badge-pill">1</span>'),
                    Div('using_akelius', css_class='col-md-5'),
                    css_class='row card-body'
                ),
                Div(
                    HTML('<span class="badge-form-0 badge-pill"></span>'),
                    Div('akelius_sessions_number', css_class='col-md-5'),
                    HTML('<span class="badge-form-0 badge-pill"></span>'),
                    Div('akelius_access', css_class='col-md-5'),
                    css_class='row card-body akelius'
                ),
                Div(
                    HTML('<span class="badge-form-0 badge-pill"></span>'),
                    Div('akelius_child_equipped', css_class='col-md-5'),
                    HTML('<span class="badge-form-0 badge-pill"></span>'),
                    Div('akelius_change_literacy', css_class='col-md-5'),
                    css_class='row card-body akelius'
                ),
                Div(
                    HTML('<span class="badge-form-0 badge-pill"></span>'),
                    Div('akelius_change_math', css_class='col-md-5 ak'),
                    HTML('<span class="badge-form-0 badge-pill"></span>'),
                    Div('akelius_change_learning', css_class='col-md-5 ak'),
                    css_class='row card-body akelius'
                ),
                Div(
                    HTML('<span class="badge-form badge-pill">2</span>'),
                    Div('using_lp', css_class='col-md-5'),
                    css_class='row card-body'
                ),
                Div(
                    HTML('<span class="badge-form-0 badge-pill"></span>'),
                    Div('lp_sessions_number', css_class='col-md-5'),
                    HTML('<span class="badge-form-0 badge-pill"></span>'),
                    Div('lp_access', css_class='col-md-5'),
                    css_class='row card-body lp'
                ),
                Div(
                    HTML('<span class="badge-form-0 badge-pill"></span>'),
                    Div('lp_child_equipped', css_class='col-md-5'),
                    HTML('<span class="badge-form-0 badge-pill"></span>'),
                    Div('lp_change_literacy', css_class='col-md-5'),
                    css_class='row card-body lp'
                ),
                Div(
                    HTML('<span class="badge-form-0 badge-pill"></span>'),
                    Div('lp_change_math', css_class='col-md-5'),
                    HTML('<span class="badge-form-0 badge-pill"></span>'),
                    Div('lp_change_learning', css_class='col-md-5'),
                    css_class='row card-body lp'
                ),
                    FormActions(
                        Submit('save', 'Save',
                               css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-success'),
                        Reset('reset', 'Reset',
                              css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-warning'),
                    ),
                    css_id='step-1'
                )
            )

    def save(self, request=None, instance=None, registry=None):

        validated_data = request.POST

        if not instance:
            instance = DigitalService.objects.create(registration_id=registry)
        else:
            instance = DigitalService.objects.get(id=instance)

        using_akelius = validated_data.get('using_akelius')
        instance.using_akelius = using_akelius
        if using_akelius == 'Yes':
            akelius_sessions_number = validated_data.get('akelius_sessions_number')
            if akelius_sessions_number:
                instance.akelius_sessions_number = int(akelius_sessions_number)
            else:
                instance.akelius_sessions_number = 0
            instance.akelius_access = validated_data.get('akelius_access')
            instance.akelius_child_equipped = validated_data.get('akelius_child_equipped')
            instance.akelius_change_literacy = validated_data.get('akelius_change_literacy')
            instance.akelius_change_math = validated_data.get('akelius_change_math')
            instance.akelius_change_learning = validated_data.get('akelius_change_learning')
        else:
            instance.akelius_sessions_number = 0
            instance.akelius_access = ''
            instance.akelius_child_equipped = ''
            instance.akelius_change_literacy = ''
            instance.akelius_change_math =''
            instance.akelius_change_learning = ''

        using_lp = validated_data.get('using_lp')
        instance.using_lp = using_lp
        if using_lp == 'Yes':
            lp_sessions_number = validated_data.get('lp_sessions_number')
            if lp_sessions_number:
                instance.lp_sessions_number = int(lp_sessions_number)
            else:
                instance.lp_sessions_number = 0
            instance.lp_access = validated_data.get('lp_access')
            instance.lp_child_equipped = validated_data.get('lp_child_equipped')
            instance.lp_change_literacy = validated_data.get('lp_change_literacy')
            instance.lp_change_math = validated_data.get('lp_change_math')
            instance.lp_change_learning = validated_data.get('lp_change_learning')
        else:
            instance.lp_sessions_number = 0
            instance.lp_access = ''
            instance.lp_child_equipped = ''
            instance.lp_change_literacy = ''
            instance.lp_change_math = ''
            instance.lp_change_learning = ''

        instance.save()

        messages.success(request, _('Your data has been sent successfully to the server'))

        update_service(registry_id=registry, service_name='Digital component', service_id=instance.id)

        return instance

    def clean(self):
        cleaned_data = super(DigitalServiceForm, self).clean()
        # akelius
        using_akelius = cleaned_data.get("using_akelius")
        akelius_sessions_number = cleaned_data.get("akelius_sessions_number")
        akelius_access = cleaned_data.get("akelius_access")
        akelius_child_equipped = cleaned_data.get("akelius_child_equipped")
        akelius_change_literacy = cleaned_data.get("akelius_change_literacy")
        akelius_change_math = cleaned_data.get("akelius_change_math")
        akelius_change_learning = cleaned_data.get("akelius_change_learning")
        if using_akelius and using_akelius == 'Yes':
            if not akelius_sessions_number:
                self.add_error('akelius_sessions_number', 'This field is required')
            if not akelius_access:
                self.add_error('akelius_access', 'This field is required')
            if not akelius_child_equipped:
                self.add_error('akelius_child_equipped', 'This field is required')
            if not akelius_change_literacy:
                self.add_error('akelius_change_literacy', 'This field is required')
            if not akelius_change_math:
                self.add_error('akelius_change_math', 'This field is required')
            if not akelius_change_learning:
                self.add_error('akelius_change_learning', 'This field is required')
        # lp
        using_lp = cleaned_data.get("using_lp")
        lp_sessions_number = cleaned_data.get("lp_sessions_number")
        lp_access = cleaned_data.get("lp_access")
        lp_child_equipped = cleaned_data.get("lp_child_equipped")
        lp_change_literacy = cleaned_data.get("lp_change_literacy")
        lp_change_math = cleaned_data.get("lp_change_math")
        lp_change_learning = cleaned_data.get("lp_change_learning")
        if using_lp and using_lp == 'Yes':
            if not lp_sessions_number:
                self.add_error('lp_sessions_number', 'This field is required')
            if not lp_access:
                self.add_error('lp_access', 'This field is required')
            if not lp_child_equipped:
                self.add_error('lp_child_equipped', 'This field is required')
            if not lp_change_literacy:
                self.add_error('lp_change_literacy', 'This field is required')
            if not lp_change_math:
                self.add_error('lp_change_math', 'This field is required')
            if not lp_change_learning:
                self.add_error('lp_change_learning', 'This field is required')

    class Meta:
        model = DigitalService
        fields = (
            'using_akelius',
            'akelius_sessions_number',
            'akelius_access',
            'akelius_child_equipped',
            'akelius_change_literacy',
            'akelius_change_math',
            'akelius_change_learning',
            'using_lp',
            'lp_sessions_number',
            'lp_access',
            'lp_child_equipped',
            'lp_change_literacy',
            'lp_change_math',
            'lp_change_learning',
        )


class HealthNutritionServiceForm(forms.ModelForm):
    # Caregivers of children 0-5 years
    baby_breastfed = forms.ChoiceField(
        widget=forms.Select, required=False,
        choices=YES_NO,
        label=_('Is the baby being Breastfed?')
    )
    # Caregivers of children 0-5 years
    infant_exclusively_breastfed = forms.ChoiceField(
        widget=forms.Select, required=False,
        choices=YES_NO,
        label=_('if yes, is it exclusively breastfeeding for infants between 0-6 months?(only brest milk no other liquids even water)')
    )
    # Caregivers of children 0-5 years
    eat_solid_food = forms.ChoiceField(
        widget=forms.Select, required=False,
        choices=YES_NO,
        label=_('Did the child start to eat solid food?')
    )
    # Caregivers of children 0-5 years
    age_eat_solid_food = forms.ChoiceField(
        widget=forms.Select, required=False,
        choices=HealthNutritionService.AGE_EAT_SOLID_FOOD,
        label=_('If yes, at which age ?')
    )
    # Caregivers of children 0-5 years
    immunization_record_screened = forms.ChoiceField(
        widget=forms.Select, required=False,
        choices=YES_NO,
        label=_('Child immunization record screened (to check the integrated ECD milestones Cards based on the age of the child- or the national immunization Calendar)')
    )
    # Caregivers of children 0-5 years
    vaccine_missing = forms.CharField(
        required=False,
        widget=forms.TextInput,
        label=_('Write the name of vaccine missing')
    )
    # Caregivers of children 0-5 years
    muac_malnutrition_screening = forms.ChoiceField(
        widget=forms.Select, required=False,
        choices=HealthNutritionService.MALNUTRITION_SCREENING,
        label=_('MUAC malnutrition screening')
    )
    # Caregivers of children 0-5 years
    development_delays_identified = forms.ChoiceField(
        widget=forms.Select, required=False,
        choices=HealthNutritionService.DEVELOPMENT_DELAYS,
        label=_('Any delays in the development milestones is being identified? (please to check the Integrated ECD milestones Cards based on the age of the child)')
    )
    # Caregivers of children 0-18 years
    eating_minimum_meals = forms.ChoiceField(
        widget=forms.Select, required=False,
        choices=YES_NO,
        label=_('Is the child eating 3 minimum meals per day?')
    )
    # Caregivers of children 0-18 years
    child_vaccinated = forms.ChoiceField(
        widget=forms.Select, required=False,
        choices=YES_NO,
        label=_('Is the child being vaccinated as per the National vaccination calendar?')
    )
    # Caregivers of children 0-18 years
    positive_parenting = forms.ChoiceField(
        widget=forms.Select, required=False,
        choices=YES_NO,
        label=_('Positive parenting and dealing with difficult children without the use of harsh punishment?')
    )
    # Caregivers of children 6-18 years
    respond_stressful_events = forms.CharField(
        required=False,
        widget=forms.TextInput,
        label=_('How children of different ages respond to and understand stressful and traumatic events?')
    )
    # Caregivers of children 6-18 years
    physical_activity = forms.ChoiceField(
        widget=forms.Select, required=False,
        choices=YES_NO,
        label=_('Is the child practicing physical activity at least twice a week')
    )
    # Caregivers of children 6-18 years
    accessing_reproductive_health = forms.ChoiceField(
        widget=forms.Select, required=False,
        choices=YES_NO,
        label=_('In case of a child marriage to ask if the child is accessing in reproductive health services')
    )
    # Counselling and sessions
    # Caregivers of children 0-5 years
    caregiver_counselling = forms.ChoiceField(
        widget=forms.Select, required=False,
        choices=YES_NO,
        label=_('Did the caregiver receive one on one counselling?')
    )
    # Caregivers of children 0-5 years
    counselling_date = forms.DateField(
        label=_("Session date"),
        required=False
    )
    # Caregivers of children 0-5 years
    next_counselling_date = forms.DateField(
        label=_("Next session date"),
        required=False
    )
    # Caregivers of children 0-5 years
    caregiver_ecd_counselling = forms.ChoiceField(
        widget=forms.Select, required=False,
        choices=YES_NO,
        label=_('Did the caregiver attended ECD group counselling?')
    )
    # Caregivers of children 0-5 years
    ecd_counselling_date = forms.DateField(
        label=_("Session date"),
        required=False
    )
    # Caregivers of children 0-5 years
    next_ecd_counselling_date = forms.DateField(
        label=_("Next session date"),
        required=False
    )
    # Caregivers of children 0-5 years
    child_screened_malnutrition = forms.ChoiceField(
        widget=forms.Select, required=False,
        choices=YES_NO,
        label=_('Was the child screened for malnutrition using MUAC tapes?')
    )
    # Caregivers of children 0-5 years
    child_malnutrition_screening = forms.ChoiceField(
        widget=forms.Select, required=False,
        choices=HealthNutritionService.MALNUTRITION_SCREENING,
        label=_('MUAC malnutrition screening')
    )
    # Caregivers of children 0-5 years
    child_immunization_screened = forms.ChoiceField(
        widget=forms.Select, required=False,
        choices=YES_NO,
        label=_('Was the child immunization record screened')
    )
    # Caregivers of children 0-5 years
    missing_vaccine = forms.CharField(
        required=False,
        widget=forms.TextInput,
        label=_('Please mention if any vaccine is missing')
    )
    # Caregivers of children 6-18 years
    attended_health_nutrition_session = forms.ChoiceField(
        widget=forms.Select, required=False,
        choices=YES_NO,
        label=_('Children attended health and nutrition session')
    )
    # Caregivers of children 6-18 years
    health_nutrition_session_title = forms.CharField(
        required=False,
        widget=forms.TextInput,
        label=_('Title of the session')
    )
    # Caregivers of children 0-5 years
    health_nutrition_session_date = TrimmedDateField(
        label=_("Date of the session"),
        required=False
    )

    child_age = forms.CharField(widget=forms.HiddenInput, required=False)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        registry = kwargs.pop('registry', None)
        instance = kwargs.pop('instance', None)
        age = int(kwargs.pop('age', None))


        super(HealthNutritionServiceForm, self).__init__(*args, **kwargs)
        if age <= 5:
            self.fields['baby_breastfed'].required = True
            self.fields['eat_solid_food'].required = True
            self.fields['immunization_record_screened'].required = True
            self.fields['vaccine_missing'].required = True
            self.fields['muac_malnutrition_screening'].required = True
            self.fields['eating_minimum_meals'].required = True
            self.fields['child_vaccinated'].required = True
            self.fields['positive_parenting'].required = True
            self.fields['development_delays_identified'].required = True
            self.fields['caregiver_counselling'].required = True
            self.fields['caregiver_ecd_counselling'].required = True
            self.fields['child_screened_malnutrition'].required = True
            self.fields['child_immunization_screened'].required = True
        if 6 <= age <= 18:
            self.fields['eating_minimum_meals'].required = True
            self.fields['child_vaccinated'].required = True
            self.fields['respond_stressful_events'].required = True
            self.fields['physical_activity'].required = True
            self.fields['accessing_reproductive_health'].required = True
            self.fields['attended_health_nutrition_session'].required = True

        form_action = reverse('mscc:service_health_nutrition_add', kwargs={'registry': registry, 'age': age})
        if instance:
            form_action = reverse('mscc:service_health_nutrition_edit', kwargs={'registry': registry, 'age': age, 'pk': instance})

        self.fields['child_age'].initial = age
        self.helper = FormHelper()
        self.helper.form_show_labels = True
        self.helper.form_action = form_action

        if age <= 5:
            self.helper.layout = Layout(
                Div(
                    Div(
                        Div('child_age', css_class='col-md-6'),
                        css_class='row card-body d-none'
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">1</span>'),
                        Div('baby_breastfed', css_class='col-md-6'),
                        css_class='row card-body'
                    ),
                    Div(
                        HTML('<span class="badge-form-0 badge-pill"></span>'),
                        Div('infant_exclusively_breastfed', css_class='col-md-11'),
                        css_class='row card-body'
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">2</span>'),
                        Div('eat_solid_food', css_class='col-md-6'),
                        Div('age_eat_solid_food', css_class='col-md-5'),
                        css_class='row card-body'
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">3</span>'),
                        Div('immunization_record_screened', css_class='col-md-11'),
                        css_class='row card-body'
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">4</span>'),
                        Div('vaccine_missing', css_class='col-md-6'),
                        css_class='row card-body'
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">5</span>'),
                        Div('muac_malnutrition_screening', css_class='col-md-6'),
                        css_class='row card-body'
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">6</span>'),
                        Div('eating_minimum_meals', css_class='col-md-6'),
                        css_class='row card-body'
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">7</span>'),
                        Div('child_vaccinated', css_class='col-md-8'),
                        css_class='row card-body'
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">8</span>'),
                        Div('positive_parenting', css_class='col-md-9'),
                        css_class='row card-body'
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">9</span>'),
                        Div('development_delays_identified', css_class='col-md-11'),
                        css_class='row card-body'
                    ),
                    Div(
                        Div('respond_stressful_events', css_class='col-md-11'),
                        css_class='row card-body d-none'
                    ),
                    Div(
                        Div('physical_activity', css_class='col-md-8'),
                        css_class='row card-body d-none'
                    ),
                    Div(
                        Div('accessing_reproductive_health', css_class='col-md-12'),
                        css_class='row card-body d-none'
                    ),
                    css_id='step-1'
                ),
                Div(
                    Div(
                        HTML('<span class="badge-form badge-pill">1</span>'),
                        Div('caregiver_counselling', css_class='col-md-6'),
                        css_class='row card-body'
                    ),
                    Div(
                        HTML('<span class="badge-form-0 badge-pill"></span>'),
                        Div('counselling_date', css_class='col-md-3'),
                        Div('next_counselling_date', css_class='col-md-3'),
                        css_class='row card-body'
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">2</span>'),
                        Div('caregiver_ecd_counselling', css_class='col-md-6'),
                        css_class='row card-body'
                    ),
                    Div(
                        HTML('<span class="badge-form-0 badge-pill"></span>'),
                        Div('ecd_counselling_date', css_class='col-md-3'),
                        Div('next_ecd_counselling_date', css_class='col-md-3'),
                        css_class='row card-body'
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">3</span>'),
                        Div('child_screened_malnutrition', css_class='col-md-6'),
                        Div('child_malnutrition_screening', css_class='col-md-5'),
                        css_class='row card-body'
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">4</span>'),
                        Div('child_immunization_screened', css_class='col-md-6'),
                        Div('missing_vaccine', css_class='col-md-5'),
                        css_class='row card-body'
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">1</span>'),
                        Div('attended_health_nutrition_session', css_class='col-md-4'),
                        Div('health_nutrition_session_title', css_class='col-md-3'),
                        Div('health_nutrition_session_date', css_class='col-md-3'),
                        css_class='row card-body d-none'
                    ),
                    FormActions(
                        Submit('save', 'Save',
                               css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-success'),
                        Reset('reset', 'Reset',
                              css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-warning'),
                    ),
                    css_id='step-2',
                )
            )
        if 6 <= age <= 18:
            self.helper.layout = Layout(
                Div(
                    Div(
                        Div('child_age', css_class='col-md-4'),
                        css_class='row card-body d-none'
                    ),
                    Div(
                        Div('baby_breastfed', css_class='col-md-4'),
                        css_class='row card-body d-none'
                    ),
                    Div(
                        Div('infant_exclusively_breastfed', css_class='col-md-12'),
                        css_class='row card-body d-none'
                    ),
                    Div(
                        Div('eat_solid_food', css_class='col-md-6'),
                        Div('age_eat_solid_food', css_class='col-md-6'),
                        css_class='row card-body d-none'
                    ),
                    Div(
                        Div('immunization_record_screened', css_class='col-md-12'),
                        css_class='row card-body d-none'
                    ),
                    Div(
                        Div('vaccine_missing', css_class='col-md-4'),
                        css_class='row card-body d-none'
                    ),
                    Div(
                        Div('muac_malnutrition_screening', css_class='col-md-6'),
                        css_class='row card-body d-none'
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">1</span>'),
                        Div('eating_minimum_meals', css_class='col-md-9'),
                        css_class='row card-body'
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">2</span>'),
                        Div('child_vaccinated', css_class='col-md-9'),
                        css_class='row card-body'
                    ),
                    Div(
                        Div('positive_parenting', css_class='col-md-9'),
                        css_class='row card-body d-none'
                    ),
                    Div(
                        Div('development_delays_identified', css_class='col-md-8'),
                        css_class='row card-body d-none'
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">3</span>'),
                        Div('respond_stressful_events', css_class='col-md-9'),
                        css_class='row card-body'
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">4</span>'),
                        Div('physical_activity', css_class='col-md-9'),
                        css_class='row card-body'
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">5</span>'),
                        Div('accessing_reproductive_health', css_class='col-md-9'),
                        css_class='row card-body'
                    ),
                    css_id='step-1'
                ),
                Div(
                    Div(
                        HTML('<span class="badge-form badge-pill">1</span>'),
                        Div('caregiver_counselling', css_class='col-md-4'),
                        Div('counselling_date', css_class='col-md-3'),
                        Div('next_counselling_date', css_class='col-md-3'),
                        css_class='row card-body d-none'
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">2</span>'),
                        Div('caregiver_ecd_counselling', css_class='col-md-4'),
                        Div('ecd_counselling_date', css_class='col-md-3'),
                        Div('next_ecd_counselling_date', css_class='col-md-3'),
                        css_class='row card-body d-none'
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">3</span>'),
                        Div('child_screened_malnutrition', css_class='col-md-4'),
                        Div('child_malnutrition_screening', css_class='col-md-6'),
                        css_class='row card-body d-none'
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">3</span>'),
                        Div('child_immunization_screened', css_class='col-md-4'),
                        Div('missing_vaccine', css_class='col-md-6'),
                        css_class='row card-body d-none'
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">1</span>'),
                        Div('attended_health_nutrition_session', css_class='col-md-6'),
                        css_class='row card-body'
                    ),
                    Div(
                        HTML('<span class="badge-form-0 badge-pill"></span>'),
                        Div('health_nutrition_session_title', css_class='col-md-3'),
                        Div('health_nutrition_session_date', css_class='col-md-3'),
                        css_class='row card-body'
                    ),
                    FormActions(
                        Submit('save', 'Save',
                               css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-success'),
                        Reset('reset', 'Reset',
                              css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-warning'),
                    ),
                    css_id='step-2',
                )
            )

    def save(self, request=None, instance=None, registry=None):

        validated_data = request.POST

        if not instance:
            instance = HealthNutritionService.objects.create(registration_id=registry)
        else:
            instance = HealthNutritionService.objects.get(id=instance)

        instance.baby_breastfed = validated_data.get('baby_breastfed')
        instance.infant_exclusively_breastfed = validated_data.get('infant_exclusively_breastfed')
        instance.eat_solid_food = validated_data.get('eat_solid_food')
        instance.age_eat_solid_food = validated_data.get('age_eat_solid_food')
        instance.immunization_record_screened = validated_data.get('immunization_record_screened')
        instance.vaccine_missing = validated_data.get('vaccine_missing')
        instance.muac_malnutrition_screening = validated_data.get('muac_malnutrition_screening')
        instance.child_vaccinated = validated_data.get('child_vaccinated')
        instance.development_delays_identified = validated_data.get('development_delays_identified')
        instance.eating_minimum_meals = validated_data.get('eating_minimum_meals')
        instance.positive_parenting = validated_data.get('positive_parenting')
        instance.respond_stressful_events = validated_data.get('respond_stressful_events')
        instance.physical_activity = validated_data.get('physical_activity')
        instance.accessing_reproductive_health = validated_data.get('accessing_reproductive_health')

        # caregiver_counselling
        caregiver_counselling = validated_data.get('caregiver_counselling')
        instance.caregiver_counselling = caregiver_counselling
        if caregiver_counselling == 'Yes':
            instance.counselling_date = validated_data.get('counselling_date')
            if validated_data.get('next_counselling_date'):
                instance.next_counselling_date = validated_data.get('next_counselling_date')
            else:
                instance.next_counselling_date = None
        else:
            instance.counselling_date = None
            instance.next_counselling_date = None

        # caregiver_ecd_counselling
        caregiver_ecd_counselling = validated_data.get('caregiver_ecd_counselling')
        instance.caregiver_ecd_counselling = caregiver_ecd_counselling
        if caregiver_ecd_counselling == 'Yes':
            instance.ecd_counselling_date = validated_data.get('ecd_counselling_date')
            if validated_data.get('next_ecd_counselling_date'):
                instance.next_ecd_counselling_date = validated_data.get('next_ecd_counselling_date')
            else:
                instance.next_ecd_counselling_date = None
        else:
            instance.ecd_counselling_date = None
            instance.next_ecd_counselling_date = None

        # child_screened_malnutrition
        child_screened_malnutrition = validated_data.get('child_screened_malnutrition')
        instance.child_screened_malnutrition = child_screened_malnutrition
        if child_screened_malnutrition == 'Yes':
            instance.child_malnutrition_screening = validated_data.get('child_malnutrition_screening')
        else:
            instance.child_malnutrition_screening = ''


        # child_immunization_screened
        child_immunization_screened = validated_data.get('child_immunization_screened')
        instance.child_immunization_screened = child_immunization_screened
        if child_immunization_screened == 'Yes':
            instance.missing_vaccine = validated_data.get('missing_vaccine')
        else:
            instance.missing_vaccine = ''

        # attended_health_nutrition_session
        attended_health_nutrition_session = validated_data.get('attended_health_nutrition_session')
        instance.attended_health_nutrition_session = attended_health_nutrition_session
        if attended_health_nutrition_session == 'Yes':
            instance.health_nutrition_session_title = validated_data.get('health_nutrition_session_title')
            session_date_str = validated_data.get('health_nutrition_session_date')
            if session_date_str:
                try:
                    instance.health_nutrition_session_date = validate_date(session_date_str)
                except ValidationError as e:
                    raise ValidationError('Session date error: {}'.format(e))
            else:
                instance.health_nutrition_session_date = None
        else:
            instance.health_nutrition_session_title = ''
            instance.health_nutrition_session_date = None

        instance.modified_by = request.user
        instance.save()

        messages.success(request, _('Your data has been sent successfully to the server'))

        update_service(registry_id=registry, service_name='Health and Nutrition', service_id=instance.id)

        return instance

    registration_id = forms.CharField(widget=forms.HiddenInput, required=False)

    def clean(self):
        cleaned_data = super(HealthNutritionServiceForm, self).clean()
        child_age = cleaned_data.get('child_age')
        if not child_age:
            child_age = self.fields['child_age'].initial
            cleaned_data['child_age'] = child_age

        age = int(child_age)
        if age <= 5:

            baby_breastfed = cleaned_data.get("baby_breastfed")
            infant_exclusively_breastfed = cleaned_data.get("infant_exclusively_breastfed")
            if baby_breastfed and baby_breastfed == 'Yes' and not infant_exclusively_breastfed:
                self.add_error('infant_exclusively_breastfed', 'This field is required')

            eat_solid_food = cleaned_data.get("eat_solid_food")
            age_eat_solid_food = cleaned_data.get("age_eat_solid_food")

            if eat_solid_food and eat_solid_food == 'Yes' and not age_eat_solid_food:
                self.add_error('age_eat_solid_food', 'This field is required')

            caregiver_counselling = cleaned_data.get("caregiver_counselling")
            counselling_date = cleaned_data.get("counselling_date")

            if caregiver_counselling and caregiver_counselling == 'Yes':
                if not counselling_date:
                    self.add_error('counselling_date', 'This field is required')

            caregiver_ecd_counselling = cleaned_data.get("caregiver_ecd_counselling")
            ecd_counselling_date = cleaned_data.get("ecd_counselling_date")

            if caregiver_ecd_counselling and caregiver_ecd_counselling == 'Yes':
                if not ecd_counselling_date:
                    self.add_error('ecd_counselling_date', 'This field is required')

            child_screened_malnutrition = cleaned_data.get("child_screened_malnutrition")
            child_malnutrition_screening = cleaned_data.get("child_malnutrition_screening")
            if child_screened_malnutrition and child_screened_malnutrition == 'Yes' and not child_malnutrition_screening:
                self.add_error('child_malnutrition_screening', 'This field is required')

            child_immunization_screened = cleaned_data.get("child_immunization_screened")
            missing_vaccine = cleaned_data.get("missing_vaccine")
            if child_immunization_screened and child_immunization_screened == 'Yes' and not missing_vaccine:
                self.add_error('missing_vaccine', 'This field is required')

        elif 6 <= age <= 18:

            attended_health_nutrition_session = cleaned_data.get("attended_health_nutrition_session")
            health_nutrition_session_title = cleaned_data.get("health_nutrition_session_title")
            health_nutrition_session_date = cleaned_data.get("health_nutrition_session_date")

            if attended_health_nutrition_session and attended_health_nutrition_session == 'Yes':
                if not health_nutrition_session_title:
                    self.add_error('health_nutrition_session_title', 'This field is required')
                if not health_nutrition_session_date:
                    self.add_error('health_nutrition_session_date', 'This field is required')

    class Meta:
        model = HealthNutritionService
        fields = (
            'baby_breastfed',
            'infant_exclusively_breastfed',
            'eat_solid_food',
            'age_eat_solid_food',
            'immunization_record_screened',
            'vaccine_missing',
            'muac_malnutrition_screening',
            'child_vaccinated',
            'development_delays_identified',
            'eating_minimum_meals',
            'positive_parenting',
            'respond_stressful_events',
            'physical_activity',
            'accessing_reproductive_health',
            'caregiver_counselling',
            'counselling_date',
            'next_counselling_date',
            'caregiver_ecd_counselling',
            'ecd_counselling_date',
            'next_ecd_counselling_date',
            'child_screened_malnutrition' ,
            'child_malnutrition_screening',
            'child_immunization_screened' ,
            'missing_vaccine'  ,
            'attended_health_nutrition_session' ,
            'health_nutrition_session_title'  ,
            'health_nutrition_session_date'
        )


class HealthNutritionReferralForm(forms.ModelForm):

    referred_development_delays = forms.ChoiceField(
        widget=forms.Select, required=False,
        choices=YES_NO,
        label=_('Was the child referred for any observed developmental delays as per the milestones cards to?')
    )
    development_delays = forms.ChoiceField(
        widget=forms.Select, required=False,
        choices=HealthNutritionReferral.DEVELOPMENT_DELAYS,
        label=_('If yes, please select')
    )
    referred_malnutrition = forms.ChoiceField(
        widget=forms.Select, required=False,
        choices=YES_NO,
        label=_('Was the child Referred for malnutrition treatment center?')
    )
    malnutrition_treatment_center = forms.ChoiceField(
        widget=forms.Select, required=False,
        choices=HealthNutritionReferral.MALNUTRITION_TREATMENT_CENTER,
        label=_('If yes, please select')
    )
    referred_anc_pnc = forms.ChoiceField(
        widget=forms.Select, required=False,
        choices=YES_NO,
        label=_('Was a Pregnant lactating women/child referred  for ANC and PNC follow up  and to receive MMS (multivitamins) to PHC?')
    )
    phc_center = forms.CharField(
        required=False,
        widget=forms.TextInput,
        label=_('Write the name of vaccine missing')
    )
    women_child_referred_iycf = forms.ChoiceField(
        widget=forms.Select, required=False,
        choices=YES_NO,
        label=_('Was a Pregnant lactating women/child with challenges on breastfeeding referred to IYCF specialists?')
    )
    women_child_referred_organization = forms.CharField(
        required=False,
        widget=forms.TextInput,
        label=_('If yes (please add name of organization referred tor)')
    )
    infant_child_referred_iycf = forms.ChoiceField(
        widget=forms.Select, required=False,
        choices=YES_NO,
        label=_('Was a Children aged 6months to 59months with challenges on infant and young child feeding practice referred to IYCF specialists and to receive Micronutrient supplements?')
    )
    infant_child_referred_organization = forms.CharField(
        required=False,
        widget=forms.TextInput,
        label=_('If yes (please add name of organization referred to)')
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        registry = kwargs.pop('registry', None)
        instance = kwargs.pop('instance', None)

        super(HealthNutritionReferralForm, self).__init__(*args, **kwargs)

        form_action = reverse('mscc:service_health_nutrition_referral_add', kwargs={'registry': registry})
        if instance:
            form_action = reverse('mscc:service_health_nutrition_referral_edit', kwargs={'registry': registry, 'pk': instance})

        self.helper = FormHelper()
        self.helper.form_show_labels = True
        self.helper.form_action = form_action
        self.helper.layout = Layout(
            Div(
                Div(
                    HTML('<span class="badge-form badge-pill">1</span>'),
                    Div('referred_development_delays', css_class='col-md-7'),
                    Div('development_delays', css_class='col-md-4'),
                    css_class='row card-body'
                ),
                Div(
                    HTML('<span class="badge-form badge-pill">2</span>'),
                    Div('referred_malnutrition', css_class='col-md-7'),
                    Div('malnutrition_treatment_center', css_class='col-md-4'),
                    css_class='row card-body'
                ),
                Div(
                    HTML('<span class="badge-form badge-pill">3</span>'),
                    Div('referred_anc_pnc', css_class='col-md-7'),
                    Div('phc_center', css_class='col-md-4'),
                    css_class='row card-body'
                ),
                Div(
                    HTML('<span class="badge-form badge-pill">4</span>'),
                    Div('women_child_referred_iycf', css_class='col-md-7'),
                    Div('women_child_referred_organization', css_class='col-md-4'),
                    css_class='row card-body'
                ),
                Div(
                    HTML('<span class="badge-form badge-pill">5</span>'),
                    Div('infant_child_referred_iycf', css_class='col-md-7'),
                    Div('infant_child_referred_organization', css_class='col-md-4'),
                    css_class='row card-body'
                ),
                FormActions(
                    Submit('save', 'Save',
                           css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-success'),
                    Reset('reset', 'Reset',
                          css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-warning'),
                ),
                css_id='step-1'
            )
        )

    def save(self, request=None, instance=None, registry=None):

        validated_data = request.POST

        if not instance:
            instance = HealthNutritionReferral.objects.create(registration_id=registry)
        else:
            instance = HealthNutritionReferral.objects.get(id=instance)
        # referred_development_delays
        referred_development_delays= validated_data.get('referred_development_delays')
        instance.referred_development_delays = referred_development_delays
        if referred_development_delays == 'Yes':
            instance.development_delays = validated_data.get('development_delays')
        else:
            instance.development_delays = ''

        # referred_malnutrition
        referred_malnutrition = validated_data.get('referred_malnutrition')
        instance.referred_malnutrition = referred_malnutrition
        if referred_malnutrition == 'Yes':
            instance.malnutrition_treatment_center = validated_data.get('malnutrition_treatment_center')
        else:
            instance.malnutrition_treatment_center = ''

        # referred_anc_pnc
        referred_anc_pnc = validated_data.get('referred_anc_pnc')
        instance.referred_anc_pnc = referred_anc_pnc
        if referred_anc_pnc == 'Yes':
            instance.phc_center = validated_data.get('phc_center')
        else:
            instance.phc_center = ''

        # women_child_referred_iycf
        women_child_referred_iycf = validated_data.get('women_child_referred_iycf')
        instance.women_child_referred_iycf = women_child_referred_iycf
        if women_child_referred_iycf == 'Yes':
            instance.women_child_referred_organization = validated_data.get('women_child_referred_organization')
        else:
            instance.women_child_referred_organization = ''

        # infant_child_referred_iycf
        infant_child_referred_iycf = validated_data.get('infant_child_referred_iycf')
        instance.infant_child_referred_iycf = infant_child_referred_iycf
        if infant_child_referred_iycf == 'Yes':
            instance.infant_child_referred_organization = validated_data.get('infant_child_referred_organization')
        else:
            instance.infant_child_referred_organization = ''

        instance.modified_by = request.user
        instance.save()

        messages.success(request, _('Your data has been sent successfully to the server'))

        update_service(registry_id=registry, service_name='Health and Nutrition', service_id=instance.id)

        return instance

    registration_id = forms.CharField(widget=forms.HiddenInput, required=False)

    def clean(self):
        cleaned_data = super(HealthNutritionReferralForm, self).clean()

        referred_development_delays = cleaned_data.get("referred_development_delays")
        development_delays = cleaned_data.get("development_delays")
        if referred_development_delays and referred_development_delays == 'Yes' and not development_delays:
            self.add_error('development_delays', 'This field is required')

        referred_malnutrition = cleaned_data.get("referred_malnutrition")
        malnutrition_treatment_center = cleaned_data.get("malnutrition_treatment_center")
        if referred_malnutrition and referred_malnutrition == 'Yes' and not malnutrition_treatment_center:
            self.add_error('malnutrition_treatment_center', 'This field is required')

        referred_anc_pnc = cleaned_data.get("referred_anc_pnc")
        phc_center = cleaned_data.get("phc_center")
        if referred_anc_pnc and referred_anc_pnc == 'Yes' and not phc_center:
            self.add_error('phc_center', 'This field is required')

        women_child_referred_iycf = cleaned_data.get("women_child_referred_iycf")
        women_child_referred_organization = cleaned_data.get("women_child_referred_organization")
        if women_child_referred_iycf and women_child_referred_iycf == 'Yes' and not women_child_referred_organization:
            self.add_error('women_child_referred_organization', 'This field is required')

        infant_child_referred_iycf = cleaned_data.get("infant_child_referred_iycf")
        infant_child_referred_organization = cleaned_data.get("infant_child_referred_organization")
        if infant_child_referred_iycf and infant_child_referred_iycf == 'Yes' and not infant_child_referred_organization:
            self.add_error('infant_child_referred_organization', 'This field is required')


    class Meta:
        model = HealthNutritionReferral
        fields = (
            'referred_development_delays',
            'development_delays',
            'referred_malnutrition',
            'malnutrition_treatment_center',
            'referred_anc_pnc',
            'phc_center',
            'women_child_referred_iycf',
            'women_child_referred_organization',
            'infant_child_referred_iycf',
            'infant_child_referred_organization',
        )


class YouthKitServiceForm(forms.ModelForm):

    # For Youth
    volunteering_experience = forms.ChoiceField(
        widget=forms.Select, required=True,
        choices=YES_NO,
        label=_('Does the adolescent have any volunteering experience?')
    )
    previous_community_initiative = forms.ChoiceField(
        widget=forms.Select, required=True,
        choices=YES_NO,
        label=_('Was the adolescent part of any previous community based initiative?')
    )
    enrollment_reason = forms.CharField(
        required=False,
        widget=forms.TextInput,
        label=_('What is the reason for the adolescent enrollment in the programme?')
    )
    pre_tests_administered = forms.ChoiceField(
        widget=forms.Select, required=True,
        choices=YES_NO,
        label=_('Were pre-tests administered to assess adolescents level?')
    )
    # Youth Assessment
    test_diagnostic_done = forms.ChoiceField(
        widget=forms.Select, required=True,
        choices=YES_NO,
        label=_('Did the adolescent undertake any Post Diagnostic tests?')
    )
    receive_passing_grade = forms.ChoiceField(
        widget=forms.Select, required=False,
        choices=YES_NO,
        label=_('Did the adolescent receive a passing grade for the tests?')
    )
    life_skills_completed = forms.ChoiceField(
        widget=forms.Select, required=True,
        choices=YES_NO,
        label=_('Did the adolescent complete the life skills package?')
    )
    participate_volunteering = forms.ChoiceField(
        widget=forms.Select, required=True,
        choices=YES_NO,
        label=_('Did the adolescent participate in any volunteering opportunity during the course of the program?')
    )
    volunteering_specify = forms.ChoiceField(
        widget=forms.Select, required=False,
        choices=YouthKitService.VOLUNTEERING,
        label=_('Please specify the volunteering opportunity')
    )
    # social_course = forms.ChoiceField(
    #     widget=forms.Select, required=True,
    #     choices=YES_NO,
    #     label=_('Did the adolescent benefit from any social innovation/entrepreneurship course?')
    # )
    yfs_course_completed = forms.ChoiceField(
        widget=forms.Select, required=True,
        choices=YES_NO,
        label=_('Did the adolescent complete the YFS course?')
    )
    training_material = forms.ChoiceField(
        widget=forms.Select, required=False,
        choices=YouthKitService.TRAINING_MATERIAL,
        label=_('What training material was provided?')
    )
    future_path = forms.ChoiceField(
        widget=forms.Select, required=True,
        choices=YouthKitService.FUTURE_PATH,
        label=_('What is the recommended future path for the adolescent?')
    )
    participate_community_initiatives = forms.ChoiceField(
        widget=forms.Select, required=True,
        choices=YES_NO,
        label=_('Did the adolescent participate/come up in community based initiatives?')
    )
    community_initiatives_specify = forms.CharField(
        required=False,
        widget=forms.TextInput,
        label=_('What is the initiative?')
    )
    adolescent_attendance = forms.ChoiceField(
        widget=forms.Select, required=True,
        choices=YouthKitService.ATTENDANCE,
        label=_('Adolescent attendance')
    )
    adolescent_dropout_reason = forms.CharField(
        required=False,
        widget=forms.TextInput,
        label=_('Reason for dropout')
    )
    adolescent_dropout_date = forms.DateField(
        label=_("Dropout Date"),
        required=False
    )
    youth_trained_mental_health = forms.ChoiceField(
        widget=forms.Select, required=True,
        choices=YES_NO,
        label=_('Is the youth trained on Mental health?')
    )

    registration_id = forms.CharField(widget=forms.HiddenInput, required=False)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        registry = kwargs.pop('registry', None)
        instance = kwargs.pop('instance', None)

        super(YouthKitServiceForm, self).__init__(*args, **kwargs)

        form_action = reverse('mscc:service_youth_kit_add', kwargs={'registry': registry})
        if instance:
            form_action = reverse('mscc:service_youth_kit_edit', kwargs={'registry': registry, 'pk': instance})

        self.helper = FormHelper()
        self.helper.form_show_labels = True
        self.helper.form_action = form_action
        self.helper.layout = Layout(
            Div(
                Div(
                    HTML('<span class="badge-form badge-pill">1</span>'),
                    Div('volunteering_experience', css_class='col-md-5'),
                    HTML('<span class="badge-form badge-pill">2</span>'),
                    Div('previous_community_initiative', css_class='col-md-6'),
                    css_class='row card-body'
                ),
                Div(
                    HTML('<span class="badge-form badge-pill">3</span>'),
                    Div('enrollment_reason', css_class='col-md-5'),
                    HTML('<span class="badge-form badge-pill">4</span>'),
                    Div('pre_tests_administered', css_class='col-md-6'),
                    css_class='row card-body'
                ),
                css_id='step-1'
            ),
            Div(
                Div(
                    HTML('<span class="badge-form badge-pill">1</span>'),
                    Div('test_diagnostic_done', css_class='col-md-5'),
                    Div('receive_passing_grade', css_class='col-md-6'),
                    css_class='row card-body'
                ),
                Div(
                    HTML('<span class="badge-form badge-pill">2</span>'),
                    Div('life_skills_completed', css_class='col-md-6'),
                    css_class='row card-body'
                ),

                Div(
                    HTML('<span class="badge-form badge-pill">3</span>'),
                    Div('participate_volunteering', css_class='col-md-7'),
                    Div('volunteering_specify', css_class='col-md-4'),
                    css_class='row card-body'
                ),
                # Div(
                #     HTML('<span class="badge-form badge-pill">5</span>'),
                #     Div('social_course', css_class='col-md-6'),
                #     css_class='row card-body'
                # ),
                Div(
                    HTML('<span class="badge-form badge-pill">4</span>'),
                    Div('yfs_course_completed', css_class='col-md-4'),
                    Div('training_material', css_class='col-md-5'),
                    css_class='row card-body'
                ),
                Div(
                    HTML('<span class="badge-form badge-pill">5</span>'),
                    Div('future_path', css_class='col-md-6'),
                    css_class='row card-body'
                ),
                Div(
                    HTML('<span class="badge-form badge-pill">6</span>'),
                    Div('participate_community_initiatives', css_class='col-md-6'),
                    Div('community_initiatives_specify', css_class='col-md-5'),
                    css_class='row card-body'
                ),
                Div(
                    HTML('<span class="badge-form badge-pill">7</span>'),
                    Div('adolescent_attendance', css_class='col-md-4'),
                    Div('adolescent_dropout_reason', css_class='col-md-4'),
                    Div('adolescent_dropout_date', css_class='col-md-3'),
                    css_class='row card-body'
                ),
                Div(
                    HTML('<span class="badge-form badge-pill">8</span>'),
                    Div('youth_trained_mental_health', css_class='col-md-6'),
                    css_class='row card-body'
                ),
                FormActions(
                    Submit('save', 'Save',
                           css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-success'),
                    Reset('reset', 'Reset',
                          css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-warning'),
                ),
                css_id='step-2',
            )
        )

    def save(self, request=None, instance=None, registry=None):

        validated_data = request.POST

        if not instance:
            instance = YouthKitService.objects.create(registration_id=registry)
        else:
            instance = YouthKitService.objects.get(id=instance)

        instance.volunteering_experience = validated_data.get('volunteering_experience')
        instance.previous_community_initiative = validated_data.get('previous_community_initiative')
        instance.enrollment_reason = validated_data.get('enrollment_reason')
        instance.pre_tests_administered = validated_data.get('pre_tests_administered')
        instance.test_diagnostic_done = validated_data.get('test_diagnostic_done')
        instance.receive_passing_grade = validated_data.get('receive_passing_grade')
        instance.life_skills_completed = validated_data.get('life_skills_completed')
        instance.participate_volunteering = validated_data.get('participate_volunteering')
        instance.volunteering_specify = validated_data.get('volunteering_specify')
        # instance.social_course = validated_data.get('social_course')
        instance.yfs_course_completed = validated_data.get('yfs_course_completed')
        instance.training_material = validated_data.get('training_material')
        instance.future_path = validated_data.get('future_path')
        instance.participate_community_initiatives = validated_data.get('participate_community_initiatives')
        instance.community_initiatives_specify = validated_data.get('community_initiatives_specify')
        instance.adolescent_attendance = validated_data.get('adolescent_attendance')
        instance.adolescent_dropout_reason = validated_data.get('adolescent_dropout_reason')
        if validated_data.get('adolescent_dropout_date'):
            instance.adolescent_dropout_date = validated_data.get('adolescent_dropout_date')
        instance.youth_trained_mental_health = validated_data.get('youth_trained_mental_health')
        instance.modified_by = request.user
        instance.save()

        messages.success(request, _('Your data has been sent successfully to the server'))

        update_service(registry_id=registry, service_name='Adolescents kit', service_id=instance.id)

        return instance

    def clean(self):
        cleaned_data = super(YouthKitServiceForm, self).clean()

        participate_volunteering = cleaned_data.get("participate_volunteering")
        volunteering_specify = cleaned_data.get("volunteering_specify")
        if participate_volunteering and participate_volunteering == 'Yes' and not volunteering_specify:
            self.add_error('volunteering_specify', 'This field is required')

        yfs_course_completed = cleaned_data.get("yfs_course_completed")
        training_material = cleaned_data.get("training_material")
        if yfs_course_completed and yfs_course_completed == 'Yes' and not training_material:
            self.add_error('training_material', 'This field is required')

        participate_community_initiatives = cleaned_data.get("participate_community_initiatives")
        community_initiatives_specify = cleaned_data.get("community_initiatives_specify")
        if participate_community_initiatives and participate_community_initiatives == 'Yes' and not community_initiatives_specify:
            self.add_error('community_initiatives_specify', 'This field is required')

        adolescent_attendance = cleaned_data.get("adolescent_attendance")
        adolescent_dropout_reason = cleaned_data.get("adolescent_dropout_reason")
        adolescent_dropout_date = cleaned_data.get("adolescent_dropout_date")
        if adolescent_attendance and adolescent_attendance == 'Dropout':
            if not adolescent_dropout_reason:
                self.add_error('adolescent_dropout_reason', 'This field is required')
            if not adolescent_dropout_date:
                self.add_error('adolescent_dropout_date', 'This field is required')

    class Meta:
        model = YouthKitService
        fields = (
            'volunteering_experience',
            'previous_community_initiative',
            'enrollment_reason',
            'pre_tests_administered',
            'test_diagnostic_done',
            'receive_passing_grade',
            'life_skills_completed',
            'participate_volunteering',
            'volunteering_specify',
            # 'social_course',
            'yfs_course_completed',
            'training_material',
            'future_path',
            'participate_community_initiatives',
            'community_initiatives_specify',
            'adolescent_attendance',
            'adolescent_dropout_reason',
            'adolescent_dropout_date',
            'youth_trained_mental_health'
        )


class YouthServiceMaharatiForm(forms.ModelForm):

    sports_taken = forms.ChoiceField(
        label=_('Sports for development'),
        widget=forms.Select, required=False,
        choices=YES_NO
    )
    sports_session_number = forms.IntegerField(
        label=_('Number of sessions'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        required=False,
        min_value=1,
        initial=1
    )
    life_skills_taken = forms.ChoiceField(
        label=_('Life skills'),
        widget=forms.Select, required=False,
        choices=YES_NO
    )
    life_skills_number = forms.IntegerField(
        label=_('Number of sessions'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        required=False,
        min_value=1,
        initial=1
    )
    youth_lead_initiatives_taken = forms.ChoiceField(
        label=_('Youth led initiatives'),
        widget=forms.Select, required=False,
        choices=YES_NO
    )
    youth_lead_initiatives_number = forms.IntegerField(
        label=_('Number of sessions'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        required=False,
        min_value=1,
        initial=1
    )
    youth_practiced_YLI_civic = forms.ChoiceField(
        label=_('Did the youth  practice YLI civic engagement'),
        widget=forms.Select, required=False,
        choices=YES_NO
    )

    registration_id = forms.CharField(widget=forms.HiddenInput, required=False)
    service_type = forms.CharField(widget=forms.HiddenInput, required=False)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        registry = kwargs.pop('registry', None)
        instance = kwargs.pop('instance', None)

        super(YouthServiceMaharatiForm, self).__init__(*args, **kwargs)

        form_action = reverse('mscc:service_youth_maharati_add',
                                  kwargs={'registry': registry })
        if instance:
            form_action = reverse('mscc:service_youth_maharati_edit',
                                  kwargs={'registry': registry, 'pk': instance})


        self.helper = FormHelper()
        self.helper.form_show_labels = True
        self.helper.form_action = form_action

        self.helper.layout = Layout(
            Div(
                Div(
                    HTML('<span class="badge-form badge-pill">1</span>'),
                    Div('sports_taken', css_class='col-md-4'),
                    Div('sports_session_number', css_class='col-md-4'),
                    css_class='row card-body '
                ),
                Div(
                    HTML('<span class="badge-form badge-pill">2</span>'),
                    Div('life_skills_taken', css_class='col-md-4'),
                    Div('life_skills_number', css_class='col-md-4'),
                    css_class='row card-body '
                ),
                Div(
                    HTML('<span class="badge-form badge-pill">3</span>'),
                    Div('youth_lead_initiatives_taken', css_class='col-md-4'),
                    Div('youth_lead_initiatives_number', css_class='col-md-4'),
                    css_class='row card-body '
                ),
                Div(
                    HTML('<span class="badge-form badge-pill">4</span>'),
                    Div('youth_practiced_YLI_civic', css_class='col-md-6'),
                    css_class='row card-body '
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
            instance = YouthService.objects.create(registration_id=registry)
        else:
            instance = YouthService.objects.get(id=instance)

        instance.service_values = request.POST
        instance.service_type = 'Maharati'
        instance.save()

        messages.success(request, _('Your data has been sent successfully to the server'))

        return instance

    def clean(self):
        cleaned_data = super(YouthServiceMaharatiForm, self).clean()

        sports_taken = cleaned_data.get("sports_taken")
        sports_session_number = cleaned_data.get("sports_session_number")
        if sports_taken and sports_taken == 'Yes' and not sports_session_number:
            self.add_error('sports_session_number', 'This field is required')

        life_skills_taken = cleaned_data.get("life_skills_taken")
        life_skills_number = cleaned_data.get("life_skills_number")
        if life_skills_taken and life_skills_taken == 'Yes' and not life_skills_number:
            self.add_error('life_skills_number', 'This field is required')

        youth_lead_initiatives_taken = cleaned_data.get("youth_lead_initiatives_taken")
        youth_lead_initiatives_number = cleaned_data.get("youth_lead_initiatives_number")
        if youth_lead_initiatives_taken and youth_lead_initiatives_taken == 'Yes' and not youth_lead_initiatives_number:
            self.add_error('youth_lead_initiatives_number', 'This field is required')

    class Meta:
        model = YouthService
        fields = (
            'service_type',
        )


class YouthServiceGilForm(forms.ModelForm):
    social_course = forms.ChoiceField(
        widget=forms.Select, required=True,
        choices=YES_NO,
        label=_('Did the adolescent benefit from any social innovation/entrepreneurship course?')
    )
    trainer_showed_knowledge = forms.ChoiceField(
        label=_('The trainer showed knowledge of the materials presented in the explanation.'),
        widget=forms.Select, required=False,
        choices=AGREE_DISAGREE
    )
    trainer_encouraged_discussions = forms.ChoiceField(
        label=_('The trainer encouraged discussions and critical thinking in the training'),
        widget=forms.Select, required=False,
        choices=AGREE_DISAGREE
    )
    trainer_provided_feedback = forms.ChoiceField(
        label=_('The trainer provided constructive feedback and directed it in a respectful and appropriate manner.'),
        widget=forms.Select, required=False,
        choices=AGREE_DISAGREE
    )
    trainer_patient_helped = forms.ChoiceField(
        label=_('The trainer was patient and helped me develop my ideas.'),
        widget=forms.Select, required=False,
        choices=AGREE_DISAGREE
    )
    training_part_useful = forms.CharField(
        label=_('In your opinion, what part of this training did you find most useful?'),
        widget=forms.Textarea, required=False
    )
    training_part_difficult = forms.CharField(
        label=_('What part of this training did you find difficult?'),
        widget=forms.Textarea, required=False
    )
    course_feel = forms.CharField(
        label=_('This course made me feel...'),
        widget=forms.Textarea, required=False
    )
    registration_id = forms.CharField(widget=forms.HiddenInput, required=False)
    service_type = forms.CharField(widget=forms.HiddenInput, required=False)


    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        registry = kwargs.pop('registry', None)
        instance = kwargs.pop('instance', None)

        super(YouthServiceGilForm, self).__init__(*args, **kwargs)

        form_action = reverse('mscc:service_youth_gil_add',
                                  kwargs={'registry': registry })
        if instance:
            form_action = reverse('mscc:service_youth_gil_edit',
                                  kwargs={'registry': registry, 'pk': instance})


        self.helper = FormHelper()
        self.helper.form_show_labels = True
        self.helper.form_action = form_action

        self.helper.layout = Layout(
            Div(
                Div(
                    HTML('<span class="badge-form badge-pill">1</span>'),
                    Div('social_course', css_class='col-md-8'),
                    css_class='row card-body '
                ),
                Div(
                    HTML('<span class="badge-form badge-pill">2</span>'),
                    Div('trainer_showed_knowledge', css_class='col-md-8'),
                    css_class='row card-body course'
                ),
                Div(
                    HTML('<span class="badge-form badge-pill">3</span>'),
                    Div('trainer_encouraged_discussions', css_class='col-md-8'),
                    css_class='row card-body course'
                ),
                Div(
                    HTML('<span class="badge-form badge-pill">4</span>'),
                    Div('trainer_provided_feedback', css_class='col-md-8'),
                    css_class='row card-body course'
                ),
                Div(
                    HTML('<span class="badge-form badge-pill">5</span>'),
                    Div('trainer_patient_helped', css_class='col-md-8'),
                    css_class='row card-body course'
                ),
                Div(
                    HTML('<span class="badge-form badge-pill">6</span>'),
                    Div('training_part_useful', css_class='col-md-8'),
                    css_class='row card-body course'
                ),
                Div(
                    HTML('<span class="badge-form badge-pill">7</span>'),
                    Div('training_part_difficult', css_class='col-md-8'),
                    css_class='row card-body course'
                ),
                Div(
                    HTML('<span class="badge-form badge-pill">8</span>'),
                    Div('course_feel', css_class='col-md-8'),
                    css_class='row card-body course'
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
            instance = YouthService.objects.create(registration_id=registry)
        else:
            instance = YouthService.objects.get(id=instance)

        instance.service_values = request.POST
        instance.service_type = 'GIL'
        instance.save()

        messages.success(request, _('Your data has been sent successfully to the server'))

        return instance

    def clean(self):
        cleaned_data = super(YouthServiceGilForm, self).clean()

    class Meta:
        model = YouthService
        fields = (
            'service_type',
        )


class FollowUpServiceForm(forms.ModelForm):

    follow_up_type = forms.ChoiceField(
        widget=forms.Select, required=True,
        choices=FollowUpService.FOLLOW_UP_TYPE,
        label=_('In case of absence, type of Follow-up done')
    )
    follow_up_number = forms.IntegerField(
        label=_('Number'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        required=True,
        min_value=1,
        initial=1
    )
    follow_up_result = forms.ChoiceField(
        widget=forms.Select, required=True,
        choices=FollowUpService.FOLLOW_UP_RESULT,
        label=_('Result of follow up')
    )
    dropout_reason = forms.CharField(
        required=False,
        widget=forms.TextInput,
        label=_('Reason for dropout')
    )
    dropout_date = forms.DateField(
        label=_("Dropout Date"),
        required=False
    )
    parent_attended_meeting = forms.ChoiceField(
        widget=forms.Select, required=True,
        choices=YES_NO,
        label=_('Did the child\'s caregiver attend parent meeting/engagment sessions')
    )
    meeting_type = forms.ChoiceField(
        widget=forms.Select, required=False,
        choices=FollowUpService.MEETING_TYPE,
        label=_('Please indicate the types of meeting')
    )
    meeting_number = forms.IntegerField(
        label=_('Number of sessions attended'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        required=False,
        min_value=0,
        initial=0
    )
    meeting_modality = forms.ChoiceField(
        widget=forms.Select, required=False,
        choices=FollowUpService.SESSION_MODALITY,
        label=_('Modality used per each session')
    )
    caregiver_attended = forms.ChoiceField(
        widget=forms.Select, required=False,
        choices=FollowUpService.CAREGIVER,
        label=_('Who attended the meetings')
    )
    caregiver_attended_other = forms.CharField(
        required=False,
        widget=forms.TextInput,
        label=_('If Other, Please specify')
    )
    pfss_sessions = forms.ChoiceField(
        widget=forms.Select, required=True,
        choices=YES_NO,
        label=_('Did they undertake FPSS sessions')
    )
    pfss_sessions_number = forms.IntegerField(
        widget=forms.NumberInput(attrs=({'maxlength': 4, 'max': 100})),
        required=False,
        label="Number of sessions attended",
        min_value=0,
        initial=0
    )
    registration_id = forms.CharField(widget=forms.HiddenInput, required=False)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        registry = kwargs.pop('registry', None)
        instance = kwargs.pop('instance', None)

        super(FollowUpServiceForm, self).__init__(*args, **kwargs)

        form_action = reverse('mscc:service_follow_up_add', kwargs={'registry': registry})
        if instance:
            form_action = reverse('mscc:service_follow_up_edit', kwargs={'registry': registry, 'pk': instance})

        self.helper = FormHelper()
        self.helper.form_show_labels = True
        self.helper.form_action = form_action
        self.helper.layout = Layout(
            Div(
                Div(
                    HTML('<span class="badge-form badge-pill">1</span>'),
                    Div('follow_up_type', css_class='col-md-4'),
                    HTML('<span class="badge-form badge-pill">2</span>'),
                    Div('follow_up_number', css_class='col-md-3'),
                    css_class='row card-body'
                ),
                Div(
                    HTML('<span class="badge-form badge-pill">3</span>'),
                    Div('follow_up_result', css_class='col-md-4'),
                    HTML('<span class="badge-form-0 badge-pill" id="span_dropout_reason"></span>'),
                    Div('dropout_reason', css_class='col-md-3'),
                    HTML('<span class="badge-form-0 badge-pill" id="span_dropout_date"></span>'),
                    Div('dropout_date', css_class='col-md-3'),
                    css_class='row card-body'
                ),
                css_id='step-1'
            ),
            Div(
                Div(
                    HTML('<span class="badge-form badge-pill">1</span>'),
                    Div('parent_attended_meeting', css_class='col-md-6'),
                    css_class='row card-body'
                ),

                Div(
                    HTML('<span class="badge-form-0 badge-pill" id="span_meeting_type"></span>'),
                    Div('meeting_type', css_class='col-md-3'),
                    HTML('<span class="badge-form-0 badge-pill" id="span_meeting_number"></span>'),
                    Div('meeting_number', css_class='col-md-3'),
                    HTML('<span class="badge-form-0 badge-pill" id="span_meeting_modality"></span>'),
                    Div('meeting_modality', css_class='col-md-3'),
                    css_class='row card-body'
                ),
                Div(
                    HTML('<span class="badge-form-0 badge-pill" id="span_caregiver_attended"></span>'),
                    Div('caregiver_attended', css_class='col-md-3'),
                    HTML('<span class="badge-form-0 badge-pill" id="span_caregiver_attended_other"></span>'),
                    Div('caregiver_attended_other', css_class='col-md-3'),
                    css_class='row card-body'
                ),
                Div(
                    HTML('<span class="badge-form badge-pill">2</span>'),
                    Div('pfss_sessions', css_class='col-md-3'),
                    HTML('<span class="badge-form-0 badge-pill" id="span_caregiver_attended_other"></span>'),
                    Div('pfss_sessions_number', css_class='col-md-3'),
                    css_class='row card-body'
                ),
                FormActions(
                    Submit('save', 'Save',
                           css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-success'),
                    Reset('reset', 'Reset',
                          css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-warning'),
                ),
                css_id='step-2',
            )
        )

    def save(self, request=None, instance=None, registry=None):

        validated_data = request.POST

        if not instance:
            instance = FollowUpService.objects.create(registration_id=registry)
        else:
            instance = FollowUpService.objects.get(id=instance)

        instance.follow_up_type = validated_data.get('follow_up_type')
        if validated_data.get('follow_up_number'):
            instance.follow_up_number = validated_data.get('follow_up_number')
        else:
            instance.follow_up_number = 1
        instance.follow_up_result = validated_data.get('follow_up_result')
        instance.dropout_reason = validated_data.get('dropout_reason')
        if validated_data.get('dropout_date'):
            instance.dropout_date = validated_data.get('dropout_date')
        instance.parent_attended_meeting = validated_data.get('parent_attended_meeting')
        instance.meeting_type = validated_data.get('meeting_type')

        if validated_data.get('meeting_number'):
            instance.meeting_number = validated_data.get('meeting_number')
        else:
            instance.meeting_number = 0

        instance.meeting_number = int(validated_data.get('meeting_number'))
        instance.meeting_modality = validated_data.get('meeting_modality')
        instance.caregiver_attended = validated_data.get('caregiver_attended')
        instance.caregiver_attended_other = validated_data.get('caregiver_attended_other')
        instance.pfss_sessions = validated_data.get('pfss_sessions')
        if validated_data.get('pfss_sessions_number'):
            instance.pfss_sessions_number = validated_data.get('pfss_sessions_number')
        else:
            instance.pfss_sessions_number = 0
        instance.modified_by = request.user
        instance.save()

        messages.success(request, _('Your data has been sent successfully to the server'))

        update_service(registry_id=registry, service_name='Caregivers Package', service_id=instance.id)

        return instance

    def clean(self):
        cleaned_data = super(FollowUpServiceForm, self).clean()
        follow_up_result = cleaned_data.get("follow_up_result")
        dropout_reason = cleaned_data.get("dropout_reason")
        dropout_date = cleaned_data.get("dropout_date")
        if follow_up_result and follow_up_result == 'Dropout/No Interest':
            if not dropout_reason:
                self.add_error('dropout_reason', 'This field is required')
            if not dropout_date:
                self.add_error('dropout_date', 'This field is required')

        parent_attended_meeting = cleaned_data.get("parent_attended_meeting")
        meeting_type = cleaned_data.get("meeting_type")
        meeting_number = cleaned_data.get("meeting_number")
        meeting_modality = cleaned_data.get("meeting_modality")
        caregiver_attended = cleaned_data.get("caregiver_attended")
        caregiver_attended_other = cleaned_data.get("caregiver_attended_other")
        if parent_attended_meeting and parent_attended_meeting == 'Yes':
            if not meeting_type:
                self.add_error('meeting_type', 'This field is required')
            if not meeting_number or meeting_number == 0:
                self.add_error('meeting_number', 'This field is required')
            if not meeting_modality:
                self.add_error('meeting_modality', 'This field is required')
            if not caregiver_attended:
                self.add_error('caregiver_attended', 'This field is required')
            elif caregiver_attended =='Other' and not caregiver_attended_other:
                self.add_error('caregiver_attended_other', 'This field is required')


        pfss_sessions = cleaned_data.get("pfss_sessions")
        pfss_sessions_number = cleaned_data.get("pfss_sessions_number")
        if pfss_sessions and pfss_sessions == 'Yes':
            if not pfss_sessions_number or pfss_sessions_number == 0:
                self.add_error('pfss_sessions_number', 'This field is required')


    class Meta:
        model = FollowUpService
        fields = (
            'follow_up_type',
            'follow_up_number',
            'follow_up_result',
            'dropout_reason',
            'dropout_date',
            'parent_attended_meeting',
            'meeting_type',
            'meeting_number',
            'meeting_modality',
            'caregiver_attended',
            'caregiver_attended_other',
            'pfss_sessions',
            'pfss_sessions_number'
        )


class YouthAssessmentForm(forms.ModelForm):

    undertake_post_diagnostic = forms.ChoiceField(
        widget=forms.Select, required=True,
        choices=YES_NO,
        label=_('Did the adolescent undertake any Post Diagnostic tests?')
    )
    receive_passing_grade = forms.ChoiceField(
        widget=forms.Select, required=False,
        choices=YES_NO,
        label=_('Did the adolescent receive a passing grade for the tests?')
    )
    complete_life_skills = forms.ChoiceField(
        widget=forms.Select, required=True,
        choices=YES_NO,
        label=_('Did the adolescent complete the life skills package?')
    )
    participate_volunteering = forms.ChoiceField(
        widget=forms.Select, required=True,
        choices=YES_NO,
        label=_('Did the adolescent participate in any volunteering opportunity during the course of the program?')
    )
    volunteering_opportunity = forms.ChoiceField(
        widget=forms.Select, required=False,
        choices=YouthAssessment.VOLUNTEERING_OPPORTUNITY,
        label=_('Is yes, please specify the volunteering opportunity')
    )
    benefit_innovation_course = forms.ChoiceField(
        widget=forms.Select, required=True,
        choices=YES_NO,
        label=_('Did the adolescent benefit from any social innovation/entrepreneurship course?')
    )
    compelete_yfs_course = forms.ChoiceField(
        widget=forms.Select, required=True,
        choices=YES_NO,
        label=_('Did the adolescent complete the YFS course?')
    )
    training_material = forms.ChoiceField(
        widget=forms.Select, required=False,
        choices=YouthAssessment.TRAINING_MATERIAL,
        label=_('What training material was provided?')
    )
    future_path = forms.ChoiceField(
        widget=forms.Select, required=True,
        choices=YouthAssessment.FUTURE_PATH,
        label=_('What is the recommended future path for the adolescent?')
    )
    participate_community_initiatives = forms.ChoiceField(
        widget=forms.Select, required=True,
        choices=YES_NO,
        label=_('Did the adolescent participate/come up in community based initiatives?')
    )
    attendance = forms.ChoiceField(
        widget=forms.Select, required=True,
        choices=YouthAssessment.ATTENDANCE,
        label=_('Adolescent attendance')
    )
    registration_id = forms.CharField(widget=forms.HiddenInput, required=False)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        registry = kwargs.pop('registry', None)
        instance = kwargs.pop('instance', None)

        super(YouthAssessmentForm, self).__init__(*args, **kwargs)

        form_action = reverse('mscc:service_youth_assessment_add', kwargs={'registry': registry})
        if instance:
            form_action = reverse('mscc:service_youth_assessment_edit', kwargs={'registry': registry, 'pk': instance})

        self.helper = FormHelper()
        self.helper.form_show_labels = True
        self.helper.form_action = form_action
        self.helper.layout = Layout(
            Div(
                Div(
                    HTML('<span class="badge-form badge-pill">1</span>'),
                    Div('undertake_post_diagnostic', css_class='col-md-5'),
                    Div('receive_passing_grade', css_class='col-md-6'),
                    css_class='row card-body'
                ),
                Div(
                    HTML('<span class="badge-form badge-pill">2</span>'),
                    Div('complete_life_skills', css_class='col-md-4'),
                    css_class='row card-body'
                ),
                Div(
                    HTML('<span class="badge-form badge-pill">3</span>'),
                    Div('participate_volunteering', css_class='col-md-7'),
                    Div('volunteering_opportunity', css_class='col-md-4'),
                    css_class='row card-body'
                ),
                Div(
                    HTML('<span class="badge-form badge-pill">4</span>'),
                    Div('benefit_innovation_course', css_class='col-md-8'),
                    css_class='row card-body'
                ),
                Div(
                    HTML('<span class="badge-form badge-pill">5</span>'),
                    Div('compelete_yfs_course', css_class='col-md-6'),
                    Div('training_material', css_class='col-md-4'),
                    css_class='row card-body'
                ),
                Div(
                    HTML('<span class="badge-form badge-pill">6</span>'),
                    Div('future_path', css_class='col-md-6'),
                    css_class='row card-body'
                ),
                Div(
                    HTML('<span class="badge-form badge-pill">7</span>'),
                    Div('participate_community_initiatives', css_class='col-md-8'),
                    css_class='row card-body'
                ),
                Div(
                    HTML('<span class="badge-form badge-pill">8</span>'),
                    Div('attendance', css_class='col-md-4'),
                    css_class='row card-body'
                ),
                FormActions(
                    Submit('save', 'Save',
                           css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-success'),
                    Reset('reset', 'Reset',
                          css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-warning'),
                ),
                css_id='step-1',
            )
        )

    def save(self, request=None, instance=None, registry=None):

        validated_data = request.POST

        if not instance:
            instance = YouthAssessment.objects.create(registration_id=registry)
        else:
            instance = YouthAssessment.objects.get(id=instance)

        instance.undertake_post_diagnostic = validated_data.get('undertake_post_diagnostic')
        instance.undertake_post_diagnostic = validated_data.get('undertake_post_diagnostic')
        instance.receive_passing_grade = validated_data.get('receive_passing_grade')
        instance.complete_life_skills = validated_data.get('complete_life_skills')
        instance.participate_volunteering = validated_data.get('participate_volunteering')
        instance.volunteering_opportunity = validated_data.get('volunteering_opportunity')
        instance.benefit_innovation_course = validated_data.get('benefit_innovation_course')
        instance.compelete_yfs_course = validated_data.get('compelete_yfs_course')
        instance.training_material = validated_data.get('training_material')
        instance.future_path = validated_data.get('future_path')
        instance.participate_community_initiatives = validated_data.get('participate_community_initiatives')
        instance.attendance = validated_data.get('attendance')
        instance.modified_by = request.user
        instance.save()

        messages.success(request, _('Your data has been sent successfully to the server'))


        return instance

    def clean(self):
        cleaned_data = super(YouthAssessmentForm, self).clean()
        undertake_post_diagnostic = cleaned_data.get("undertake_post_diagnostic")
        receive_passing_grade = cleaned_data.get("receive_passing_grade")
        if undertake_post_diagnostic and undertake_post_diagnostic == 'Yes' and not receive_passing_grade:
            self.add_error('receive_passing_grade', 'This field is required')

        participate_volunteering = cleaned_data.get("participate_volunteering")
        volunteering_opportunity = cleaned_data.get("volunteering_opportunity")
        if participate_volunteering and participate_volunteering == 'Yes' and not volunteering_opportunity:
            self.add_error('volunteering_opportunity', 'This field is required')

        compelete_yfs_course = cleaned_data.get("compelete_yfs_course")
        training_material = cleaned_data.get("training_material")
        if compelete_yfs_course and compelete_yfs_course == 'Yes' and not training_material:
            self.add_error('training_material', 'This field is required')

    class Meta:
        model = YouthAssessment
        fields = (
            'undertake_post_diagnostic',
            'receive_passing_grade',
            'complete_life_skills',
            'participate_volunteering',
            'volunteering_opportunity',
            'benefit_innovation_course',
            'compelete_yfs_course',
            'training_material',
            'future_path',
            'participate_community_initiatives',
            'attendance'
        )


class YouthReferralForm(forms.ModelForm):

    refer_tvet = forms.ChoiceField(
        widget=forms.Select, required=True,
        choices=YES_NO,
        label=_('Did the partner refer youth who are above 18 to the TVET centers')
    )
    refer_innovation = forms.ChoiceField(
        widget=forms.Select, required=False,
        choices=YES_NO,
        label=_('Did the partner refer youth who are above 18 to the  innovation hubs GIL?')
    )
    registration_id = forms.CharField(widget=forms.HiddenInput, required=False)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        registry = kwargs.pop('registry', None)
        instance = kwargs.pop('instance', None)

        super(YouthReferralForm, self).__init__(*args, **kwargs)

        form_action = reverse('mscc:service_youth_referral_add', kwargs={'registry': registry})
        if instance:
            form_action = reverse('mscc:service_youth_referral_edit', kwargs={'registry': registry, 'pk': instance})

        self.helper = FormHelper()
        self.helper.form_show_labels = True
        self.helper.form_action = form_action
        self.helper.layout = Layout(
            Div(
                Div(
                    HTML('<span class="badge-form badge-pill">1</span>'),
                    Div('refer_tvet', css_class='col-md-5'),
                    css_class='row card-body'
                ),
                Div(
                    HTML('<span class="badge-form badge-pill">2</span>'),
                    Div('refer_innovation', css_class='col-md-4'),
                    css_class='row card-body'
                ),
                FormActions(
                    Submit('save', 'Save',
                           css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-success'),
                    Reset('reset', 'Reset',
                          css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-warning'),
                ),
                css_id='step-1',
            )
        )

    def save(self, request=None, instance=None, registry=None):

        validated_data = request.POST

        if not instance:
            instance = YouthReferral.objects.create(registration_id=registry)
        else:
            instance = YouthReferral.objects.get(id=instance)

        instance.refer_tvet = validated_data.get('refer_tvet')
        instance.refer_innovation = validated_data.get('refer_innovation')
        instance.modified_by = request.user
        instance.save()

        messages.success(request, _('Your data has been sent successfully to the server'))

        return instance

    class Meta:
        model = YouthReferral
        fields = (
            'refer_tvet',
            'refer_innovation',
        )


class RecreationalForm(forms.ModelForm):
    sports = forms.ChoiceField(
        widget=forms.Select, required=True,
        choices=YES_NO,
        label=_('Sports for Development Programmes')
    )
    sports_nbr_sessions = forms.IntegerField(
        widget=forms.NumberInput(attrs=({'maxlength': 4, 'max': 100})),
        required=False,
        label="Number of sessions attended",
        initial=0
    )
    qudwa = forms.ChoiceField(
        widget=forms.Select, required=True,
        choices=YES_NO,
        label=_('Qudwa initiatives')
    )
    qudwa_nbr_sessions = forms.IntegerField(
        widget=forms.NumberInput(attrs=({'maxlength': 4, 'max': 100})),
        required=False,
        label="Number of sessions attended",
        initial=0
    )
    community_events = forms.ChoiceField(
        widget=forms.Select, required=True,
        choices=(
            ('No', 'No'),
            ('Theater plays', 'Theater plays'),
            ('Arts', 'Arts'),
            ('Music', 'Music'),
            ('Others', 'Others')
        ),
        label=_('Community Events')
    )
    community_events_nbr_sessions = forms.IntegerField(
        widget=forms.NumberInput(attrs=({'maxlength': 4, 'max': 100})),
        required=False,
        label="Number of sessions attended",
        initial=0
    )
    registration_id = forms.CharField(widget=forms.HiddenInput, required=False)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        registry = kwargs.pop('registry', None)
        instance = kwargs.pop('instance', None)

        super(RecreationalForm, self).__init__(*args, **kwargs)

        form_action = reverse('mscc:service_recreational_add', kwargs={'registry': registry})
        if instance:
            form_action = reverse('mscc:service_recreational_edit', kwargs={'registry': registry, 'pk': instance})

        self.helper = FormHelper()
        self.helper.form_show_labels = True
        self.helper.form_action = form_action

        self.helper.layout = Layout(
            Div(
                Div(
                    HTML('<h3>What Recreational activities did the child attend:</h3>'),
                    css_class='row card-body mb-5'
                ),
                Div(
                    HTML('<span class="badge-form badge-pill">1</span>'),
                    Div('sports', css_class='col-md-4'),
                    Div('sports_nbr_sessions', css_class='col-md-4'),
                    css_class='row card-body'
                ),
                Div(
                    HTML('<span class="badge-form badge-pill">2</span>'),
                    Div('qudwa', css_class='col-md-4'),
                    Div('qudwa_nbr_sessions', css_class='col-md-4'),
                    css_class='row card-body'
                ),
                Div(
                    HTML('<span class="badge-form badge-pill">3</span>'),
                    Div('community_events', css_class='col-md-4'),
                    Div('community_events_nbr_sessions', css_class='col-md-4'),
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
        if not instance:
            instance = Recreational.objects.create(registration_id=registry)
        else:
            instance = Recreational.objects.get(id=instance)

        instance.assessment = request.POST
        instance.save()

        messages.success(request, _('Your data has been sent successfully to the server'))

        return instance

    class Meta:
        model = Recreational
        fields = ()


class LegoServiceForm(forms.ModelForm):
    # Children 7-14 years
    participating_lego_sessions = forms.ChoiceField(
        widget=forms.Select, required=False,
        choices=YES_NO,
        label=_('Is the child participating in CBPSS LEGO sessions?')
    )
    # Children 3-14 years
    participating_education_sessions = forms.ChoiceField(
        widget=forms.Select, required=False,
        choices=YES_NO,
        label=_('Is the child participating in Education sessions supported by LEGO activities?')
    )
    # Children 3-14 years
    participating_lego_play_sessions = forms.ChoiceField(
        widget=forms.Select, required=False,
        choices=YES_NO,
        label=_('Is the child participating in LEGO free-play sessions?')
    )

    child_age = forms.CharField(widget=forms.HiddenInput, required=False)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        registry = kwargs.pop('registry', None)
        instance = kwargs.pop('instance', None)
        age = int(kwargs.pop('age', None))

        super(LegoServiceForm, self).__init__(*args, **kwargs)

        if 3 <= age <= 14:
            self.fields['participating_education_sessions'].required = True
            self.fields['participating_lego_play_sessions'].required = True
        if 7 <= age <= 14:
            self.fields['participating_lego_sessions'].required = True
            self.fields['participating_education_sessions'].required = True
            self.fields['participating_lego_play_sessions'].required = True

        form_action = reverse('mscc:service_lego_add', kwargs={'registry': registry, 'age': age})
        if instance:
            form_action = reverse('mscc:service_lego_edit', kwargs={'registry': registry, 'age': age, 'pk': instance})

        self.fields['child_age'].initial = age
        self.helper = FormHelper()
        self.helper.form_show_labels = True
        self.helper.form_action = form_action

        if 3 <= age <= 14:
            self.helper.layout = Layout(
                Div(
                    Div(
                        Div('child_age', css_class='col-md-6'),
                        css_class='row card-body d-none'
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">1</span>'),
                        Div('participating_education_sessions', css_class='col-md-8'),
                        css_class='row card-body'
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">1</span>'),
                        Div('participating_lego_sessions', css_class='col-md-8'),
                        css_class='row card-body d-none'
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">2</span>'),
                        Div('participating_lego_play_sessions', css_class='col-md-8'),
                        css_class='row card-body'
                    ),
                    FormActions(
                        Submit('save', 'Save',
                               css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-success'),
                        Reset('reset', 'Reset',
                              css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-warning'),
                    ),
                    css_id='step-1'
                )
            )
        if 7 <= age <= 14:
            self.helper.layout = Layout(
                Div(
                    Div(
                        Div('child_age', css_class='col-md-6'),
                        css_class='row card-body d-none'
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">1</span>'),
                        Div('participating_lego_sessions', css_class='col-md-8'),
                        css_class='row card-body'
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">2</span>'),
                        Div('participating_education_sessions', css_class='col-md-8'),
                        css_class='row card-body'
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">3</span>'),
                        Div('participating_lego_play_sessions', css_class='col-md-8'),
                        css_class='row card-body'
                    ),
                    FormActions(
                        Submit('save', 'Save',
                               css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-success'),
                        Reset('reset', 'Reset',
                              css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-warning'),
                    ),
                    css_id='step-1'
                )
            )

    def save(self, request=None, instance=None, registry=None):

        validated_data = request.POST

        if not instance:
            instance = LegoService.objects.create(registration_id=registry)
        else:
            instance = LegoService.objects.get(id=instance)

        instance.participating_lego_sessions = validated_data.get('participating_lego_sessions')
        instance.participating_education_sessions = validated_data.get('participating_education_sessions')
        instance.participating_lego_play_sessions = validated_data.get('participating_lego_play_sessions')
        instance.modified_by = request.user
        instance.save()

        messages.success(request, _('Your data has been sent successfully to the server'))

        update_service(registry_id=registry, service_name='LEGO', service_id=instance.id)

        return instance

    registration_id = forms.CharField(widget=forms.HiddenInput, required=False)

    class Meta:
        model = LegoService
        fields = (
            'participating_lego_sessions',
            'participating_education_sessions',
            'participating_lego_play_sessions',
        )

