from __future__ import unicode_literals, absolute_import, division

from django.utils.translation import gettext as _
from django import forms
from django.urls import reverse
from django.contrib import messages

from crispy_forms.helper import FormHelper

from crispy_forms.bootstrap import (
    FormActions,
    InlineCheckboxes
)
from crispy_forms.layout import Layout, Fieldset, Button, Submit, Div, Field, HTML, Reset
from dal import autocomplete
from student_registration.users.templatetags.custom_tags import has_group

from student_registration.students.models import (
    Student,
    Person,
    Nationality,
    IDType,
)
from student_registration.schools.models import (
    School,
    ClassRoom,
    EducationalLevel,
    PartnerOrganization,
)
from student_registration.locations.models import Location
from .models import (
    CLM,
    BLN,
    ABLN,
    RS,
    CBECE,
    Cycle,
    Disability,
    Assessment,
    CLMRound,
    ABLN_FC,
    BLN_FC,
    RS_FC,
    CBECE_FC,
    Center,
    GeneralQuestionnaire,
    Outreach,
    Bridging
)
from .serializers import (
    BLNSerializer,
    RSSerializer,
    CBECESerializer,
    ABLNSerializer,
    ABLN_FCSerializer,
    BLN_FCSerializer,
    RS_FCSerializer,
    CBECE_FCSerializer,
    GeneralQuestionnaireSerializer,
    OutreachSerializer,
    BridgingSerializer,
)

from django.forms.widgets import ClearableFileInput

YES_NO_CHOICE = ((1, _("Yes")), (0, _("No")))

import datetime
YEARS = list(((str(x), x) for x in range(Person.CURRENT_YEAR-20, Person.CURRENT_YEAR-2)))
YEARS.insert(0, ('', '---------'))

DAYS = list(((str(x), x) for x in range(1, 32)))
DAYS.insert(0, ('', '---------'))

MONTHS = (
            ('', '----------'),
            ('1', _('January')),
            ('2', _('February')),
            ('3', _('March')),
            ('4', _('April')),
            ('5', _('May')),
            ('6', _('June')),
            ('7', _('July')),
            ('8', _('August')),
            ('9', _('September')),
            ('10', _('October')),
            ('11', _('November')),
            ('12', _('December')),
        )

FAMILY_STATUS = (
    ('', '----------'),
    ('married', _('Married')),
    ('engaged', _('Engaged')),
    ('divorced', _('Divorced')),
    ('widower', _('Widower')),
    ('single', _('Single')),
)

PARTICIPATION = (
    ('', '----------'),
    ('less_than_5days', _('Less than 5 absence days')),
    ('5_10_days', _('5 to 10 absence days')),
    ('10_15_days', _('10 to 15 absence days')),
    ('more_than_15days', _('More than 15 absence days')),
    ('no_absence', _('No Absence'))
)

LEARNING_RESULT = (
    ('', '----------'),
    ('repeat_level', _('Repeat level')),
    ('graduated_next_level', _('Referred to the next level')),
    ('graduated_to_formal_kg', _('Referred to formal education - KG')),
    ('graduated_to_formal_level1', _('Referred to formal education - Level 1')),
    ('referred_to_another_program', _('Referred to another program')),
    ('dropout', _('Dropout, referral not possible'))
)

REGISTRATION_LEVEL = (
    ('', '----------'),
    ('level_one', _('Level one')),
    ('level_two', _('Level two')),

)


class CustomClearableFileInput(ClearableFileInput):
    template_name = 'students/clearable_file_input.html'


class CommonForm(forms.ModelForm):

    YEARS_CT = list(((str(x), x) for x in range(1940, Person.CURRENT_YEAR - 18)))
    YEARS_CT.insert(0, ('', '---------'))

    search_clm_student = forms.CharField(
        label=_("Search a student"),
        widget=forms.TextInput,
        required=False
    )
    search_outreach_student = forms.CharField(
        label=_("Search a student from old registration"),
        widget=forms.TextInput,
        required=False
    )
    search_Kobo_outreach_student = forms.CharField(
        label=_("Search a student from Kobo data"),
        widget=forms.TextInput,
        required=False
    )
    governorate = forms.ModelChoiceField(
        queryset=Location.objects.filter(parent__isnull=True), widget=forms.Select,
        label=_('Governorate'),
        empty_label='-------',
        required=True, to_field_name='id',
        # initial=0
    )
    district = forms.ModelChoiceField(
        queryset=Location.objects.filter(parent__isnull=False), widget=forms.Select,
        label=_('District'),
        empty_label='-------',
        required=True, to_field_name='id',
        # initial=0
    )
    cadaster = forms.ModelChoiceField(
        queryset=Location.objects.filter(parent__isnull=False), widget=forms.Select,
        label=_('Cadaster'),
        empty_label='-------',
        required=True, to_field_name='id',
        # initial=0
    )
    round = forms.ModelChoiceField(
        queryset=CLMRound.objects.all(), widget=forms.Select,
        label=_('Round'),
        empty_label='-------',
        required=True, to_field_name='id',
        initial=0
    )
    # round_start_date = forms.DateField(
    #     label=_("Round start date"),
    #     required=True
    # )
    language = forms.ChoiceField(
        label=_('The language supported in the program'),
        widget=forms.Select,
        choices=CLM.LANGUAGES, required=True,
        initial='english_arabic'
    )

    student_first_name = forms.CharField(
        label=_("First name"),
        widget=forms.TextInput, required=True
    )
    student_father_name = forms.CharField(
        label=_("Father name"),
        widget=forms.TextInput, required=True
    )
    student_last_name = forms.CharField(
        label=_("Last name"),
        widget=forms.TextInput, required=True
    )
    student_sex = forms.ChoiceField(
        label=_("Gender"),
        widget=forms.Select, required=True,
        choices=(
            ('', '----------'),
            ('Male', _('Male')),
            ('Female', _('Female')),
        )
    )
    # student_birthday_year = forms.ChoiceField(
    #     label=_("Birthday year"),
    #     widget=forms.Select, required=True,
    #     choices=YEARS
    # )
    student_birthday_month = forms.ChoiceField(
        label=_("Birthday month"),
        widget=forms.Select, required=True,
        choices=MONTHS
    )
    student_birthday_day = forms.ChoiceField(
        label=_("Birthday day"),
        widget=forms.Select, required=True,
        choices=DAYS
    )
    student_nationality = forms.ModelChoiceField(
        label=_("Nationality"),
        queryset=Nationality.objects.exclude(id=9), widget=forms.Select,
        required=True, to_field_name='id',
    )
    main_caregiver_nationality = forms.ModelChoiceField(
        label=_("Nationality"),
        queryset=Nationality.objects.exclude(id=9), widget=forms.Select,
        required=False, to_field_name='id',
    )
    student_mother_fullname = forms.CharField(
        label=_("Mother fullname"),
        widget=forms.TextInput, required=True
    )
    student_address = forms.CharField(
        label=_("The area where the child resides"),
        widget=forms.TextInput, required=True
    )
    student_p_code = forms.CharField(
        label=_('P-Code If a child lives in a tent / Brax in a random camp'),
        widget=forms.TextInput, required=False,
        max_length=50,
    )
    # student_id_number = forms.CharField(
    #     label=_('ID number'),
    #     widget=forms.TextInput, required=False
    # )

    disability = forms.ModelChoiceField(
        queryset=Disability.objects.filter(active=True), widget=forms.Select,
        label=_('Does the child have any disability or special need?'),
        required=True, to_field_name='id',
        initial=1
    )
    hh_educational_level = forms.ModelChoiceField(
        queryset=EducationalLevel.objects.exclude(id=3), widget=forms.Select,
        label=_('What is the educational level of the mother?'),
        required=False, to_field_name='id',
    )
    father_educational_level = forms.ModelChoiceField(
        queryset=EducationalLevel.objects.exclude(id=3), widget=forms.Select,
        label=_('What is the educational level of the father?'),
        required=False, to_field_name='id',
    )
    student_id = forms.CharField(widget=forms.HiddenInput, required=False)
    enrollment_id = forms.CharField(widget=forms.HiddenInput, required=False)
    partner_name = forms.CharField(widget=forms.HiddenInput, required=False)
    clm_type = forms.CharField(widget=forms.HiddenInput, required=False)
    caretaker_first_name = forms.CharField(
        label=_("Caregiver First Name"),
        widget=forms.TextInput, required=False
    )
    caretaker_middle_name = forms.CharField(
        label=_("Caregiver Middle Name"),
        widget=forms.TextInput, required=False
    )
    caretaker_last_name = forms.CharField(
        label=_("Caregiver Last Name"),
        widget=forms.TextInput, required=False
    )
    caretaker_mother_name = forms.CharField(
        label=_("Caregiver Mother Name"),
        widget=forms.TextInput, required=False
    )
    caretaker_birthday_year = forms.ChoiceField(
        label=_("Caregiver birthday year"),
        widget=forms.Select, required=False,
        choices = YEARS_CT,
    )
    caretaker_birthday_month = forms.ChoiceField(
        label=_("Caregiver birthday month"),
        widget=forms.Select, required=False,
        choices=MONTHS
    )
    caretaker_birthday_day = forms.ChoiceField(
        label=_("Caregiver birthday day"),
        widget=forms.Select, required=False,
        choices=DAYS
    )


    # participation = forms.ChoiceField(
    #     label=_('How was the level of child participation in the program?'),
    #     widget=forms.Select, required=False,
    #     choices=PARTICIPATION,
    #     initial=''
    # )
    # barriers = forms.MultipleChoiceField(
    #     label=_('The main barriers affecting the daily attendance and performance of the child or drop out of programme? (Select more than one if applicable)'),
    #     choices=CLM.BARRIERS,
    #     widget=forms.CheckboxSelectMultiple,
    #     required=False
    # )
    # learning_result = forms.ChoiceField(
    #     label=_('Based on the overall score, what is the recommended learning path?'),
    #     widget=forms.Select, required=False,
    #     choices=(
    #         ('', '----------'),
    #         ('repeat_level', _('Repeat level')),
    #         ('graduated_next_level', _('Referred to the next level')),
    #         ('graduated_to_formal_kg', _('Referred to formal education - KG')),
    #         ('graduated_to_formal_level1', _('Referred to formal education - Level 1')),
    #         ('referred_to_another_program', _('Referred to another program')),
    #         # ('dropout', _('Dropout from school'))
    #     ),
    #     initial=''
    # )

    def __init__(self, *args, **kwargs):
        super(CommonForm, self).__init__(*args, **kwargs)

    # def clean(self):
    #     from django.db.models import Q
    #     cleaned_data = super(CommonForm, self).clean()
    #     id_number = cleaned_data.get('student_id_number')
    #     internal_number = cleaned_data.get('internal_number')
    #     queryset = self.Meta.model.objects.all()
    #
    #     if queryset.filter(Q(student__id_number=id_number) | Q(internal_number=internal_number)).count():
    #         raise forms.ValidationError(
    #             _("Child already registered in your organization")
    #         )

    def save(self, request=None, instance=None, serializer=None):
        if instance:
            serializer = serializer(instance, data=request.POST)
            if serializer.is_valid():
                instance = serializer.update(validated_data=serializer.validated_data, instance=instance)
                instance.modified_by = request.user
                instance.save()
                request.session['instance_id'] = instance.id
                messages.success(request, _('Your data has been sent successfully to the server'))
            else:
                messages.warning(request, serializer.errors)
        else:
            serializer = serializer(data=request.POST)
            if serializer.is_valid():
                instance = serializer.create(validated_data=serializer.validated_data)
                instance.owner = request.user
                instance.modified_by = request.user
                instance.partner = request.user.partner
                instance.save()
                request.session['instance_id'] = instance.id
                messages.success(request, _('Your data has been sent successfully to the server'))
            else:
                messages.warning(request, serializer.errors)

        return instance

    class Meta:
        model = CLM
        fields = (
            'first_attendance_date',
            'round',
            'governorate',
            'district',
            'cadaster',
            'language',
            'student_first_name',
            'student_father_name',
            'student_last_name',
            'student_sex',
            'student_birthday_month',
            'student_birthday_day',
            'student_nationality',
            'student_mother_fullname',
            'student_address',
            'student_p_code',
            # 'student_id_number',
            'internal_number',
            'disability',
            # 'have_labour',
            # 'labours',
            # 'labour_hours',
            'hh_educational_level',
            'father_educational_level',
            # 'participation',
            # 'barriers',
            # 'learning_result',
            'student_id',
            'enrollment_id',
            'partner_name',
            # 'comments',
            # 'unsuccessful_pretest_reason',
            # 'unsuccessful_posttest_reason',
            'caretaker_birthday_year',
            'caretaker_birthday_month',
            'caretaker_birthday_day'
        )
        initial_fields = fields
        widgets = {}

    class Media:
        js = (
            # 'js/jquery-3.3.1.min.js',
            # 'js/jquery-ui-1.12.1.js',
            # 'js/validator.js',
            # 'js/registrations.js',
        )


