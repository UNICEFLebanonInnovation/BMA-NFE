from __future__ import unicode_literals, absolute_import, division

from django.utils.translation import gettext as _
from django import forms
from django.forms import modelformset_factory
from django.urls import reverse
from django.contrib import messages
from django.shortcuts import  render
from crispy_forms.helper import FormHelper
from crispy_forms.bootstrap import FormActions, Accordion, PrependedText, InlineCheckboxes, InlineRadios
from crispy_forms.layout import Layout, Fieldset, Button, Submit, Div, Field, HTML, ButtonHolder, Reset

from .models import School, PartnerOrganization, Club, ClubType,  Meeting, CommunityInitiative, HealthVisit
from student_registration.locations.models import Location
from .serializers import SchoolSerializer


class SchoolForm(forms.ModelForm):
    type = forms.ChoiceField(
        label=_("School Type"),
        widget=forms.Select, required=True,
        choices=School.TYPE
    )
    operating_shift = forms.ChoiceField(
        label=_("Operating shift"),
        widget=forms.Select, required=False,
        choices=School.OPERATING_SHIFT
    )
    number = forms.IntegerField(
        label=_('School CERD Number'),
        widget=forms.TextInput(attrs={'placeholder': _('e.g. 1234')}), required=False
    )
    name = forms.CharField(
        label=_("School name"),
        widget=forms.TextInput(attrs={'placeholder': _('e.g. Al Hikma Public School')}), required=True
    )
    director_name = forms.CharField(
        label=_("School director name"),
        widget=forms.TextInput(attrs={'placeholder': _('Full name of the director')}), required=True
    )
    land_phone_number = forms.RegexField(
        label=_('School land phone number'),
        regex=r'^[0-9]{2}-[0-9]{6}$',
        widget=forms.TextInput(attrs={'placeholder': 'Format: 00-00000'})
    )
    email = forms.EmailField(
        label=_('School email'),
        widget=forms.TextInput(attrs={'placeholder': 'Format: school@email.com'})
    )
    governorate = forms.ModelChoiceField(
        queryset=Location.objects.filter(parent__isnull=True), widget=forms.Select,
        label=_('Governorate'),
        empty_label='-------',
        required=False, to_field_name='id',
    )
    district = forms.ModelChoiceField(
        queryset=Location.objects.filter(parent__isnull=False), widget=forms.Select,
        label=_('District'),
        empty_label='-------',
        required=False, to_field_name='id',
        # initial=0
    )
    cadaster = forms.ModelChoiceField(
        queryset=Location.objects.filter(parent__isnull=False), widget=forms.Select,
        label=_('Cadaster'),
        empty_label='-------',
        required=False, to_field_name='id',
        # initial=0
    )
    longitude = forms.FloatField(
        label=_('School GPS (longitude)'),
        widget=forms.NumberInput(attrs=({'maxlength': 12, 'placeholder': '35.xxxx'})),
        min_value=0, required=True
    )
    latitude = forms.FloatField(
        label=_('School GPS (latitude)'),
        widget=forms.NumberInput(attrs=({'maxlength': 12, 'placeholder': '33.xxxx'})),
        min_value=0, required=True
    )
    registration_level = forms.MultipleChoiceField(
        label=_('Registration level'),
        choices=School.REGISTRATION_LEVEL,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    school_capacity = forms.IntegerField(
        label=_('School capacity'),
        widget=forms.TextInput(attrs={'placeholder': '0'}), required=False,
        help_text=_('Total student capacity of the school building.')
    )
    empty_building = forms.ChoiceField(
        label=_("Available empty building/closed campus"),
        widget=forms.Select, required=True,
        choices=School.YES_NO
    )
    number_children = forms.IntegerField(
        label=_('Total Number of children enrolled (excluding Dirasa)'),
        widget=forms.TextInput, required=True
    )
    number_children_male = forms.IntegerField(
        label=_('Total Number of children enrolled (male)'),
        widget=forms.TextInput, required=True
    )
    number_children_female = forms.IntegerField(
        label=_('Total Number of children enrolled (female)'),
        widget=forms.TextInput, required=True
    )
    number_children_lebanese = forms.IntegerField(
        label=_('Total Number of children enrolled (Lebanese)'),
        widget=forms.TextInput, required=True
    )
    number_children_non_lebanese = forms.IntegerField(
        label=_('Total Number of children enrolled (non Lebanese)'),
        widget=forms.TextInput, required=True
    )
    number_children_sbp = forms.IntegerField(
        label=_('Total Number of children enrolled (Dirasa only)'),
        widget=forms.TextInput, required=True
    )
    number_children_male_sbp = forms.IntegerField(
        label=_('Total Number of children enrolled (male, Dirasa only)'),
        widget=forms.TextInput, required=True
    )
    number_children_female_sbp = forms.IntegerField(
        label=_('Total Number of children enrolled (female, Dirasa only)'),
        widget=forms.TextInput, required=True
    )
    number_children_lebanese_sbp = forms.IntegerField(
        label=_('Total Number of children enrolled (Lebanese, Dirasa only)'),
        widget=forms.TextInput, required=True
    )
    number_children_non_lebanese_sbp = forms.IntegerField(
        label=_('Total Number of children enrolled (non Lebanese, Dirasa only)'),
        widget=forms.TextInput, required=True
    )
    CWD_accessible = forms.ChoiceField(
        label=_("Is the school accessible for CWD?"),
        widget=forms.Select, required=True,
        choices=School.YES_NO
    )
    internet_available = forms.ChoiceField(
        label=_("Availability of Internet"),
        widget=forms.Select, required=True,
        choices=School.YES_NO
    )
    school_digital_capacity = forms.IntegerField(
        label=_('Number of devices'),
        widget=forms.TextInput, required=False
    )
    is_closed = forms.ChoiceField(
        label=_("Is the school closed?"),
        widget=forms.Select, required=True,
        choices=School.TRUE_FALSE,
        initial=False
    )
    working_days = forms.MultipleChoiceField(
        label=_('Please indicate working days'),
        choices=School.DAYS_OF_THE_WEEK,
        widget=forms.CheckboxSelectMultiple,
        required=True
    )
    academic_year_start = forms.DateField(
        label=_("Dirasa Start Date"),
        required=True
    )
    academic_year_end = forms.DateField(
        label=_("Dirasa End Date"),
        required=True
    )
    receive_supplies = forms.ChoiceField(
        label=_("Did the school receive school supplies/stationery?"),
        widget=forms.Select, required=True,
        choices=School.YES_NO
    )
    admin_staff_number = forms.IntegerField(
        label=_("Number of Admin staff in the school"),
        widget=forms.NumberInput(attrs={'min': 0, 'placeholder': '0'}),
        required=True,
        min_value=0,
    )
    offer_digital_learning = forms.ChoiceField(
        label=_("Does the school offer digital learning services?"),
        widget=forms.Select, required=False,
        choices=School.YES_NO
    )
    have_digital_hub = forms.ChoiceField(
        label=_("Does the school have a digital hub?"),
        widget=forms.Select, required=False,
        choices=School.YES_NO
    )
    neaby_phcc = forms.CharField(
        label=_("Nearby PHCC name"),
        widget=forms.TextInput(attrs={'placeholder': _('Nearby PHCC name')}),
        required=False
    )

    number_dirasa_children_disability = forms.IntegerField(
        label=_('Total number of Children With Disability (Dirasa only)'),
        widget=forms.TextInput, required=False
    )
    number_total_children_disability = forms.IntegerField(
        label=_('Total number of Children With Disability (Excluding Dirasa)'),
        widget=forms.TextInput, required=False
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(SchoolForm, self).__init__(*args, **kwargs)

        choices = list()
        choices.append(('grade_one', _('Grade one')))
        choices.append(('grade_two', _('Grade two')))
        choices.append(('grade_three', _('Grade three')))
        choices.append(('grade_four', _('Grade four')))
        choices.append(('grade_five', _('Grade five')))
        choices.append(('grade_six', _('Grade six')))
        choices.append(('grade_seven', _('Grade seven')))
        choices.append(('grade_eight', _('Grade eight')))
        choices.append(('grade_nine', _('Grade nine')))

        self.fields['registration_level'].choices = choices

        instance = kwargs['instance'] if 'instance' in kwargs else ''
        form_action = reverse('schools:school_add')

        if instance:
            form_action = reverse('schools:school_edit', kwargs={'pk': instance.id})
        self.helper = FormHelper()
        self.helper.form_show_labels = True
        self.helper.form_action = form_action

        self.helper.layout = Layout(
            Div(
                Div(
                    HTML('<span class="badge-form badge-pill">1</span>'),
                    Div('number', css_class='col-md-3'),
                    HTML('<span class="badge-form badge-pill">2</span>'),
                    Div('name', css_class='col-md-3'),
                    HTML('<span class="badge-form badge-pill">3</span>'),
                    Div('type', css_class='col-md-3'),
                    HTML('<span class="badge-form badge-pill">4</span>'),
                    Div('operating_shift', css_class='col-md-3'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<span class="badge-form badge-pill">5</span>'),
                    Div('director_name', css_class='col-md-3'),
                    HTML('<span class="badge-form badge-pill">6</span>'),
                    Div('land_phone_number', css_class='col-md-3'),
                    HTML('<span class="badge-form badge-pill">7</span>'),
                    Div('email', css_class='col-md-3'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<span class="badge-form badge-pill">8</span>'),
                    Div('governorate', css_class='col-md-3'),
                    HTML('<span class="badge-form badge-pill">9</span>'),
                    Div('district', css_class='col-md-3'),
                    HTML('<span class="badge-form badge-pill">10</span>'),
                    Div('cadaster', css_class='col-md-3'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<span class="badge-form-2 badge-pill">11</span>'),
                    Div('longitude', css_class='col-md-3'),
                    HTML('<span class="badge-form-2 badge-pill">12</span>'),
                    Div('latitude', css_class='col-md-3'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<span class="badge-form-2 badge-pill">13</span>'),
                    Div('is_closed', css_class='col-md-3 '),
                    HTML('<span class="badge-form-2 badge-pill">14</span>'),
                    Div('admin_staff_number', css_class='col-md-3 '),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<span class="badge-form-2 badge-pill">15</span>'),
                    Div('offer_digital_learning', css_class='col-md-3 '),
                    HTML('<span class="badge-form-2 badge-pill">16</span>'),
                    Div('have_digital_hub', css_class='col-md-3 '),
                    HTML('<span class="badge-form-2 badge-pill">17</span>'),
                    Div('neaby_phcc', css_class='col-md-3 '),
                    css_class='row card-body',
                ),
                css_id='step-1'

            ),
            Div(
                Div(
                    HTML('<span class="badge-form badge-pill">1</span>'),
                    Div('registration_level', css_class='col-md-3 multiple-choice'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<span class="badge-form badge-pill">2</span>'),
                    Div('school_capacity', css_class='col-md-3'),
                    HTML('<span class="badge-form badge-pill">3</span>'),
                    Div('empty_building', css_class='col-md-3'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<span class="badge-form badge-pill">4</span>'),
                    Div('number_children', css_class='col-md-3'),
                    HTML('<span class="badge-form badge-pill">5</span>'),
                    Div('number_children_male', css_class='col-md-3'),
                    HTML('<span class="badge-form badge-pill">6</span>'),
                    Div('number_children_female', css_class='col-md-3'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<span class="badge-form badge-pill">7</span>'),
                    Div('number_children_lebanese', css_class='col-md-3'),
                    HTML('<span class="badge-form badge-pill">8</span>'),
                    Div('number_children_non_lebanese', css_class='col-md-3'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<span class="badge-form badge-pill">9</span>'),
                    Div('number_children_sbp', css_class='col-md-3'),
                    HTML('<span class="badge-form-2 badge-pill">10</span>'),
                    Div('number_children_male_sbp', css_class='col-md-3'),
                    HTML('<span class="badge-form-2 badge-pill">11</span>'),
                    Div('number_children_female_sbp', css_class='col-md-3'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<span class="badge-form-2 badge-pill">12</span>'),
                    Div('number_children_lebanese_sbp', css_class='col-md-3'),
                    HTML('<span class="badge-form-2 badge-pill">13</span>'),
                    Div('number_children_non_lebanese_sbp', css_class='col-md-3'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<span class="badge-form-2 badge-pill">14</span>'),
                    Div('CWD_accessible', css_class='col-md-3'),
                    HTML('<span class="badge-form-2 badge-pill">15</span>'),
                    Div('receive_supplies', css_class='col-md-3'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<span class="badge-form-2 badge-pill">16</span>'),
                    Div('internet_available', css_class='col-md-3'),
                    HTML('<span class="badge-form-2 badge-pill">17</span>'),
                    Div('digital_learning_programme', css_class='col-md-3'),
                    HTML('<span class="badge-form-2 badge-pill" id="span_school_digital_capacity">18</span>'),
                    Div('school_digital_capacity', css_class='col-md-3'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<span class="badge-form-2 badge-pill">19</span>'),
                    Div('number_dirasa_children_disability', css_class='col-md-3'),
                    HTML('<span class="badge-form-2 badge-pill">20</span>'),
                    Div('number_total_children_disability', css_class='col-md-3'),
                    css_class='row card-body',
                ),
                css_id='step-2'
            ),
            Div(
                Div(
                    HTML('<span class="badge-form badge-pill">1</span>'),
                    Div('working_days', css_class='col-md-3 multiple-choice'),

                    css_class='row card-body',
                ),
                Div(
                    HTML('<span class="badge-form badge-pill">2</span>'),
                    Div('academic_year_start', css_class='col-md-3'),
                    HTML('<span class="badge-form badge-pill">3</span>'),
                    Div('academic_year_end', css_class='col-md-3'),
                    css_class='row card-body',
                ),
                css_id='step-3'
            ),
            Div(
                FormActions(
                    Submit('save', 'Save',
                           css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-success'),
                    Reset('reset', 'Reset',
                          css_class='btn-shadow btn-wide float-right btn-pill mr-3 btn-hover-shine btn btn-warning'),
                ),
                css_id='step-4'
            )
        )

    # def save(self, instance=None, request=None):
    #     instance = super(SchoolForm, self).save()
    #     messages.success(request, _('Your data has been sent successfully to the server'))

    def save(self, request=None, instance=None):
        if instance:
            instance = super(SchoolForm, self).save()
            serializer = SchoolSerializer(instance, data=request.POST)
            if serializer.is_valid():
                instance = serializer.update(validated_data=serializer.validated_data, instance=instance)
                instance.modified_by = request.user
                instance.save()
                request.session['instance_id'] = instance.id
                messages.success(request, _('Your data has been sent successfully to the server'))
            else:
                messages.warning(request, serializer.errors)
        else:
            serializer = SchoolSerializer(data=request.POST)
            if serializer.is_valid():
                instance = serializer.create(validated_data=serializer.validated_data)
                instance.owner = request.user
                instance.modified_by = request.user
                instance.save()
                request.session['instance_id'] = instance.id
                partner = request.user.partner
                partner.schools.add(instance)
                partner.save()
                messages.success(request, _('Your data has been sent successfully to the server'))
            else:
                messages.warning(request, serializer.errors)

        return instance


    def clean(self):
        cleaned_data = super(SchoolForm, self).clean()

        digital_learning_programme = cleaned_data.get("digital_learning_programme")
        school_digital_capacity = cleaned_data.get("school_digital_capacity")
        if digital_learning_programme == "yes" and not school_digital_capacity:
            self.add_error('school_digital_capacity', 'This field is required')


    class Meta:
        model = School
        fields = (
            'id',
            'number',
            'name',
            'director_name',
            'land_phone_number',
            'email',
            'governorate',
            'district',
            'cadaster',
            'longitude',
            'latitude',
            'registration_level',
            'school_capacity',
            'empty_building',
            'number_children',
            'number_children_male',
            'number_children_female',
            'number_children_lebanese',
            'number_children_non_lebanese',
            'number_children_sbp',
            'number_children_male_sbp',
            'number_children_female_sbp',
            'number_children_lebanese_sbp',
            'number_children_non_lebanese_sbp',
            'CWD_accessible',
            'internet_available',
            'digital_learning_programme',
            'school_digital_capacity',
            'is_closed',
            'working_days',
            'academic_year_start',
            'academic_year_end',
            'receive_supplies',
            'admin_staff_number',
            'offer_digital_learning',
            'have_digital_hub',
            'neaby_phcc',
            'number_dirasa_children_disability',
            'number_total_children_disability',
            'type',
            'operating_shift',
        )


class ClubForm(forms.ModelForm):

    club_name = forms.CharField(
        label=_("Club name"),
        widget=forms.TextInput(attrs={'placeholder': _('e.g. Science Club')}), required=True
    )
    number_clubs = forms.IntegerField(
        label=_('Number of Clubs'),
        widget=forms.TextInput, required=False
    )
    club_type = forms.ModelChoiceField(
        queryset=ClubType.objects.all(), widget=forms.Select,
        label=_('Club Type'),
        empty_label='-------',
        required=False, to_field_name='id',
        initial=0
    )
    number_children = forms.IntegerField(
        label=_('Total Number of Children'),
        widget=forms.TextInput, required=False
    )

    school_id = forms.CharField(widget=forms.HiddenInput, required=False)

    def __init__(self, *args, **kwargs):

        self.request = kwargs.pop('request', None)
        school_id = kwargs.pop('school_id', None)
        pk = kwargs.pop('pk', None)

        super(ClubForm, self).__init__(*args, **kwargs)

        form_action = reverse('schools:club_add', kwargs={'school_id': school_id})
        if pk:
            form_action = reverse('schools:club_edit',
                                  kwargs={'school_id': school_id, 'pk': pk})

        self.helper = FormHelper()
        self.helper.form_show_labels = True
        self.helper.form_action = form_action
        self.helper.layout = Layout(
            Div(
                Div(
                    HTML('<span class="badge-form-2 badge-pill">1</span>'),
                    Div('club_name', css_class='col-md-3'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<span class="badge-form badge-pill">2</span>'),
                    Div('number_clubs', css_class='col-md-3'),
                    HTML('<span class="badge-form badge-pill">3</span>'),
                    Div('club_type', css_class='col-md-3'),
                    HTML('<span class="badge-form badge-pill">4</span>'),
                    Div('number_children', css_class='col-md-3'),
                    css_class='row card-body',
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

    def save(self, request=None, instance=None, school_id=None):
        validated_data = request.POST

        if not instance:
            instance = Club.objects.create(school_id=school_id)
            instance.owner = request.user
        else:
            instance = Club.objects.get(id=instance)

        instance.club_name = validated_data.get('club_name')
        instance.number_clubs = validated_data.get('number_clubs')
        instance.club_type_id = validated_data.get('club_type')
        instance.number_children = validated_data.get('number_children')
        instance.modified_by = request.user
        instance.save()

        messages.success(request, _('Your data has been sent successfully to the server'))

        return instance

    class Meta:
        model = Club
        fields = (
            'club_name',
            'number_clubs',
            'club_type',
            'number_children'
        )


class MeetingForm(forms.ModelForm):

    meeting_name = forms.CharField(
        label=_("Meeting Name"),
        widget=forms.TextInput(attrs={'placeholder': _('e.g. Monthly Staff Meeting')}), required=True
    )
    meeting_date = forms.DateField(
        label=_('Meeting Date'),
        widget=forms.TextInput(attrs={'class': 'datepicker', 'autocomplete': 'off'}),
        required=True
    )
    number_participants = forms.IntegerField(
        label=_('Number of Participants'),
        widget=forms.TextInput, required=False
    )
    school_id = forms.CharField(widget=forms.HiddenInput, required=False)


    def __init__(self, *args, **kwargs):

        self.request = kwargs.pop('request', None)
        school_id = kwargs.pop('school_id', None)
        pk = kwargs.pop('pk', None)

        super(MeetingForm, self).__init__(*args, **kwargs)

        form_action = reverse('schools:meeting_add', kwargs={'school_id': school_id})
        if pk:
            form_action = reverse('schools:meeting_edit',
                                  kwargs={'school_id': school_id, 'pk': pk})

        self.helper = FormHelper()
        self.helper.form_show_labels = True
        self.helper.form_action = form_action
        self.helper.layout = Layout(
            Div(
                Div(
                    HTML('<span class="badge-form badge-pill">1</span>'),
                    Div('meeting_name', css_class='col-md-3'),
                    HTML('<span class="badge-form badge-pill">2</span>'),
                    Div('meeting_date', css_class='col-md-3'),
                    HTML('<span class="badge-form badge-pill">3</span>'),
                    Div('number_participants', css_class='col-md-3'),
                    css_class='row card-body',
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

    def save(self, request=None, instance=None, school_id=None):
        validated_data = request.POST

        if not instance:
            instance = Meeting.objects.create(school_id=school_id)
            instance.owner = request.user
        else:
            instance = Meeting.objects.get(id=instance)

        instance.meeting_name = validated_data.get('meeting_name')
        instance.meeting_date = validated_data.get('meeting_date')
        instance.number_participants = validated_data.get('number_participants')
        instance.modified_by = request.user
        instance.save()

        messages.success(request, _('Your data has been sent successfully to the server'))

        return instance

    class Meta:
        model = Meeting
        fields = (
            'meeting_name',
            'meeting_date',
            'number_participants'
        )


class CommunityInitiativeForm(forms.ModelForm):

    community_group_name = forms.CharField(
        label=_("Community Group Name"),
        widget=forms.TextInput(attrs={'placeholder': _('e.g. Parents Committee')}), required=True
    )
    number_initiatives = forms.IntegerField(
        label=_('Number of Initiatives'),
        widget=forms.TextInput, required=False
    )
    school_id = forms.CharField(widget=forms.HiddenInput, required=False)

    def __init__(self, *args, **kwargs):

        self.request = kwargs.pop('request', None)
        school_id = kwargs.pop('school_id', None)
        pk = kwargs.pop('pk', None)

        super(CommunityInitiativeForm, self).__init__(*args, **kwargs)

        form_action = reverse('schools:community_initiative_add', kwargs={'school_id': school_id})
        if pk:
            form_action = reverse('schools:community_initiative_edit',
                                  kwargs={'school_id': school_id, 'pk': pk})

        self.helper = FormHelper()
        self.helper.form_show_labels = True
        self.helper.form_action = form_action
        self.helper.layout = Layout(
            Div(
                Div(
                    HTML('<span class="badge-form badge-pill">1</span>'),
                    Div('community_group_name', css_class='col-md-3'),
                    HTML('<span class="badge-form badge-pill">2</span>'),
                    Div('number_initiatives', css_class='col-md-3'),
                    css_class='row card-body',
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

    def save(self, request=None, instance=None, school_id=None):
        validated_data = request.POST

        if not instance:
            instance = CommunityInitiative.objects.create(school_id=school_id)
            instance.owner = request.user
        else:
            instance = CommunityInitiative.objects.get(id=instance)

        instance.community_group_name = validated_data.get('community_group_name')
        instance.number_initiatives = validated_data.get('number_initiatives')
        instance.modified_by = request.user
        instance.save()

        messages.success(request, _('Your data has been sent successfully to the server'))

        return instance

    class Meta:
        model = CommunityInitiative
        fields = (
            'community_group_name',
            'number_initiatives',
        )


class HealthVisitForm(forms.ModelForm):
    focal_point_name = forms.CharField(
        label=_("Health Focal Point Name"),
        widget=forms.TextInput(attrs={'placeholder': _('Full name of focal point')}), required=True
    )
    number_visits = forms.IntegerField(
        label=_('Number of Visits'),
        widget=forms.TextInput, required=False
    )
    date_first_visit = forms.DateField(
        label=_('Date of First Visit'),
        widget=forms.TextInput(attrs={'class': 'datepicker', 'autocomplete': 'off'}),
        required=True
    )
    date_last_visit = forms.DateField(
        label=_('Date of Last Visit'),
        widget=forms.TextInput(attrs={'class': 'datepicker', 'autocomplete': 'off'}),
        required=True
    )
    summary = forms.CharField(
        label=_('Summary'),
        widget=forms.Textarea, required=False
    )
    school_id = forms.CharField(widget=forms.HiddenInput, required=False)

    def __init__(self, *args, **kwargs):

        self.request = kwargs.pop('request', None)
        school_id = kwargs.pop('school_id', None)
        pk = kwargs.pop('pk', None)

        super(HealthVisitForm, self).__init__(*args, **kwargs)

        form_action = reverse('schools:health_visit_add', kwargs={'school_id': school_id})
        if pk:
            form_action = reverse('schools:health_visit_edit',
                                  kwargs={'school_id': school_id, 'pk': pk})

        self.helper = FormHelper()
        self.helper.form_show_labels = True
        self.helper.form_action = form_action
        self.helper.layout = Layout(
            Div(
                Div(
                    HTML('<span class="badge-form badge-pill">1</span>'),
                    Div('focal_point_name', css_class='col-md-3'),
                    HTML('<span class="badge-form badge-pill">2</span>'),
                    Div('number_visits', css_class='col-md-3'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<span class="badge-form badge-pill">3</span>'),
                    Div('date_first_visit', css_class='col-md-3'),
                    HTML('<span class="badge-form badge-pill">4</span>'),
                    Div('date_last_visit', css_class='col-md-3'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<span class="badge-form badge-pill">5</span>'),
                    Div('summary', css_class='col-md-3'),
                    css_class='row card-body',
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

    def save(self, request=None, instance=None, school_id=None):
        validated_data = request.POST

        if not instance:
            instance = HealthVisit.objects.create(school_id=school_id)
            instance.owner = request.user
        else:
            instance = HealthVisit.objects.get(id=instance)

        instance.focal_point_name = validated_data.get('focal_point_name')
        instance.number_visits = validated_data.get('number_visits')
        instance.date_first_visit = validated_data.get('date_first_visit')
        instance.date_last_visit = validated_data.get('date_last_visit')
        instance.summary = validated_data.get('summary')
        instance.modified_by = request.user
        instance.save()

        messages.success(request, _('Your data has been sent successfully to the server'))

        return instance

    class Meta:
        model = HealthVisit
        fields = (
            'focal_point_name',
            'number_visits',
            'date_first_visit',
            'date_last_visit',
            'summary'
        )
