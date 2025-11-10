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

from .models import School, PartnerOrganization, EducationYear, Evaluation, Club, ClubType,  Meeting, CommunityInitiative, HealthVisit
from student_registration.locations.models import Location
from .serializers import SchoolSerializer


class ProfileForm(forms.ModelForm):

    email = forms.EmailField(
        label=_('School email'),
        widget=forms.TextInput(attrs={'placeholder': 'Format: school@email.com'})
    )
    land_phone_number = forms.RegexField(
        label=_('School land phone number'),
        regex=r'^[0-9]{2}-[0-9]{6}$',
        widget=forms.TextInput(attrs={'placeholder': 'Format: 00-00000'})
    )
    fax_number = forms.RegexField(
        label=_('School fax number'),
        regex=r'^[0-9]{2}-[0-9]{6}$',
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Format: 00-00000'})
    )
    director_phone_number = forms.RegexField(
        label=_('School director cell phone'),
        regex=r'^[0-9]{2}-[0-9]{6}$',
        widget=forms.TextInput(attrs={'placeholder': 'Format: 00-00000'})
    )
    it_phone_number = forms.RegexField(
        label=_('School IT phone number'),
        regex=r'^[0-9]{2}-[0-9]{6}$',
        widget=forms.TextInput(attrs={'placeholder': 'Format: 00-00000'})
    )

    academic_year_start = forms.DateField(
        label=_('School year start date'),
        widget=forms.TextInput,
        required=True
    )

    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)

        current_education_year = EducationYear.objects.get(current_year=True)

        self.helper = FormHelper()
        self.helper.form_show_labels = True
        self.helper.form_action = reverse('schools:profile', kwargs={})
        self.helper.layout = Layout(
            Fieldset(
                None,
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('School information') + '</h4>')
                ),
                Div(
                    HTML('<span class="badge-form-2 badge-pill">1</span>'),
                    Div('director_name', css_class='col-md-3'),
                    HTML('<span class="badge-form-2 badge-pill">2</span>'),
                    Div('land_phone_number', css_class='col-md-3'),
                    HTML('<span class="badge-form-2 badge-pill">3</span>'),
                    Div('fax_number', css_class='col-md-3'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<span class="badge-form-2 badge-pill">4</span>'),
                    Div('director_phone_number', css_class='col-md-3'),
                    HTML('<span class="badge-form-2 badge-pill">5</span>'),
                    Div('email', css_class='col-md-3'),
                    HTML('<span class="badge-form-2 badge-pill">6</span>'),
                    Div('certified_foreign_language', css_class='col-md-3'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<span class="badge-form-2 badge-pill">7</span>'),
                    Div('comments', css_class='col-md-3'),
                    HTML('<span class="badge-form-2 badge-pill">8</span>'),
                    Div('weekend', css_class='col-md-3'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<span class="badge-form-2 badge-pill">9</span>'),
                    Div('it_name', css_class='col-md-3'),
                    HTML('<span class="badge-form-2 badge-pill">10</span>'),
                    Div('it_phone_number', css_class='col-md-3'),
                    HTML('<span class="badge-form-2 badge-pill">11</span>'),
                    Div('coordinator', css_class='col-md-3'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<span class="badge-form-2 badge-pill">12</span>'),
                    Div('is_2nd_shift', css_class='col-md-3'),
                    HTML('<span class="badge-form-2 badge-pill">13</span>'),
                    Div('is_alp', css_class='col-md-3'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<span class="badge-form-2 badge-pill">14</span>'),
                    Div('number_students_2nd_shift', css_class='col-md-3'),
                    HTML('<span class="badge-form-2 badge-pill">15</span>'),
                    Div('number_students_alp', css_class='col-md-3'),
                    css_class='row card-body',
                ),
                css_class='bd-callout bd-callout-warning'
            ),
            Fieldset(
                None,
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' +
                         _('Bank Accounts Information') + '</h4>')
                ),
                Div(
                    HTML('<span class="badge-form-2 badge-pill">1</span>'),
                    Div('iban_base1', css_class='col-md-5'),

                    HTML('<span class="badge-form-2 badge-pill">2</span>'),
                    Div('bank_Base1', css_class='col-md-3'),
                    HTML('<span class="badge-form-2 badge-pill">3</span>'),
                    Div('branch_base1', css_class='col-md-3'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<span class="badge-form-2 badge-pill">4</span>'),
                    Div('iban_base2', css_class='col-md-5'),

                    HTML('<span class="badge-form-2 badge-pill">5</span>'),
                    Div('bank_Base2', css_class='col-md-3'),
                    HTML('<span class="badge-form-2 badge-pill">6</span>'),
                    Div('branch_base2', css_class='col-md-3'),
                    css_class='row card-body',
                ),
                css_class='bd-callout bd-callout-warning'
            ),
            Fieldset(
                None,
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' +
                         _('Current academic year') + ' ' + current_education_year.name + '</h4>')
                ),
                Div(
                    HTML('<span class="badge-form-2 badge-pill">1</span>'),
                    Div('academic_year_start', css_class='col-md-3'),
                    HTML('<span class="badge-form-2 badge-pill">2</span>'),
                    Div('academic_year_end', css_class='col-md-3'),
                    HTML('<span class="badge-form-2 badge-pill">3</span>'),
                    Div('academic_year_exam_end', css_class='col-md-3'),
                    css_class='row card-body',
                ),
                css_class='bd-callout bd-callout-warning'
            ),
            FormActions(
                Submit('save', _('Save')),
            )
        )

    def save(self, instance=None, request=None):
        instance = super(ProfileForm, self).save()
        messages.success(request, _('Your data has been sent successfully to the server'))

    class Meta:
        model = School
        fields = (
            'academic_year_start',
            'academic_year_end',
            'academic_year_exam_end',
            'director_name',
            'land_phone_number',
            'director_phone_number',
            'it_name',
            'it_phone_number',
            #'field_coordinator_name',
            'coordinator',
            'fax_number',
            'email',
            'certified_foreign_language',
            'comments',
            'weekend',
            'is_2nd_shift',
            'is_alp',
            'number_students_2nd_shift',
            'number_students_alp',
            'bank_Base1',
            'branch_base1',
            'iban_base1',
            'bank_Base2',
            'branch_base2',
            'iban_base2',
        )
        initial_fields = fields
        widgets = {}

    class Media:
        js = ()


class PartnerForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(PartnerForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_show_labels = True
        self.helper.form_action = reverse('schools:partner', kwargs={})

        self.helper.layout = Layout(
            Fieldset(
                None,
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('CLM round') + '</h4>')
                ),
                Div(
                    HTML('<span class="badge-form-2 badge-pill">1</span>'),
                    Div('bln_round', css_class='col-md-3'),
                    HTML('<span class="badge-form-2 badge-pill">2</span>'),
                    Div('rs_round', css_class='col-md-3'),
                    HTML('<span class="badge-form-2 badge-pill">3</span>'),
                    Div('cbece_round', css_class='col-md-3'),
                    css_class='row card-body',
                ),
                css_class='bd-callout bd-callout-warning'
            ),
            FormActions(
                Submit('save', _('Save')),
            )
        )

    def save(self, instance=None, request=None):
        instance = super(PartnerForm, self).save()
        messages.success(request, _('Your data has been sent successfully to the server'))

    class Meta:
        model = PartnerOrganization
        fields = (
            'bln_round',
            'rs_round',
            'cbece_round',
        )
        initial_fields = fields
        widgets = {}

    class Media:
        js = ()


class EvaluationForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(EvaluationForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_show_labels = True
        self.helper.form_action = reverse('schools:evaluation', kwargs={})
        self.fields['implemented_de_prep'].label = ''
        self.fields['reasons_no_de_prep'].label = False

        self.fields['implemented_de'].label = ''
        self.fields['reasons_no_de'].label = False

        self.fields['implemented_de_2'].label = ''
        self.fields['reasons_no_de_2'].label = False

        self.fields['implemented_de_3'].label = ''
        self.fields['reasons_no_de_3'].label = False

        self.fields['implemented_de_9'].label = ''
        self.fields['reasons_no_de_9'].label = False

        self.fields['implemented_de_prep'].label = ''
        self.fields['reasons_no_de_prep'].label = False

        self.helper.layout = Layout(
            Fieldset(
                None,
                Div(
                    HTML('<span class="badge-form-2 badge-pill">1</span>'),
                    Div('total_teaching_days', css_class='col-md-4'),
                    Div('total_teaching_days_tillnow', css_class='col-md-4'),
                    css_class='row card-body',
                    style="background: #E3F2FC;",
                ),
                css_class='bd-callout bd-callout-warning'
            ),

            Fieldset(
                None,
                Div(
                    HTML('<div><label><font color="navy"><b>'+_('Evaluation for Prep-Ece')+'</b></font></label></div>'),
                    HTML('<div><br><a class="btn btn-info" href={% url "schools:update_classroom_cprep" pk=' +
                         str(self.instance.id) + ' %}>' + _('Prep-Ece') + '  </a></div>'),
                    Fieldset(
                        None,
                        Div(
                            HTML('<span class="badge-form-2 badge-pill">1</span>'),
                            HTML(_('Have you implemented distance education ?')),
                            Div('implemented_de_prep', css_class='col-md-3', id='implemented-de-prep'),
                            css_class='row card-body',
                        ),
                        Div(
                            Div('reasons_no_de_prep', css_class='col-md-10', id='reasons-no-de-prep'),
                            css_class='row card-body',

                        ),
                        css_class='bd-callout bd-callout-warning',
                    ),
                    Fieldset(
                        None,
                        Div(
                            HTML('<span class="badge-form-2 badge-pill">2</span>'),
                            Div('steps_de_prep', css_class='col-md-10'),
                            css_class='row card-body',
                        ),
                        css_class='bd-callout bd-callout-warning'
                    ),
                    Fieldset(
                        None,
                        Div(
                            HTML('<span class="badge-form-2 badge-pill">3</span>'),
                            Div('challenges_de_prep', css_class='col-md-10'),
                            css_class='row card-body',
                        ),
                        css_class='bd-callout bd-callout-warning'
                    ),

                    Fieldset(
                        None,
                        Div(
                            HTML('<span class="badge-form-2 badge-pill">4</span>'),
                            Div('evaluate_steps_de_prep', css_class='col-md-10'),
                            css_class='row card-body',
                        ),
                        css_class='bd-callout bd-callout-warning'
                    ),
                ),
                style="background: #F8FAFC;",
            ),

            Fieldset(
                None,
                Div(
                    HTML('<div><label><font color="navy"><b>' + _(
                        'Evaluation for Cylce 1') + '</b></font></label></div>'),
                    HTML('<div><br><a class="btn btn-success" href={% url "schools:update_classroom_c1" pk=' +
                         str(self.instance.id) + ' %}>' + _('Cycle 1') + '  </a></div>'),
                    HTML('<div><br><a class="btn btn-info" href={% url "schools:update_classroom" pk=' +
                         str(self.instance.id) + ' %}>' + _('Cycle 2') + '  </a></div>'),
                    HTML('<div><br><a class="btn btn-success" href={% url "schools:update_classroom_c3" pk=' +
                         str(self.instance.id) + ' %}>' + _('Cycle 3') + '  </a></div>'),

                    Fieldset(
                        None,
                        Div(
                            HTML('<span class="badge-form-2 badge-pill">1</span>'),
                            HTML(_('Have you implemented distance education ?')),
                            Div('implemented_de', css_class='col-md-3'),
                            Div('reasons_no_de', css_class='col-md-10'),
                            css_class='row card-body',
                        ),
                        css_class='bd-callout bd-callout-warning'

                    ),
                    Fieldset(
                        None,
                        Div(
                            HTML('<span class="badge-form-2 badge-pill">2</span>'),
                            Div('steps_de', css_class='col-md-10'),
                            css_class='row card-body',
                        ),
                        css_class='bd-callout bd-callout-warning'
                    ),
                    Fieldset(
                        None,
                        Div(
                            HTML('<span class="badge-form-2 badge-pill">3</span>'),
                            Div('challenges_de', css_class='col-md-10'),
                            css_class='row card-body',
                        ),
                        css_class='bd-callout bd-callout-warning'
                    ),

                    Fieldset(
                        None,
                        Div(
                            HTML('<span class="badge-form-2 badge-pill">4</span>'),
                            Div('evaluate_steps_de', css_class='col-md-10'),
                            css_class='row card-body',
                        ),
                        css_class='bd-callout bd-callout-warning'
                    ),
                ),
                style="background: #FDFFD8;",
            ),

            Fieldset(
                None,
                Div(
                    HTML('<div><label><font color="navy"><b>' + _(
                        'Evaluation for Cycle 2') + '</b></font></label></div>'),
                    HTML('<div><br><a class="btn btn-info" href={% url "schools:update_classroom_c4" pk=' +
                         str(self.instance.id) + ' %}>' + _('Cycle 4') + '  </a></div>'),
                    HTML('<div><br><a class="btn btn-success" href={% url "schools:update_classroom_c5" pk=' +
                         str(self.instance.id) + ' %}>' + _('Cycle 5') + '  </a></div>'),
                    HTML('<div><br><a class="btn btn-info" href={% url "schools:update_classroom_c6" pk=' +
                         str(self.instance.id) + ' %}>' + _('Cycle 6') + '  </a></div>'),
                    Fieldset(
                        None,
                        Div(
                            HTML('<span class="badge-form-2 badge-pill">1</span>'),
                            HTML(_('Have you implemented distance education ?')),
                            Div('implemented_de_2', css_class='col-md-3'),
                            Div('reasons_no_de_2', css_class='col-md-10'),
                            css_class='row card-body',
                        ),
                        css_class='bd-callout bd-callout-warning'

                    ),
                    Fieldset(
                        None,
                        Div(
                            HTML('<span class="badge-form-2 badge-pill">2</span>'),
                            Div('steps_de_2', css_class='col-md-10'),
                            css_class='row card-body',
                        ),
                        css_class='bd-callout bd-callout-warning'
                    ),
                    Fieldset(
                        None,
                        Div(
                            HTML('<span class="badge-form-2 badge-pill">3</span>'),
                            Div('challenges_de_2', css_class='col-md-10'),
                            css_class='row card-body',
                        ),
                        css_class='bd-callout bd-callout-warning'
                    ),

                    Fieldset(
                        None,
                        Div(
                            HTML('<span class="badge-form-2 badge-pill">4</span>'),
                            Div('evaluate_steps_de_2', css_class='col-md-10'),
                            css_class='row card-body',
                        ),
                        css_class='bd-callout bd-callout-warning'
                    ),
                ),
                style="background: #F8FAFC;",
            ),

            Fieldset(
                None,
                Div(
                    HTML('<div><label><font color="navy"><b>' + _(
                        'Evaluation for Cycle 3') + '</b></font></label></div>'),
                    HTML('<div><br><a class="btn btn-success" href={% url "schools:update_classroom_c7" pk=' +
                         str(self.instance.id) + ' %}>' + _('Cycle 7') + '  </a></div>'),
                    HTML('<div><br><a class="btn btn-info" href={% url "schools:update_classroom_c8" pk=' +
                         str(self.instance.id) + ' %}>' + _('Cycle 8') + '  </a></div>'),
                    Fieldset(
                        None,
                        Div(
                            HTML('<span class="badge-form-2 badge-pill">1</span>'),
                            HTML(_('Have you implemented distance education ?')),
                            Div('implemented_de_3', css_class='col-md-3'),
                            Div('reasons_no_de_3', css_class='col-md-10'),
                            css_class='row card-body',
                        ),
                        css_class='bd-callout bd-callout-warning'

                    ),
                    Fieldset(
                        None,
                        Div(
                            HTML('<span class="badge-form-2 badge-pill">2</span>'),
                            Div('steps_de_3', css_class='col-md-10'),
                            css_class='row card-body',
                        ),
                        css_class='bd-callout bd-callout-warning'
                    ),
                    Fieldset(
                        None,
                        Div(
                            HTML('<span class="badge-form-2 badge-pill">3</span>'),
                            Div('challenges_de_3', css_class='col-md-10'),
                            css_class='row card-body',
                        ),
                        css_class='bd-callout bd-callout-warning'
                    ),

                    Fieldset(
                        None,
                        Div(
                            HTML('<span class="badge-form-2 badge-pill">4</span>'),
                            Div('evaluate_steps_de_3', css_class='col-md-10'),
                            css_class='row card-body',
                        ),
                        css_class='bd-callout bd-callout-warning'
                    ),
                    style="background: #FDFFD8;",
                ),
            ),

            Fieldset(
                None,
                Div(
                    HTML('<div><label><font color="navy"><b>' + _(
                        'Evaluation for Grade 9') + '</b></font></label></div>'),
                    HTML('<div><br><a class="btn btn-success" href={% url "schools:update_classroom_c9" pk=' +
                         str(self.instance.id) + ' %}>' + _('Cycle 9') + '  </a></div>'),
                    css_class='bd-callout bd-callout-warning'
                ),
                Fieldset(
                    None,
                    Div(
                        HTML('<span class="badge-form-2 badge-pill">1</span>'),
                        HTML(_('Have you implemented distance education ?')),
                        Div('implemented_de_9', css_class='col-md-3'),
                        Div('reasons_no_de_9', css_class='col-md-10'),
                        css_class='row card-body',
                    ),
                    css_class='bd-callout bd-callout-warning'

                ),
                Fieldset(
                    None,
                    Div(
                        HTML('<span class="badge-form-2 badge-pill">2</span>'),
                        Div('steps_de_9', css_class='col-md-10'),
                        css_class='row card-body',
                    ),
                    css_class='bd-callout bd-callout-warning'
                ),
                Fieldset(
                    None,
                    Div(
                        HTML('<span class="badge-form-2 badge-pill">3</span>'),
                        Div('challenges_de_9', css_class='col-md-10'),
                        css_class='row card-body',
                    ),
                    css_class='bd-callout bd-callout-warning'
                ),

                Fieldset(
                    None,
                    Div(
                        HTML('<span class="badge-form-2 badge-pill">4</span>'),
                        Div('evaluate_steps_de_9', css_class='col-md-10'),
                        css_class='row card-body',
                    ),
                    css_class='bd-callout bd-callout-warning'
                ),
                style="background: #F8FAFC;",
            ),
            Fieldset(
                None,
                Div(
                    HTML('<span class="badge-form-2 badge-pill">2</span>'),
                    Div('other_notes_de', css_class='col-md-10'),
                    css_class='row card-body',
                    style="background: #E3F2FC;",
                ),
            ),
            FormActions(
                Submit('save', _('Save')),
            ),
        )

    def save(self, instance=None, request=None):
        instance = super(EvaluationForm, self).save()
        messages.success(request, _('Your data has been sent successfully to the server'))

    class Meta:
        model = Evaluation
        fields = ('total_teaching_days', 'total_teaching_days_tillnow', 'implemented_de', 'reasons_no_de', 'challenges_de', 'steps_de',
                  'evaluate_steps_de', 'other_notes_de',
                  'implemented_de_2', 'reasons_no_de_2', 'challenges_de_2', 'steps_de_2', 'evaluate_steps_de_2',
                  'implemented_de_3', 'reasons_no_de_3', 'challenges_de_3', 'steps_de_3', 'evaluate_steps_de_3',
                  'implemented_de_9', 'reasons_no_de_9', 'challenges_de_9', 'steps_de_9', 'evaluate_steps_de_9',
                  'implemented_de_prep', 'reasons_no_de_prep', 'challenges_de_prep', 'steps_de_prep', 'evaluate_steps_de_prep',
                  )
        initial_fields = fields
        widgets = {}

    class Media:
        js = ()


class Classroom_Form(forms.ModelForm):
    class Meta:
        model = Evaluation
        exclude = ()

    def __init__(self, *args, **kwargs):
        super(Classroom_Form, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-3 create-label'
        self.helper.field_class = 'col-md-9'
        self.fields['c2_eng_completed'].label = False
        self.fields['c2_eng_completed_de'].label = False
        self.fields['c2_eng_remaining_de'].label = False
        self.fields['c2_fr_completed'].label = False
        self.fields['c2_fr_completed_de'].label = False
        self.fields['c2_fr_remaining_de'].label = False
        self.fields['c2_math_completed'].label = False
        self.fields['c2_math_completed_de'].label = False
        self.fields['c2_math_remaining_de'].label = False
        self.fields['c2_sc_completed'].label = False
        self.fields['c2_sc_completed_de'].label = False
        self.fields['c2_sc_remaining_de'].label = False
        self.fields['c2_ara_completed'].label = False
        self.fields['c2_ara_completed_de'].label = False
        self.fields['c2_ara_remaining_de'].label = False
        self.fields['c2_civic_completed'].label = False
        self.fields['c2_civic_completed_de'].label = False
        self.fields['c2_civic_remaining_de'].label = False
        self.fields['c2_geo_completed'].label = False
        self.fields['c2_geo_completed_de'].label = False
        self.fields['c2_geo_remaining_de'].label = False
        self.helper.layout = Layout(
            Fieldset(
                None,
                Div(
                    Div('owner', css_class='col-md-10', hidden="true"),
                    Div('school', css_class='col-md-10', hidden="true"),
                    Div('education_year', css_class='col-md-10', hidden="true"),

                    Div('total_teaching_days', css_class='col-md-10', hidden="true"),
                    Div('implemented_de', css_class='col-md-10', hidden="true"),
                    Div('reasons_no_de', css_class='col-md-10', hidden="true"),
                    Div('challenges_de', css_class='col-md-10', hidden="true"),
                    Div('steps_de', css_class='col-md-10 hidden', hidden="true"),
                    Div('evaluate_steps_de', css_class='col-md-10', hidden="true"),
                    Div('other_notes_de', css_class='col-md-10', hidden="true"),

                    Div('total_teaching_days_tillnow', css_class='col-md-10', hidden="true"),
                    Div('implemented_de_2', css_class='col-md-10', hidden="true"),
                    Div('reasons_no_de_2', css_class='col-md-10', hidden="true"),
                    Div('challenges_de_2', css_class='col-md-10', hidden="true"),
                    Div('steps_de_2', css_class='col-md-10 hidden', hidden="true"),
                    Div('evaluate_steps_de_2', css_class='col-md-10', hidden="true"),

                    Div('implemented_de_3', css_class='col-md-10', hidden="true"),
                    Div('reasons_no_de_3', css_class='col-md-10', hidden="true"),
                    Div('challenges_de_3', css_class='col-md-10', hidden="true"),
                    Div('steps_de_3', css_class='col-md-10 hidden', hidden="true"),
                    Div('evaluate_steps_de_3', css_class='col-md-10', hidden="true"),

                    Div('implemented_de_9', css_class='col-md-10', hidden="true"),
                    Div('reasons_no_de_9', css_class='col-md-10', hidden="true"),
                    Div('challenges_de_9', css_class='col-md-10', hidden="true"),
                    Div('steps_de_9', css_class='col-md-10 hidden', hidden="true"),
                    Div('evaluate_steps_de_9', css_class='col-md-10', hidden="true"),

                    Div('implemented_de_prep', css_class='col-md-10', hidden="true"),
                    Div('reasons_no_de_prep', css_class='col-md-10', hidden="true"),
                    Div('challenges_de_prep', css_class='col-md-10', hidden="true"),
                    Div('steps_de_prep', css_class='col-md-10 hidden', hidden="true"),
                    Div('evaluate_steps_de_prep', css_class='col-md-10', hidden="true"),


                    css_class='row card-body',
                ),
            ),
            Fieldset(
                None,
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Grade 2') + '</h4>')
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th bgcolor="D7E1E8" width="25%"></th>'),
                    HTML('<th bgcolor="D7E1E8" width="25%" align="center"><label> <font color="navy" size="3">' + _(
                        'The number of lessons completed till february') + '</font></label> </th>'),
                    HTML('<th bgcolor="D7E1E8" width="25%" align="center"><label> <font color="navy" size="3">' + _(
                        'Number of lessons accomplished through distance education in march') + '</font></label> </th>'),
                    HTML('<th bgcolor="D7E1E8" width="25%"align="center"><label> <font color="navy" size="3">' + _(
                        'Number of lessons remaining') + '</font></label> </th>'),

                    HTML('</table>'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge-form-2 badge-pill">' + _(
                        'Arabic') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c2_ara_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c2_ara_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c2_ara_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge-form-2 badge-pill">' + _(
                        'English') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c2_eng_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c2_eng_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c2_eng_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge-form-2 badge-pill">' + _(
                        'Frensh') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c2_fr_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c2_fr_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c2_fr_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge-form-2 badge-pill">' + _(
                        'Math') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c2_math_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c2_math_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c2_math_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge-form-2 badge-pill">' + _(
                        'Science') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c2_sc_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c2_sc_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c2_sc_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge-form-2 badge-pill">' + _(
                        'Civic Education') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c2_civic_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c2_civic_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c2_civic_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge-form-2 badge-pill">' + _(
                        'Geography') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c2_geo_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c2_geo_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c2_geo_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row card-body',
                ),
                css_class='bd-callout bd-callout-warning'
            ),
            FormActions(
                Submit('save', _('Save')),
            )
        )

        def save(self, instance=None, request=None):
            instance = super(Classroom_Form, self).save()
            messages.success(request, _('Your data has been sent successfully to the server'))

        class Meta:
            model = Evaluation
            fields = ('c2_eng_completed', 'c2_eng_completed_de', 'c2_eng_remaining_de',
                      'c2_fr_completed', 'c2_fr_completed_de', 'c2_fr_remaining_de',
                      'c2_math_completed', 'c2_math_completed_de', 'c2_math_remaining_de',
                      'c2_sc_completed', 'c2_sc_completed_de', 'c2_sc_remaining_de',
                      'c2_ara_completed', 'c2_ara_completed_de', 'c2_ara_remaining_de',
                      'c2_civic_completed', 'c2_civic_completed_de', 'c2_civic_remaining_de',
                      'c2_geo_completed', 'c2_geo_completed_de', 'c2_geo_remaining_de',
                      'owner', 'school', 'education_year','total_teaching_days', 'implemented_de', 'reasons_no_de',
                      'challenges_de', 'steps_de', 'evaluate_steps_de', 'other_notes_de',
                      )
            initial_fields = fields
            widgets = {}

        class Media:
            js = ()