class BridgingForm(CommonForm):

    REGISTRATION_LEVEL = (
        ('', '----------'),
        ('level_one', _('Level one')),
        ('level_two', _('Level two')),
        ('level_three', _('Level three')),
        ('level_one_pm', _('Level one PM shift')),
        ('level_two_pm', _('Level two PM shift')),
        ('level_three_pm', _('Level three PM shift')),
        ('level_four_pm', _('Level four PM shift')),
        ('level_five_pm', _('Level five PM shift')),
        ('level_six_pm', _('Level six PM shift')),
        ('grade_one', _('Grade one')),
        ('grade_two', _('Grade two')),
        ('grade_three', _('Grade three')),
        ('grade_four', _('Grade four')),
        ('grade_five', _('Grade five')),
        ('grade_six', _('Grade six')),
        ('grade_seven', _('Grade seven')),
        ('grade_eight', _('Grade eight')),
        ('grade_nine', _('Grade nine')),
        # ('level_four', _('Level four')),
        # ('level_five', _('Level five')),
        # ('level_six', _('Level six'))
    )

    YEARS_Bridging = list(((str(x), x) for x in range(Person.CURRENT_YEAR - 14, Person.CURRENT_YEAR - 5)))
    YEARS_Bridging.insert(0, ('', '---------'))
    language = forms.ChoiceField(
        label=_("The language supported in the program"),
        widget=forms.Select, required=True,
        choices=Bridging.LANGUAGES,
        initial='yes'
    )
    first_attendance_date = forms.DateField(
        label=_("First attendance date"),
        required=False
    )
    residence_type = forms.ChoiceField(
        label=_("Residence Type"),
        widget=forms.Select, required=True,
        choices=Bridging.RESIDENCE_TYPE,
        initial='yes'
    )
    miss_school_date = forms.DateField(
        label=_("Miss school date"),
        required=False,
    )

    new_registry = forms.ChoiceField(
        label=_("First time registered Bridging?"),
        widget=forms.Select, required=True,
        choices=(('yes', _("Yes")), ('no', _("No"))),
        initial='yes'
    )
    round = forms.ModelChoiceField(
        queryset=CLMRound.objects.filter(current_round_bridging=True), widget=forms.Select,
        label=_('Academic year'),
        empty_label='-------',
        required=True, to_field_name='id',
    )
    round_start_date = forms.DateField(
        label=_("Round start date"),
        required=False
    )
    registration_level = forms.ChoiceField(
        label=_("Registration level"),
        widget=forms.Select, required=True,
        choices=REGISTRATION_LEVEL
    )
    school = forms.ModelChoiceField(
        queryset=School.objects.filter(is_closed=False), widget=forms.Select,
        label=_('School Name'),
        empty_label='-------',
        required=False, to_field_name='id',
        initial=0
    )

    student_birthday_year = forms.ChoiceField(
        label=_("Birthday year"),
        widget=forms.Select, required=True,
        choices=YEARS_Bridging
    )

    student_family_status = forms.ChoiceField(
        label=_('What is the family status of the child?'),
        widget=forms.Select, required=True,
        choices=Student.FAMILY_STATUS,
        initial='single'
    )
    student_have_children = forms.TypedChoiceField(
        label=_("Does the child have children?"),
        choices=YES_NO_CHOICE,
        coerce=lambda x: bool(int(x)),
        widget=forms.RadioSelect,
        required=True,
    )
    student_number_children = forms.IntegerField(
        label=_('How many children does this child have?'),
        widget=forms.TextInput, required=False
    )

    have_labour_single_selection = forms.ChoiceField(
        label=_('Does the child participate in work?'),
        widget=forms.Select, required=True,
        choices=CLM.HAVE_LABOUR,
        initial='no'
    )
    labours_single_selection = forms.ChoiceField(
        label=_('What is the type of work ?'),
        widget=forms.Select, required=False,
        choices=CLM.LABOURS
    )
    labours_other_specify = forms.CharField(
        label=_('Please specify(hotel, restaurant, transport, personal services such as cleaning, '
                'hair care, cooking and childcare)'),
        widget=forms.TextInput, required=False
    )

    labour_hours = forms.CharField(
        label=_('How many hours does this child work in a day?'),
        widget=forms.TextInput, required=False
    )
    labour_weekly_income = forms.ChoiceField(
        label=_('What is the income of the child per week?'),
        widget=forms.Select,
        choices=Student.STUDENT_INCOME,
        initial='single',
        required=False
    )
    education_status = forms.ChoiceField(
        label=_('Education status'),
        widget=forms.Select, required=True,
        choices=(
            ('No Registered in any school before', _('Not Registered in any school before')),
            ('Was registered in BLN program', _('Was registered in BLN program')),
            ('Was registered in formal school and didnt continue',
             _('Was registered in formal school and didnt continue')),
            ('Was registered in CBECE program', _('Was registered in CBECE program')),
            ('Was registered in ALP program and didnt continue', _('Was registered in ALP program and didnt continue'))

        ),
        initial=''
    )

    other_nationality = forms.CharField(
        label=_('Specify the nationality'),
        widget=forms.TextInput, required=False
    )

    phone_number = forms.RegexField(
        regex=r'^((03)|(70)|(71)|(76)|(78)|(79)|(81))-\d{6}$',
        widget=forms.TextInput(attrs={'placeholder': 'Format: XX-XXXXXX'}),
        required=True,
        label=_('Main Phone number')
    )
    phone_number_confirm = forms.RegexField(
        regex=r'^((03)|(70)|(71)|(76)|(78)|(79)|(81))-\d{6}$',
        widget=forms.TextInput(attrs={'placeholder': 'Format: XX-XXXXXX'}),
        required=True,
        label=_('Main Phone number confirm')
    )
    second_phone_number = forms.RegexField(
        regex=r'^((03)|(70)|(71)|(76)|(78)|(79)|(81))-\d{6}$',
        widget=forms.TextInput(attrs={'placeholder': 'Format: XX-XXXXXX'}),
        required=False,
        label=_('Second Phone Number')
    )
    second_phone_number_confirm = forms.RegexField(
        regex=r'^((03)|(70)|(71)|(76)|(78)|(79)|(81))-\d{6}$',
        widget=forms.TextInput(attrs={'placeholder': 'Format: XX-XXXXXX'}),
        required=False,
        label=_('Second Phone Number confirm')
    )

    id_type = forms.ChoiceField(
        label=_("ID type of the Child"),
        widget=forms.Select(attrs=({'translation': _('Child no ID confirmation popup message')})),
        required=True,
        choices=(
            ('', '----------'),
            ('UNHCR Registered', _('UNHCR Registered')),
            ('UNHCR Recorded', _("UNHCR Recorded")),
            ('Syrian national ID', _("Syrian national ID")),
            ('Palestinian national ID', _("Palestinian national ID")),
            ('Lebanese national ID', _("Lebanese national ID")),
            ('Lebanese Extract of Record', _("Lebanese Extract of Record")),
            ('Other nationality', _("Other nationality")),
            ('Child have no ID', _("Child have no ID"))
        ),
        initial=''
    )
    # case_number = forms.RegexField(
    #     regex = r'^((245)|(380)|(568)|(705)|(781)|(909)|(947)|(954)|(781)|(LEB)|(leb)|(LB1)|(LB2)|(lb2)|(LBE)|(lbe)|(b6a)|(B6A))-[0-9]{2}[C-](?:\d{5}|\d{6})$',
    #     widget=forms.TextInput(attrs={'placeholder': 'Format: XXX-XXCXXXXX or XXX-XX-XXXXXX'}),
    #     required=False,
    #     label=_('UNHCR Case Number')
    # )
    # case_number_confirm = forms.RegexField(
    #     regex = r'^((245)|(380)|(568)|(705)|(781)|(909)|(947)|(954)|(781)|(LEB)|(leb)|(LB1)|(LB2)|(lb2)|(LBE)|(lbe)|(b6a)|(B6A))-[0-9]{2}[C-](?:\d{5}|\d{6})$',
    #     widget=forms.TextInput(attrs={'placeholder': 'Format: XXX-XXCXXXXX or XXX-XX-XXXXXX'}),
    #     required=False,
    #     label=_('Confirm UNHCR Case Number')
    # )
    # parent_individual_case_number = forms.RegexField(
    #     regex=r'^((245)|(380)|(568)|(705)|(781)|(909)|(947)|(954)|(781)|(LEB)|(leb)|(LB1)|(LB2)|(lb2)|(LBE)|(lbe)|(b6a)|(B6A))-[0-9]{8}$',
    #     widget=forms.TextInput(attrs={'placeholder': 'Format: XXX-XXXXXXXX'}),
    #     required=False,
    #     label=_(
    #         'Caregiver Individual ID from the certificate (Optional, in case not listed in the certificate)')
    # )
    # parent_individual_case_number_confirm = forms.RegexField(
    #     regex=r'^((245)|(380)|(568)|(705)|(781)|(909)|(947)|(954)|(781)|(LEB)|(leb)|(LB1)|(LB2)|(lb2)|(LBE)|(lbe)|(b6a)|(B6A))-[0-9]{8}$',
    #     widget=forms.TextInput(attrs={'placeholder': 'Format: XXX-XXXXXXXX'}),
    #     required=False,
    #     label=_(
    #         'Confirm Caregiver Individual ID from the certificate')
    # )
    individual_case_number = forms.RegexField(
        regex=r'^((245)|(380)|(568)|(705)|(781)|(909)|(947)|(954)|(781)|(LEB)|(leb)|(LB1)|(LB2)|(lb2)|(LBE)|(lbe)|(b6a)|(B6A))-[0-9]{8}$',
        widget=forms.TextInput(attrs={'placeholder': 'Format: XXX-XXXXXXXX'}),
        required=False,
        label=_(
            'Individual ID of the Child from the certificate')
    )
    individual_case_number_confirm = forms.RegexField(
        regex=r'^((245)|(380)|(568)|(705)|(781)|(909)|(947)|(954)|(781)|(LEB)|(leb)|(LB1)|(LB2)|(lb2)|(LBE)|(lbe)|(b6a)|(B6A))-[0-9]{8}$',
        widget=forms.TextInput(attrs={'placeholder': 'Format: XXX-XXXXXXXX'}),
        required=False,
        label=_(
                'Confirm Individual ID of the Child from the certificate')
    )
    recorded_number = forms.RegexField(
        regex=r'^((245)|(380)|(568)|(705)|(781)|(909)|(947)|(954)|(781)|(LEB)|(leb)|(LB1)|(LB2)|(lb2)|(LBE)|(lbe)|(b6a)|(B6A))-[0-9]{2}[C-](?:\d{5}|\d{6})$|^LB-\d{3}-\d{6}|\d{7}$|^86A-\d{2}-\d{5}$',
        widget=forms.TextInput(attrs={'placeholder': 'Format: LEB-XXCXXXXX or LB-XXX-XXXXXX'}),
        required=False,
        label=_('UNHCR Barcode number (Shifra number)')
    )
    recorded_number_confirm = forms.RegexField(
        regex=r'^((245)|(380)|(568)|(705)|(781)|(909)|(947)|(954)|(781)|(LEB)|(leb)|(LB1)|(LB2)|(lb2)|(LBE)|(lbe)|(b6a)|(B6A))-[0-9]{2}[C-](?:\d{5}|\d{6})$|^LB-\d{3}-\d{6}|\d{7}$|^86A-\d{2}-\d{5}$',
        widget=forms.TextInput(attrs={'placeholder': 'Format: LEB-XXCXXXXX or LB-XXX-XXXXXX'}),
        required=False,
        label=_('Confirm UNHCR Barcode number (Shifra number)')
    )

    national_number = forms.RegexField(
        regex=r'^\d{12}$',
        widget=forms.TextInput(attrs={'placeholder': 'Format: XXXXXXXXXXXX'}),
        required=False,
        label=_('Lebanese ID number of the child')
    )
    national_number_confirm = forms.RegexField(
        regex=r'^\d{12}$',
        widget=forms.TextInput(attrs={'placeholder': 'Format: XXXXXXXXXXXX'}),
        required=False,
        label=_('Confirm Lebanese ID number of the child (optional)')
    )
    syrian_national_number = forms.RegexField(
        regex=r'^\d{11}$',
        required=False,
        label=_('National ID number of the child')
    )
    syrian_national_number_confirm = forms.RegexField(
        regex=r'^\d{11}$',
        required=False,
        label=_('Confirm National ID number of the child')
    )
    sop_national_number = forms.CharField(
        required=False,
        label=_('Palestinian ID number of the child')
    )
    sop_national_number_confirm = forms.CharField(
        required=False,
        label=_('Confirm Palestinian ID number of the child')
    )
    # parent_national_number = forms.RegexField(
    #     regex=r'^\d{12}$',
    #     widget=forms.TextInput(attrs={'placeholder': 'Format: XXXXXXXXXXXX'}),
    #     required=False,
    #     label=_('Lebanese ID number of the Caregiver')
    # )
    # parent_national_number_confirm = forms.RegexField(
    #     regex=r'^\d{12}$',
    #     widget=forms.TextInput(attrs={'placeholder': 'Format: XXXXXXXXXXXX'}),
    #     required=False,
    #     label=_('Confirm Lebanese ID number of the Caregiver')
    # )
    # parent_syrian_national_number = forms.RegexField(
    #     regex=r'^\d{11}$',
    #     required=False,
    #     label=_('National ID number of the Caregiver (Mandatory)')
    # )
    # parent_syrian_national_number_confirm = forms.RegexField(
    #     regex=r'^\d{11}$',
    #     required=False,
    #     label=_('Confirm National ID number of the Caregiver (Mandatory)')
    # )
    # parent_sop_national_number = forms.CharField(
    #     # regex=r'^\d{11}$',
    #     required=False,
    #     label=_('Palestinian ID number of the Caregiver (Mandatory)')
    # )
    # parent_sop_national_number_confirm = forms.CharField(
    #     # regex=r'^\d{11}$',
    #     required=False,
    #     label=_('Confirm Palestinian ID number of the Caregiver (Mandatory)')
    # )
    #
    # parent_other_number = forms.CharField(
    #     required=False,
    #     label=_('ID number of the Caregiver (Mandatory)')
    # )
    # parent_other_number_confirm = forms.CharField(
    #     required=False,
    #     label=_('Confirm ID number of the Caregiver (Mandatory)')
    # )
    other_number = forms.CharField(
        required=False,
        label=_(' ID number of the child')
    )
    other_number_confirm = forms.CharField(
        required=False,
        label=_('Confirm ID number of the child')
    )
    individual_extract_record = forms.CharField(
        required=False,
        label=_('Lebanese Extract of Record of the child')
    )
    individual_extract_record_confirm = forms.CharField(
        required=False,
        label=_('Confirm Lebanese Extract of Record of the child')
    )

    no_child_id_confirmation = forms.CharField(widget=forms.HiddenInput, required=False)
    no_parent_id_confirmation = forms.CharField(widget=forms.HiddenInput, required=False)

    source_of_identification = forms.ChoiceField(
        label=_("Source of identification of the child to Bridging"),
        widget=forms.Select,
        required=True,
        choices=(
            ('', '----------'),
            ('CP partner referral', _('CP partner referral')),
            ('Awarness Session', _('Awarness Session')),
            ('Child parents', _('Child parents')),
            ('From Profiling Database', _('From Profiling Database')),
            ('Referred by the municipality / Other formal sources', _('Referred by the municipality / Other formal sources')),
            ('From Displaced Community', _('From Displaced Community')),
            ('From Hosted Community', _('From Hosted Community')),
            ('From Other NGO', _('From Other NGO')),
            ('School Director', _('School Director')),
            ('RIMS', _('RIMS'))
        ),
        initial=''
    )
    source_of_identification_specify = forms.CharField(
        label=_('Please specify'),
        widget=forms.TextInput, required=False
    )
    rims_case_number = forms.CharField(
        required=False,
        label=_('RIMS Case Number')
    )

    arabic_alphabet_knowledge = forms.FloatField(
        label=_('Arabic Alphabet Knowledge'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=False
    )
    arabic_familiar_words = forms.FloatField(
        label=_('Arabic Familiar words'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=False
    )
    arabic_reading_comprehension = forms.FloatField(
        label=_('Arabic Reading Comprehension'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=False
    )
    english_alphabet_knowledge = forms.FloatField(
        label=_('English Alphabet Knowledge'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=False
    )
    english_familiar_words = forms.FloatField(
        label=_('English Familiar words'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=False
    )
    english_reading_comprehension = forms.FloatField(
        label=_('English Reading Comprehension'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=False
    )
    french_alphabet_knowledge = forms.FloatField(
        label=_('French Alphabet Knowledge'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=False
    )
    french_familiar_words = forms.FloatField(
        label=_('French Familiar words'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=False
    )
    french_reading_comprehension = forms.FloatField(
        label=_('French Reading Comprehension'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=False
    )
    math = forms.FloatField(
        label=_('Math'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=False
    )
    exam1 = forms.FloatField(
        label=_('Exam 1'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=False
    )
    main_caregiver = forms.ChoiceField(
        label=_("Main Caregiver"),
        widget=forms.Select, required=True,
        choices=(
            ('', '----------'),
            ('mother', _('Mother')),
            ('father', _('Father')),
            ('other', _('Other')),
        )
    )
    main_caregiver_nationality_other =  forms.CharField(
        label=_('Please specify'),
        widget=forms.TextInput, required=False
    )

    student_p_code = forms.CharField(
        label=_('P-Code If a child lives in a tent / Brax in a random camp'),
        widget=forms.TextInput, required=False
    )

    governorate = forms.ModelChoiceField(
        queryset=Location.objects.filter(parent__isnull=True), widget=forms.Select,
        label=_('Child Governorate'),
        empty_label='-------',
        required=True, to_field_name='id',
    )
    district = forms.ModelChoiceField(
        queryset=Location.objects.filter(parent__isnull=False), widget=forms.Select,
        label=_('Child District'),
        empty_label='-------',
        required=True, to_field_name='id',
        # initial=0
    )
    cadaster = forms.ModelChoiceField(
        queryset=Location.objects.filter(parent__isnull=False), widget=forms.Select,
        label=_('Child Cadaster'),
        empty_label='-------',
        required=True, to_field_name='id',
        # initial=0
    )
    consent_parents = forms.FileField(
        label=_("Consent from parents"),
        required=False,
        widget=CustomClearableFileInput
    )
    registration_date = forms.DateField(
        label=_("Registration date"),
        required=True,
    )
    enrolled_formal_education = forms.ChoiceField(
        label=_("Was this child enrolled in Formal Education last year and dropped out due to lack of documentation?"),
        widget=forms.Select, required=True,
        choices=CLM.YES_NO
    )
    child_outreach = forms.IntegerField(widget=forms.HiddenInput, required=False)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(BridgingForm, self).__init__(*args, **kwargs)

        display_registry = ''
        instance = kwargs['instance'] if 'instance' in kwargs else ''
        form_action = reverse('clm:bridging_add')
        self.fields['clm_type'].initial = 'Bridging'
        self.fields['new_registry'].initial = 'yes'

        is_Kayany = False
        if self.request.user.partner:
            is_Kayany = self.request.user.partner.is_Kayany
        choices = list()
        if not is_Kayany:
            choices.append(('level_one', _('Level one')))
            choices.append(('level_two', _('Level two')))
            choices.append(('level_three', _('Level three')))
            choices.append(('level_four', _('Level four')))
            choices.append(('level_five', _('Level five')))
            choices.append(('level_six', _('Level six')))
            choices.append(('level_one_pm', _('Level one PM shift')))
            choices.append(('level_two_pm', _('Level two PM shift')))
            choices.append(('level_three_pm', _('Level three PM shift')))
            choices.append(('level_four_pm', _('Level four PM shift')))
            choices.append(('level_five_pm', _('Level five PM shift')))
            choices.append(('level_six_pm', _('Level six PM shift')))
        else:
            choices.append(('grade_one', _('Grade one')))
            choices.append(('grade_two', _('Grade two')))
            choices.append(('grade_three', _('Grade three')))
            choices.append(('grade_four', _('Grade four')))
            choices.append(('grade_five', _('Grade five')))
            choices.append(('grade_six', _('Grade six')))
            choices.append(('grade_seven', _('Grade seven')))
            choices.append(('grade_eight', _('Grade eight')))
            choices.append(('grade_nine', _('Grade nine')))

            # add year 2010 if Kayany
            years = list(((str(y), y) for y in range(Person.CURRENT_YEAR - 15, Person.CURRENT_YEAR - 5)))
            years.insert(0, ('', '---------'))
            self.fields['student_birthday_year'].choices = years

        self.fields['registration_level'].choices = choices

        if instance:
            display_registry = ' d-none'
            form_action = reverse('clm:bridging_edit', kwargs={'pk': instance.id})

        self.helper = FormHelper()
        self.helper.form_show_labels = True
        self.helper.form_action = form_action

        if not is_Kayany:

            self.helper.layout = Layout(
                Div(
                    Div(
                        'clm_type',
                        'student_id',
                        'enrollment_id',
                        'partner_name',
                    ),
                    Div(
                        Div('new_registry', css_class='col-md-3'),
                        css_class='row card-body',
                    ),
                    Div(
                        Div('search_clm_student', css_class='col-md-3'),
                        Div('search_Kobo_outreach_student', css_class='col-md-3'),
                        css_class='row card-body',
                    ),
                    css_id='step-1',
                    style='display: none;'
                ),
                Div(
                    Div(
                        HTML('<span class="badge-form badge-pill">2</span>'),
                        Div('round', css_class='col-md-3'),
                        HTML('<span class="badge-form badge-pill">3</span>'),
                        Div('registration_date', css_class='col-md-3'),
                        Div('round_start_date', css_class='col-md-3 d-none'),
                        css_class='row card-body',
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">4</span>'),
                        Div('governorate', css_class='col-md-3'),
                        HTML('<span class="badge-form badge-pill">5</span>'),
                        Div('district', css_class='col-md-3'),
                        css_class='row card-body',
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">6</span>'),
                        Div('cadaster', css_class='col-md-3'),
                        HTML('<span class="badge-form badge-pill">7</span>'),
                        Div('school', css_class='col-md-3'),
                        HTML('<span class="badge-form badge-pill">8</span>'),
                        Div('language', css_class='col-md-3'),
                        css_class='row card-body',
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">9</span>'),
                        Div('student_address', css_class='col-md-3'),
                        HTML('<span class="badge-form-2 badge-pill">10</span>'),
                        Div('residence_type', css_class='col-md-3'),
                        HTML('<span class="badge-form-2 badge-pill">11</span>'),
                        Div('registration_level', css_class='col-md-3'),
                        Div('first_attendance_date', css_class='col-md-3 d-none'),
                        css_class='row card-body',
                    ),
                    Div(
                        HTML('<span class="badge-form-2 badge-pill">12</span>'),
                        Div('enrolled_formal_education', css_class='col-md-4'),
                        css_class='row card-body',
                    ),
                    css_id='step-2',
                    style='display: none;'
                ),
                Div(
                    Div(
                        HTML('<span class="badge-form badge-pill">1</span>'),
                        Div('student_first_name', css_class='col-md-3'),
                        HTML('<span class="badge-form badge-pill">2</span>'),
                        Div('student_father_name', css_class='col-md-3'),
                        HTML('<span class="badge-form badge-pill">3</span>'),
                        Div('student_last_name', css_class='col-md-3'),
                        css_class='row card-body',
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">4</span>'),
                        Div('student_mother_fullname', css_class='col-md-3'),
                        HTML('<span class="badge-form badge-pill">5</span>'),
                        Div('student_sex', css_class='col-md-3'),
                        css_class='row card-body',
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">6</span>'),
                        Div('student_nationality', css_class='col-md-3'),
                        HTML('<span class="badge-form badge-pill" id="span_other_nationality">7</span>'),
                        Div('other_nationality', css_class='col-md-3'),
                        css_class='row card-body',
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">8</span>'),
                        Div('student_birthday_year', css_class='col-md-2'),
                        HTML('<span class="badge-form badge-pill">9</span>'),
                        Div('student_birthday_month', css_class='col-md-2'),
                        HTML('<span class="badge-form-2 badge-pill">10</span>'),
                        Div('student_birthday_day', css_class='col-md-2'),
                        css_class='row card-body',
                    ),
                    Div(
                        HTML('<span class="badge-form-2 badge-pill">11</span>'),
                        Div('student_p_code', css_class='col-md-3'),
                        HTML('<span class="badge-form-2 badge-pill">12</span>'),
                        Div('disability', css_class='col-md-3'),
                        css_class='row card-body',
                    ),
                    Div(
                        HTML('<span class="badge-form-2 badge-pill">13</span>'),
                        Div('education_status', css_class='col-md-3'),
                        HTML('<span class="badge-form-2 badge-pill" id="span_miss_school_date">14</span>'),
                        Div('miss_school_date', css_class='col-md-3'),
                        css_class='row card-body',
                    ),
                    Div(
                        HTML('<span class="badge-form-2 badge-pill">15</span>'),
                        Div('internal_number', css_class='col-md-3'),
                        HTML('<span class="badge-form-2 badge-pill">16</span>'),
                        Div('source_of_identification', css_class='col-md-3'),
                        css_class='row card-body',
                    ),
                    Div(
                        HTML('<span class="badge-form-2 badge-pill" id="span_rims_case_number">17</span>'),
                        Div('rims_case_number', css_class='col-md-3'),
                        css_class='row card-body',
                    ),
                    Div(
                        HTML('<span class="badge-form-2 badge-pill" id="span_source_of_identification_specify">17</span>'),
                        Div('source_of_identification_specify', css_class='col-md-3'),
                        css_class='row card-body',
                    ),
                    Div(
                        HTML('<span class="badge-form-2 badge-pill">15</span>'),
                        Div('id_type', css_class='col-md-3'),
                        css_class='row card-body',
                    ),
                    # Div(
                    #     HTML('<span class="badge-form-2 badge-pill">15</span>'),
                    #     Div('case_number', css_class='col-md-4'),
                    #     HTML('<span class="badge-form-2 badge-pill">16</span>'),
                    #     Div('case_number_confirm', css_class='col-md-4'),
                    #     HTML('<span style="padding-top: 37px;">' +
                    #          '<a class="image-link" href="/static/images/unhcr_certificate.jpg" target="_blank">' +
                    #          '<img src="/static/images/icon-help.png" width="25px" height="25px;"/></a></span>'),
                    #     css_class='row child_id  d-none card-body',
                    # ),
                    # Div(
                    #     HTML('<span class="badge-form-2 badge-pill">17</span>'),
                    #     Div('parent_individual_case_number', css_class='col-md-4'),
                    #     HTML('<span class="badge-form-2 badge-pill">18</span>'),
                    #     Div('parent_individual_case_number_confirm', css_class='col-md-4'),
                    #     HTML('<span style="padding-top: 37px;">' +
                    #          '<a class="image-link" href="/static/images/UNHCR_individualID.jpg" target="_blank">' +
                    #          '<img src="/static/images/icon-help.png" width="25px" height="25px;"/></a></span>'),
                    #     css_class='row child_id  d-none card-body',
                    # ),
                    Div(
                        HTML('<span class="badge-form-2 badge-pill">16</span>'),
                        Div('individual_case_number', css_class='col-md-4'),
                        HTML('<span class="badge-form-2 badge-pill">17</span>'),
                        Div('individual_case_number_confirm', css_class='col-md-4'),
                        HTML('<span style="padding-top: 37px;">' +
                             '<a class="image-link" href="/static/images/UNHCR_individualID.jpg" target="_blank">' +
                             '<img src="/static/images/icon-help.png" width="25px" height="25px;"/></a></span>'),
                        css_class='row child_id child_id1 card-body',
                    ),
                    Div(
                        HTML('<span class="badge-form-2 badge-pill">16</span>'),
                        Div('recorded_number', css_class='col-md-4'),
                        HTML('<span class="badge-form-2 badge-pill">17</span>'),
                        Div('recorded_number_confirm', css_class='col-md-4'),
                        HTML('<span style="padding-top: 37px;">' +
                             '<a class="image-link" href="/static/images/UNHCR_barcode.jpg" target="_blank">' +
                             '<img src="/static/images/icon-help.png" width="25px" height="25px;"/></a></span>'),
                        css_class='row child_id child_id2 card-body',
                    ),
                    # Div(
                    #     HTML('<span class="badge-form-2 badge-pill">19</span>'),
                    #     Div('parent_national_number', css_class='col-md-4'),
                    #     HTML('<span class="badge-form-2 badge-pill">20</span>'),
                    #     Div('parent_national_number_confirm', css_class='col-md-4'),
                    #     HTML('<span style="padding-top: 37px;">' +
                    #          '<a class="image-link" href="/static/images/lebanese_nationalID.png" target="_blank">' +
                    #          '<img src="/static/images/icon-help.png" width="25px" height="25px;"/></a></span>'),
                    #     css_class='row child_id  d-none card-body',
                    # ),
                    Div(
                        HTML('<span class="badge-form-2 badge-pill">16</span>'),
                        Div('national_number', css_class='col-md-4'),
                        HTML('<span class="badge-form-2 badge-pill">17</span>'),
                        Div('national_number_confirm', css_class='col-md-4'),
                        HTML('<span style="padding-top: 37px;">' +
                             '<a class="image-link" href="/static/images/lebanese_nationalID.png" target="_blank">' +
                             '<img src="/static/images/icon-help.png" width="25px" height="25px;"/></a></span>'),
                        css_class='row child_id child_id3 card-body',
                    ),
                    # Div(
                    #     HTML('<span class="badge-form-2 badge-pill">23</span>'),
                    #     Div('parent_syrian_national_number', css_class='col-md-4'),
                    #     HTML('<span class="badge-form-2 badge-pill">24</span>'),
                    #     Div('parent_syrian_national_number_confirm', css_class='col-md-4'),
                    #     HTML('<span style="padding-top: 37px;">' +
                    #          '<a class="image-link" href="/static/images/Syrian_passport.png" target="_blank">' +
                    #          '<img src="/static/images/icon-help.png" width="25px" height="25px;"/></a></span>'),
                    #     css_class='row child_id  d-none card-body',
                    # ),
                    Div(
                        HTML('<span class="badge-form-2 badge-pill">16</span>'),
                        Div('syrian_national_number', css_class='col-md-4'),
                        HTML('<span class="badge-form-2 badge-pill">17</span>'),
                        Div('syrian_national_number_confirm', css_class='col-md-4'),
                        HTML('<span style="padding-top: 37px;">' +
                             '<a class="image-link" href="/static/images/Syrian_passport.png" target="_blank">' +
                             '<img src="/static/images/icon-help.png" width="25px" height="25px;"/></a></span>'),
                        css_class='row child_id child_id4 card-body',
                    ),
                    # Div(
                    #     HTML('<span class="badge-form-2 badge-pill">27</span>'),
                    #     Div('parent_sop_national_number', css_class='col-md-4'),
                    #     HTML('<span class="badge-form-2 badge-pill">28</span>'),
                    #     Div('parent_sop_national_number_confirm', css_class='col-md-4'),
                    #     HTML('<span style="padding-top: 37px;">' +
                    #          '<a class="image-link" href="/static/images/Palestinian_from_Lebanon.png" target="_blank">' +
                    #          '<img src="/static/images/icon-help.png" width="25px" height="25px;"/></a></span>'),
                    #     css_class='row child_id  d-none card-body',
                    # ),
                    Div(
                        HTML('<span class="badge-form-2 badge-pill">16</span>'),
                        Div('sop_national_number', css_class='col-md-4'),
                        HTML('<span class="badge-form-2 badge-pill">17</span>'),
                        Div('sop_national_number_confirm', css_class='col-md-4'),
                        HTML('<span style="padding-top: 37px;">' +
                             '<a class="image-link" href="/static/images/Palestinian_from_Lebanon.png" target="_blank">' +
                             '<img src="/static/images/icon-help.png" width="25px" height="25px;"/></a></span>'),
                        css_class='row child_id child_id5 card-body',
                    ),
                    # Div(
                    #     HTML('<span class="badge-form-2 badge-pill">31</span>'),
                    #     Div('parent_other_number', css_class='col-md-4'),
                    #     HTML('<span class="badge-form-2 badge-pill">32</span>'),
                    #     Div('parent_other_number_confirm', css_class='col-md-4'),
                    #     css_class='row child_id  d-none card-body',
                    # ),
                    Div(
                        HTML('<span class="badge-form-2 badge-pill">16</span>'),
                        Div('other_number', css_class='col-md-4'),
                        HTML('<span class="badge-form-2 badge-pill">17</span>'),
                        Div('other_number_confirm', css_class='col-md-4'),
                        css_class='row child_id child_id6 card-body',
                    ),
                    Div(
                        HTML('<span class="badge-form-2 badge-pill">16</span>'),
                        Div('individual_extract_record', css_class='col-md-4'),
                        HTML('<span class="badge-form-2 badge-pill">17</span>'),
                        Div('individual_extract_record_confirm', css_class='col-md-4'),
                        css_class='row child_id child_id7 card-body',
                    ),
                    Div(
                        HTML('<span class="badge-form-2 badge-pill">16</span>'),
                        Div('source_of_transportation', css_class='col-md-3'),
                        css_class='row d-none card-body',
                    ),
                    css_id='step-3',
                    style='display: none;'
                ),
                Div(
                    Div(
                        HTML('<span class="badge-form badge-pill">1</span>'),
                        Div('hh_educational_level', css_class='col-md-3'),
                        HTML('<span class="badge-form badge-pill">2</span>'),
                        Div('father_educational_level', css_class='col-md-3'),
                        css_class='row card-body',
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">3</span>'),
                        Div('phone_number', css_class='col-md-3'),
                        HTML('<span class="badge-form badge-pill">4</span>'),
                        Div('phone_number_confirm', css_class='col-md-3'),
                        HTML('<span class="badge-form badge-pill">5</span>'),
                        Div('phone_owner', css_class='col-md-3'),
                        css_class='row card-body',
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">6</span>'),
                        Div('second_phone_number', css_class='col-md-3'),
                        HTML('<span class="badge-form badge-pill">7</span>'),
                        Div('second_phone_number_confirm', css_class='col-md-3'),
                        HTML('<span class="badge-form badge-pill">8</span>'),
                        Div('second_phone_owner', css_class='col-md-3'),
                        css_class='row card-body',
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">9</span>'),
                        Div('main_caregiver', css_class='col-md-3'),
                        HTML('<span class="badge-form-2 badge-pill" id="span_other_caregiver_relationship">10</span>'),
                        Div('other_caregiver_relationship', css_class='col-md-3'),
                        css_class='row card-body',
                    ),
                    Div(
                        HTML('<span class="badge-form-2 badge-pill">11</span>'),
                        Div('main_caregiver_nationality', css_class='col-md-3'),
                        HTML('<span class="badge-form-2 badge-pill" id="span_main_caregiver_nationality_other">12</span>'),
                        Div('main_caregiver_nationality_other', css_class='col-md-3'),
                        css_class='row card-body',
                    ),
                    Div(
                        HTML('<span class="badge-form-2 badge-pill">13</span>'),
                        Div('caretaker_first_name', css_class='col-md-3'),
                        HTML('<span class="badge-form-2 badge-pill">14</span>'),
                        Div('caretaker_middle_name', css_class='col-md-3'),
                        css_class='row card-body',
                    ),
                    Div(
                        HTML('<span class="badge-form-2 badge-pill">15</span>'),
                        Div('caretaker_last_name', css_class='col-md-3'),
                        HTML('<span class="badge-form-2 badge-pill">16</span>'),
                        Div('caretaker_mother_name', css_class='col-md-3'),
                        css_class='row card-body',
                    ),
                    Div(
                        HTML('<span class="badge-form-2 badge-pill">17</span>'),
                        Div('caretaker_birthday_year', css_class='col-md-2'),
                        HTML('<span class="badge-form-2 badge-pill">18</span>'),
                        Div('caretaker_birthday_month', css_class='col-md-2'),
                        HTML('<span class="badge-form-2 badge-pill">19</span>'),
                        Div('caretaker_birthday_day', css_class='col-md-2'),
                        css_class='row card-body',
                    ),
                    css_id='step-4',
                    style='display: none;'
                ),
                Div(
                    Div(
                        HTML('<span class="badge-form badge-pill">1</span>'),
                        Div('student_family_status', css_class='col-md-4'),
                        HTML('<span class="badge-form badge-pill" id=span_student_have_children">2</span>'),
                        Div('student_have_children', css_class='col-md-4', css_id='student_have_children'),
                        HTML('<span class="badge-form badge-pill" id="span_student_number_children">3</span>'),
                        Div('student_number_children', css_class='col-md-3'),
                        css_class='row card-body',
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">4</span>'),
                        Div('have_labour_single_selection', css_class='col-md-3'),
                        css_class='row card-body',
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">5</span>'),
                        Div('labours_single_selection', css_class='col-md-3', css_id='labours'),
                        HTML('<span class="badge-form badge-pill" id="span_labours_other_specify">6</span>'),
                        Div('labours_other_specify', css_class='col-md-3'),
                        css_class='row card-body',
                        id='labour_details_1'
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">7</span>'),
                        Div('labour_hours', css_class='col-md-3', css_id='labour_hours'),
                        HTML('<span class="badge-form badge-pill">8</span>'),
                        Div('labour_weekly_income', css_class='col-md-3'),
                        css_class='row card-body',
                        id='labour_details_2'
                    ),
                    css_id='step-5',
                    style='display: none;'
                ),
                Div(
                    Div(
                        HTML('<span class="badge-form badge-pill" id="span_arabic">1</span>'),
                        Div('arabic_alphabet_knowledge', css_class='col-md-3'),
                        Div('arabic_familiar_words', css_class='col-md-3'),
                        Div('arabic_reading_comprehension', css_class='col-md-3'),
                        css_class='row card-body',
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill" id="span_english">2</span>'),
                        Div('english_alphabet_knowledge', css_class='col-md-3'),
                        Div('english_familiar_words', css_class='col-md-3'),
                        Div('english_reading_comprehension', css_class='col-md-3'),
                        css_class='row card-body',
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill" id="span_french">3</span>'),
                        Div('french_alphabet_knowledge', css_class='col-md-3'),
                        Div('french_familiar_words', css_class='col-md-3'),
                        Div('french_reading_comprehension', css_class='col-md-3'),
                        css_class='row card-body',
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill" id="span_math">4</span>'),
                        Div('math', css_class='col-md-3'),
                        css_class='row card-body',
                    ),
                    css_id='step-6',
                    style='display: none;'
                ),
                Div(
                    Div(
                        HTML('<span class="badge-form badge-pill">1</span>'),
                        Div('consent_parents', css_class='col-md-3'),
                        css_class='row card-body',
                    ),
                    FormActions(
                        Submit('save', 'Save',
                               css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-success'),
                        Reset('reset', 'Reset',
                              css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-warning'),
                    ),
                    css_id='step-7',
                    style='display: none;'
                )
            )
        else:
            self.helper.layout = Layout(
                Div(
                    Div(
                        'clm_type',
                        'student_id',
                        'enrollment_id',
                        'partner_name',
                    ),
                    Div(
                        Div('new_registry', css_class='col-md-3'),
                        css_class='row card-body',
                    ),
                    Div(
                        Div('search_clm_student', css_class='col-md-3'),
                        Div('search_Kobo_outreach_student', css_class='col-md-3'),
                        css_class='row card-body',
                    ),
                    css_id='step-1',
                    style='display: none;'
                ),
                Div(
                    Div(
                        HTML('<span class="badge-form badge-pill">2</span>'),
                        Div('round', css_class='col-md-3'),
                        HTML('<span class="badge-form badge-pill">3</span>'),
                        Div('registration_date', css_class='col-md-3'),
                        Div('round_start_date', css_class='col-md-3 d-none'),
                        css_class='row card-body',
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">4</span>'),
                        Div('governorate', css_class='col-md-3'),
                        HTML('<span class="badge-form badge-pill">5</span>'),
                        Div('district', css_class='col-md-3'),
                        css_class='row card-body',
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">6</span>'),
                        Div('cadaster', css_class='col-md-3'),
                        HTML('<span class="badge-form badge-pill">7</span>'),
                        Div('school', css_class='col-md-3'),
                        HTML('<span class="badge-form badge-pill">8</span>'),
                        Div('language', css_class='col-md-3'),
                        css_class='row card-body',
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">9</span>'),
                        Div('student_address', css_class='col-md-3'),
                        HTML('<span class="badge-form-2 badge-pill">10</span>'),
                        Div('residence_type', css_class='col-md-3'),
                        HTML('<span class="badge-form-2 badge-pill">11</span>'),
                        Div('registration_level', css_class='col-md-3'),
                        Div('first_attendance_date', css_class='col-md-3 d-none'),
                        css_class='row card-body',
                    ),
                    Div(
                        HTML('<span class="badge-form-2 badge-pill">12</span>'),
                        Div('enrolled_formal_education', css_class='col-md-4'),
                        css_class='row card-body',
                    ),
                    css_id='step-2',
                    style='display: none;'
                ),
                Div(
                    Div(
                        HTML('<span class="badge-form badge-pill">1</span>'),
                        Div('student_first_name', css_class='col-md-3'),
                        HTML('<span class="badge-form badge-pill">2</span>'),
                        Div('student_father_name', css_class='col-md-3'),
                        HTML('<span class="badge-form badge-pill">3</span>'),
                        Div('student_last_name', css_class='col-md-3'),
                        css_class='row card-body',
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">4</span>'),
                        Div('student_mother_fullname', css_class='col-md-3'),
                        HTML('<span class="badge-form badge-pill">5</span>'),
                        Div('student_sex', css_class='col-md-3'),
                        css_class='row card-body',
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">6</span>'),
                        Div('student_nationality', css_class='col-md-3'),
                        HTML('<span class="badge-form badge-pill" id="span_other_nationality">7</span>'),
                        Div('other_nationality', css_class='col-md-3'),
                        css_class='row card-body',
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">8</span>'),
                        Div('student_birthday_year', css_class='col-md-2'),
                        HTML('<span class="badge-form badge-pill">9</span>'),
                        Div('student_birthday_month', css_class='col-md-2'),
                        HTML('<span class="badge-form-2 badge-pill">10</span>'),
                        Div('student_birthday_day', css_class='col-md-2'),
                        css_class='row card-body',
                    ),
                    Div(
                        HTML('<span class="badge-form-2 badge-pill">11</span>'),
                        Div('student_p_code', css_class='col-md-3'),
                        HTML('<span class="badge-form-2 badge-pill">12</span>'),
                        Div('disability', css_class='col-md-3'),
                        css_class='row card-body',
                    ),
                    Div(
                        HTML('<span class="badge-form-2 badge-pill">13</span>'),
                        Div('education_status', css_class='col-md-3'),
                        HTML('<span class="badge-form-2 badge-pill" id="span_miss_school_date">14</span>'),
                        Div('miss_school_date', css_class='col-md-3'),
                        css_class='row card-body',
                    ),
                    Div(
                        HTML('<span class="badge-form-2 badge-pill">15</span>'),
                        Div('internal_number', css_class='col-md-3'),
                        HTML('<span class="badge-form-2 badge-pill">16</span>'),
                        Div('source_of_identification', css_class='col-md-3'),
                        css_class='row card-body',
                    ),
                    Div(
                        HTML('<span class="badge-form-2 badge-pill" id="span_rims_case_number">17</span>'),
                        Div('rims_case_number', css_class='col-md-3'),
                        css_class='row card-body',
                    ),
                    Div(
                        HTML(
                            '<span class="badge-form-2 badge-pill" id="span_source_of_identification_specify">17</span>'),
                        Div('source_of_identification_specify', css_class='col-md-3'),
                        css_class='row card-body',
                    ),
                    Div(
                        HTML('<span class="badge-form-2 badge-pill">15</span>'),
                        Div('id_type', css_class='col-md-3'),
                        css_class='row card-body',
                    ),
                    # Div(
                    #     HTML('<span class="badge-form-2 badge-pill">15</span>'),
                    #     Div('case_number', css_class='col-md-4'),
                    #     HTML('<span class="badge-form-2 badge-pill">16</span>'),
                    #     Div('case_number_confirm', css_class='col-md-4'),
                    #     HTML('<span style="padding-top: 37px;">' +
                    #          '<a class="image-link" href="/static/images/unhcr_certificate.jpg" target="_blank">' +
                    #          '<img src="/static/images/icon-help.png" width="25px" height="25px;"/></a></span>'),
                    #     css_class='row child_id  d-none card-body',
                    # ),
                    # Div(
                    #     HTML('<span class="badge-form-2 badge-pill">17</span>'),
                    #     Div('parent_individual_case_number', css_class='col-md-4'),
                    #     HTML('<span class="badge-form-2 badge-pill">18</span>'),
                    #     Div('parent_individual_case_number_confirm', css_class='col-md-4'),
                    #     HTML('<span style="padding-top: 37px;">' +
                    #          '<a class="image-link" href="/static/images/UNHCR_individualID.jpg" target="_blank">' +
                    #          '<img src="/static/images/icon-help.png" width="25px" height="25px;"/></a></span>'),
                    #     css_class='row child_id  d-none card-body',
                    # ),
                    Div(
                        HTML('<span class="badge-form-2 badge-pill">16</span>'),
                        Div('individual_case_number', css_class='col-md-4'),
                        HTML('<span class="badge-form-2 badge-pill">17</span>'),
                        Div('individual_case_number_confirm', css_class='col-md-4'),
                        HTML('<span style="padding-top: 37px;">' +
                             '<a class="image-link" href="/static/images/UNHCR_individualID.jpg" target="_blank">' +
                             '<img src="/static/images/icon-help.png" width="25px" height="25px;"/></a></span>'),
                        css_class='row child_id child_id1 card-body',
                    ),
                    Div(
                        HTML('<span class="badge-form-2 badge-pill">16</span>'),
                        Div('recorded_number', css_class='col-md-4'),
                        HTML('<span class="badge-form-2 badge-pill">17</span>'),
                        Div('recorded_number_confirm', css_class='col-md-4'),
                        HTML('<span style="padding-top: 37px;">' +
                             '<a class="image-link" href="/static/images/UNHCR_barcode.jpg" target="_blank">' +
                             '<img src="/static/images/icon-help.png" width="25px" height="25px;"/></a></span>'),
                        css_class='row child_id child_id2 card-body',
                    ),
                    # Div(
                    #     HTML('<span class="badge-form-2 badge-pill">19</span>'),
                    #     Div('parent_national_number', css_class='col-md-4'),
                    #     HTML('<span class="badge-form-2 badge-pill">20</span>'),
                    #     Div('parent_national_number_confirm', css_class='col-md-4'),
                    #     HTML('<span style="padding-top: 37px;">' +
                    #          '<a class="image-link" href="/static/images/lebanese_nationalID.png" target="_blank">' +
                    #          '<img src="/static/images/icon-help.png" width="25px" height="25px;"/></a></span>'),
                    #     css_class='row child_id  d-none card-body',
                    # ),
                    Div(
                        HTML('<span class="badge-form-2 badge-pill">16</span>'),
                        Div('national_number', css_class='col-md-4'),
                        HTML('<span class="badge-form-2 badge-pill">17</span>'),
                        Div('national_number_confirm', css_class='col-md-4'),
                        HTML('<span style="padding-top: 37px;">' +
                             '<a class="image-link" href="/static/images/lebanese_nationalID.png" target="_blank">' +
                             '<img src="/static/images/icon-help.png" width="25px" height="25px;"/></a></span>'),
                        css_class='row child_id child_id3 card-body',
                    ),
                    # Div(
                    #     HTML('<span class="badge-form-2 badge-pill">23</span>'),
                    #     Div('parent_syrian_national_number', css_class='col-md-4'),
                    #     HTML('<span class="badge-form-2 badge-pill">24</span>'),
                    #     Div('parent_syrian_national_number_confirm', css_class='col-md-4'),
                    #     HTML('<span style="padding-top: 37px;">' +
                    #          '<a class="image-link" href="/static/images/Syrian_passport.png" target="_blank">' +
                    #          '<img src="/static/images/icon-help.png" width="25px" height="25px;"/></a></span>'),
                    #     css_class='row child_id  d-none card-body',
                    # ),
                    Div(
                        HTML('<span class="badge-form-2 badge-pill">16</span>'),
                        Div('syrian_national_number', css_class='col-md-4'),
                        HTML('<span class="badge-form-2 badge-pill">17</span>'),
                        Div('syrian_national_number_confirm', css_class='col-md-4'),
                        HTML('<span style="padding-top: 37px;">' +
                             '<a class="image-link" href="/static/images/Syrian_passport.png" target="_blank">' +
                             '<img src="/static/images/icon-help.png" width="25px" height="25px;"/></a></span>'),
                        css_class='row child_id child_id4 card-body',
                    ),
                    # Div(
                    #     HTML('<span class="badge-form-2 badge-pill">27</span>'),
                    #     Div('parent_sop_national_number', css_class='col-md-4'),
                    #     HTML('<span class="badge-form-2 badge-pill">28</span>'),
                    #     Div('parent_sop_national_number_confirm', css_class='col-md-4'),
                    #     HTML('<span style="padding-top: 37px;">' +
                    #          '<a class="image-link" href="/static/images/Palestinian_from_Lebanon.png" target="_blank">' +
                    #          '<img src="/static/images/icon-help.png" width="25px" height="25px;"/></a></span>'),
                    #     css_class='row child_id  d-none card-body',
                    # ),
                    Div(
                        HTML('<span class="badge-form-2 badge-pill">16</span>'),
                        Div('sop_national_number', css_class='col-md-4'),
                        HTML('<span class="badge-form-2 badge-pill">17</span>'),
                        Div('sop_national_number_confirm', css_class='col-md-4'),
                        HTML('<span style="padding-top: 37px;">' +
                             '<a class="image-link" href="/static/images/Palestinian_from_Lebanon.png" target="_blank">' +
                             '<img src="/static/images/icon-help.png" width="25px" height="25px;"/></a></span>'),
                        css_class='row child_id child_id5 card-body',
                    ),
                    # Div(
                    #     HTML('<span class="badge-form-2 badge-pill">31</span>'),
                    #     Div('parent_other_number', css_class='col-md-4'),
                    #     HTML('<span class="badge-form-2 badge-pill">32</span>'),
                    #     Div('parent_other_number_confirm', css_class='col-md-4'),
                    #     css_class='row child_id  d-none card-body',
                    # ),
                    Div(
                        HTML('<span class="badge-form-2 badge-pill">16</span>'),
                        Div('other_number', css_class='col-md-4'),
                        HTML('<span class="badge-form-2 badge-pill">17</span>'),
                        Div('other_number_confirm', css_class='col-md-4'),
                        css_class='row child_id child_id6 card-body',
                    ),
                    Div(
                        HTML('<span class="badge-form-2 badge-pill">16</span>'),
                        Div('individual_extract_record', css_class='col-md-4'),
                        HTML('<span class="badge-form-2 badge-pill">17</span>'),
                        Div('individual_extract_record_confirm', css_class='col-md-4'),
                        css_class='row child_id child_id7 card-body',
                    ),
                    Div(
                        HTML('<span class="badge-form-2 badge-pill">16</span>'),
                        Div('source_of_transportation', css_class='col-md-3'),
                        css_class='row d-none card-body',
                    ),
                    css_id='step-3',
                    style='display: none;'
                ),
                Div(
                    Div(
                        HTML('<span class="badge-form badge-pill">1</span>'),
                        Div('hh_educational_level', css_class='col-md-3'),
                        HTML('<span class="badge-form badge-pill">2</span>'),
                        Div('father_educational_level', css_class='col-md-3'),
                        css_class='row card-body',
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">3</span>'),
                        Div('phone_number', css_class='col-md-3'),
                        HTML('<span class="badge-form badge-pill">4</span>'),
                        Div('phone_number_confirm', css_class='col-md-3'),
                        HTML('<span class="badge-form badge-pill">5</span>'),
                        Div('phone_owner', css_class='col-md-3'),
                        css_class='row card-body',
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">6</span>'),
                        Div('second_phone_number', css_class='col-md-3'),
                        HTML('<span class="badge-form badge-pill">7</span>'),
                        Div('second_phone_number_confirm', css_class='col-md-3'),
                        HTML('<span class="badge-form badge-pill">8</span>'),
                        Div('second_phone_owner', css_class='col-md-3'),
                        css_class='row card-body',
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">9</span>'),
                        Div('main_caregiver', css_class='col-md-3'),
                        HTML('<span class="badge-form-2 badge-pill" id="span_other_caregiver_relationship">10</span>'),
                        Div('other_caregiver_relationship', css_class='col-md-3'),
                        css_class='row card-body',
                    ),
                    Div(
                        HTML('<span class="badge-form-2 badge-pill">11</span>'),
                        Div('main_caregiver_nationality', css_class='col-md-3'),
                        HTML(
                            '<span class="badge-form-2 badge-pill" id="span_main_caregiver_nationality_other">12</span>'),
                        Div('main_caregiver_nationality_other', css_class='col-md-3'),
                        css_class='row card-body',
                    ),
                    Div(
                        HTML('<span class="badge-form-2 badge-pill">13</span>'),
                        Div('caretaker_first_name', css_class='col-md-3'),
                        HTML('<span class="badge-form-2 badge-pill">14</span>'),
                        Div('caretaker_middle_name', css_class='col-md-3'),
                        css_class='row card-body',
                    ),
                    Div(
                        HTML('<span class="badge-form-2 badge-pill">15</span>'),
                        Div('caretaker_last_name', css_class='col-md-3'),
                        HTML('<span class="badge-form-2 badge-pill">16</span>'),
                        Div('caretaker_mother_name', css_class='col-md-3'),
                        css_class='row card-body',
                    ),
                    Div(
                        HTML('<span class="badge-form-2 badge-pill">17</span>'),
                        Div('caretaker_birthday_year', css_class='col-md-2'),
                        HTML('<span class="badge-form-2 badge-pill">18</span>'),
                        Div('caretaker_birthday_month', css_class='col-md-2'),
                        HTML('<span class="badge-form-2 badge-pill">19</span>'),
                        Div('caretaker_birthday_day', css_class='col-md-2'),
                        css_class='row card-body',
                    ),
                    css_id='step-4',
                    style='display: none;'
                ),
                Div(
                    Div(
                        HTML('<span class="badge-form badge-pill">1</span>'),
                        Div('student_family_status', css_class='col-md-4'),
                        HTML('<span class="badge-form badge-pill" id=span_student_have_children">2</span>'),
                        Div('student_have_children', css_class='col-md-4', css_id='student_have_children'),
                        HTML('<span class="badge-form badge-pill" id="span_student_number_children">3</span>'),
                        Div('student_number_children', css_class='col-md-3'),
                        css_class='row card-body',
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">4</span>'),
                        Div('have_labour_single_selection', css_class='col-md-3'),
                        css_class='row card-body',
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">5</span>'),
                        Div('labours_single_selection', css_class='col-md-3', css_id='labours'),
                        HTML('<span class="badge-form badge-pill" id="span_labours_other_specify">6</span>'),
                        Div('labours_other_specify', css_class='col-md-3'),
                        css_class='row card-body',
                        id='labour_details_1'
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">7</span>'),
                        Div('labour_hours', css_class='col-md-3', css_id='labour_hours'),
                        HTML('<span class="badge-form badge-pill">8</span>'),
                        Div('labour_weekly_income', css_class='col-md-3'),
                        css_class='row card-body',
                        id='labour_details_2'
                    ),
                    css_id='step-5',
                    style='display: none;'
                ),
                Div(
                    Div(
                        HTML('<span class="badge-form-2 badge-pill" id="span_exam1">1</span>'),
                        Div('exam1', css_class='col-md-3'),
                        css_class='row card-body',
                    ),
                    css_id='step-6',
                    style='display: none;'
                ),
                Div(
                    Div(
                        HTML('<span class="badge-form badge-pill">1</span>'),
                        Div('consent_parents', css_class='col-md-3'),
                        css_class='row card-body',
                    ),
                    FormActions(
                        Submit('save', 'Save',
                               css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-success'),
                        Reset('reset', 'Reset',
                              css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-warning'),
                    ),
                    css_id='step-7',
                    style='display: none;'
                )
            )

        school_id = 0
        partner_id = 0
        clm_bridging_all = False

        if self.request.user.school:
            school_id = self.request.user.school.id
        if self.request.user.partner_id:
            partner_id = self.request.user.partner_id
        clm_bridging_all = has_group(self.request.user, 'CLM_BRIDGING_ALL')

        queryset = School.objects.filter(is_closed=False).all()

        if not clm_bridging_all:
            if school_id and school_id > 0:
                queryset = School.objects.filter(id=school_id)

            elif partner_id and partner_id > 0:
                queryset = School.objects.filter(is_closed=False,
                                                 id__in=PartnerOrganization
                                                 .objects
                                                 .filter(id=partner_id)
                                                 .values_list('schools', flat=True))
            else:
                queryset =queryset.none()

        self.fields['school'] = forms.ModelChoiceField(
            queryset=queryset, widget=forms.Select,
            label=_('School Name'),
            empty_label='-------',
            required=True, to_field_name='id',
        )

    def clean(self):
        cleaned_data = super(BridgingForm, self).clean()

        # check if date is valid
        year = cleaned_data.get("student_birthday_year")
        month = cleaned_data.get("student_birthday_month")
        day = cleaned_data.get("student_birthday_day")
        if not year:
            self.add_error('student_birthday_year', 'This field is required')
        if not month:
            self.add_error('student_birthday_month', 'This field is required')
        if not day:
            self.add_error('student_birthday_day', 'This field is required')

        if year and month and day:
            try:
                year = int(year)
                month = int(month)
                day = int(day)
                datetime.datetime(year, month, day)
            except ValueError:
                self.add_error('student_birthday_year', 'The entered date is not valid.')

        phone_number = cleaned_data.get("phone_number")
        phone_number_confirm = cleaned_data.get("phone_number_confirm")
        second_phone_number = cleaned_data.get("second_phone_number")
        second_phone_number_confirm = cleaned_data.get("second_phone_number_confirm")
        id_type = cleaned_data.get("id_type")
        individual_case_number = cleaned_data.get("individual_case_number")
        individual_case_number_confirm = cleaned_data.get("individual_case_number_confirm")
        recorded_number = cleaned_data.get("recorded_number")
        recorded_number_confirm = cleaned_data.get("recorded_number_confirm")
        national_number = cleaned_data.get("national_number")
        national_number_confirm = cleaned_data.get("national_number_confirm")
        syrian_national_number = cleaned_data.get("syrian_national_number")
        syrian_national_number_confirm = cleaned_data.get("syrian_national_number_confirm")
        sop_national_number = cleaned_data.get("sop_national_number")
        sop_national_number_confirm = cleaned_data.get("sop_national_number_confirm")
        other_number = cleaned_data.get("other_number")
        other_number_confirm = cleaned_data.get("other_number_confirm")
        individual_extract_record = cleaned_data.get("individual_extract_record")
        individual_extract_record_confirm = cleaned_data.get("individual_extract_record_confirm")
        education_status = cleaned_data.get("education_status")
        miss_school_date = cleaned_data.get("miss_school_date")
        student_nationality = cleaned_data.get("student_nationality")
        other_nationality = cleaned_data.get("other_nationality")
        main_caregiver = cleaned_data.get("main_caregiver")
        other_caregiver_relationship = cleaned_data.get("other_caregiver_relationship")
        main_caregiver_nationality = cleaned_data.get("main_caregiver_nationality")
        main_caregiver_nationality_other = cleaned_data.get("main_caregiver_nationality_other")
        have_labour_single_selection = cleaned_data.get("have_labour_single_selection")
        labours_single_selection = cleaned_data.get("labours_single_selection")
        labour_hours = cleaned_data.get("labour_hours")
        labour_weekly_income = cleaned_data.get("labour_weekly_income")
        student_have_children = cleaned_data.get("student_have_children")
        student_number_children = cleaned_data.get("student_number_children")
        labours_other_specify = cleaned_data.get("labours_other_specify")
        source_of_identification = cleaned_data.get("source_of_identification")
        source_of_identification_specify = cleaned_data.get("source_of_identification_specify")
        rims_case_number = cleaned_data.get("rims_case_number")

        if source_of_identification == 'Other Sources':
            if not source_of_identification_specify:
                self.add_error('source_of_identification_specify', 'This field is required')
        if source_of_identification == 'RIMS':
            if not rims_case_number:
                self.add_error('rims_case_number', 'This field is required')
        if labours_single_selection == 'other_many_other':
            if not labours_other_specify:
                self.add_error('labours_other_specify', 'This field is required')

        if education_status == 'Was registered in formal school and didnt continue':
            if not miss_school_date:
                self.add_error('miss_school_date', 'This field is required')
        if student_nationality and student_nationality.id == 6:
            if not other_nationality:
                self.add_error('other_nationality', 'This field is required')
        if main_caregiver == 'other':
            if not other_caregiver_relationship:
                self.add_error('other_caregiver_relationship', 'This field is required')
        if main_caregiver_nationality and main_caregiver_nationality.id == 6:
            if not main_caregiver_nationality_other:
                self.add_error('main_caregiver_nationality_other', 'This field is required')
        if student_have_children:
            if not student_number_children:
                self.add_error('student_number_children', 'This field is required')
        if have_labour_single_selection != 'no':
            if not labours_single_selection:
                self.add_error('labours_single_selection', 'This field is required')
            if not labour_hours:
                self.add_error('labour_hours', 'This field is required')
            if not labour_weekly_income:
                self.add_error('labour_weekly_income', 'This field is required')

        if phone_number != phone_number_confirm:
            msg = "The phone numbers are not matched"
            self.add_error('phone_number_confirm', msg)
        if second_phone_number != second_phone_number_confirm:
            msg = "The phone numbers are not matched"
            self.add_error('second_phone_number_confirm', msg)

        if id_type == 'UNHCR Registered':
            if not individual_case_number:
                self.add_error('individual_case_number', 'This field is required')
            if individual_case_number != individual_case_number_confirm:
                msg = "The individual case numbers are not matched"
                self.add_error('individual_case_number_confirm', msg)

        if id_type == 'UNHCR Recorded':
            if not recorded_number:
                self.add_error('recorded_number', 'This field is required')

            if recorded_number != recorded_number_confirm:
                msg = "The recorded numbers are not matched"
                self.add_error('recorded_number_confirm', msg)

        if id_type == 'Syrian national ID':
            if not syrian_national_number:
                self.add_error('syrian_national_number', 'This field is required')

            if not syrian_national_number_confirm:
                self.add_error('syrian_national_number_confirm', 'This field is required')

            if syrian_national_number and not len(syrian_national_number) == 11:
                msg = "Please enter a valid number (11 digits)"
                self.add_error('syrian_national_number', msg)

            if syrian_national_number_confirm and not len(syrian_national_number_confirm) == 11:
                msg = "Please enter a valid number (11 digits)"
                self.add_error('syrian_national_number_confirm', msg)

            if syrian_national_number != syrian_national_number_confirm:
                msg = "The national numbers are not matched"
                self.add_error('syrian_national_number_confirm', msg)

        if id_type == 'Lebanese national ID':
            if not national_number:
                self.add_error('national_number', 'This field is required')

            if not national_number_confirm:
                self.add_error('national_number_confirm', 'This field is required')

            if national_number and not len(national_number) == 12:
                msg = "Please enter a valid number (12 digits)"
                self.add_error('national_number', msg)

            if national_number_confirm and not len(national_number_confirm) == 12:
                msg = "Please enter a valid number (12 digits)"
                self.add_error('national_number_confirm', msg)

            if national_number != national_number_confirm:
                msg = "The national numbers are not matched"
                self.add_error('national_number_confirm', msg)

        if id_type == 'Lebanese Extract of Record':
            if not individual_extract_record:
                self.add_error('individual_extract_record', 'This field is required')
            if individual_extract_record != individual_extract_record_confirm:
                msg = "The Parent Extract Record are not matched"
                self.add_error('individual_extract_record_confirm', msg)

        if id_type == 'Palestinian national ID':
            if not sop_national_number:
                self.add_error('sop_national_number', 'This field is required')

            if not sop_national_number_confirm:
                self.add_error('sop_national_number_confirm', 'This field is required')

            if sop_national_number != sop_national_number_confirm:
                msg = "The national numbers are not matched"
                self.add_error('sop_national_number_confirm', msg)

        if id_type == 'Other nationality':
            if not other_number:
                self.add_error('other_number', 'This field is required')

            if not other_number_confirm:
                self.add_error('other_number_confirm', 'This field is required')

            if other_number != other_number_confirm:
                msg = "The ID numbers are not matched"
                self.add_error('other_number_confirm', msg)

        # grades Max Value validation
        registration_level = cleaned_data.get("registration_level")
        language = cleaned_data.get("language")

        if self.request.user.partner and not self.request.user.partner.is_Kayany:
            arabic_alphabet_knowledge = cleaned_data.get("arabic_alphabet_knowledge")
            arabic_familiar_words = cleaned_data.get("arabic_familiar_words")
            arabic_reading_comprehension = cleaned_data.get("arabic_reading_comprehension")

            english_alphabet_knowledge = cleaned_data.get("english_alphabet_knowledge")
            english_familiar_words = cleaned_data.get("english_familiar_words")
            english_reading_comprehension = cleaned_data.get("english_reading_comprehension")

            french_alphabet_knowledge = cleaned_data.get("french_alphabet_knowledge")
            french_familiar_words = cleaned_data.get("french_familiar_words")
            french_reading_comprehension = cleaned_data.get("french_reading_comprehension")

            math = cleaned_data.get("math")

            if arabic_alphabet_knowledge is None:
                self.add_error('arabic_alphabet_knowledge', 'This field is required')
            elif arabic_alphabet_knowledge > 48:
                self.add_error('arabic_alphabet_knowledge', 'This value is greater that 48')

            if arabic_familiar_words is None:
                self.add_error('arabic_familiar_words', 'This field is required')
            elif arabic_familiar_words > 20:
                self.add_error('arabic_familiar_words', 'This value is greater that 20')

            if arabic_reading_comprehension is None:
                self.add_error('arabic_reading_comprehension', 'This field is required')
            elif arabic_reading_comprehension > 10:
                self.add_error('arabic_reading_comprehension', 'This value is greater that 10')

            if language == 'english_arabic':
                if english_alphabet_knowledge is None:
                    self.add_error('english_alphabet_knowledge', 'This field is required')
                elif english_alphabet_knowledge > 48:
                    self.add_error('english_alphabet_knowledge', 'This value is greater that 48')

                if english_familiar_words is None:
                    self.add_error('english_familiar_words', 'This field is required')
                elif english_familiar_words > 20:
                    self.add_error('english_familiar_words', 'This value is greater that 20')

                if english_reading_comprehension is None:
                    self.add_error('english_reading_comprehension', 'This field is required')
                elif english_reading_comprehension > 10:
                    self.add_error('english_reading_comprehension', 'This value is greater that 10')

            elif language == 'french_arabic':
                if french_alphabet_knowledge is None:
                    self.add_error('french_alphabet_knowledge', 'This field is required')
                elif french_alphabet_knowledge > 48:
                    self.add_error('french_alphabet_knowledge', 'This value is greater that 48')

                if french_familiar_words is None:
                    self.add_error('french_familiar_words', 'This field is required')
                elif french_familiar_words > 20:
                    self.add_error('french_familiar_words', 'This value is greater that 20')

                if french_reading_comprehension is None:
                    self.add_error('french_reading_comprehension', 'This field is required')
                elif french_reading_comprehension > 10:
                    self.add_error('french_reading_comprehension', 'This value is greater that 10')

            if math is None:
                self.add_error('math', 'This field is required')
            elif registration_level == 'level_one' and math > 50:
                self.add_error('math', 'This value is greater that 50')
            elif registration_level == 'level_two' and math > 88:
                self.add_error('math', 'This value is greater that 88')
            elif math > 103:
                self.add_error('math', 'This value is greater that 103')
        else:
            exam1 = cleaned_data.get("exam1")
            if exam1 is None:
                self.add_error('exam1', 'This field is required')
            elif exam1 > 20:
                self.add_error('exam1', 'This value is greater that 20')

        student_p_code = cleaned_data.get("student_p_code")
        if student_p_code and len(student_p_code) > 50:
            self.add_error('student_p_code', _('P-Code must not exceed 50 characters.'))

    def save(self, request=None, instance=None, serializer=None):

        from student_registration.students.utils import generate_one_unique_id

        instance = super(BridgingForm, self).save(request=request, instance=instance, serializer=BridgingSerializer)
        instance.save()

        consent_parents = request.FILES.get('consent_parents', False)
        if consent_parents:
            instance.consent_parents = consent_parents

        instance.pre_test = {
            "Bridging_ASSESSMENT/arabic_alphabet_knowledge": request.POST.get('arabic_alphabet_knowledge'),
            "Bridging_ASSESSMENT/arabic_familiar_words": request.POST.get('arabic_familiar_words'),
            "Bridging_ASSESSMENT/arabic_reading_comprehension": request.POST.get('arabic_reading_comprehension'),

            "Bridging_ASSESSMENT/english_alphabet_knowledge": request.POST.get('english_alphabet_knowledge'),
            "Bridging_ASSESSMENT/english_familiar_words": request.POST.get('english_familiar_words'),
            "Bridging_ASSESSMENT/english_reading_comprehension": request.POST.get('english_reading_comprehension'),

            "Bridging_ASSESSMENT/french_alphabet_knowledge": request.POST.get('french_alphabet_knowledge'),
            "Bridging_ASSESSMENT/french_familiar_words": request.POST.get('french_familiar_words'),
            "Bridging_ASSESSMENT/french_reading_comprehension": request.POST.get('french_reading_comprehension'),
            "Bridging_ASSESSMENT/math": request.POST.get('math'),
            "Bridging_ASSESSMENT/exam1": request.POST.get('exam1')

        }

        instance.save()

        if instance:
            instance.student.unicef_id = generate_one_unique_id(
                str(instance.student.pk),
                instance.student.first_name,
                instance.student.father_name,
                instance.student.last_name,
                instance.student.mother_fullname,
                instance.student.birthdate,
                instance.student.nationality_name_en,
                instance.student.sex
            )
            instance.student.save()

        return instance

    class Meta:
        model = Bridging
        fields = CommonForm.Meta.fields + (
            'first_attendance_date',
            'child_outreach',
            'residence_type',
            'student_birthday_year',
            'have_labour_single_selection',
            'labours_single_selection',
            'labours_other_specify',
            'labour_hours',
            'phone_number',
            'phone_number_confirm',
            'phone_owner',
            'second_phone_number',
            'second_phone_number_confirm',
            'second_phone_owner',
            'id_type',
            # 'case_number',
            # 'case_number_confirm',
            'individual_case_number',
            'individual_case_number_confirm',
            # 'parent_individual_case_number',
            # 'parent_individual_case_number_confirm',
            'recorded_number',
            'recorded_number_confirm',
            'national_number',
            'national_number_confirm',
            'syrian_national_number',
            'syrian_national_number_confirm',
            'sop_national_number',
            'sop_national_number_confirm',
            # 'parent_national_number',
            # 'parent_national_number_confirm',
            # 'parent_syrian_national_number',
            # 'parent_syrian_national_number_confirm',
            # 'parent_sop_national_number',
            # 'parent_sop_national_number_confirm',
            # 'parent_other_number',
            # 'parent_other_number_confirm',
            'other_number',
            'other_number_confirm',
            'individual_extract_record',
            'individual_extract_record_confirm',
            'no_child_id_confirmation',
            'source_of_identification',
            'rims_case_number',
            'source_of_identification_specify',
            'other_nationality',
            'education_status',
            'caretaker_first_name',
            'caretaker_middle_name',
            'caretaker_last_name',
            'caretaker_mother_name',
            'miss_school_date',
            'student_have_children',
            'student_family_status',
            'student_number_children',
            'round_start_date',
            'cadaster',
            'school',
            'registration_level',
            'main_caregiver',
            'main_caregiver_nationality',
            'other_caregiver_relationship',
            'labour_weekly_income',
            'source_of_transportation',
            'student_p_code',
            'consent_parents',
            'registration_date',
            'enrolled_formal_education'
        )

    class Media:
        js = (
            # 'js/jquery-3.3.1.min.js',
            # 'js/jquery-ui-1.12.1.js',
            # 'js/validator.js',
            # 'js/registrations.js',
        )


class BridgingAssessmentForm(forms.ModelForm):
    REGISTRATION_LEVEL = (
        ('', '----------'),
        ('level_one', _('Level one')),
        ('level_two', _('Level two')),
        ('level_three', _('Level three')),
        ('level_four', _('Level four')),
        ('level_five', _('Level five')),
        ('level_six', _('Level six'))
    )
    participation = forms.ChoiceField(
        label=_('How was the level of child participation in the program?'),
        widget=forms.Select, required=True,
        choices=(
                ('', '----------'),
                ('no_absence', _('No Absence')),
                ('less_than_5days', _('Less than 5 absence days')),
                ('5_10_days', _('5 to 10 absence days')),
                ('10_15_days', _('10 to 15 absence days')),
                ('15_25_days', _('15 to 25 absence days')),
                ('more_than_25days', _('More than 25 absence days')),

            ),
        initial=''
    )

    learning_result = forms.ChoiceField(
        label=_('Based on the overall score, what is the recommended learning path?'),
        widget=forms.Select, required=False,
        choices=Bridging.LEARNING_RESULT
    )
    dropout_reason = forms.CharField(
        label=_('Dropout reason'),
        widget=forms.TextInput, required=False
    )
    dropout_date = forms.DateField(
        label=_("Dropout date"),
        required=False
    )
    learning_result_other = forms.CharField(
        label=_('Please specify'),
        widget=forms.TextInput, required=False
    )
    referral_school = forms.CharField(
        label=_('Formal Education School '),
        widget=forms.TextInput, required=False
    )
    referral_school_type = forms.ChoiceField(
        label=_('School Type'),
        choices=Bridging.SCHOOL_TYPE,
        widget=forms.Select,
        required=False
    )
    barriers_single = forms.ChoiceField(
        label=_('The main barriers affecting the daily attendance and performance '
                'of the child or drop out of programme?'),
        choices=CLM.BARRIERS,
        widget=forms.Select,
        required=False
    )
    barriers_other = forms.CharField(
        label=_('Please specify'),
        widget=forms.TextInput, required=False
    )
    test_done = forms.ChoiceField(
        label=_("Post test has been done"),
        widget=forms.Select, required=True,
        choices=CLM.YES_NO,
        initial='yes'
    )

    round_complete = forms.ChoiceField(
        label=_("Dirasa Round complete"),
        widget=forms.Select, required=False,
        choices=CLM.YES_NO
    )
    arabic_alphabet_knowledge = forms.FloatField(
        label=_('Arabic Alphabet Knowledge'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=False
    )
    arabic_familiar_words = forms.FloatField(
        label=_('Arabic Familiar words'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=False
    )
    arabic_reading_comprehension = forms.FloatField(
        label=_('Arabic Reading Comprehension'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=False
    )
    english_alphabet_knowledge = forms.FloatField(
        label=_('English Alphabet Knowledge'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=False
    )
    english_familiar_words = forms.FloatField(
        label=_('English Familiar words'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=False
    )
    english_reading_comprehension = forms.FloatField(
        label=_('English Reading Comprehension'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=False
    )
    french_alphabet_knowledge = forms.FloatField(
        label=_('French Alphabet Knowledge'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=False
    )
    french_familiar_words = forms.FloatField(
        label=_('French Familiar words'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=False
    )
    french_reading_comprehension = forms.FloatField(
        label=_('French Reading Comprehension'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=False
    )
    math = forms.FloatField(
        label=_('Math'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=False
    )
    exam3 = forms.FloatField(
        label=_('Exam 3'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=False
    )
    follow_up_type = forms.ChoiceField(
        label=_('Type of follow up'),
        widget=forms.Select, required=False,
        choices=(
            ('none', _('----------')),
            ('Phone', _('Phone Call')),
            ('House visit', _('House Visit')),
            ('Family Visit', _('Family Visit')),
        ),
        initial=''
    )
    child_health_examed = forms.ChoiceField(
        label=_("Did the child receive health exam"),
        widget=forms.Select, required=False,
        choices=(('yes', _("Yes")), ('no', _("No")))
    )
    child_health_concern = forms.ChoiceField(
        label=_("Anything to worry about"),
        widget=forms.Select, required=False,
        choices=CLM.YES_NO
    )
    registration_level = forms.ChoiceField(
        label=_("Registration level"),
        widget=forms.Select, required=False,
        choices=REGISTRATION_LEVEL
    )
    language = forms.ChoiceField(
        label=_('The language supported in the program'),
        widget=forms.Select,
        choices=CLM.LANGUAGES, required=False,
        initial='english_arabic'
    )
    community_Liaison_follow_up = forms.ChoiceField(
        label=_("Was the community Liaison at school level involved in follow up on child absence or drop out?"),
        widget=forms.Select, required=False,
        choices=CLM.YES_NO,
    )
    community_liaison_specify = forms.CharField(
        label=_('specify'),
        widget=forms.TextInput, required=False
    )

    clm_type = forms.CharField(widget=forms.HiddenInput, required=False)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(BridgingAssessmentForm, self).__init__(*args, **kwargs)

        post_test = ''
        post_test_button = ' btn-outline-secondary disabled'
        instance = kwargs['instance'] if 'instance' in kwargs else ''
        self.fields['clm_type'].initial = 'Bridging'

        is_Kayany = False
        if self.request.user.partner:
            is_Kayany = self.request.user.partner.is_Kayany

        display_assessment = ''
        form_action = reverse('clm:bridging_post_assessment', kwargs={'pk': instance.id})

        if instance.post_test:
            post_test_button = ' btn-outline-success '
            post_test = instance.assessment_form(
                stage='post_test',
                assessment_slug='Bridging_post_test',
                callback=self.request.build_absolute_uri(
                    reverse('clm:bridging_post_assessment', kwargs={'pk': instance.id}))
            )

        self.helper = FormHelper()
        self.helper.form_show_labels = True
        self.helper.form_action = form_action
        if not is_Kayany:

            self.helper.layout = Layout(
                Div(
                    Div(
                        Div('registration_level', css_class='col-md-3 d-none'),
                        Div('language', css_class='col-md-3 d-none'),
                        css_class='row card-body',
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">1</span>'),
                        Div('participation', css_class='col-md-3'),
                        HTML('<span class="badge-form badge-pill" id="span_barriers_single">2</span>'),
                        Div('barriers_single', css_class='col-md-4'),
                        HTML('<span class="badge-form badge-pill" id="span_barriers_other">3</span>'),
                        Div('barriers_other', css_class='col-md-2'),
                        css_class='row card-body',
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill" id="span_community_Liaison_follow_up">4</span>'),
                        Div('community_Liaison_follow_up', css_class='col-md-4'),
                        HTML('<span class="badge-form badge-pill" id="span_community_liaison_specify">5</span>'),
                        Div('community_liaison_specify', css_class='col-md-4'),
                        css_class='row community_Liaison card-body',
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">6</span>'),
                        Div('test_done', css_class='col-md-3'),
                        HTML('<span class="badge-form badge-pill" id="span_round_complete">7</span>'),
                        Div('round_complete', css_class='col-md-3'),
                        css_class='row card-body',
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">8</span>'),
                        Div('learning_result', css_class='col-md-4'),
                        HTML('<span class="badge-form badge-pill" id="span_learning_result_other">9</span>'),
                        Div('learning_result_other', css_class='col-md-4'),
                        css_class='row card-body',
                    ),
                    Div(
                        HTML('<span class="badge-form-2 badge-pill" id="span_dropout_reason">10</span>'),
                        Div('dropout_reason', css_class='col-md-3'),
                        HTML('<span class="badge-form-2 badge-pill" id="span_dropout_date">11</span>'),
                        Div('dropout_date', css_class='col-md-3'),
                        css_class='row card-body',
                    ),
                    Div(
                        HTML('<span class="badge-form-2 badge-pill" id="span_referral_school">12</span>'),
                        Div('referral_school', css_class='col-md-4'),
                        HTML('<span class="badge-form-2 badge-pill" id="span_referral_school_type">13</span>'),
                        Div('referral_school_type', css_class='col-md-4'),
                        css_class='row card-body',
                    ),
                    Div(
                        HTML('<span class="badge-form-2 badge-pill" id="span_arabic">14</span>'),
                        Div('arabic_alphabet_knowledge', css_class='col-md-3'),
                        Div('arabic_familiar_words', css_class='col-md-3'),
                        Div('arabic_reading_comprehension', css_class='col-md-3'),
                        css_class='row grades card-body',
                    ),
                    Div(
                        HTML('<span class="badge-form-2 badge-pill" id="span_english">15</span>'),
                        Div('english_alphabet_knowledge', css_class='col-md-3'),
                        Div('english_familiar_words', css_class='col-md-3'),
                        Div('english_reading_comprehension', css_class='col-md-3'),
                        css_class='row grades card-body',
                    ),
                    Div(
                        HTML('<span class="badge-form-2 badge-pill" id="span_french">16</span>'),
                        Div('french_alphabet_knowledge', css_class='col-md-3'),
                        Div('french_familiar_words', css_class='col-md-3'),
                        Div('french_reading_comprehension', css_class='col-md-3'),
                        css_class='row grades card-body',
                    ),
                    Div(
                        HTML('<span class="badge-form-2 badge-pill" id="span_math">17</span>'),
                        Div('math', css_class='col-md-3'),
                        css_class='row grades card-body',
                    ),
                    FormActions(
                        Submit('save', 'Save',
                               css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-success'),
                        Reset('reset', 'Reset',
                              css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-warning'),
                    )
                )
            )
        else:
            self.helper.layout = Layout(
                Div(
                    Div(
                        Div('registration_level', css_class='col-md-3 d-none'),
                        Div('language', css_class='col-md-3 d-none'),
                        css_class='row card-body',
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">1</span>'),
                        Div('participation', css_class='col-md-3'),
                        HTML('<span class="badge-form badge-pill" id="span_barriers_single">2</span>'),
                        Div('barriers_single', css_class='col-md-4'),
                        HTML('<span class="badge-form badge-pill" id="span_barriers_other">3</span>'),
                        Div('barriers_other', css_class='col-md-2'),
                        css_class='row card-body',
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill" id="span_community_Liaison_follow_up">4</span>'),
                        Div('community_Liaison_follow_up', css_class='col-md-4'),
                        HTML('<span class="badge-form badge-pill" id="span_community_liaison_specify">5</span>'),
                        Div('community_liaison_specify', css_class='col-md-4'),
                        css_class='row community_Liaison card-body',
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">6</span>'),
                        Div('test_done', css_class='col-md-3'),
                        HTML('<span class="badge-form badge-pill" id="span_round_complete">7</span>'),
                        Div('round_complete', css_class='col-md-3'),
                        css_class='row card-body',
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">8</span>'),
                        Div('learning_result', css_class='col-md-4'),
                        HTML('<span class="badge-form badge-pill" id="span_learning_result_other">9</span>'),
                        Div('learning_result_other', css_class='col-md-4'),
                        css_class='row card-body',
                    ),
                    Div(
                        HTML('<span class="badge-form-2 badge-pill" id="span_dropout_reason">10</span>'),
                        Div('dropout_reason', css_class='col-md-3'),
                        HTML('<span class="badge-form-2 badge-pill" id="span_dropout_date">11</span>'),
                        Div('dropout_date', css_class='col-md-3'),
                        css_class='row card-body',
                    ),
                    Div(
                        HTML('<span class="badge-form-2 badge-pill" id="span_referral_school">12</span>'),
                        Div('referral_school', css_class='col-md-4'),
                        HTML('<span class="badge-form-2 badge-pill" id="span_referral_school_type">13</span>'),
                        Div('referral_school_type', css_class='col-md-4'),
                        css_class='row card-body',
                    ),
                    Div(
                        HTML('<span class="badge-form-2 badge-pill" id="span_exam3">14</span>'),
                        Div('exam3', css_class='col-md-3'),
                        css_class='row grades card-body',
                    ),
                    FormActions(
                        Submit('save', 'Save',
                               css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-success'),
                        Reset('reset', 'Reset',
                              css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-warning'),
                    )
                )
            )

    def clean(self):
        cleaned_data = super(BridgingAssessmentForm, self).clean()

        learning_result = cleaned_data.get("learning_result")
        learning_result_other = cleaned_data.get("learning_result_other")
        dropout_date = cleaned_data.get("dropout_date")
        dropout_reason = cleaned_data.get("dropout_reason")
        referral_school = cleaned_data.get("referral_school")
        referral_school_type = cleaned_data.get("referral_school_type")

        barriers_single = cleaned_data.get("barriers_single")
        barriers_other = cleaned_data.get("barriers_other")

        test_done = cleaned_data.get("test_done")
        round_complete = cleaned_data.get("round_complete")

        participation = cleaned_data.get("participation")
        community_Liaison_follow_up = cleaned_data.get("community_Liaison_follow_up")
        community_liaison_specify = cleaned_data.get("community_liaison_specify")

        if participation != 'no_absence':
            if not barriers_single:
                self.add_error('barriers_single', 'This field is required')
            if not community_Liaison_follow_up:
                self.add_error('community_Liaison_follow_up', 'This field is required')
            elif community_Liaison_follow_up == 'yes':
                if not community_liaison_specify:
                    self.add_error('community_liaison_specify', 'This field is required')

        if test_done == 'yes':
            if not round_complete:
                self.add_error('round_complete', 'This field is required')

        if learning_result == 'other' and not learning_result_other:
            self.add_error('learning_result_other', 'This field is required')

        if learning_result == 'dropout' and not dropout_date:
            self.add_error('dropout_date', 'This field is required')
        if learning_result == 'dropout' and not dropout_reason:
            self.add_error('dropout_reason', 'This field is required')

        if learning_result == 'referred_public_school' and not referral_school:
            self.add_error('referral_school', 'This field is required')
        if learning_result == 'referred_public_school' and not referral_school_type:
            self.add_error('referral_school_type', 'This field is required')

        if barriers_single == 'other':
            if not barriers_other:
                self.add_error('barriers_other', 'This field is required')

        # grades Max Value validation
        registration_level = cleaned_data.get("registration_level")
        language = cleaned_data.get("language")

        arabic_alphabet_knowledge = cleaned_data.get("arabic_alphabet_knowledge")
        arabic_familiar_words = cleaned_data.get("arabic_familiar_words")
        arabic_reading_comprehension = cleaned_data.get("arabic_reading_comprehension")

        english_alphabet_knowledge = cleaned_data.get("english_alphabet_knowledge")
        english_familiar_words = cleaned_data.get("english_familiar_words")
        english_reading_comprehension = cleaned_data.get("english_reading_comprehension")

        french_alphabet_knowledge = cleaned_data.get("french_alphabet_knowledge")
        french_familiar_words = cleaned_data.get("french_familiar_words")
        french_reading_comprehension = cleaned_data.get("french_reading_comprehension")

        math = cleaned_data.get("math")
        # social_emotional = cleaned_data.get("social_emotional")
        # artistic = cleaned_data.get("artistic")

        if test_done == 'yes':
            if self.request.user.partner and not self.request.user.partner.is_Kayany:
                if arabic_alphabet_knowledge is None:
                    self.add_error('arabic_alphabet_knowledge', 'This field is required')
                elif arabic_alphabet_knowledge > 48:
                    self.add_error('arabic_alphabet_knowledge', 'This value is greater that 48')

                if arabic_familiar_words is None:
                    self.add_error('arabic_familiar_words', 'This field is required')
                elif arabic_familiar_words > 20:
                    self.add_error('arabic_familiar_words', 'This value is greater that 20')

                if arabic_reading_comprehension is None:
                    self.add_error('arabic_reading_comprehension', 'This field is required')
                elif arabic_reading_comprehension > 10:
                    self.add_error('arabic_reading_comprehension', 'This value is greater that 10')

                if language == 'english_arabic':
                    if english_alphabet_knowledge is None:
                        self.add_error('english_alphabet_knowledge', 'This field is required')
                    elif english_alphabet_knowledge > 48:
                        self.add_error('english_alphabet_knowledge', 'This value is greater that 48')

                    if english_familiar_words is None:
                        self.add_error('english_familiar_words', 'This field is required')
                    elif english_familiar_words > 20:
                        self.add_error('english_familiar_words', 'This value is greater that 20')

                    if english_reading_comprehension is None:
                        self.add_error('english_reading_comprehension', 'This field is required')
                    elif english_reading_comprehension > 10:
                        self.add_error('english_reading_comprehension', 'This value is greater that 10')

                elif language == 'french_arabic':
                    if french_alphabet_knowledge is None:
                        self.add_error('french_alphabet_knowledge', 'This field is required')
                    elif french_alphabet_knowledge > 48:
                        self.add_error('french_alphabet_knowledge', 'This value is greater that 48')

                    if french_familiar_words is None:
                        self.add_error('french_familiar_words', 'This field is required')
                    elif french_familiar_words > 20:
                        self.add_error('french_familiar_words', 'This value is greater that 20')

                    if french_reading_comprehension is None:
                        self.add_error('french_reading_comprehension', 'This field is required')
                    elif french_reading_comprehension > 10:
                        self.add_error('french_reading_comprehension', 'This value is greater that 10')

                if math is None:
                    self.add_error('math', 'This field is required')
                elif registration_level == 'level_one' and math > 50:
                    self.add_error('math', 'This value is greater that 50')
                elif registration_level == 'level_two' and math > 88:
                    self.add_error('math', 'This value is greater that 88')
                elif math > 103:
                    self.add_error('math', 'This value is greater that 103')
            else:
                exam3 = cleaned_data.get("exam3")
                if exam3 is None:
                    self.add_error('exam3', 'This field is required')
                elif exam3 > 20:
                    self.add_error('exam3', 'This value is greater that 20')


    def save(self, instance=None, request=None):
        instance = super(BridgingAssessmentForm, self).save()
        # instance = super(BridgingAssessmentForm, self).save(request=request, instance=instance, serializer=BridgingSerializer)

        instance.modified_by = request.user

        instance.post_test = {
            "Bridging_ASSESSMENT/arabic_alphabet_knowledge": request.POST.get('arabic_alphabet_knowledge'),
            "Bridging_ASSESSMENT/arabic_familiar_words": request.POST.get('arabic_familiar_words'),
            "Bridging_ASSESSMENT/arabic_reading_comprehension": request.POST.get('arabic_reading_comprehension'),

            "Bridging_ASSESSMENT/english_alphabet_knowledge": request.POST.get('english_alphabet_knowledge'),
            "Bridging_ASSESSMENT/english_familiar_words": request.POST.get('english_familiar_words'),
            "Bridging_ASSESSMENT/english_reading_comprehension": request.POST.get('english_reading_comprehension'),

            "Bridging_ASSESSMENT/french_alphabet_knowledge": request.POST.get('french_alphabet_knowledge'),
            "Bridging_ASSESSMENT/french_familiar_words": request.POST.get('french_familiar_words'),
            "Bridging_ASSESSMENT/french_reading_comprehension": request.POST.get('french_reading_comprehension'),
            "Bridging_ASSESSMENT/math": request.POST.get('math'),
            "Bridging_ASSESSMENT/exam3": request.POST.get('exam3')
                # "Bridging_ASSESSMENT/social_emotional": request.POST.get('social_emotional'),
                # "Bridging_ASSESSMENT/artistic": request.POST.get('artistic'),
            }

        instance.save()
        messages.success(request, _('Your data has been sent successfully to the server'))

    class Meta:
        model = Bridging
        fields = (
            'participation',
            'barriers_single',
            'barriers_other',
            'test_done',
            'round_complete',
            'learning_result',
            'learning_result_other',
            'dropout_reason',
            'dropout_date',
            'referral_school',
            'referral_school_type',
            'community_Liaison_follow_up',
            'community_liaison_specify',
        )


class BridgingMidAssessmentForm(forms.ModelForm):
    REGISTRATION_LEVEL = (
        ('', '----------'),
        ('level_one', _('Level one')),
        ('level_two', _('Level two')),
        ('level_three', _('Level three')),
        ('level_four', _('Level four')),
        ('level_five', _('Level five')),
        ('level_six', _('Level six'))
    )
    mid_test_done = forms.ChoiceField(
        label=_("Mid test has been done"),
        widget=forms.Select, required=True,
        choices=Bridging.YES_NO,
    )
    arabic_alphabet_knowledge = forms.FloatField(
        label=_('Arabic Alphabet Knowledge'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=False
    )
    arabic_familiar_words = forms.FloatField(
        label=_('Arabic Familiar words'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=False
    )
    arabic_reading_comprehension = forms.FloatField(
        label=_('Arabic Reading Comprehension'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=False
    )
    english_alphabet_knowledge = forms.FloatField(
        label=_('English Alphabet Knowledge'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=False
    )
    english_familiar_words = forms.FloatField(
        label=_('English Familiar words'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=False
    )
    english_reading_comprehension = forms.FloatField(
        label=_('English Reading Comprehension'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=False
    )
    french_alphabet_knowledge = forms.FloatField(
        label=_('French Alphabet Knowledge'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=False
    )
    french_familiar_words = forms.FloatField(
        label=_('French Familiar words'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=False
    )
    french_reading_comprehension = forms.FloatField(
        label=_('French Reading Comprehension'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=False
    )
    math = forms.FloatField(
        label=_('Math'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=False
    )
    exam2 = forms.FloatField(
        label=_('Exam 2'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=False
    )
    registration_level = forms.ChoiceField(
        label=_("Registration level"),
        widget=forms.Select, required=False,
        choices=REGISTRATION_LEVEL
    )
    language = forms.ChoiceField(
        label=_('The language supported in the program'),
        widget=forms.Select,
        choices=CLM.LANGUAGES, required=False,
        initial='english_arabic'
    )
    clm_type = forms.CharField(widget=forms.HiddenInput, required=False)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        number = kwargs.pop('number', None)
        super(BridgingMidAssessmentForm, self).__init__(*args, **kwargs)

        post_test = ''
        post_test_button = ' btn-outline-secondary disabled'
        instance = kwargs['instance'] if 'instance' in kwargs else ''
        self.fields['clm_type'].initial = 'Bridging'
        is_Kayany = False
        if self.request.user.partner:
            is_Kayany = self.request.user.partner.is_Kayany

        display_assessment = ''
        assessment_number = int(number)
        form_action = reverse('clm:bridging_mid_assessment', kwargs={'pk': instance.id, 'number': number})
        if not is_Kayany:
            header_text = 'Mid Test 1'
        else:
            header_text = 'Exam 2'

        if assessment_number == 1 and instance.post_test:
            post_test_button = ' btn-outline-success '
            post_test = instance.assessment_form(
                stage='post_test',
                assessment_slug='Bridging_post_test',
                callback=self.request.build_absolute_uri(
                    reverse('clm:bridging_mid_assessment', kwargs={'pk': instance.id, 'number': number}))
            )
        if assessment_number == 2 and instance.post_test:
            header_text = 'Mid Test 2'
            post_test_button = ' btn-outline-success '
            post_test = instance.assessment_form(
                stage='post_test',
                assessment_slug='Bridging_post_test',
                callback=self.request.build_absolute_uri(
                    reverse('clm:bridging_mid_assessment', kwargs={'pk': instance.id, 'number': number}))
            )

        self.helper = FormHelper()
        self.helper.form_show_labels = True
        self.helper.form_action = form_action
        if not is_Kayany:

            self.helper.layout = Layout(
                Div(
                    Div(
                        HTML('<h4 id="alternatives-to-hidden-labels">' + _(header_text) + '</h4>'),
                        css_class='row card-body',
                    ),
                    Div(
                        Div('registration_level', css_class='col-md-3 d-none'),
                        Div('language', css_class='col-md-3 d-none'),
                        css_class='row card-body',
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">1</span>'),
                        Div('mid_test_done', css_class='col-md-3'),
                        css_class='row card-body',
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill" id="span_arabic">2</span>'),
                        Div('arabic_alphabet_knowledge', css_class='col-md-3'),
                        Div('arabic_familiar_words', css_class='col-md-3'),
                        Div('arabic_reading_comprehension', css_class='col-md-3'),
                        css_class='row grades card-body',
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill" id="span_english">3</span>'),
                        Div('english_alphabet_knowledge', css_class='col-md-3'),
                        Div('english_familiar_words', css_class='col-md-3'),
                        Div('english_reading_comprehension', css_class='col-md-3'),
                        css_class='row grades card-body',
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill" id="span_french">4</span>'),
                        Div('french_alphabet_knowledge', css_class='col-md-3'),
                        Div('french_familiar_words', css_class='col-md-3'),
                        Div('french_reading_comprehension', css_class='col-md-3'),
                        css_class='row grades card-body',
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill" id="span_math">5</span>'),
                        Div('math', css_class='col-md-3'),
                        css_class='row grades card-body',
                    ),
                    FormActions(
                        Submit('save', 'Save',
                               css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-success'),
                        Reset('reset', 'Reset',
                              css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-warning'),
                    )
                )
            )

        else:
            self.helper.layout = Layout(
                Div(
                    Div(
                        HTML('<h4 id="alternatives-to-hidden-labels">' + _(header_text) + '</h4>'),
                        css_class='row card-body',
                    ),
                    Div(
                        Div('registration_level', css_class='col-md-3 d-none'),
                        Div('language', css_class='col-md-3 d-none'),
                        css_class='row card-body',
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill">1</span>'),
                        Div('mid_test_done', css_class='col-md-3'),
                        css_class='row card-body',
                    ),
                    Div(
                        HTML('<span class="badge-form badge-pill" id="span_exam2">2</span>'),
                        Div('exam2', css_class='col-md-3'),
                        css_class='row grades card-body',
                    ),
                    FormActions(
                        Submit('save', 'Save',
                               css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-success'),
                        Reset('reset', 'Reset',
                              css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-warning'),
                    )
                )
            )

    def clean(self):
        cleaned_data = super(BridgingMidAssessmentForm, self).clean()

        mid_test_done = cleaned_data.get("mid_test_done")

        if mid_test_done == 'yes':
            # grades Max Value validation
            registration_level = cleaned_data.get("registration_level")
            language = cleaned_data.get("language")

            if self.request.user.partner and not self.request.user.partner.is_Kayany:
                arabic_alphabet_knowledge = cleaned_data.get("arabic_alphabet_knowledge")
                arabic_familiar_words = cleaned_data.get("arabic_familiar_words")
                arabic_reading_comprehension = cleaned_data.get("arabic_reading_comprehension")

                english_alphabet_knowledge = cleaned_data.get("english_alphabet_knowledge")
                english_familiar_words = cleaned_data.get("english_familiar_words")
                english_reading_comprehension = cleaned_data.get("english_reading_comprehension")

                french_alphabet_knowledge = cleaned_data.get("french_alphabet_knowledge")
                french_familiar_words = cleaned_data.get("french_familiar_words")
                french_reading_comprehension = cleaned_data.get("french_reading_comprehension")

                math = cleaned_data.get("math")

                if arabic_alphabet_knowledge is None:
                    self.add_error('arabic_alphabet_knowledge', 'This field is required')
                elif arabic_alphabet_knowledge > 48:
                    self.add_error('arabic_alphabet_knowledge', 'This value is greater that 48')

                if arabic_familiar_words is None:
                    self.add_error('arabic_familiar_words', 'This field is required')
                elif arabic_familiar_words > 20:
                    self.add_error('arabic_familiar_words', 'This value is greater that 20')

                if arabic_reading_comprehension is None:
                    self.add_error('arabic_reading_comprehension', 'This field is required')
                elif arabic_reading_comprehension > 10:
                    self.add_error('arabic_reading_comprehension', 'This value is greater that 10')

                if language == 'english_arabic':
                    if english_alphabet_knowledge is None:
                        self.add_error('english_alphabet_knowledge', 'This field is required')
                    elif english_alphabet_knowledge > 48:
                        self.add_error('english_alphabet_knowledge', 'This value is greater that 48')

                    if english_familiar_words is None:
                        self.add_error('english_familiar_words', 'This field is required')
                    elif english_familiar_words > 20:
                        self.add_error('english_familiar_words', 'This value is greater that 20')

                    if english_reading_comprehension is None:
                        self.add_error('english_reading_comprehension', 'This field is required')
                    elif english_reading_comprehension > 10:
                        self.add_error('english_reading_comprehension', 'This value is greater that 10')

                elif language == 'french_arabic':
                    if french_alphabet_knowledge is None:
                        self.add_error('french_alphabet_knowledge', 'This field is required')
                    elif french_alphabet_knowledge > 48:
                        self.add_error('french_alphabet_knowledge', 'This value is greater that 48')

                    if french_familiar_words is None:
                        self.add_error('french_familiar_words', 'This field is required')
                    elif french_familiar_words > 20:
                        self.add_error('french_familiar_words', 'This value is greater that 20')

                    if french_reading_comprehension is None:
                        self.add_error('french_reading_comprehension', 'This field is required')
                    elif french_reading_comprehension > 10:
                        self.add_error('french_reading_comprehension', 'This value is greater that 10')

                if math is None:
                    self.add_error('math', 'This field is required')
                elif registration_level == 'level_one' and math > 50:
                    self.add_error('math', 'This value is greater that 50')
                elif registration_level == 'level_two' and math > 88:
                    self.add_error('math', 'This value is greater that 88')
                elif math > 103:
                    self.add_error('math', 'This value is greater that 103')
            else:
                exam2 = cleaned_data.get("exam2")
                if exam2 is None:
                    self.add_error('exam2', 'This field is required')
                elif exam2 > 20:
                    self.add_error('exam2', 'This value is greater that 20')

    def save(self, instance=None, request=None, number=None):
        instance = super(BridgingMidAssessmentForm, self).save()
        instance.modified_by = request.user

        assessment_number = int(number)
        if assessment_number == 1 and request.POST.get('mid_test_done') == 'yes':
            instance.mid_test1 = {
                "Bridging_ASSESSMENT/mid_test_done": request.POST.get('mid_test_done'),
                "Bridging_ASSESSMENT/arabic_alphabet_knowledge": request.POST.get('arabic_alphabet_knowledge'),
                "Bridging_ASSESSMENT/arabic_familiar_words": request.POST.get('arabic_familiar_words'),
                "Bridging_ASSESSMENT/arabic_reading_comprehension": request.POST.get('arabic_reading_comprehension'),

                "Bridging_ASSESSMENT/english_alphabet_knowledge": request.POST.get('english_alphabet_knowledge'),
                "Bridging_ASSESSMENT/english_familiar_words": request.POST.get('english_familiar_words'),
                "Bridging_ASSESSMENT/english_reading_comprehension": request.POST.get('english_reading_comprehension'),

                "Bridging_ASSESSMENT/french_alphabet_knowledge": request.POST.get('french_alphabet_knowledge'),
                "Bridging_ASSESSMENT/french_familiar_words": request.POST.get('french_familiar_words'),
                "Bridging_ASSESSMENT/french_reading_comprehension": request.POST.get('french_reading_comprehension'),
                "Bridging_ASSESSMENT/math": request.POST.get('math'),
                "Bridging_ASSESSMENT/exam2": request.POST.get('exam2'),
            }
        elif assessment_number == 2 and request.POST.get('mid_test_done') == 'yes':
            instance.mid_test2 = {
                "Bridging_ASSESSMENT/mid_test_done": request.POST.get('mid_test_done'),

                "Bridging_ASSESSMENT/arabic_alphabet_knowledge": request.POST.get('arabic_alphabet_knowledge'),
                "Bridging_ASSESSMENT/arabic_familiar_words": request.POST.get('arabic_familiar_words'),
                "Bridging_ASSESSMENT/arabic_reading_comprehension": request.POST.get('arabic_reading_comprehension'),

                "Bridging_ASSESSMENT/english_alphabet_knowledge": request.POST.get('english_alphabet_knowledge'),
                "Bridging_ASSESSMENT/english_familiar_words": request.POST.get('english_familiar_words'),
                "Bridging_ASSESSMENT/english_reading_comprehension": request.POST.get('english_reading_comprehension'),

                "Bridging_ASSESSMENT/french_alphabet_knowledge": request.POST.get('french_alphabet_knowledge'),
                "Bridging_ASSESSMENT/french_familiar_words": request.POST.get('french_familiar_words'),
                "Bridging_ASSESSMENT/french_reading_comprehension": request.POST.get('french_reading_comprehension'),
                "Bridging_ASSESSMENT/math": request.POST.get('math'),
                "Bridging_ASSESSMENT/exam2": request.POST.get('exam2'),
            }
        else:
            instance.mid_test1 = {
                "Bridging_ASSESSMENT/mid_test_done": 'no'
            }
            instance.mid_test2 = {
                "Bridging_ASSESSMENT/mid_test_done": 'no'
            }

        instance.save()
        messages.success(request, _('Your data has been sent successfully to the server'))

    class Meta:
        model = Bridging
        fields = (
        )


class BridgingServiceForm(forms.ModelForm):
    receiving_social_assistance = forms.ChoiceField(
        label=_("Is the child receiving social assistance?"),
        widget=forms.Select, required=True,
        choices=CLM.YES_NO
    )
    receiving_transportation_support = forms.ChoiceField(
        label=_("Is the Child Receiving Transportation Support?"),
        widget=forms.Select, required=True,
        choices=CLM.YES_NO
    )
    using_digital_platform = forms.ChoiceField(
        label=_("Is the Child Using a digital platform (Akelius or  Learning Passport)"),
        widget=forms.Select, required=True,
        choices=(
            ('', '----------'),
            ('yes_akelius)', _("Yes (Akelius)")),
            ('yes_learning_passport)', _("Yes (Learning Passport)")),
            ('no', _("No"))
        )
    )
    basic_stationery = forms.ChoiceField(
        label=_("Did the child receive basic stationery?"),
        widget=forms.Select, required=True,
        choices=CLM.YES_NO
    )
    cp_referral = forms.ChoiceField(
        label=_("CP Followup"),
        widget=forms.Select, required=True,
        choices=(
            ('', '----------'),
            ('yes', _("Yes")),
            ('no', _("No")))
    )
    referal_health = forms.ChoiceField(
        label=_("Referral health"),
        widget=forms.Select, required=True,
        choices=CLM.YES_NO
    )
    referal_wash = forms.ChoiceField(
        label=_("Referral wash"),
        widget=forms.Select, required=True,
        choices=CLM.YES_NO
    )
    referal_other = forms.ChoiceField(
        label=_("Referral other"),
        widget=forms.Select, required=True,
        choices=CLM.YES_NO
    )
    referal_other_specify = forms.CharField(
        label=_('Please specify'),
        widget=forms.TextInput, required=False
    )

    child_received_internet = forms.ChoiceField(
        label=_("child received internet"),
        widget=forms.Select, required=False,
        choices=CLM.YES_NO
    )

    clm_type = forms.CharField(widget=forms.HiddenInput, required=False)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(BridgingServiceForm, self).__init__(*args, **kwargs)

        instance = kwargs['instance'] if 'instance' in kwargs else ''
        self.fields['clm_type'].initial = 'Bridging'

        form_action = reverse('clm:bridging_service', kwargs={'pk': instance.id})

        self.helper = FormHelper()
        self.helper.form_show_labels = True
        self.helper.form_action = form_action
        self.helper.layout = Layout(
            Div(
                Div(
                    HTML('<span class="badge-form badge-pill">1</span>'),
                    Div('receiving_social_assistance', css_class='col-md-4'),
                    HTML('<span class="badge-form badge-pill">2</span>'),
                    Div('receiving_transportation_support', css_class='col-md-4'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<span class="badge-form badge-pill">3</span>'),
                    Div('using_digital_platform', css_class='col-md-4'),
                    HTML('<span class="badge-form badge-pill">4</span>'),
                    Div('basic_stationery', css_class='col-md-4'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<span class="badge-form badge-pill">5</span>'),
                    Div('cp_referral', css_class='col-md-4'),
                    HTML('<span class="badge-form badge-pill">6</span>'),
                    Div('referal_wash', css_class='col-md-4'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<span class="badge-form badge-pill">7</span>'),
                    Div('referal_health', css_class='col-md-4 '),
                    HTML('<span class="badge-form badge-pill">8</span>'),
                    Div('referal_other', css_class='col-md-4'),
                    HTML('<span class="badge-form badge-pill" id="span_referal_other_specify">9</span>'),
                    Div('referal_other_specify', css_class='col-md-2'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<span class="badge-form-2 badge-pill">10</span>'),
                    Div('child_received_internet', css_class='col-md-4'),
                    css_class='row d-none',
                ),
                FormActions(
                    Submit('save', 'Save',
                           css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-success'),
                    Reset('reset', 'Reset',
                          css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-warning'),
                )
            )
        )

    def clean(self):
        cleaned_data = super(BridgingServiceForm, self).clean()

        referal_other = cleaned_data.get("referal_other")
        referal_other_specify = cleaned_data.get("referal_other_specify")
        if referal_other == 'yes':
            if not referal_other_specify:
                self.add_error('referal_other_specify', 'This field is required')

    def save(self, instance=None, request=None):
        instance = super(BridgingServiceForm, self).save()
        # instance = super(BridgingAssessmentForm, self).save(request=request, instance=instance, serializer=BridgingSerializer)
        instance.modified_by = request.user
        instance.save()
        messages.success(request, _('Your data has been sent successfully to the server'))

    class Meta:
        model = Bridging
        fields = (
            'receiving_social_assistance',
            'receiving_transportation_support',
            'using_digital_platform',
            'basic_stationery',
            'cp_referral',
            'referal_wash',
            'referal_health',
            'referal_other',
            'referal_other_specify',
            'child_received_internet',
        )


class BridgingFollowupForm(forms.ModelForm):

    phone_call_number = forms.IntegerField(
        label=_('Please enter the number phone calls'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=False
    )
    house_visit_number = forms.IntegerField(
        label=_('Please enter the number of house visits'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=False
    )
    family_visit_number = forms.IntegerField(
        label=_('Please enter the number parent visits'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=False
    )
    phone_call_follow_up_result = forms.ChoiceField(
        label=_('Result of follow up'),
        widget=forms.Select, required=False,
        choices=(
            ('child back', _('Child returned to Round')),
            ('child transfer to difficulty center', _('Child referred to specialized services')),
            ('child transfer to protection', _('Child referred to protection')),
            ('child transfer to medical', _('Child referred to Health programme')),
            ('Intensive followup', _('Follow-up with parents')),
            ('dropout', _('Dropout/No Interest')),
        ),
        initial=''
    )
    house_visit_follow_up_result = forms.ChoiceField(
        label=_('Result of follow up'),
        widget=forms.Select, required=False,
        choices=(
            ('child back', _('Child returned to Round')),
            ('child transfer to difficulty center', _('Child referred to specialized services')),
            ('child transfer to protection', _('Child referred to protection')),
            ('child transfer to medical', _('Child referred to Health programme')),
            ('Intensive followup', _('Follow-up with parents')),
            ('dropout', _('Dropout/No Interest')),
        ),
        initial=''
    )
    family_visit_follow_up_result = forms.ChoiceField(
        label=_('Result of follow up'),
        widget=forms.Select, required=False,
        choices=(
            ('child back', _('Child returned to Round')),
            ('child transfer to difficulty center', _('Child referred to specialized services')),
            ('child transfer to protection', _('Child referred to protection')),
            ('child transfer to medical', _('Child referred to Health programme')),
            ('Intensive followup', _('Follow-up with parents')),
            ('dropout', _('Dropout/No Interest')),
        ),
        initial=''
    )
    parent_attended_visits = forms.ChoiceField(
        label=_("Parents attended parents meeting"),
        widget=forms.Select, required=False,
        choices=(('yes', _("Yes")), ('no', _("No"))),
        initial='yes'
    )
    pss_session_attended = forms.ChoiceField(
        label=_("Attended PSS Session"),
        widget=forms.Select, required=True,
        choices=(('yes', _("Yes")), ('no', _("No")))
    )
    pss_session_number = forms.IntegerField(
        label=_('Please enter the number of sessions'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=False
    )
    pss_session_modality = forms.MultipleChoiceField(
        label=_('Please indicate modality'),
        choices=CLM.SESSION_MODALITY,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    pss_parent_attended = forms.ChoiceField(
        label=_("Parent who attended the parents meeting"),
        widget=forms.Select, required=False,
        choices=(
            ('', '----------'),
            ('mother', _('Mother')),
            ('father', _('Father')),
            ('other', _('Other')),
        )
    )
    pss_parent_attended_other = forms.CharField(
        label=_('Please specify'),
        widget=forms.TextInput, required=False
    )
    covid_session_attended = forms.ChoiceField(
        label=_("Attended covid Session"),
        widget=forms.Select, required=False,
        choices=(('yes', _("Yes")), ('no', _("No")))
    )
    covid_session_number = forms.IntegerField(
        label=_('Please enter the number of sessions'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=False
    )
    covid_session_modality = forms.MultipleChoiceField(
        label=_('Please indicate modality'),
        choices=CLM.SESSION_MODALITY,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    covid_parent_attended = forms.ChoiceField(
        label=_("Parent who attended the parents meeting"),
        widget=forms.Select, required=False,
        choices=(
            ('', '----------'),
            ('mother', _('Mother')),
            ('father', _('Father')),
            ('other', _('Other')),
        )
    )
    covid_parent_attended_other = forms.CharField(
        label=_('Please specify'),
        widget=forms.TextInput, required=False
    )
    followup_session_attended = forms.ChoiceField(
        label=_("Attended followup Session"),
        widget=forms.Select, required=True,
        choices=(('yes', _("Yes")), ('no', _("No")))
    )
    followup_session_number = forms.IntegerField(
        label=_('Please enter the number of sessions'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        min_value=0, required=False
    )

    followup_session_modality = forms.MultipleChoiceField(
        label=_('Please indicate modality'),
        choices=CLM.SESSION_MODALITY,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    followup_parent_attended = forms.ChoiceField(
        label=_("Parent who attended the parents meeting"),
        widget=forms.Select, required=False,
        choices=(
            ('', '----------'),
            ('mother', _('Mother')),
            ('father', _('Father')),
            ('other', _('Other')),
        )
    )
    followup_parent_attended_other = forms.CharField(
        label=_('Please specify'),
        widget=forms.TextInput, required=False
    )
    school_contacted_caretaker = forms.ChoiceField(
        label=_("Have the child caregivers been contacted by the School Community Laison"),
        widget=forms.Select, required=True,
        choices=(('yes', _("Yes")), ('no', _("No")))
    )
    discussion_topic = forms.CharField(
        label=_('Please specify what has been discussed'),
        widget=forms.TextInput, required=False
    )

    clm_type = forms.CharField(widget=forms.HiddenInput, required=False)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(BridgingFollowupForm, self).__init__(*args, **kwargs)

        post_test = ''
        post_test_button = ' btn-outline-secondary disabled'
        instance = kwargs['instance'] if 'instance' in kwargs else ''
        self.fields['clm_type'].initial = 'Bridging'

        display_followup = ''
        form_action = reverse('clm:bridging_followup', kwargs={'pk': instance.id})

        if instance.post_test:
            followup_button = ' btn-outline-success '
            followup = instance.assessment_form(
                stage='followup',
                assessment_slug='bridging_followup',
                callback=self.request.build_absolute_uri(
                    reverse('clm:bridging_followup', kwargs={'pk': instance.id}))
            )

        self.helper = FormHelper()
        self.helper.form_show_labels = True
        self.helper.form_action = form_action
        self.helper.layout = Layout(
            Div(
                Div(
                    HTML('<span class="badge-form badge-pill">1</span>'),
                    Div('phone_call_number', css_class='col-md-3'),
                    HTML('<span class="badge-form badge-pill">2</span>'),
                    Div('phone_call_follow_up_result', css_class='col-md-3'),
                    css_class='row card-body'
                ),
                Div(
                    HTML('<span class="badge-form badge-pill">3</span>'),
                    Div('house_visit_number', css_class='col-md-3'),
                    HTML('<span class="badge-form badge-pill">4</span>'),
                    Div('house_visit_follow_up_result', css_class='col-md-3'),
                    css_class='row card-body'
                ),
                Div(
                    HTML('<span class="badge-form badge-pill">5</span>'),
                    Div('family_visit_number', css_class='col-md-3'),
                    HTML('<span class="badge-form badge-pill">6</span>'),
                    Div('family_visit_follow_up_result', css_class='col-md-3'),
                    css_class='row card-body'
                ),
                # css_id='follow_up step-1',
                css_id='step-1',
            ),
            Div(
                Div(
                    HTML('<span class="badge-form badge-pill">1</span>'),
                    Div('parent_attended_visits', css_class='col-md-3'),
                    # HTML('<span class="badge-form-2 badge-pill">2</span>'),
                    # Div('visits_number', css_class='col-md-4'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<span class="badge-form badge-pill">2</span>'),
                    Div('pss_session_attended', css_class='col-md-2'),
                    HTML('<span class="badge-form badge-pill" id="span_pss_session_modality">3</span>'),
                    Div('pss_session_modality', css_class='col-md-2 multiple-checbkoxes'),
                    HTML('<span class="badge-form badge-pill" id="span_pss_session_number">4</span>'),
                    Div('pss_session_number', css_class='col-md-2'),
                    HTML('<span class="badge-form badge-pill" id="span_pss_parent_attended">5</span>'),
                    Div('pss_parent_attended', css_class='col-md-2'),
                    HTML('<span class="badge-form badge-pill" id="span_pss_parent_attended_other">6</span>'),
                    Div('pss_parent_attended_other', css_class='col-md-2'),
                    css_class='row parent_visits card-body',
                ),
                Div(
                    HTML('<span class="badge-form badge-pill">7</span>'),
                    Div('covid_session_attended', css_class='col-md-2'),
                    HTML('<span class="badge-form badge-pill" id="span_covid_session_modality">8</span>'),
                    Div('covid_session_modality', css_class='col-md-2 multiple-checbkoxes'),
                    HTML('<span class="badge-form badge-pill" id="span_covid_session_number">9</span>'),
                    Div('covid_session_number', css_class='col-md-2'),
                    HTML('<span class="badge-form-2 badge-pill" id="span_covid_parent_attended">10</span>'),
                    Div('covid_parent_attended', css_class='col-md-2'),
                    HTML('<span class="badge-form-2 badge-pill" id="span_covid_parent_attended_other">11</span>'),
                    Div('covid_parent_attended_other', css_class='col-md-2'),
                    css_class='row d-none card-body',
                ),
                Div(
                    HTML('<span class="badge-form-2 badge-pill">12</span>'),
                    Div('followup_session_attended', css_class='col-md-2'),
                    HTML('<span class="badge-form-2 badge-pill" id="span_followup_session_modality">13</span>'),
                    Div('followup_session_modality', css_class='col-md-2 multiple-checbkoxes'),
                    HTML('<span class="badge-form-2 badge-pill" id="span_followup_session_number">14</span>'),
                    Div('followup_session_number', css_class='col-md-2'),
                    HTML('<span class="badge-form-2 badge-pill" id="span_followup_parent_attended">15</span>'),
                    Div('followup_parent_attended', css_class='col-md-2'),
                    HTML('<span class="badge-form-2 badge-pill" id="span_followup_parent_attended_other">16</span>'),
                    Div('followup_parent_attended_other', css_class='col-md-2'),
                    css_class='row parent_visits card-body',
                ),
                Div(
                    HTML('<span class="badge-form-2 badge-pill">17</span>'),
                    Div('school_contacted_caretaker', css_class='col-md-4'),
                    HTML('<span class="badge-form-2 badge-pill" id= "span_discussion_topic">18</span>'),
                    Div('discussion_topic', css_class='col-md-4'),
                    css_class='row card-body',
                ),
                # Div(
                #     HTML('<span class="badge-form-2 badge-pill">4</span>'),
                #     Div('child_health_examed', css_class='col-md-4'),
                #     HTML('<span class="badge-form-2 badge-pill">5</span>'),
                #     Div('child_health_concern', css_class='col-md-4'),
                #     css_class='row card-body',
                # ),
                FormActions(
                    Submit('save', 'Save',
                           css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-success'),
                    Reset('reset', 'Reset',
                          css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-warning'),
                ),
                # css_id='visits step-2',
                css_id='step-2',
            )
        )

    def clean(self):
        cleaned_data = super(BridgingFollowupForm, self).clean()

    def save(self, instance=None, request=None):
        instance = super(BridgingFollowupForm, self).save()
        # instance = super(BridgingFollowupForm, self).save(request=request, instance=instance, serializer=BridgingSerializer)

        instance.modified_by = request.user
        instance.save()
        messages.success(request, _('Your data has been sent successfully to the server'))

    class Meta:
        model = Bridging
        fields = (
            'phone_call_number',
            'house_visit_number',
            'family_visit_number',
            'phone_call_follow_up_result' ,
            'house_visit_follow_up_result' ,
            'family_visit_follow_up_result' ,
            'parent_attended_visits',
            'pss_session_attended',
            'pss_session_number',
            'pss_session_modality',
            'pss_parent_attended',
            'pss_parent_attended_other',
            'covid_session_attended',
            'covid_session_number',
            'covid_session_modality',
            'covid_parent_attended',
            'covid_parent_attended_other',
            'followup_session_attended',
            'followup_session_number',
            'followup_session_modality',
            'followup_parent_attended_other',
            'followup_parent_attended',
            'school_contacted_caretaker',
            'discussion_topic',
            # 'child_health_examed',
            # 'child_health_concern',
        )


class InclusionAdminForm(forms.ModelForm):

    student = forms.ModelChoiceField(
        queryset=Student.objects.all(),
        widget=autocomplete.ModelSelect2(url='student_autocomplete')
    )

    def __init__(self, *args, **kwargs):
        super(InclusionAdminForm, self).__init__(*args, **kwargs)

    class Meta:
        model = BLN
        fields = '__all__'

