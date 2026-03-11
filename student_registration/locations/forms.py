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
from student_registration.locations.models import Location
from .models import (
    Center
)
from student_registration.schools.models import PartnerOrganization


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
        widget=forms.TextInput(attrs={'placeholder': _('e.g. Hope Community Center')}),
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
        widget=forms.NumberInput(attrs=({'maxlength': 12, 'placeholder': '35.xxxx'})),
        min_value=0, required=True
    )
    latitude = forms.FloatField(
        label=_('Center GPS (latitude)'),
        widget=forms.NumberInput(attrs=({'maxlength': 12, 'placeholder': '33.xxxx'})),
        min_value=0, required=True
    )
    manager_name = forms.CharField(
        label=_("Center Manager name"),
        widget=forms.TextInput(attrs={'placeholder': _('Full name of center manager')}), required=True
    )
    phone_number = forms.RegexField(
        regex=r'^\d{2}-\d{6}$',
        widget=forms.TextInput(attrs={'placeholder': 'Format: XX-XXXXXX (e.g. 01-123456)'}),
        required=True,
        label=_('Phone number'),
        help_text=_('Landline or official mobile number.')
    )
    email = forms.RegexField(
        regex=r'^\b[\w\.-]+@[\w\.-]+\.\w{2,4}\b',
        widget=forms.TextInput(attrs={'placeholder': _('center@example.com')}),
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
        widget=forms.NumberInput(attrs=({'maxlength': 4, 'placeholder': '0'})),
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
        widget=forms.TextInput(attrs={'placeholder': _('e.g. Al-Razi PHC')}), required=True,
        help_text=_('Primary Healthcare Center closest to this location.')
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
            Fieldset(
                _('General Information'),
                Div(
                    Div('name', css_class='col-md-6'),
                    Div('type', css_class='col-md-6'),
                    css_class='row mb-3',
                ),
            ),
            Fieldset(
                _('Location & Accessibility'),
                Div(
                    Div('governorate', css_class='col-md-4'),
                    Div('caza', css_class='col-md-4'),
                    Div('cadaster', css_class='col-md-4'),
                    css_class='row mb-3',
                ),
                Div(
                    Div('longitude', css_class='col-md-4'),
                    Div('latitude', css_class='col-md-4'),
                    Div('cwd_accessible', css_class='col-md-4'),
                    css_class='row mb-3',
                ),
            ),
            Fieldset(
                _('Management & Contact'),
                Div(
                    Div('manager_name', css_class='col-md-4'),
                    Div('phone_number', css_class='col-md-4'),
                    Div('email', css_class='col-md-4'),
                    css_class='row mb-3',
                ),
            ),
            Fieldset(
                _('Provided Services & Programs'),
                Div(
                    Div('provided_packages', css_class='col-md-6 bg-light p-3 rounded-3'),
                    Div('programs', css_class='col-md-6 bg-light p-3 rounded-3'),
                    css_class='row mb-3 mx-0',
                ),
                Div(
                    Div('offer_digital_learning', css_class='col-md-4'),
                    Div('have_digital_hub', css_class='col-md-4'),
                    Div('admin_staff_number', css_class='col-md-4'),
                    css_class='row mb-3',
                ),
                Div(
                    Div('neaby_phcc', css_class='col-md-8'),
                    Div('is_active', css_class='col-md-4'),
                    css_class='row mb-4',
                ),
            ),
            FormActions(
                Submit('save', _('Save Center Details'),
                       css_class='btn btn-primary px-5 fw-bold'),
                Reset('reset', _('Reset Form'),
                      css_class='btn btn-outline-secondary ms-2'),
                css_class='d-flex justify-content-end border-top pt-4'
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