class Classroom_Form_c1(forms.ModelForm):
    class Meta:
        model = Evaluation
        exclude = ()

    def __init__(self, *args, **kwargs):
        super(Classroom_Form_c1, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-3 create-label'
        self.helper.field_class = 'col-md-9'
        self.fields['c1_eng_completed'].label = False
        self.fields['c1_eng_completed_de'].label = False
        self.fields['c1_eng_remaining_de'].label = False
        self.fields['c1_fr_completed'].label = False
        self.fields['c1_fr_completed_de'].label = False
        self.fields['c1_fr_remaining_de'].label = False
        self.fields['c1_math_completed'].label = False
        self.fields['c1_math_completed_de'].label = False
        self.fields['c1_math_remaining_de'].label = False
        self.fields['c1_sc_completed'].label = False
        self.fields['c1_sc_completed_de'].label = False
        self.fields['c1_sc_remaining_de'].label = False
        self.fields['c1_ara_completed'].label = False
        self.fields['c1_ara_completed_de'].label = False
        self.fields['c1_ara_remaining_de'].label = False
        self.fields['c1_civic_completed'].label = False
        self.fields['c1_civic_completed_de'].label = False
        self.fields['c1_civic_remaining_de'].label = False
        self.fields['c1_geo_completed'].label = False
        self.fields['c1_geo_completed_de'].label = False
        self.fields['c1_geo_remaining_de'].label = False
        self.helper.layout = Layout(
            Fieldset(
                None,
                Div(
                    Div('owner', css_class='col-md-10', hidden="true"),
                    Div('school', css_class='col-md-10', hidden="true"),
                    Div('education_year', css_class='col-md-10', hidden="true"),

                    Div('total_teaching_days', css_class='col-md-10', hidden="true"),
                    Div('implemented_de', css_class='col-md-10', hidden="true"),
                    Div('reasons_no_de', css_class='col-md-10', hidden="true"),
                    Div('challenges_de', css_class='col-md-10', hidden="true"),
                    Div('steps_de', css_class='col-md-10 hidden', hidden="true"),
                    Div('evaluate_steps_de', css_class='col-md-10', hidden="true"),
                    Div('other_notes_de', css_class='col-md-10', hidden="true"),

                    Div('total_teaching_days_tillnow', css_class='col-md-10', hidden="true"),
                    Div('implemented_de_2', css_class='col-md-10', hidden="true"),
                    Div('reasons_no_de_2', css_class='col-md-10', hidden="true"),
                    Div('challenges_de_2', css_class='col-md-10', hidden="true"),
                    Div('steps_de_2', css_class='col-md-10 hidden', hidden="true"),
                    Div('evaluate_steps_de_2', css_class='col-md-10', hidden="true"),

                    Div('implemented_de_3', css_class='col-md-10', hidden="true"),
                    Div('reasons_no_de_3', css_class='col-md-10', hidden="true"),
                    Div('challenges_de_3', css_class='col-md-10', hidden="true"),
                    Div('steps_de_3', css_class='col-md-10 hidden', hidden="true"),
                    Div('evaluate_steps_de_3', css_class='col-md-10', hidden="true"),

                    Div('implemented_de_9', css_class='col-md-10', hidden="true"),
                    Div('reasons_no_de_9', css_class='col-md-10', hidden="true"),
                    Div('challenges_de_9', css_class='col-md-10', hidden="true"),
                    Div('steps_de_9', css_class='col-md-10 hidden', hidden="true"),
                    Div('evaluate_steps_de_9', css_class='col-md-10', hidden="true"),

                    Div('implemented_de_prep', css_class='col-md-10', hidden="true"),
                    Div('reasons_no_de_prep', css_class='col-md-10', hidden="true"),
                    Div('challenges_de_prep', css_class='col-md-10', hidden="true"),
                    Div('steps_de_prep', css_class='col-md-10 hidden', hidden="true"),
                    Div('evaluate_steps_de_prep', css_class='col-md-10', hidden="true"),

                    css_class='row card-body',
                ),
            ),
            Fieldset(
                None,
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Grade 1') + '</h4>')
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th bgcolor="D7E1E8" width="25%"></th>'),
                    HTML('<th bgcolor="D7E1E8" width="25%" align="center"><label > <font color="navy" size="3" >' + _(
                        'The number of lessons completed till february') + '</font></label> </th>'),
                    HTML('<th bgcolor="D7E1E8" width="25%" align="center"><label> <font color="navy" size="3">' + _(
                        'Number of lessons accomplished through distance education in march') + '</font></label> </th>'),
                    HTML('<th bgcolor="D7E1E8" width="25%"align="center"><label> <font color="navy" size="3">' + _(
                        'Number of lessons remaining') + '</font></label> </th>'),

                    HTML('</table>'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge-form-2 badge-pill">' + _(
                        'Arabic') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c1_ara_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c1_ara_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c1_ara_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge-form-2 badge-pill">' + _(
                        'English') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c1_eng_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c1_eng_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c1_eng_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge-form-2 badge-pill">' + _(
                        'Frensh') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c1_fr_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c1_fr_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c1_fr_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge-form-2 badge-pill">' + _(
                        'Math') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c1_math_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c1_math_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c1_math_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge-form-2 badge-pill">' + _(
                        'Science') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c1_sc_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c1_sc_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c1_sc_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge-form-2 badge-pill">' + _(
                        'Civic Education') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c1_civic_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c1_civic_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c1_civic_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge-form-2 badge-pill">' + _(
                        'Geography') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c1_geo_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c1_geo_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c1_geo_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row card-body',
                ),
                css_class='bd-callout bd-callout-warning'
            ),
            FormActions(
                Submit('save', _('Save')),
            )
        )

        def save(self, instance=None, request=None):
            instance = super(Classroom_Form_c1, self).save()
            messages.success(request, _('Your data has been sent successfully to the server'))

        class Meta:
            model = Evaluation
            fields = ('c1_eng_completed', 'c1_eng_completed_de', 'c1_eng_remaining_de',
                      'c1_fr_completed', 'c1_fr_completed_de', 'c1_fr_remaining_de',
                      'c1_math_completed', 'c1_math_completed_de', 'c1_math_remaining_de',
                      'c1_sc_completed', 'c1_sc_completed_de', 'c1_sc_remaining_de',
                      'c1_ara_completed', 'c1_ara_completed_de', 'c1_ara_remaining_de',
                      'c1_civic_completed', 'c1_civic_completed_de', 'c1_civic_remaining_de',
                      'c1_geo_completed', 'c1_geo_completed_de', 'c1_geo_remaining_de',
                      'owner', 'school', 'education_year','total_teaching_days', 'implemented_de', 'reasons_no_de',
                      'challenges_de', 'steps_de', 'evaluate_steps_de', 'other_notes_de',
                      )
            initial_fields = fields
            widgets = {}

        class Media:
            js = ()


