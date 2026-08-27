from django import forms
from django.utils.translation import gettext_lazy as _
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Fieldset, Div, HTML, Submit
from .models import ALPRegistration, ALPTeacher, ALPGrading

class ALPRegistrationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False

        self.helper.layout = Layout(
            Fieldset(
                _('Child Information'),
                Div(
                    Div('child', css_class='form-group col-md-6 mb-0'),
                    Div('school', css_class='form-group col-md-6 mb-0'),
                    css_class='row'
                ),
                Div(
                    Div('student_old', css_class='form-group col-md-6 mb-0'),
                    Div('registration_date', css_class='form-group col-md-6 mb-0'),
                    css_class='row'
                ),
                Div(
                    Div('partner_unique_number', css_class='form-group col-md-12 mb-0'),
                    css_class='row'
                ),
                Div(
                    Div('source_of_identification', css_class='form-group col-md-6 mb-0'),
                    Div('source_of_identification_specify', css_class='form-group col-md-6 mb-0'),
                    css_class='row'
                ),
                Div(
                    Div('cash_support_programmes', css_class='form-group col-md-12 mb-0'),
                    css_class='row'
                ),
            ),
            Fieldset(
                _('Education Status'),
                Div(
                    Div('round', css_class='form-group col-md-6 mb-0'),
                    Div('programme', css_class='form-group col-md-6 mb-0'),
                    css_class='row'
                )
            ),
            Fieldset(
                _('Labour Details'),
                Div(
                    Div('have_labour', css_class='form-group col-md-6 mb-0'),
                    Div('labour_type', css_class='form-group col-md-6 mb-0'),
                    css_class='row'
                ),
                Div(
                    Div('labour_type_specify', css_class='form-group col-md-6 mb-0'),
                    Div('labour_hours', css_class='form-group col-md-6 mb-0'),
                    css_class='row'
                ),
                Div(
                    Div('labour_weekly_income', css_class='form-group col-md-6 mb-0'),
                    Div('labour_condition', css_class='form-group col-md-6 mb-0'),
                    css_class='row'
                )
            )
        )

    class Meta:
        model = ALPRegistration
        fields = [
            'child', 'school', 'student_old', 'registration_date', 'partner_unique_number',
            'source_of_identification', 'source_of_identification_specify', 'cash_support_programmes',
            'round', 'programme',
            'have_labour', 'labour_type', 'labour_type_specify', 'labour_hours', 'labour_weekly_income', 'labour_condition'
        ]
        widgets = {
            'registration_date': forms.DateInput(attrs={'type': 'date'}),
            'source_of_identification_specify': forms.Textarea(attrs={'rows': 2}),
        }

class ALPTeacherForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Div(
                Div('first_name', css_class='form-group col-md-4 mb-0'),
                Div('father_name', css_class='form-group col-md-4 mb-0'),
                Div('last_name', css_class='form-group col-md-4 mb-0'),
                css_class='row'
            ),
            Div(
                Div('phone_number', css_class='form-group col-md-6 mb-0'),
                Div('sex', css_class='form-group col-md-6 mb-0'),
                css_class='row'
            ),
            Div(
                Div('school', css_class='form-group col-md-12 mb-0'),
                css_class='row'
            )
        )

    class Meta:
        model = ALPTeacher
        fields = ['first_name', 'father_name', 'last_name', 'phone_number', 'sex', 'school']

class ALPGradingForm(forms.ModelForm):
    class Meta:
        model = ALPGrading
        fields = ['registration', 'grading_data']
