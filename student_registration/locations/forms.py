from __future__ import unicode_literals, absolute_import, division

from student_registration.users.templatetags.custom_tags import has_group
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

from django.forms.widgets import ClearableFileInput
from student_registration.locations.models import Location
from .models import (
    Center,
    ProgramStaff
)
from student_registration.schools.models import PartnerOrganization


class CustomClearableFileInput(ClearableFileInput):
    template_name = 'staff/clearable_file_input.html'


class CenterAdminForm(forms.ModelForm):
    name = forms.CharField(
        label=_("Center name"),
        widget=forms.TextInput, required=True
    )
    partner = forms.ModelChoiceField(
        queryset=PartnerOrganization.objects.all(),
        widget=forms.Select,
        label=_('Partner'),
        empty_label='-------',
        required=True,
        to_field_name='id',
    )
    governorate = forms.ModelChoiceField(
        queryset=Location.objects.filter(parent__isnull=True),
        widget=forms.Select,
        label=_('Governorate'),
        empty_label='-------',
        required=True,
        to_field_name='id',
    )
    type = forms.ChoiceField(
        label=_('Type'),
        widget=forms.Select, required=True,
        choices=(
            ('', '----------'),
            ('Municipality', _('Municipality')),
            ('Collective Settlement', _('Collective Settlement')),
            ('Informal Settlement', _('Informal Settlement')),
            ('Welfare Center', _('Welfare Center')),
            ('Community Hub', _('Community Hub')),
        ),
        initial=''
    )
    provided_packages = forms.MultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple,
        choices= Center.PROVIDED_PACKAGES,
    )
    is_active = forms.BooleanField(
        label="Is the center active?",
        required=False,
        initial=True
    )

    def __init__(self, *args, **kwargs):
        super(CenterAdminForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Center
        fields = (
            'name',
            'partner',
            'governorate',
            'type',
            'provided_packages',
            'is_active'
        )


class CenterForm(forms.ModelForm):
    name = forms.CharField(
        label=_("Center name"),
        widget=forms.TextInput,
        required = False
    )
    governorate = forms.ModelChoiceField(
        queryset=Location.objects.filter(parent__isnull=True),
        widget=forms.Select,
        label=_('Governorate'),
        empty_label='-------',
        required=True,
        to_field_name='id',
    )
    caza = forms.ModelChoiceField(
        queryset=Location.objects.filter(parent__isnull=False, type=2),
        widget=forms.Select,
        label=_('Caza'),
        empty_label='-------',
        required=True,
        to_field_name='id',
    )
    cadaster = forms.ModelChoiceField(
        required=True,
        queryset=Location.objects.filter(parent__isnull=False, type=3),
        widget=autocomplete.ModelSelect2(url='location_autocomplete'),
        label=_('Cadaster')
    )
    longitude = forms.FloatField(
        label=_('Center GPS (longitude)'),
        widget=forms.NumberInput(attrs=({'maxlength': 12})),
        min_value=0, required=True
    )
    latitude = forms.FloatField(
        label=_('Center GPS (latitude)'),
        widget=forms.NumberInput(attrs=({'maxlength': 12})),
        min_value=0, required=True
    )
    manager_name = forms.CharField(
        label=_("Center Manager name"),
        widget=forms.TextInput, required=True
    )
    phone_number = forms.RegexField(
        regex=r'^\d{2}-\d{6}$',
        widget=forms.TextInput(attrs={'placeholder': 'Format: XX-XXXXXX'}),
        required=True,
        label=_('Phone number')
    )
    email = forms.RegexField(
        regex=r'^\b[\w\.-]+@[\w\.-]+\.\w{2,4}\b',
        required=False,
        label=_('Email')
    )
    type = forms.ChoiceField(
        label=_('Type'),
        widget=forms.Select, required=True,
        choices=Center.TYPE,
        initial=''
    )
    provided_packages = forms.MultipleChoiceField(
        label=_('Provided Services'),
        required=True,
        widget=forms.CheckboxSelectMultiple,
        choices=Center.PROVIDED_PACKAGES
    )
    programs = forms.MultipleChoiceField(
        label=_('Education Program'),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        choices=Center.PROGRAM
    )
    cwd_accessible = forms.ChoiceField(
        label=_("Is the center accessible for CWD ?"),
        widget=forms.Select, required=False,
        choices=Center.YES_NO,
    )
    admin_staff_number = forms.IntegerField(
        label=_('Number of Admin staff in the center'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        required=True,
        initial=0,
        min_value=0
    )
    is_active = forms.ChoiceField(
        label=_("Is the center active?"),
        widget=forms.Select, required=True,
        choices=Center.TRUE_FALSE,
        initial=False
    )
    offer_digital_learning = forms.ChoiceField(
        label=_("Does the center offer digital learning services?"),
        widget=forms.Select, required=False,
        choices=Center.YES_NO,
    )
    have_digital_hub = forms.ChoiceField(
        label=_("Does the center have a digital hub?"),
        widget=forms.Select, required=False,
        choices=Center.YES_NO,
    )
    neaby_phcc = forms.CharField(
        label=_("Nearby PHCC name"),
        widget=forms.TextInput, required=True
    )
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        pk = kwargs.pop('pk', None)
        super(CenterForm, self).__init__(*args, **kwargs)
        form_action = reverse('locations:center_add')

        if pk:
            form_action = reverse('locations:center_edit', kwargs={'pk': pk})

        self.helper = FormHelper()
        self.helper.form_show_labels = True
        self.helper.form_action = form_action
        self.helper.layout = Layout(
            Div(
                Div(
                    HTML('<span class="badge-form badge-pill">1</span>'),
                    Div('name', css_class='col-md-3 disabled-input'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<span class="badge-form badge-pill">2</span>'),
                    Div('governorate', css_class='col-md-3'),
                    HTML('<span class="badge-form badge-pill">3</span>'),
                    Div('caza', css_class='col-md-3'),
                    HTML('<span class="badge-form badge-pill">4</span>'),
                    Div('cadaster', css_class='col-md-3'),
                    css_class='row card-body',
                ),
                Div(

                    HTML('<span class="badge-form badge-pill">5</span>'),
                    Div('longitude', css_class='col-md-3'),
                    HTML('<span class="badge-form badge-pill">6</span>'),
                    Div('latitude', css_class='col-md-3'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<span class="badge-form badge-pill">7</span>'),
                    Div('manager_name', css_class='col-md-3'),
                    HTML('<span class="badge-form badge-pill">8</span>'),
                    Div('phone_number', css_class='col-md-3'),
                    HTML('<span class="badge-form badge-pill">9</span>'),
                    Div('email', css_class='col-md-3'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<span class="badge-form-2 badge-pill">10</span>'),
                    Div('type', css_class='col-md-3'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<span class="badge-form-2 badge-pill">11</span>'),
                    Div('provided_packages', css_class='col-md-3  multiple-choice'),
                    HTML('<span class="badge-form-2 badge-pill">12</span>'),
                    Div('programs', css_class='col-md-3  multiple-choice'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<span class="badge-form-2 badge-pill">13</span>'),
                    Div('cwd_accessible', css_class='col-md-3'),
                    HTML('<span class="badge-form-2 badge-pill">14</span>'),
                    Div('admin_staff_number', css_class='col-md-3'),
                    css_class='row card-body',
                ),

                Div(
                    HTML('<span class="badge-form-2 badge-pill">15</span>'),
                    Div('offer_digital_learning', css_class='col-md-3'),
                    HTML('<span class="badge-form-2 badge-pill">16</span>'),
                    Div('have_digital_hub', css_class='col-md-3'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<span class="badge-form-2 badge-pill">17</span>'),
                    Div('neaby_phcc', css_class='col-md-3'),
                    HTML('<span class="badge-form-2 badge-pill">18</span>'),
                    Div('is_active', css_class='col-md-3'),
                    css_class='row card-body',
                ),
                FormActions(
                    Submit('save', 'Save',
                           css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-success'),
                    Reset('reset', 'Reset',
                          css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-warning'),

                ),
                css_id='step-1',
            ),
        )

    def save(self, request=None, instance=None):
        validated_data = request.POST

        if not instance:
            instance = Center.objects.create()
        else:
            instance = Center.objects.get(id=instance)


        instance.governorate_id = validated_data.get('governorate')
        instance.caza_id = validated_data.get('caza')
        instance.cadaster_id = validated_data.get('cadaster')
        instance.longitude = validated_data.get('longitude')
        instance.latitude = validated_data.get('latitude')
        instance.manager_name = validated_data.get('manager_name')
        instance.phone_number = validated_data.get('phone_number')
        instance.email = validated_data.get('email')
        instance.type = validated_data.get('type')
        instance.provided_packages = validated_data.getlist('provided_packages')
        instance.programs = validated_data.getlist('programs')
        instance.cwd_accessible = validated_data.get('cwd_accessible')
        if validated_data.get('admin_staff_number'):
            instance.admin_staff_number = validated_data.get('admin_staff_number')
        else:
            instance.admin_staff_number = 0
        instance.is_active = validated_data.get('is_active')
        instance.modified_by = request.user
        instance.offer_digital_learning = validated_data.get('offer_digital_learning')
        instance.have_digital_hub = validated_data.get('have_digital_hub')
        instance.neaby_phcc = validated_data.get('neaby_phcc')

        instance.save()

        messages.success(request, _('Your data has been sent successfully to the server'))
        return instance
    class Meta:
        model = Center
        fields = (
            'name',
            'governorate',
            'caza',
            'cadaster',
            'longitude',
            'latitude',
            'manager_name',
            'phone_number',
            'email',
            'type',
            'provided_packages',
            'programs',
            'cwd_accessible',
            'admin_staff_number',
            'is_active',
            'offer_digital_learning',
            'have_digital_hub',
            'neaby_phcc'
        )


class ProgramStaffForm(forms.ModelForm):

    facilitator_name = forms.CharField(
        label=_("Facilitator Name"),
        widget=forms.TextInput,
        required=True
    )
    gender = forms.ChoiceField(
        label=_('Gender'),
        widget=forms.Select, required=True,
        choices=ProgramStaff.GENDER,
        initial=''
    )
    phone_number = forms.RegexField(
        regex=r'^\d{2}-\d{6}$',
        widget=forms.TextInput(attrs={'placeholder': 'Format: XX-XXXXXX'}),
        required=True,
        label=_('Phone number')
    )
    email = forms.RegexField(
        regex=r'^\b[\w\.-]+@[\w\.-]+\.\w{2,4}\b',
        required=False,
        label=_('Email')
    )
    subject = forms.MultipleChoiceField(
        label=_('Subject'),
        required=True,
        widget=forms.CheckboxSelectMultiple,
        choices=ProgramStaff.SUBJECT
    )
    programs = forms.MultipleChoiceField(
        label=_('Program'),
        required=True,
        widget=forms.CheckboxSelectMultiple,
        choices=ProgramStaff.PROGRAM
    )
    weekly_hours_taught = forms.IntegerField(
        label=_('Number of Hours Taught Per Week'),
        widget=forms.NumberInput(attrs=({'maxlength': 4})),
        required=False,
        initial=0,
        min_value=0
    )
    attendance_training = forms.ChoiceField(
        label=_("Facilitator Attendance to training ?"),
        widget=forms.Select, required=False,
        choices=Center.YES_NO,
    )
    training_topics = forms.MultipleChoiceField(
        label=_('Topics of facilitator training'),
        required=True,
        widget=forms.CheckboxSelectMultiple,
        choices=ProgramStaff.TOPICS
    )
    attach_cv = forms.FileField(
        label=_("CV"),
        required=False,
        widget=CustomClearableFileInput
    )
    attach_diploma = forms.FileField(
        label=_("Diploma"),
        required=False,
        widget=CustomClearableFileInput
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        center_id = kwargs.pop('center_id', None)
        pk = kwargs.pop('pk', None)
        super(ProgramStaffForm, self).__init__(*args, **kwargs)
        form_action = reverse('locations:program_staff_add',  kwargs={'center_id': center_id})

        if pk:
            form_action = reverse('locations:program_staff_edit',  kwargs={'center_id': center_id, 'pk': pk})

        self.helper = FormHelper()
        self.helper.form_show_labels = True
        self.helper.form_action = form_action
        self.helper.layout = Layout(
            Div(
                Div(
                    HTML('<span class="badge-form badge-pill">1</span>'),
                    Div('facilitator_name', css_class='col-md-3'),
                    HTML('<span class="badge-form badge-pill">2</span>'),
                    Div('gender', css_class='col-md-3'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<span class="badge-form badge-pill">3</span>'),
                    Div('phone_number', css_class='col-md-3'),
                    HTML('<span class="badge-form badge-pill">4</span>'),
                    Div('email', css_class='col-md-3'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<span class="badge-form-2 badge-pill">10</span>'),
                    Div('subject', css_class='col-md-3  multiple-choice'),
                    HTML('<span class="badge-form-2 badge-pill">11</span>'),
                    Div('programs', css_class='col-md-3  multiple-choice'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<span class="badge-form-2 badge-pill">13</span>'),
                    Div('weekly_hours_taught', css_class='col-md-3'),
                    HTML('<span class="badge-form-2 badge-pill">14</span>'),
                    Div('attendance_training', css_class='col-md-3'),
                    HTML('<span class="badge-form-2 badge-pill">14</span>'),
                    Div('training_topics', css_class='col-md-3  multiple-choice'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<span class="badge-form-2 badge-pill">13</span>'),
                    Div('attach_cv', css_class='col-md-3'),
                    HTML('<span class="badge-form-2 badge-pill">14</span>'),
                    Div('attach_diploma', css_class='col-md-3'),
                    css_class='row card-body',
                ),

                FormActions(
                    Submit('save', 'Save',
                           css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-success'),
                    Reset('reset', 'Reset',
                          css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-warning'),

                ),
                css_id='step-1',
            ),
        )

    def save(self, request=None, instance=None, center_id=None):
        validated_data = request.POST

        data = request.POST.copy()
        data.update(request.FILES)

        if not instance:
            instance = ProgramStaff.objects.create(center_id=center_id)
            instance.owner = request.user
        else:
            instance = ProgramStaff.objects.get(id=instance)

        instance.facilitator_name = validated_data.get('facilitator_name')
        instance.gender = validated_data.get('gender')
        instance.phone_number = validated_data.get('phone_number')
        instance.email = validated_data.get('email')
        instance.subject = validated_data.getlist('subject')
        instance.programs = validated_data.getlist('programs')
        weekly_hours = validated_data.get('weekly_hours_taught')
        weekly_hours_str = (weekly_hours or '').strip()
        instance.weekly_hours_taught = int(weekly_hours_str) if weekly_hours_str else 0
        instance.attendance_training = validated_data.get('attendance_training')
        instance.training_topics = validated_data.getlist('training_topics')
        attach_cv = request.FILES.get('attach_cv', False)
        if attach_cv:
            instance.attach_cv = attach_cv
        attach_diploma = request.FILES.get('attach_diploma', False)
        if attach_diploma:
            instance.attach_diploma = attach_diploma
        instance.modified_by = request.user

        instance.save()

        messages.success(request, _('Your data has been sent successfully to the server'))
        return instance

    class Meta:
        model = ProgramStaff
        fields = (
            'facilitator_name',
            'gender',
            'phone_number',
            'email',
            'subject',
            'programs',
            'weekly_hours_taught',
            'attendance_training',
            'training_topics',
            'attach_cv',
            'attach_diploma'
        )