class Classroom_Form_c3(forms.ModelForm):
    class Meta:
        model = Evaluation
        exclude = ()

    def __init__(self, *args, **kwargs):
        super(Classroom_Form_c3, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-3 create-label'
        self.helper.field_class = 'col-md-9'
        self.fields['c3_eng_completed'].label = False
        self.fields['c3_eng_completed_de'].label = False
        self.fields['c3_eng_remaining_de'].label = False
        self.fields['c3_fr_completed'].label = False
        self.fields['c3_fr_completed_de'].label = False
        self.fields['c3_fr_remaining_de'].label = False
        self.fields['c3_math_completed'].label = False
        self.fields['c3_math_completed_de'].label = False
        self.fields['c3_math_remaining_de'].label = False
        self.fields['c3_sc_completed'].label = False
        self.fields['c3_sc_completed_de'].label = False
        self.fields['c3_sc_remaining_de'].label = False
        self.fields['c3_ara_completed'].label = False
        self.fields['c3_ara_completed_de'].label = False
        self.fields['c3_ara_remaining_de'].label = False
        self.fields['c3_civic_completed'].label = False
        self.fields['c3_civic_completed_de'].label = False
        self.fields['c3_civic_remaining_de'].label = False
        self.fields['c3_geo_completed'].label = False
        self.fields['c3_geo_completed_de'].label = False
        self.fields['c3_geo_remaining_de'].label = False
        self.helper.layout = Layout(
            Fieldset(
                None,
                Div(
                    Div('owner', css_class='col-md-10', hidden="true"),
                    Div('school', css_class='col-md-10', hidden="true"),
                    Div('education_year', css_class='col-md-10', hidden="true"),

                    Div('total_teaching_days', css_class='col-md-10', hidden="true"),
                    Div('implemented_de', css_class='col-md-10', hidden="true"),
                    Div('reasons_no_de', css_class='col-md-10', hidden="true"),
                    Div('challenges_de', css_class='col-md-10', hidden="true"),
                    Div('steps_de', css_class='col-md-10 hidden', hidden="true"),
                    Div('evaluate_steps_de', css_class='col-md-10', hidden="true"),
                    Div('other_notes_de', css_class='col-md-10', hidden="true"),

                    Div('total_teaching_days_tillnow', css_class='col-md-10', hidden="true"),
                    Div('implemented_de_2', css_class='col-md-10', hidden="true"),
                    Div('reasons_no_de_2', css_class='col-md-10', hidden="true"),
                    Div('challenges_de_2', css_class='col-md-10', hidden="true"),
                    Div('steps_de_2', css_class='col-md-10 hidden', hidden="true"),
                    Div('evaluate_steps_de_2', css_class='col-md-10', hidden="true"),

                    Div('implemented_de_3', css_class='col-md-10', hidden="true"),
                    Div('reasons_no_de_3', css_class='col-md-10', hidden="true"),
                    Div('challenges_de_3', css_class='col-md-10', hidden="true"),
                    Div('steps_de_3', css_class='col-md-10 hidden', hidden="true"),
                    Div('evaluate_steps_de_3', css_class='col-md-10', hidden="true"),

                    Div('implemented_de_9', css_class='col-md-10', hidden="true"),
                    Div('reasons_no_de_9', css_class='col-md-10', hidden="true"),
                    Div('challenges_de_9', css_class='col-md-10', hidden="true"),
                    Div('steps_de_9', css_class='col-md-10 hidden', hidden="true"),
                    Div('evaluate_steps_de_9', css_class='col-md-10', hidden="true"),

                    Div('implemented_de_prep', css_class='col-md-10', hidden="true"),
                    Div('reasons_no_de_prep', css_class='col-md-10', hidden="true"),
                    Div('challenges_de_prep', css_class='col-md-10', hidden="true"),
                    Div('steps_de_prep', css_class='col-md-10 hidden', hidden="true"),
                    Div('evaluate_steps_de_prep', css_class='col-md-10', hidden="true"),

                    css_class='row card-body',
                ),
            ),
            Fieldset(
                None,
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Grade 3') + '</h4>')
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th bgcolor="D7E1E8" width="25%"></th>'),
                    HTML('<th bgcolor="D7E1E8" width="25%" align="center"><label> <font color="navy" size="3">' + _(
                        'The number of lessons completed till february') + '</font></label> </th>'),
                    HTML('<th bgcolor="D7E1E8" width="25%" align="center"><label> <font color="navy" size="3">' + _(
                        'Number of lessons accomplished through distance education in march') + '</font></label> </th>'),
                    HTML('<th bgcolor="D7E1E8" width="25%"align="center"><label> <font color="navy" size="3">' + _(
                        'Number of lessons remaining') + '</font></label> </th>'),

                    HTML('</table>'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge-form-2 badge-pill">' + _(
                        'Arabic') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c3_ara_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c3_ara_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c3_ara_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge-form-2 badge-pill">' + _(
                        'English') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c3_eng_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c3_eng_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c3_eng_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge-form-2 badge-pill">' + _(
                        'Frensh') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c3_fr_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c3_fr_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c3_fr_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge-form-2 badge-pill">' + _(
                        'Math') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c3_math_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c3_math_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c3_math_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge-form-2 badge-pill">' + _(
                        'Science') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c3_sc_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c3_sc_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c3_sc_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge-form-2 badge-pill">' + _(
                        'Civic Education') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c3_civic_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c3_civic_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c3_civic_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge-form-2 badge-pill">' + _(
                        'Geography') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c3_geo_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c3_geo_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c3_geo_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row card-body',
                ),
                css_class='bd-callout bd-callout-warning'
            ),
            FormActions(
                Submit('save', _('Save')),
            )
        )

        def save(self, instance=None, request=None):
            instance = super(Classroom_Form_c3, self).save()
            messages.success(request, _('Your data has been sent successfully to the server'))

        class Meta:
            model = Evaluation
            fields = ('c3_eng_completed', 'c3_eng_completed_de', 'c3_eng_remaining_de',
                      'c3_fr_completed', 'c3_fr_completed_de', 'c3_fr_remaining_de',
                      'c3_math_completed', 'c3_math_completed_de', 'c3_math_remaining_de',
                      'c3_sc_completed', 'c3_sc_completed_de', 'c3_sc_remaining_de',
                      'c3_ara_completed', 'c3_ara_completed_de', 'c3_ara_remaining_de',
                      'c3_civic_completed', 'c3_civic_completed_de', 'c3_civic_remaining_de',
                      'c3_geo_completed', 'c3_geo_completed_de', 'c3_geo_remaining_de',
                      'owner', 'school', 'education_year','total_teaching_days', 'implemented_de', 'reasons_no_de',
                      'challenges_de', 'steps_de', 'evaluate_steps_de', 'other_notes_de',
                      )
            initial_fields = fields
            widgets = {}

        class Media:
            js = ()


class Classroom_Form_c4(forms.ModelForm):
    class Meta:
        model = Evaluation
        exclude = ()

    def __init__(self, *args, **kwargs):
        super(Classroom_Form_c4, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-3 create-label'
        self.helper.field_class = 'col-md-9'
        self.fields['c4_eng_completed'].label = False
        self.fields['c4_eng_completed_de'].label = False
        self.fields['c4_eng_remaining_de'].label = False
        self.fields['c4_fr_completed'].label = False
        self.fields['c4_fr_completed_de'].label = False
        self.fields['c4_fr_remaining_de'].label = False
        self.fields['c4_math_completed'].label = False
        self.fields['c4_math_completed_de'].label = False
        self.fields['c4_math_remaining_de'].label = False
        self.fields['c4_sc_completed'].label = False
        self.fields['c4_sc_completed_de'].label = False
        self.fields['c4_sc_remaining_de'].label = False
        self.fields['c4_ara_completed'].label = False
        self.fields['c4_ara_completed_de'].label = False
        self.fields['c4_ara_remaining_de'].label = False
        self.fields['c4_civic_completed'].label = False
        self.fields['c4_civic_completed_de'].label = False
        self.fields['c4_civic_remaining_de'].label = False
        self.fields['c4_geo_completed'].label = False
        self.fields['c4_geo_completed_de'].label = False
        self.fields['c4_geo_remaining_de'].label = False
        self.helper.layout = Layout(
            Fieldset(
                None,
                Div(
                    Div('owner', css_class='col-md-10', hidden="true"),
                    Div('school', css_class='col-md-10', hidden="true"),
                    Div('education_year', css_class='col-md-10', hidden="true"),

                    Div('total_teaching_days', css_class='col-md-10', hidden="true"),
                    Div('implemented_de', css_class='col-md-10', hidden="true"),
                    Div('reasons_no_de', css_class='col-md-10', hidden="true"),
                    Div('challenges_de', css_class='col-md-10', hidden="true"),
                    Div('steps_de', css_class='col-md-10 hidden', hidden="true"),
                    Div('evaluate_steps_de', css_class='col-md-10', hidden="true"),
                    Div('other_notes_de', css_class='col-md-10', hidden="true"),

                    Div('total_teaching_days_tillnow', css_class='col-md-10', hidden="true"),
                    Div('implemented_de_2', css_class='col-md-10', hidden="true"),
                    Div('reasons_no_de_2', css_class='col-md-10', hidden="true"),
                    Div('challenges_de_2', css_class='col-md-10', hidden="true"),
                    Div('steps_de_2', css_class='col-md-10 hidden', hidden="true"),
                    Div('evaluate_steps_de_2', css_class='col-md-10', hidden="true"),

                    Div('implemented_de_3', css_class='col-md-10', hidden="true"),
                    Div('reasons_no_de_3', css_class='col-md-10', hidden="true"),
                    Div('challenges_de_3', css_class='col-md-10', hidden="true"),
                    Div('steps_de_3', css_class='col-md-10 hidden', hidden="true"),
                    Div('evaluate_steps_de_3', css_class='col-md-10', hidden="true"),

                    Div('implemented_de_9', css_class='col-md-10', hidden="true"),
                    Div('reasons_no_de_9', css_class='col-md-10', hidden="true"),
                    Div('challenges_de_9', css_class='col-md-10', hidden="true"),
                    Div('steps_de_9', css_class='col-md-10 hidden', hidden="true"),
                    Div('evaluate_steps_de_9', css_class='col-md-10', hidden="true"),

                    Div('implemented_de_prep', css_class='col-md-10', hidden="true"),
                    Div('reasons_no_de_prep', css_class='col-md-10', hidden="true"),
                    Div('challenges_de_prep', css_class='col-md-10', hidden="true"),
                    Div('steps_de_prep', css_class='col-md-10 hidden', hidden="true"),
                    Div('evaluate_steps_de_prep', css_class='col-md-10', hidden="true"),

                    css_class='row card-body',
                ),
            ),
            Fieldset(
                None,
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Grade 4') + '</h4>')
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th bgcolor="D7E1E8" width="25%"></th>'),
                    HTML('<th bgcolor="D7E1E8" width="25%" align="center"><label> <font color="navy" size="3">' + _(
                        'The number of lessons completed till february') + '</font></label> </th>'),
                    HTML('<th bgcolor="D7E1E8" width="25%" align="center"><label> <font color="navy" size="3">' + _(
                        'Number of lessons accomplished through distance education in march') + '</font></label> </th>'),
                    HTML('<th bgcolor="D7E1E8" width="25%"align="center"><label> <font color="navy" size="3">' + _(
                        'Number of lessons remaining') + '</font></label> </th>'),

                    HTML('</table>'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge-form-2 badge-pill">' + _(
                        'Arabic') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c4_ara_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c4_ara_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c4_ara_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge-form-2 badge-pill">' + _(
                        'English') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c4_eng_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c4_eng_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c4_eng_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge-form-2 badge-pill">' + _(
                        'Frensh') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c4_fr_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c4_fr_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c4_fr_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge-form-2 badge-pill">' + _(
                        'Math') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c4_math_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c4_math_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c4_math_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge-form-2 badge-pill">' + _(
                        'Science') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c4_sc_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c4_sc_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c4_sc_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge-form-2 badge-pill">' + _(
                        'Civic Education') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c4_civic_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c4_civic_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c4_civic_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge-form-2 badge-pill">' + _(
                        'Geography') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c4_geo_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c4_geo_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c4_geo_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row card-body',
                ),
                css_class='bd-callout bd-callout-warning'
            ),
            FormActions(
                Submit('save', _('Save')),
            )
        )

        def save(self, instance=None, request=None):
            instance = super(Classroom_Form_c4, self).save()
            messages.success(request, _('Your data has been sent successfully to the server'))

        class Meta:
            model = Evaluation
            fields = ('c4_eng_completed', 'c4_eng_completed_de', 'c4_eng_remaining_de',
                      'c4_fr_completed', 'c4_fr_completed_de', 'c4_fr_remaining_de',
                      'c4_math_completed', 'c4_math_completed_de', 'c4_math_remaining_de',
                      'c4_sc_completed', 'c4_sc_completed_de', 'c4_sc_remaining_de',
                      'c4_ara_completed', 'c4_ara_completed_de', 'c4_ara_remaining_de',
                      'c4_civic_completed', 'c4_civic_completed_de', 'c4_civic_remaining_de',
                      'c4_geo_completed', 'c4_geo_completed_de', 'c4_geo_remaining_de',
                      'owner', 'school', 'education_year', 'total_teaching_days', 'implemented_de', 'reasons_no_de',
                      'challenges_de', 'steps_de', 'evaluate_steps_de', 'other_notes_de',
                      )
            initial_fields = fields
            widgets = {}

        class Media:
            js = ()


class Classroom_Form_c5(forms.ModelForm):
    class Meta:
        model = Evaluation
        exclude = ()

    def __init__(self, *args, **kwargs):
        super(Classroom_Form_c5, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-3 create-label'
        self.helper.field_class = 'col-md-9'
        self.fields['c5_eng_completed'].label = False
        self.fields['c5_eng_completed_de'].label = False
        self.fields['c5_eng_remaining_de'].label = False
        self.fields['c5_fr_completed'].label = False
        self.fields['c5_fr_completed_de'].label = False
        self.fields['c5_fr_remaining_de'].label = False
        self.fields['c5_math_completed'].label = False
        self.fields['c5_math_completed_de'].label = False
        self.fields['c5_math_remaining_de'].label = False
        self.fields['c5_sc_completed'].label = False
        self.fields['c5_sc_completed_de'].label = False
        self.fields['c5_sc_remaining_de'].label = False
        self.fields['c5_ara_completed'].label = False
        self.fields['c5_ara_completed_de'].label = False
        self.fields['c5_ara_remaining_de'].label = False
        self.fields['c5_civic_completed'].label = False
        self.fields['c5_civic_completed_de'].label = False
        self.fields['c5_civic_remaining_de'].label = False
        self.fields['c5_geo_completed'].label = False
        self.fields['c5_geo_completed_de'].label = False
        self.fields['c5_geo_remaining_de'].label = False
        self.helper.layout = Layout(
            Fieldset(
                None,
                Div(
                    Div('owner', css_class='col-md-10', hidden="true"),
                    Div('school', css_class='col-md-10', hidden="true"),
                    Div('education_year', css_class='col-md-10', hidden="true"),

                    Div('total_teaching_days', css_class='col-md-10', hidden="true"),
                    Div('implemented_de', css_class='col-md-10', hidden="true"),
                    Div('reasons_no_de', css_class='col-md-10', hidden="true"),
                    Div('challenges_de', css_class='col-md-10', hidden="true"),
                    Div('steps_de', css_class='col-md-10 hidden', hidden="true"),
                    Div('evaluate_steps_de', css_class='col-md-10', hidden="true"),
                    Div('other_notes_de', css_class='col-md-10', hidden="true"),

                    Div('total_teaching_days_tillnow', css_class='col-md-10', hidden="true"),
                    Div('implemented_de_2', css_class='col-md-10', hidden="true"),
                    Div('reasons_no_de_2', css_class='col-md-10', hidden="true"),
                    Div('challenges_de_2', css_class='col-md-10', hidden="true"),
                    Div('steps_de_2', css_class='col-md-10 hidden', hidden="true"),
                    Div('evaluate_steps_de_2', css_class='col-md-10', hidden="true"),

                    Div('implemented_de_3', css_class='col-md-10', hidden="true"),
                    Div('reasons_no_de_3', css_class='col-md-10', hidden="true"),
                    Div('challenges_de_3', css_class='col-md-10', hidden="true"),
                    Div('steps_de_3', css_class='col-md-10 hidden', hidden="true"),
                    Div('evaluate_steps_de_3', css_class='col-md-10', hidden="true"),

                    Div('implemented_de_9', css_class='col-md-10', hidden="true"),
                    Div('reasons_no_de_9', css_class='col-md-10', hidden="true"),
                    Div('challenges_de_9', css_class='col-md-10', hidden="true"),
                    Div('steps_de_9', css_class='col-md-10 hidden', hidden="true"),
                    Div('evaluate_steps_de_9', css_class='col-md-10', hidden="true"),

                    Div('implemented_de_prep', css_class='col-md-10', hidden="true"),
                    Div('reasons_no_de_prep', css_class='col-md-10', hidden="true"),
                    Div('challenges_de_prep', css_class='col-md-10', hidden="true"),
                    Div('steps_de_prep', css_class='col-md-10 hidden', hidden="true"),
                    Div('evaluate_steps_de_prep', css_class='col-md-10', hidden="true"),

                    css_class='row card-body',
                ),
            ),
            Fieldset(
                None,
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Grade 5') + '</h4>')
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th bgcolor="D7E1E8" width="25%"></th>'),
                    HTML('<th bgcolor="D7E1E8" width="25%" align="center"><label> <font color="navy" size="3">' + _(
                        'The number of lessons completed till february') + '</font></label> </th>'),
                    HTML('<th bgcolor="D7E1E8" width="25%" align="center"><label> <font color="navy" size="3">' + _(
                        'Number of lessons accomplished through distance education in march') + '</font></label> </th>'),
                    HTML('<th bgcolor="D7E1E8" width="25%"align="center"><label> <font color="navy" size="3">' + _(
                        'Number of lessons remaining') + '</font></label> </th>'),

                    HTML('</table>'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge-form-2 badge-pill">' + _(
                        'Arabic') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c5_ara_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c5_ara_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c5_ara_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge-form-2 badge-pill">' + _(
                        'English') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c5_eng_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c5_eng_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c5_eng_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge-form-2 badge-pill">' + _(
                        'Frensh') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c5_fr_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c5_fr_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c5_fr_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge-form-2 badge-pill">' + _(
                        'Math') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c5_math_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c5_math_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c5_math_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge-form-2 badge-pill">' + _(
                        'Science') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c5_sc_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c5_sc_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c5_sc_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge-form-2 badge-pill">' + _(
                        'Civic Education') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c5_civic_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c5_civic_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c5_civic_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge-form-2 badge-pill">' + _(
                        'Geography') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c5_geo_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c5_geo_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c5_geo_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row card-body',
                ),
                css_class='bd-callout bd-callout-warning'
            ),
            FormActions(
                Submit('save', _('Save')),
            )
        )

        def save(self, instance=None, request=None):
            instance = super(Classroom_Form_c5, self).save()
            messages.success(request, _('Your data has been sent successfully to the server'))

        class Meta:
            model = Evaluation
            fields = ('c5_eng_completed', 'c5_eng_completed_de', 'c5_eng_remaining_de',
                      'c5_fr_completed', 'c5_fr_completed_de', 'c5_fr_remaining_de',
                      'c5_math_completed', 'c5_math_completed_de', 'c5_math_remaining_de',
                      'c5_sc_completed', 'c5_sc_completed_de', 'c5_sc_remaining_de',
                      'c5_ara_completed', 'c5_ara_completed_de', 'c5_ara_remaining_de',
                      'c5_civic_completed', 'c5_civic_completed_de', 'c5_civic_remaining_de',
                      'c5_geo_completed', 'c5_geo_completed_de', 'c5_geo_remaining_de',
                      'owner', 'school', 'education_year','total_teaching_days', 'implemented_de', 'reasons_no_de',
                      'challenges_de', 'steps_de', 'evaluate_steps_de', 'other_notes_de',
                      )
            initial_fields = fields
            widgets = {}

        class Media:
            js = ()


class Classroom_Form_c6(forms.ModelForm):
    class Meta:
        model = Evaluation
        exclude = ()

    def __init__(self, *args, **kwargs):
        super(Classroom_Form_c6, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-3 create-label'
        self.helper.field_class = 'col-md-9'
        self.fields['c6_eng_completed'].label = False
        self.fields['c6_eng_completed_de'].label = False
        self.fields['c6_eng_remaining_de'].label = False
        self.fields['c6_fr_completed'].label = False
        self.fields['c6_fr_completed_de'].label = False
        self.fields['c6_fr_remaining_de'].label = False
        self.fields['c6_math_completed'].label = False
        self.fields['c6_math_completed_de'].label = False
        self.fields['c6_math_remaining_de'].label = False
        self.fields['c6_sc_completed'].label = False
        self.fields['c6_sc_completed_de'].label = False
        self.fields['c6_sc_remaining_de'].label = False
        self.fields['c6_ara_completed'].label = False
        self.fields['c6_ara_completed_de'].label = False
        self.fields['c6_ara_remaining_de'].label = False
        self.fields['c6_civic_completed'].label = False
        self.fields['c6_civic_completed_de'].label = False
        self.fields['c6_civic_remaining_de'].label = False
        self.fields['c6_geo_completed'].label = False
        self.fields['c6_geo_completed_de'].label = False
        self.fields['c6_geo_remaining_de'].label = False
        self.helper.layout = Layout(
            Fieldset(
                None,
                Div(
                    Div('owner', css_class='col-md-10', hidden="true"),
                    Div('school', css_class='col-md-10', hidden="true"),
                    Div('education_year', css_class='col-md-10', hidden="true"),

                    Div('total_teaching_days', css_class='col-md-10', hidden="true"),
                    Div('implemented_de', css_class='col-md-10', hidden="true"),
                    Div('reasons_no_de', css_class='col-md-10', hidden="true"),
                    Div('challenges_de', css_class='col-md-10', hidden="true"),
                    Div('steps_de', css_class='col-md-10 hidden', hidden="true"),
                    Div('evaluate_steps_de', css_class='col-md-10', hidden="true"),
                    Div('other_notes_de', css_class='col-md-10', hidden="true"),

                    Div('total_teaching_days_tillnow', css_class='col-md-10', hidden="true"),
                    Div('implemented_de_2', css_class='col-md-10', hidden="true"),
                    Div('reasons_no_de_2', css_class='col-md-10', hidden="true"),
                    Div('challenges_de_2', css_class='col-md-10', hidden="true"),
                    Div('steps_de_2', css_class='col-md-10 hidden', hidden="true"),
                    Div('evaluate_steps_de_2', css_class='col-md-10', hidden="true"),

                    Div('implemented_de_3', css_class='col-md-10', hidden="true"),
                    Div('reasons_no_de_3', css_class='col-md-10', hidden="true"),
                    Div('challenges_de_3', css_class='col-md-10', hidden="true"),
                    Div('steps_de_3', css_class='col-md-10 hidden', hidden="true"),
                    Div('evaluate_steps_de_3', css_class='col-md-10', hidden="true"),

                    Div('implemented_de_9', css_class='col-md-10', hidden="true"),
                    Div('reasons_no_de_9', css_class='col-md-10', hidden="true"),
                    Div('challenges_de_9', css_class='col-md-10', hidden="true"),
                    Div('steps_de_9', css_class='col-md-10 hidden', hidden="true"),
                    Div('evaluate_steps_de_9', css_class='col-md-10', hidden="true"),

                    Div('implemented_de_prep', css_class='col-md-10', hidden="true"),
                    Div('reasons_no_de_prep', css_class='col-md-10', hidden="true"),
                    Div('challenges_de_prep', css_class='col-md-10', hidden="true"),
                    Div('steps_de_prep', css_class='col-md-10 hidden', hidden="true"),
                    Div('evaluate_steps_de_prep', css_class='col-md-10', hidden="true"),

                    css_class='row card-body',
                ),
            ),
            Fieldset(
                None,
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Grade 6') + '</h4>')
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th bgcolor="D7E1E8" width="25%"></th>'),
                    HTML('<th bgcolor="D7E1E8" width="25%" align="center"><label> <font color="navy" size="3">' + _(
                        'The number of lessons completed till february') + '</font></label> </th>'),
                    HTML('<th bgcolor="D7E1E8" width="25%" align="center"><label> <font color="navy" size="3">' + _(
                        'Number of lessons accomplished through distance education in march') + '</font></label> </th>'),
                    HTML('<th bgcolor="D7E1E8" width="25%"align="center"><label> <font color="navy" size="3">' + _(
                        'Number of lessons remaining') + '</font></label> </th>'),

                    HTML('</table>'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge-form-2 badge-pill">' + _(
                        'Arabic') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c6_ara_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c6_ara_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c6_ara_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge-form-2 badge-pill">' + _(
                        'English') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c6_eng_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c6_eng_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c6_eng_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge-form-2 badge-pill">' + _(
                        'Frensh') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c6_fr_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c6_fr_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c6_fr_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge-form-2 badge-pill">' + _(
                        'Math') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c6_math_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c6_math_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c6_math_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge-form-2 badge-pill">' + _(
                        'Science') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c6_sc_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c6_sc_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c6_sc_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge-form-2 badge-pill">' + _(
                        'Civic Education') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c6_civic_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c6_civic_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c6_civic_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge-form-2 badge-pill">' + _(
                        'Geography') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c6_geo_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c6_geo_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c6_geo_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row card-body',
                ),
                css_class='bd-callout bd-callout-warning'
            ),
            FormActions(
                Submit('save', _('Save')),
            )
        )

        def save(self, instance=None, request=None):
            instance = super(Classroom_Form_c6, self).save()
            messages.success(request, _('Your data has been sent successfully to the server'))

        class Meta:
            model = Evaluation
            fields = ('c6_eng_completed', 'c6_eng_completed_de', 'c6_eng_remaining_de',
                      'c6_fr_completed', 'c6_fr_completed_de', 'c6_fr_remaining_de',
                      'c6_math_completed', 'c6_math_completed_de', 'c6_math_remaining_de',
                      'c6_sc_completed', 'c6_sc_completed_de', 'c6_sc_remaining_de',
                      'c6_ara_completed', 'c6_ara_completed_de', 'c6_ara_remaining_de',
                      'c6_civic_completed', 'c6_civic_completed_de', 'c6_civic_remaining_de',
                      'c6_geo_completed', 'c6_geo_completed_de', 'c6_geo_remaining_de',
                      'owner', 'school', 'education_year','total_teaching_days', 'implemented_de', 'reasons_no_de',
                      'challenges_de', 'steps_de', 'evaluate_steps_de', 'other_notes_de',
                      )
            initial_fields = fields
            widgets = {}

        class Media:
            js = ()


class Classroom_Form_c7(forms.ModelForm):
    class Meta:
        model = Evaluation
        exclude = ()

    def __init__(self, *args, **kwargs):
        super(Classroom_Form_c7, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-3 create-label'
        self.helper.field_class = 'col-md-9'
        self.fields['c7_eng_completed'].label = False
        self.fields['c7_eng_completed_de'].label = False
        self.fields['c7_eng_remaining_de'].label = False
        self.fields['c7_fr_completed'].label = False
        self.fields['c7_fr_completed_de'].label = False
        self.fields['c7_fr_remaining_de'].label = False
        self.fields['c7_math_completed'].label = False
        self.fields['c7_math_completed_de'].label = False
        self.fields['c7_math_remaining_de'].label = False
        self.fields['c7_sc_completed'].label = False
        self.fields['c7_sc_completed_de'].label = False
        self.fields['c7_sc_remaining_de'].label = False
        self.fields['c7_ara_completed'].label = False
        self.fields['c7_ara_completed_de'].label = False
        self.fields['c7_ara_remaining_de'].label = False
        self.fields['c7_civic_completed'].label = False
        self.fields['c7_civic_completed_de'].label = False
        self.fields['c7_civic_remaining_de'].label = False
        self.fields['c7_geo_completed'].label = False
        self.fields['c7_geo_completed_de'].label = False
        self.fields['c7_geo_remaining_de'].label = False

        self.fields['c7_his_completed'].label = False
        self.fields['c7_his_completed_de'].label = False
        self.fields['c7_his_remaining_de'].label = False

        self.fields['c7_che_completed'].label = False
        self.fields['c7_che_completed_de'].label = False
        self.fields['c7_che_remaining_de'].label = False

        self.fields['c7_phy_completed'].label = False
        self.fields['c7_phy_completed_de'].label = False
        self.fields['c7_phy_remaining_de'].label = False
        self.helper.layout = Layout(
            Fieldset(
                None,
                Div(
                    Div('owner', css_class='col-md-10', hidden="true"),
                    Div('school', css_class='col-md-10', hidden="true"),
                    Div('education_year', css_class='col-md-10', hidden="true"),

                    Div('total_teaching_days', css_class='col-md-10', hidden="true"),
                    Div('implemented_de', css_class='col-md-10', hidden="true"),
                    Div('reasons_no_de', css_class='col-md-10', hidden="true"),
                    Div('challenges_de', css_class='col-md-10', hidden="true"),
                    Div('steps_de', css_class='col-md-10 hidden', hidden="true"),
                    Div('evaluate_steps_de', css_class='col-md-10', hidden="true"),
                    Div('other_notes_de', css_class='col-md-10', hidden="true"),

                    Div('total_teaching_days_tillnow', css_class='col-md-10', hidden="true"),
                    Div('implemented_de_2', css_class='col-md-10', hidden="true"),
                    Div('reasons_no_de_2', css_class='col-md-10', hidden="true"),
                    Div('challenges_de_2', css_class='col-md-10', hidden="true"),
                    Div('steps_de_2', css_class='col-md-10 hidden', hidden="true"),
                    Div('evaluate_steps_de_2', css_class='col-md-10', hidden="true"),

                    Div('implemented_de_3', css_class='col-md-10', hidden="true"),
                    Div('reasons_no_de_3', css_class='col-md-10', hidden="true"),
                    Div('challenges_de_3', css_class='col-md-10', hidden="true"),
                    Div('steps_de_3', css_class='col-md-10 hidden', hidden="true"),
                    Div('evaluate_steps_de_3', css_class='col-md-10', hidden="true"),

                    Div('implemented_de_9', css_class='col-md-10', hidden="true"),
                    Div('reasons_no_de_9', css_class='col-md-10', hidden="true"),
                    Div('challenges_de_9', css_class='col-md-10', hidden="true"),
                    Div('steps_de_9', css_class='col-md-10 hidden', hidden="true"),
                    Div('evaluate_steps_de_9', css_class='col-md-10', hidden="true"),

                    Div('implemented_de_prep', css_class='col-md-10', hidden="true"),
                    Div('reasons_no_de_prep', css_class='col-md-10', hidden="true"),
                    Div('challenges_de_prep', css_class='col-md-10', hidden="true"),
                    Div('steps_de_prep', css_class='col-md-10 hidden', hidden="true"),
                    Div('evaluate_steps_de_prep', css_class='col-md-10', hidden="true"),

                    css_class='row card-body',
                ),
            ),
            Fieldset(
                None,
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Grade 7') + '</h4>')
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th bgcolor="D7E1E8" width="25%"></th>'),
                    HTML('<th bgcolor="D7E1E8" width="25%" align="center"><label> <font color="navy" size="3">' + _(
                        'The number of lessons completed till february') + '</font></label> </th>'),
                    HTML('<th bgcolor="D7E1E8" width="25%" align="center"><label> <font color="navy" size="3">' + _(
                        'Number of lessons accomplished through distance education in march') + '</font></label> </th>'),
                    HTML('<th bgcolor="D7E1E8" width="25%"align="center"><label> <font color="navy" size="3">' + _(
                        'Number of lessons remaining') + '</font></label> </th>'),

                    HTML('</table>'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge-form-2 badge-pill">' + _(
                        'Arabic') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c7_ara_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c7_ara_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c7_ara_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge-form-2 badge-pill">' + _(
                        'English') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c7_eng_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c7_eng_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c7_eng_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge-form-2 badge-pill">' + _(
                        'Frensh') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c7_fr_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c7_fr_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c7_fr_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge-form-2 badge-pill">' + _(
                        'Math') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c7_math_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c7_math_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c7_math_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge-form-2 badge-pill">' + _(
                        'Science') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c7_sc_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c7_sc_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c7_sc_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge-form-2 badge-pill">' + _(
                        'Civic Education') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c7_civic_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c7_civic_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c7_civic_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge-form-2 badge-pill">' + _(
                        'Geography') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c7_geo_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c7_geo_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c7_geo_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge-form-2 badge-pill">' + _(
                        'Physics') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c7_phy_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c7_phy_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c7_phy_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge-form-2 badge-pill">' + _(
                        'Chemistry') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c7_che_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c7_che_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c7_che_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge-form-2 badge-pill">' + _(
                        'History') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c7_his_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c7_his_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c7_his_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row card-body',
                ),
                css_class='bd-callout bd-callout-warning'
            ),
            FormActions(
                Submit('save', _('Save')),
            )
        )

        def save(self, instance=None, request=None):
            instance = super(Classroom_Form_c7, self).save()
            messages.success(request, _('Your data has been sent successfully to the server'))

        class Meta:
            model = Evaluation
            fields = ('c7_eng_completed', 'c7_eng_completed_de', 'c7_eng_remaining_de',
                      'c7_fr_completed', 'c7_fr_completed_de', 'c7_fr_remaining_de',
                      'c7_math_completed', 'c7_math_completed_de', 'c7_math_remaining_de',
                      'c7_sc_completed', 'c7_sc_completed_de', 'c7_sc_remaining_de',
                      'c7_ara_completed', 'c7_ara_completed_de', 'c7_ara_remaining_de',
                      'c7_civic_completed', 'c7_civic_completed_de', 'c7_civic_remaining_de',
                      'c7_geo_completed', 'c7_geo_completed_de', 'c7_geo_remaining_de',
                      'c7_his_completed', 'c7_his_completed_de', 'c7_his_remaining_de',
                      'c7_che_completed', 'c7_che_completed_de', 'c7_che_remaining_de',
                      'c7_phy_completed', 'c7_phy_completed_de', 'c7_phy_remaining_de',
                      'owner', 'school', 'education_year','total_teaching_days', 'implemented_de', 'reasons_no_de',
                      'challenges_de', 'steps_de', 'evaluate_steps_de', 'other_notes_de',
                      )
            initial_fields = fields
            widgets = {}

        class Media:
            js = ()


class Classroom_Form_c8(forms.ModelForm):
    class Meta:
        model = Evaluation
        exclude = ()

    def __init__(self, *args, **kwargs):
        super(Classroom_Form_c8, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-3 create-label'
        self.helper.field_class = 'col-md-9'
        self.fields['c8_eng_completed'].label = False
        self.fields['c8_eng_completed_de'].label = False
        self.fields['c8_eng_remaining_de'].label = False
        self.fields['c8_fr_completed'].label = False
        self.fields['c8_fr_completed_de'].label = False
        self.fields['c8_fr_remaining_de'].label = False
        self.fields['c8_math_completed'].label = False
        self.fields['c8_math_completed_de'].label = False
        self.fields['c8_math_remaining_de'].label = False
        self.fields['c8_sc_completed'].label = False
        self.fields['c8_sc_completed_de'].label = False
        self.fields['c8_sc_remaining_de'].label = False
        self.fields['c8_ara_completed'].label = False
        self.fields['c8_ara_completed_de'].label = False
        self.fields['c8_ara_remaining_de'].label = False
        self.fields['c8_civic_completed'].label = False
        self.fields['c8_civic_completed_de'].label = False
        self.fields['c8_civic_remaining_de'].label = False
        self.fields['c8_geo_completed'].label = False
        self.fields['c8_geo_completed_de'].label = False
        self.fields['c8_geo_remaining_de'].label = False
        self.fields['c8_his_completed'].label = False
        self.fields['c8_his_completed_de'].label = False
        self.fields['c8_his_remaining_de'].label = False

        self.fields['c8_che_completed'].label = False
        self.fields['c8_che_completed_de'].label = False
        self.fields['c8_che_remaining_de'].label = False

        self.fields['c8_phy_completed'].label = False
        self.fields['c8_phy_completed_de'].label = False
        self.fields['c8_phy_remaining_de'].label = False
        self.helper.layout = Layout(
            Fieldset(
                None,
                Div(
                    Div('owner', css_class='col-md-10', hidden="true"),
                    Div('school', css_class='col-md-10', hidden="true"),
                    Div('education_year', css_class='col-md-10', hidden="true"),

                    Div('total_teaching_days', css_class='col-md-10', hidden="true"),
                    Div('implemented_de', css_class='col-md-10', hidden="true"),
                    Div('reasons_no_de', css_class='col-md-10', hidden="true"),
                    Div('challenges_de', css_class='col-md-10', hidden="true"),
                    Div('steps_de', css_class='col-md-10 hidden', hidden="true"),
                    Div('evaluate_steps_de', css_class='col-md-10', hidden="true"),
                    Div('other_notes_de', css_class='col-md-10', hidden="true"),

                    Div('total_teaching_days_tillnow', css_class='col-md-10', hidden="true"),
                    Div('implemented_de_2', css_class='col-md-10', hidden="true"),
                    Div('reasons_no_de_2', css_class='col-md-10', hidden="true"),
                    Div('challenges_de_2', css_class='col-md-10', hidden="true"),
                    Div('steps_de_2', css_class='col-md-10 hidden', hidden="true"),
                    Div('evaluate_steps_de_2', css_class='col-md-10', hidden="true"),

                    Div('implemented_de_3', css_class='col-md-10', hidden="true"),
                    Div('reasons_no_de_3', css_class='col-md-10', hidden="true"),
                    Div('challenges_de_3', css_class='col-md-10', hidden="true"),
                    Div('steps_de_3', css_class='col-md-10 hidden', hidden="true"),
                    Div('evaluate_steps_de_3', css_class='col-md-10', hidden="true"),

                    Div('implemented_de_9', css_class='col-md-10', hidden="true"),
                    Div('reasons_no_de_9', css_class='col-md-10', hidden="true"),
                    Div('challenges_de_9', css_class='col-md-10', hidden="true"),
                    Div('steps_de_9', css_class='col-md-10 hidden', hidden="true"),
                    Div('evaluate_steps_de_9', css_class='col-md-10', hidden="true"),

                    Div('implemented_de_prep', css_class='col-md-10', hidden="true"),
                    Div('reasons_no_de_prep', css_class='col-md-10', hidden="true"),
                    Div('challenges_de_prep', css_class='col-md-10', hidden="true"),
                    Div('steps_de_prep', css_class='col-md-10 hidden', hidden="true"),
                    Div('evaluate_steps_de_prep', css_class='col-md-10', hidden="true"),

                    css_class='row card-body',
                ),
            ),
            Fieldset(
                None,
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Grade 8') + '</h4>')
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th bgcolor="D7E1E8" width="25%"></th>'),
                    HTML('<th bgcolor="D7E1E8" width="25%" align="center"><label> <font color="navy" size="3">' + _(
                        'The number of lessons completed till february') + '</font></label> </th>'),
                    HTML('<th bgcolor="D7E1E8" width="25%" align="center"><label> <font color="navy" size="3">' + _(
                        'Number of lessons accomplished through distance education in march') + '</font></label> </th>'),
                    HTML('<th bgcolor="D7E1E8" width="25%"align="center"><label> <font color="navy" size="3">' + _(
                        'Number of lessons remaining') + '</font></label> </th>'),

                    HTML('</table>'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge-form-2 badge-pill">' + _(
                        'Arabic') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c8_ara_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c8_ara_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c8_ara_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge-form-2 badge-pill">' + _(
                        'English') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c8_eng_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c8_eng_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c8_eng_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge-form-2 badge-pill">' + _(
                        'Frensh') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c8_fr_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c8_fr_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c8_fr_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge-form-2 badge-pill">' + _(
                        'Math') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c8_math_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c8_math_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c8_math_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge-form-2 badge-pill">' + _(
                        'Science') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c8_sc_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c8_sc_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c8_sc_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge-form-2 badge-pill">' + _(
                        'Civic Education') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c8_civic_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c8_civic_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c8_civic_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge-form-2 badge-pill">' + _(
                        'Geography') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c8_geo_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c8_geo_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c8_geo_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge-form-2 badge-pill">' + _(
                        'Physics') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c8_phy_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c8_phy_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c8_phy_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge-form-2 badge-pill">' + _(
                        'Chemistry') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c8_che_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c8_che_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c8_che_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge-form-2 badge-pill">' + _(
                        'History') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c8_his_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c8_his_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c8_his_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row card-body',
                ),
                css_class='bd-callout bd-callout-warning'
            ),
            FormActions(
                Submit('save', _('Save')),
            )
        )

        def save(self, instance=None, request=None):
            instance = super(Classroom_Form_c8, self).save()
            messages.success(request, _('Your data has been sent successfully to the server'))

        class Meta:
            model = Evaluation
            fields = ('c8_eng_completed', 'c8_eng_completed_de', 'c8_eng_remaining_de',
                      'c8_fr_completed', 'c8_fr_completed_de', 'c8_fr_remaining_de',
                      'c8_math_completed', 'c8_math_completed_de', 'c8_math_remaining_de',
                      'c8_sc_completed', 'c8_sc_completed_de', 'c8_sc_remaining_de',
                      'c8_ara_completed', 'c8_ara_completed_de', 'c8_ara_remaining_de',
                      'c8_civic_completed', 'c8_civic_completed_de', 'c8_civic_remaining_de',
                      'c8_geo_completed', 'c8_geo_completed_de', 'c8_geo_remaining_de',
                      'c8_his_completed', 'c8_his_completed_de', 'c8_his_remaining_de',
                      'c8_che_completed', 'c8_che_completed_de', 'c8_che_remaining_de',
                      'c8_phy_completed', 'c8_phy_completed_de', 'c8_phy_remaining_de',
                      'owner', 'school', 'education_year','total_teaching_days', 'implemented_de', 'reasons_no_de',
                      'challenges_de', 'steps_de', 'evaluate_steps_de', 'other_notes_de',
                      )
            initial_fields = fields
            widgets = {}

        class Media:
            js = ()


class Classroom_Form_c9(forms.ModelForm):
    class Meta:
        model = Evaluation
        exclude = ()

    def __init__(self, *args, **kwargs):
        super(Classroom_Form_c9, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-3 create-label'
        self.helper.field_class = 'col-md-9'
        self.fields['c9_eng_completed'].label = False
        self.fields['c9_eng_completed_de'].label = False
        self.fields['c9_eng_remaining_de'].label = False
        self.fields['c9_fr_completed'].label = False
        self.fields['c9_fr_completed_de'].label = False
        self.fields['c9_fr_remaining_de'].label = False
        self.fields['c9_math_completed'].label = False
        self.fields['c9_math_completed_de'].label = False
        self.fields['c9_math_remaining_de'].label = False
        self.fields['c9_sc_completed'].label = False
        self.fields['c9_sc_completed_de'].label = False
        self.fields['c9_sc_remaining_de'].label = False
        self.fields['c9_ara_completed'].label = False
        self.fields['c9_ara_completed_de'].label = False
        self.fields['c9_ara_remaining_de'].label = False
        self.fields['c9_civic_completed'].label = False
        self.fields['c9_civic_completed_de'].label = False
        self.fields['c9_civic_remaining_de'].label = False
        self.fields['c9_geo_completed'].label = False
        self.fields['c9_geo_completed_de'].label = False
        self.fields['c9_geo_remaining_de'].label = False
        self.fields['c9_his_completed'].label = False
        self.fields['c9_his_completed_de'].label = False
        self.fields['c9_his_remaining_de'].label = False

        self.fields['c9_che_completed'].label = False
        self.fields['c9_che_completed_de'].label = False
        self.fields['c9_che_remaining_de'].label = False

        self.fields['c9_phy_completed'].label = False
        self.fields['c9_phy_completed_de'].label = False
        self.fields['c9_phy_remaining_de'].label = False
        self.fields['c9_total_std'].label = False
        self.fields['c9_total_std_de'].label = False
        self.fields['c9_total_teachers'].label = False
        self.fields['c9_total_teachers_de'].label = False
        self.helper.layout = Layout(
            Fieldset(
                None,
                Div(
                    Div('owner', css_class='col-md-10', hidden="true"),
                    Div('school', css_class='col-md-10', hidden="true"),
                    Div('education_year', css_class='col-md-10', hidden="true"),

                    Div('total_teaching_days', css_class='col-md-10', hidden="true"),
                    Div('implemented_de', css_class='col-md-10', hidden="true"),
                    Div('reasons_no_de', css_class='col-md-10', hidden="true"),
                    Div('challenges_de', css_class='col-md-10', hidden="true"),
                    Div('steps_de', css_class='col-md-10 hidden', hidden="true"),
                    Div('evaluate_steps_de', css_class='col-md-10', hidden="true"),
                    Div('other_notes_de', css_class='col-md-10', hidden="true"),

                    Div('total_teaching_days_tillnow', css_class='col-md-10', hidden="true"),
                    Div('implemented_de_2', css_class='col-md-10', hidden="true"),
                    Div('reasons_no_de_2', css_class='col-md-10', hidden="true"),
                    Div('challenges_de_2', css_class='col-md-10', hidden="true"),
                    Div('steps_de_2', css_class='col-md-10 hidden', hidden="true"),
                    Div('evaluate_steps_de_2', css_class='col-md-10', hidden="true"),

                    Div('implemented_de_3', css_class='col-md-10', hidden="true"),
                    Div('reasons_no_de_3', css_class='col-md-10', hidden="true"),
                    Div('challenges_de_3', css_class='col-md-10', hidden="true"),
                    Div('steps_de_3', css_class='col-md-10 hidden', hidden="true"),
                    Div('evaluate_steps_de_3', css_class='col-md-10', hidden="true"),

                    Div('implemented_de_9', css_class='col-md-10', hidden="true"),
                    Div('reasons_no_de_9', css_class='col-md-10', hidden="true"),
                    Div('challenges_de_9', css_class='col-md-10', hidden="true"),
                    Div('steps_de_9', css_class='col-md-10 hidden', hidden="true"),
                    Div('evaluate_steps_de_9', css_class='col-md-10', hidden="true"),

                    Div('implemented_de_prep', css_class='col-md-10', hidden="true"),
                    Div('reasons_no_de_prep', css_class='col-md-10', hidden="true"),
                    Div('challenges_de_prep', css_class='col-md-10', hidden="true"),
                    Div('steps_de_prep', css_class='col-md-10 hidden', hidden="true"),
                    Div('evaluate_steps_de_prep', css_class='col-md-10', hidden="true"),

                    css_class='row card-body',
                ),
            ),
            Fieldset(
                None,
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Grade 9') + '</h4>')
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th bgcolor="D7E1E8" width="25%"></th>'),
                    HTML('<th bgcolor="D7E1E8" width="25%" align="center"><label> <font color="navy" size="3">' + _(
                        'The number of lessons completed till february') + '</font></label> </th>'),
                    HTML('<th bgcolor="D7E1E8" width="25%" align="center"><label> <font color="navy" size="3">' + _(
                        'Number of lessons accomplished through distance education in march') + '</font></label> </th>'),
                    HTML('<th bgcolor="D7E1E8" width="25%"align="center"><label> <font color="navy" size="3">' + _(
                        'Number of lessons remaining') + '</font></label> </th>'),

                    HTML('</table>'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge-form-2 badge-pill">' + _(
                        'Arabic') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c9_ara_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c9_ara_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c9_ara_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge-form-2 badge-pill">' + _(
                        'English') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c9_eng_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c9_eng_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c9_eng_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge-form-2 badge-pill">' + _(
                        'Frensh') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c9_fr_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c9_fr_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c9_fr_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge-form-2 badge-pill">' + _(
                        'Math') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c9_math_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c9_math_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c9_math_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge-form-2 badge-pill">' + _(
                        'Science') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c9_sc_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c9_sc_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c9_sc_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge-form-2 badge-pill">' + _(
                        'Civic Education') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c9_civic_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c9_civic_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c9_civic_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge-form-2 badge-pill">' + _(
                        'Geography') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c9_geo_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c9_geo_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c9_geo_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge-form-2 badge-pill">' + _(
                        'Physics') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c9_phy_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c9_phy_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c9_phy_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge-form-2 badge-pill">' + _(
                        'Chemistry') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c9_che_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c9_che_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c9_che_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge-form-2 badge-pill">' + _(
                        'History') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c9_his_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c9_his_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('c9_his_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row card-body',
                ),
                Div(
                  None,
                ),
                Div(
                    HTML('<label> ' + _('Total of teachers') + '</label>'),
                    Div('c9_total_teachers', css_class='col-md-5'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<label> ' + _('Number of teachers who have committed to distance education') + '</label>'),
                    Div('c9_total_teachers_de', css_class='col-md-5'),
                    css_class='row card-body',
                ),
                Div(
                  HTML('<label> '+_('Total of students')+'</label>'),
                  Div('c9_total_std', css_class='col-md-4'),
                  css_class='row card-body',
                ),
                Div(
                    HTML('<label> ' + _('Total of students they follow distance education') + '</label>'),
                    Div('c9_total_std_de', css_class='col-md-4'),
                    css_class='row card-body',
                ),

                css_class='bd-callout bd-callout-warning'
            ),
            FormActions(
                Submit('save', _('Save')),
            )
        )

        def save(self, instance=None, request=None):
            instance = super(Classroom_Form_c9, self).save()
            messages.success(request, _('Your data has been sent successfully to the server'))

        class Meta:
            model = Evaluation
            fields = ('c9_eng_completed', 'c9_eng_completed_de', 'c9_eng_remaining_de',
                      'c9_fr_completed', 'c9_fr_completed_de', 'c9_fr_remaining_de',
                      'c9_math_completed', 'c9_math_completed_de', 'c9_math_remaining_de',
                      'c9_sc_completed', 'c9_sc_completed_de', 'c9_sc_remaining_de',
                      'c9_ara_completed', 'c9_ara_completed_de', 'c9_ara_remaining_de',
                      'c9_civic_completed', 'c9_civic_completed_de', 'c9_civic_remaining_de',
                      'c9_geo_completed', 'c9_geo_completed_de', 'c9_geo_remaining_de',
                      'c9_his_completed', 'c9_his_completed_de', 'c9_his_remaining_de',
                      'c9_che_completed', 'c9_che_completed_de', 'c9_che_remaining_de',
                      'c9_phy_completed', 'c9_phy_completed_de', 'c9_phy_remaining_de',
                      'c9_total_std', 'c9_total_std_de',
                      'c9_total_teachers', 'c9_total_teachers_de',
                      'owner', 'school', 'education_year','total_teaching_days', 'implemented_de', 'reasons_no_de',
                      'challenges_de', 'steps_de', 'evaluate_steps_de', 'other_notes_de',
                      )
            initial_fields = fields
            widgets = {}

        class Media:
            js = ()


class Classroom_Form_cprep(forms.ModelForm):
    class Meta:
        model = Evaluation
        exclude = ()

    def __init__(self, *args, **kwargs):
        super(Classroom_Form_cprep, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-3 create-label'
        self.helper.field_class = 'col-md-9'
        self.fields['cprep_eng_completed'].label = False
        self.fields['cprep_eng_completed_de'].label = False
        self.fields['cprep_eng_remaining_de'].label = False
        self.fields['cprep_fr_completed'].label = False
        self.fields['cprep_fr_completed_de'].label = False
        self.fields['cprep_fr_remaining_de'].label = False
        self.fields['cprep_math_completed'].label = False
        self.fields['cprep_math_completed_de'].label = False
        self.fields['cprep_math_remaining_de'].label = False
        self.fields['cprep_sc_completed'].label = False
        self.fields['cprep_sc_completed_de'].label = False
        self.fields['cprep_sc_remaining_de'].label = False
        self.fields['cprep_ara_completed'].label = False
        self.fields['cprep_ara_completed_de'].label = False
        self.fields['cprep_ara_remaining_de'].label = False
        self.fields['cprep_civic_completed'].label = False
        self.fields['cprep_civic_completed_de'].label = False
        self.fields['cprep_civic_remaining_de'].label = False
        self.fields['cprep_geo_completed'].label = False
        self.fields['cprep_geo_completed_de'].label = False
        self.fields['cprep_geo_remaining_de'].label = False
        self.helper.layout = Layout(
            Fieldset(
                None,
                Div(
                    Div('owner', css_class='col-md-10', hidden="true"),
                    Div('school', css_class='col-md-10', hidden="true"),
                    Div('education_year', css_class='col-md-10', hidden="true"),

                    Div('total_teaching_days', css_class='col-md-10', hidden="true"),
                    Div('implemented_de', css_class='col-md-10', hidden="true"),
                    Div('reasons_no_de', css_class='col-md-10', hidden="true"),
                    Div('challenges_de', css_class='col-md-10', hidden="true"),
                    Div('steps_de', css_class='col-md-10 hidden', hidden="true"),
                    Div('evaluate_steps_de', css_class='col-md-10', hidden="true"),

                    Div('total_teaching_days_tillnow', css_class='col-md-10', hidden="true"),
                    Div('implemented_de_2', css_class='col-md-10', hidden="true"),
                    Div('reasons_no_de_2', css_class='col-md-10', hidden="true"),
                    Div('challenges_de_2', css_class='col-md-10', hidden="true"),
                    Div('steps_de_2', css_class='col-md-10 hidden', hidden="true"),
                    Div('evaluate_steps_de_2', css_class='col-md-10', hidden="true"),

                    Div('implemented_de_3', css_class='col-md-10', hidden="true"),
                    Div('reasons_no_de_3', css_class='col-md-10', hidden="true"),
                    Div('challenges_de_3', css_class='col-md-10', hidden="true"),
                    Div('steps_de_3', css_class='col-md-10 hidden', hidden="true"),
                    Div('evaluate_steps_de_3', css_class='col-md-10', hidden="true"),

                    Div('implemented_de_9', css_class='col-md-10', hidden="true"),
                    Div('reasons_no_de_9', css_class='col-md-10', hidden="true"),
                    Div('challenges_de_9', css_class='col-md-10', hidden="true"),
                    Div('steps_de_9', css_class='col-md-10 hidden', hidden="true"),
                    Div('evaluate_steps_de_9', css_class='col-md-10', hidden="true"),

                    Div('implemented_de_prep', css_class='col-md-10', hidden="true"),
                    Div('reasons_no_de_prep', css_class='col-md-10', hidden="true"),
                    Div('challenges_de_prep', css_class='col-md-10', hidden="true"),
                    Div('steps_de_prep', css_class='col-md-10 hidden', hidden="true"),
                    Div('evaluate_steps_de_prep', css_class='col-md-10', hidden="true"),
                    Div('other_notes_de', css_class='col-md-10', hidden="true"),

                    css_class='row card-body',
                ),
            ),
            Fieldset(
                None,
                Div(
                    HTML('<h4 id="alternatives-to-hidden-labels">' + _('Grade Prep-Ece') + '</h4>')
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th bgcolor="D7E1E8" width="25%"></th>'),
                    HTML('<th bgcolor="D7E1E8" width="25%" align="center"><label> <font color="navy" size="3">' + _(
                        'The number of lessons completed till february') + '</font></label> </th>'),
                    HTML('<th bgcolor="D7E1E8" width="25%" align="center"><label> <font color="navy" size="3">' + _(
                        'Number of lessons accomplished through distance education in march') + '</font></label> </th>'),
                    HTML('<th bgcolor="D7E1E8" width="25%"align="center"><label> <font color="navy" size="3">' + _(
                        'Number of lessons remaining') + '</font></label> </th>'),

                    HTML('</table>'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge-form-2 badge-pill">' + _(
                        'Arabic') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('cprep_ara_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('cprep_ara_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('cprep_ara_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge-form-2 badge-pill">' + _(
                        'English') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('cprep_eng_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('cprep_eng_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('cprep_eng_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge-form-2 badge-pill">' + _(
                        'Frensh') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('cprep_fr_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('cprep_fr_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('cprep_fr_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge-form-2 badge-pill">' + _(
                        'Math') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('cprep_math_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('cprep_math_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('cprep_math_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge-form-2 badge-pill">' + _(
                        'Science') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('cprep_sc_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('cprep_sc_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('cprep_sc_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge-form-2 badge-pill">' + _(
                        'Civic Education') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('cprep_civic_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('cprep_civic_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('cprep_civic_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<table border="1" width="100%">'),
                    HTML('<th width="25%" align="center"><span class="badge-form-2 badge-pill">' + _(
                        'Geography') + '</span></th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('cprep_geo_completed', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('cprep_geo_completed_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('<th width="25%" align="center">'),
                    Div('cprep_geo_remaining_de', css_class='col-md-10'),
                    HTML('</th>'),
                    HTML('</table>'),
                    css_class='row card-body',
                ),
                css_class='bd-callout bd-callout-warning'
            ),
            FormActions(
                Submit('save', _('Save')),
            )
        )

        def save(self, instance=None, request=None):
            instance = super(Classroom_Form_cprep, self).save()
            messages.success(request, _('Your data has been sent successfully to the server'))

        class Meta:
            model = Evaluation
            fields = ('cprep_eng_completed', 'cprep_eng_completed_de', 'cprep_eng_remaining_de',
                      'cprep_fr_completed', 'cprep_fr_completed_de', 'cprep_fr_remaining_de',
                      'cprep_math_completed', 'cprep_math_completed_de', 'cprep_math_remaining_de',
                      'cprep_sc_completed', 'cprep_sc_completed_de', 'cprep_sc_remaining_de',
                      'cprep_ara_completed', 'cprep_ara_completed_de', 'cprep_ara_remaining_de',
                      'cprep_civic_completed', 'cprep_civic_completed_de', 'cprep_civic_remaining_de',
                      'cprep_geo_completed', 'cprep_geo_completed_de', 'cprep_geo_remaining_de',
                      'owner', 'school', 'education_year','total_teaching_days', 'implemented_de', 'reasons_no_de',
                      'challenges_de', 'steps_de', 'evaluate_steps_de', 'other_notes_de',
                      )
            initial_fields = fields
            widgets = {}

        class Media:
            js = ()


class SchoolForm(forms.ModelForm):
    type = forms.ChoiceField(
        label=_("School Type"),
        widget=forms.Select, required=True,
        choices=School.TYPE
    )
    number = forms.IntegerField(
        label=_('School CERD Number'),
        widget=forms.TextInput, required=False
    )
    name = forms.CharField(
        label=_("School name"),
        widget=forms.TextInput, required=True
    )
    director_name = forms.CharField(
        label=_("School director name"),
        widget=forms.TextInput, required=True
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
        widget=forms.NumberInput(attrs=({'maxlength': 12})),
        min_value=0, required=True
    )
    latitude = forms.FloatField(
        label=_('School GPS (latitude)'),
        widget=forms.NumberInput(attrs=({'maxlength': 12})),
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
        widget=forms.TextInput, required=False
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
    number_dirasa_children_disability = forms.IntegerField(
        label=_('Total number of Children With Disability (Dirasa only)'),
        widget=forms.TextInput, required=False
    )
    number_total_children_disability = forms.IntegerField(
        label=_('Total number of Children With Disability (Excluding Dirasa)'),
        widget=forms.TextInput, required=False
    )
    benefit_wfp_service = forms.ChoiceField(
        label=_("Is the school benefiting from WFP services?"),
        widget=forms.Select, required=True,
        choices=School.YES_NO
    )
    wfp_service_type = forms.ChoiceField(
        label=_("Service Type"),
        widget=forms.Select, required=False,
        choices=School.WFP_SERVICE_TYPE
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(SchoolForm, self).__init__(*args, **kwargs)

        is_Kayany = False
        if self.request.user.partner:
            is_Kayany = self.request.user.partner.is_Kayany
        choices = list()
        if not is_Kayany:
            choices.append(('Level one', _('Level one')))
            choices.append(('Level two', _('Level two')))
            choices.append(('Level three', _('Level three')))
            choices.append(('Level four', _('Level four')))
            choices.append(('Level five', _('Level five')))
            choices.append(('Level six', _('Level six')))
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

        self.fields['registration_level'].choices = choices

        instance = kwargs['instance'] if 'instance' in kwargs else ''
        form_action = reverse('schools:school_add')

        if instance:
            form_action = reverse('schools:school_edit', kwargs={'pk': instance.id})
        current_education_year = EducationYear.objects.get(current_year=True)
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
                    css_class='row card-body',
                ),
                Div(
                    HTML('<span class="badge-form badge-pill">4</span>'),
                    Div('director_name', css_class='col-md-3'),
                    HTML('<span class="badge-form badge-pill">5</span>'),
                    Div('land_phone_number', css_class='col-md-3'),
                    HTML('<span class="badge-form badge-pill">6</span>'),
                    Div('email', css_class='col-md-3'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<span class="badge-form badge-pill">7</span>'),
                    Div('governorate', css_class='col-md-3'),
                    HTML('<span class="badge-form badge-pill">8</span>'),
                    Div('district', css_class='col-md-3'),
                    HTML('<span class="badge-form badge-pill">9</span>'),
                    Div('cadaster', css_class='col-md-3'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<span class="badge-form-2 badge-pill">10</span>'),
                    Div('longitude', css_class='col-md-3'),
                    HTML('<span class="badge-form-2 badge-pill">11</span>'),
                    Div('latitude', css_class='col-md-3'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<span class="badge-form-2 badge-pill">12</span>'),
                    Div('is_closed', css_class='col-md-3 '),
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
                Div(
                    HTML('<span class="badge-form badge-pill">1</span>'),
                    Div('benefit_wfp_service', css_class='col-md-3'),
                    HTML('<span class="badge-form badge-pill" id="span_wfp_service_type">2</span>'),
                    Div('wfp_service_type', css_class='col-md-3'),
                    css_class='row card-body',
                ),
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

        benefit_wfp_service = cleaned_data.get('benefit_wfp_service')
        wfp_service_type = cleaned_data.get("wfp_service_type")
        if benefit_wfp_service == "yes" and not wfp_service_type:
            self.add_error('wfp_service_type', 'This field is required')

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
            'number_dirasa_children_disability',
            'number_total_children_disability',
            'type',
            'benefit_wfp_service',
            'wfp_service_type',
        )


class ClubForm(forms.ModelForm):

    club_name = forms.CharField(
        label=_("Club name"),
        widget=forms.TextInput, required=True
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
        widget=forms.TextInput, required=True
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
        widget=forms.TextInput, required=True
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
        widget=forms.TextInput, required=True
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
