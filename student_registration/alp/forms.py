from django import forms
from django.utils.translation import gettext_lazy as _
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Fieldset, Div, HTML, Submit, Reset
from crispy_forms.bootstrap import FormActions
from django.urls import reverse

from .models import ALPRegistration, ALPTeacher, ALPGrading, ALPRound
from .mixins import ALPSchoolFilterMixin
from student_registration.students.models import AttachmentType, IDType, Nationality, Training
from student_registration.schools.models import School
from student_registration.students.widgets import CustomClearableFileInput


class ALPSchoolProfileForm(forms.ModelForm):
    """School details that an ALP school focal point may maintain."""

    class Meta:
        model = School
        fields = (
            'number', 'name', 'type', 'director_name', 'land_phone_number',
            'email', 'governorate', 'district', 'cadaster', 'longitude',
            'latitude', 'registration_level', 'school_capacity',
        )
        widgets = {'registration_level': forms.CheckboxSelectMultiple}


class ALPRegistrationForm(ALPSchoolFilterMixin, forms.ModelForm):
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

class ALPTeacherForm(ALPSchoolFilterMixin, forms.ModelForm):
    round = forms.ModelChoiceField(
        queryset=ALPRound.objects.filter(current_year=True), widget=forms.Select,
        label=_('Academic year'),
        empty_label='-------',
        required=True, to_field_name='id',
    )
    school = forms.ModelChoiceField(
        queryset=School.objects.filter(is_closed=False).order_by('-id'), widget=forms.Select,
        label=_('School'),
        empty_label='-------',
        required=True, to_field_name='id',
        initial=0
    )
    first_name = forms.CharField(
        label=_("First name"),
        widget=forms.TextInput(attrs={'placeholder': _('e.g. Mohamad')}), required=True
    )
    father_name = forms.CharField(
        label=_("Father name"),
        widget=forms.TextInput(attrs={'placeholder': _('e.g. Ahmad')}), required=True
    )
    last_name = forms.CharField(
        label=_("Last name"),
        widget=forms.TextInput(attrs={'placeholder': _('e.g. Al Sayed')}), required=True
    )
    mother_fullname = forms.CharField(
        label=_('Mother full name'),
        widget=forms.TextInput(attrs={'placeholder': _('e.g. Fatima Al Ali')}),
        required=True
    )
    sex = forms.ChoiceField(
        label=_("Gender"),
        widget=forms.Select, required=False,
        choices=(
            ('', '----------'),
            ('Male', _('Male')),
            ('Female', _('Female')),
        )
    )
    birthdate = forms.DateField(label=_('Birth date'), widget=forms.TextInput(attrs={'type': 'date'}), required=False)
    id_type = forms.ModelChoiceField(
        queryset=IDType.objects.all(),
        widget=forms.Select,
        label=_('ID type'),
        empty_label=_('-------'),
        required=False,
        to_field_name='id',
    )
    id_number = forms.CharField(label=_('ID number'), widget=forms.TextInput, required=False)
    nationality = forms.ModelChoiceField(
        queryset=Nationality.objects.all(),
        widget=forms.Select,
        label=_('Nationality'),
        empty_label=_('-------'),
        required=False,
        to_field_name='id',
    )
    phone_number = forms.RegexField(
        regex=r'^((03)|(70)|(71)|(76)|(78)|(79)|(81))-\d{6}$',
        widget=forms.TextInput(attrs={'placeholder': 'Format: XX-XXXXXX (e.g. 70-123456)'}),
        required=True,
        label=_('Main Phone number'),
        help_text=_('Mobile number of the teacher.')
    )
    email = forms.RegexField(
        regex=r'^\b[\w\.-]+@[\w\.-]+\.\w{2,4}\b',
        widget=forms.TextInput(attrs={'placeholder': _('teacher@example.com')}),
        required=False,
        label=_('Email')
    )
    subjects_provided = forms.MultipleChoiceField(
        label=_('Subjects provided'),
        choices=ALPTeacher.SUBJECT_PROVIDED,
        widget=forms.CheckboxSelectMultiple,
        required=True
    )
    registration_level = forms.MultipleChoiceField(
        label=_('Grade level'),
        choices=ALPTeacher.REGISTRATION_LEVEL,
        widget=forms.CheckboxSelectMultiple,
        required=True
    )
    teacher_assignment = forms.ChoiceField(
        label=_('Teacher Assignment'),
        widget=forms.Select,
        required=False,
        choices=ALPTeacher.TEACHER_ASSIGNMENT,
    )
    teaching_hours_private_school = forms.IntegerField(
        label=_('Number of teaching hours in private school'),
        widget=forms.TextInput, required=False
    )
    teaching_hours_mscc = forms.IntegerField(
        label=_('Number of teaching hours'),
        widget=forms.TextInput, required=False
    )
    trainings = forms.ModelMultipleChoiceField(
        queryset=Training.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label=_('Topics of teacher training'),
    )
    years_of_experience = forms.IntegerField(
        label=_('Years of experience in NFE/FE'),
        required=False,
    )
    training_sessions_attended = forms.IntegerField(
        label=_('Number of teacher training sessions (attended)'),
        widget=forms.TextInput, required=False
    )
    training_date_of_completion = forms.DateField(
        label=_('Date of completion of the listed training'),
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False,
    )
    extra_coaching = forms.ChoiceField(
        label=_('Extra coaching'),
        widget=forms.Select,
        required=True,
        choices=ALPTeacher.YES_NO,
    )
    extra_coaching_specify = forms.CharField(
        label=_('Please specify'),
        widget=forms.TextInput, required=False
    )
    attach_short_description_1 = forms.CharField(
        label=_("Description"),
        widget=forms.TextInput, required=False
    )
    attach_file_1 = forms.FileField(
        label=_("Attachment"),
        required=False,
        widget=CustomClearableFileInput
    )
    attach_type_1 = forms.ModelChoiceField(
        queryset=AttachmentType.objects.all(), widget=forms.Select,
        label=_('Type'),
        empty_label='-------',
        required=False, to_field_name='id',
        initial=0
    )
    attach_short_description_2 = forms.CharField(
        label=_("Description"),
        widget=forms.TextInput, required=False
    )
    attach_file_2 = forms.FileField(
        label=_("Attachment"),
        required=False,
        widget=CustomClearableFileInput
    )
    attach_type_2 = forms.ModelChoiceField(
        queryset=AttachmentType.objects.all(), widget=forms.Select,
        label=_('Type'),
        empty_label='-------',
        required=False, to_field_name='id',
        initial=0
    )
    attach_short_description_3 = forms.CharField(
        label=_("Description"),
        widget=forms.TextInput, required=False
    )
    attach_file_3 = forms.FileField(
        label=_("Attachment"),
        required=False,
        widget=CustomClearableFileInput
    )
    attach_type_3 = forms.ModelChoiceField(
        queryset=AttachmentType.objects.all(), widget=forms.Select,
        label=_('Type'),
        empty_label='-------',
        required=False, to_field_name='id',
        initial=0
    )
    attach_short_description_4 = forms.CharField(
        label=_("Description"),
        widget=forms.TextInput, required=False
    )
    attach_file_4 = forms.FileField(
        label=_("Attachment"),
        required=False,
        widget=CustomClearableFileInput
    )
    attach_type_4 = forms.ModelChoiceField(
        queryset=AttachmentType.objects.all(), widget=forms.Select,
        label=_('Type'),
        empty_label='-------',
        required=False, to_field_name='id',
        initial=0
    )
    attach_short_description_5 = forms.CharField(
        label=_("Description"),
        widget=forms.TextInput, required=False
    )
    attach_file_5 = forms.FileField(
        label=_("Attachment"),
        required=False,
        widget=CustomClearableFileInput
    )
    attach_type_5 = forms.ModelChoiceField(
        queryset=AttachmentType.objects.all(), widget=forms.Select,
        label=_('Type'),
        empty_label='-------',
        required=False, to_field_name='id',
        initial=0
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(ALPTeacherForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.form_show_labels = True

        self.helper.layout = Layout(
            Fieldset(
                _('Identity & Contact'),
                Div(
                    Div('first_name', css_class='col-md-4'),
                    Div('father_name', css_class='col-md-4'),
                    Div('last_name', css_class='col-md-4'),
                    css_class='row mb-3'
                ),
                Div(
                    Div('mother_fullname', css_class='col-md-4'),
                    Div('sex', css_class='col-md-4'),
                    Div('birthdate', css_class='col-md-4'),
                    css_class='row mb-3'
                ),
                Div(
                    Div('nationality', css_class='col-md-4'),
                    Div('id_type', css_class='col-md-4'),
                    Div('id_number', css_class='col-md-4'),
                    css_class='row mb-3'
                ),
                Div(
                    Div('phone_number', css_class='col-md-6'),
                    Div('email', css_class='col-md-6'),
                    css_class='row mb-3'
                ),
            ),
            Fieldset(
                _('Assignment & Qualifications'),
                Div(
                    Div('school', css_class='col-md-6'),
                    Div('round', css_class='col-md-6'),
                    css_class='row mb-3'
                ),
                Div(
                    Div('teacher_assignment', css_class='col-md-4'),
                    Div('teaching_hours_private_school', css_class='col-md-4'),
                    Div('teaching_hours_mscc', css_class='col-md-4'),
                    css_class='row mb-3'
                ),
                Div(
                    Div('subjects_provided', css_class='col-md-6 bg-light p-3 rounded-3'),
                    Div('registration_level', css_class='col-md-6 bg-light p-3 rounded-3'),
                    css_class='row mb-3 mx-0'
                ),
                Div(
                    Div('trainings', css_class='col-md-4'),
                    Div('training_sessions_attended', css_class='col-md-4'),
                    Div('training_date_of_completion', css_class='col-md-4'),
                    css_class='row mb-3'
                ),
                Div(
                    Div('years_of_experience', css_class='col-md-4'),
                    Div('extra_coaching', css_class='col-md-4'),
                    Div('extra_coaching_specify', css_class='col-md-4'),
                    css_class='row mb-3'
                ),
            ),
            Fieldset(
                _('Required Documents'),
                Div(
                    Div('attach_file_1', css_class='col-md-6'),
                    Div('attach_type_1', css_class='col-md-3'),
                    Div('attach_short_description_1', css_class='col-md-3'),
                    css_class='row mb-2 align-items-end'
                ),
                Div(
                    Div('attach_file_2', css_class='col-md-6'),
                    Div('attach_type_2', css_class='col-md-3'),
                    Div('attach_short_description_2', css_class='col-md-3'),
                    css_class='row mb-2 align-items-end'
                ),
                Div(
                    Div('attach_file_3', css_class='col-md-6'),
                    Div('attach_type_3', css_class='col-md-3'),
                    Div('attach_short_description_3', css_class='col-md-3'),
                    css_class='row mb-2 align-items-end'
                ),
                Div(
                    Div('attach_file_4', css_class='col-md-6'),
                    Div('attach_type_4', css_class='col-md-3'),
                    Div('attach_short_description_4', css_class='col-md-3'),
                    css_class='row mb-2 align-items-end'
                ),
            ),
            FormActions(
                Submit('save', _('Complete Registration'), css_class='btn btn-primary px-5 fw-bold shadow-sm'),
                Reset('reset', _('Clear Form'), css_class='btn btn-outline-secondary ms-2'),
                css_class='d-flex justify-content-end border-top pt-4 mt-4'
            )
        )

    def clean(self):
        cleaned_data = super(ALPTeacherForm, self).clean()
        teacher_assignment = cleaned_data.get('teacher_assignment')
        teaching_hours_private_school = cleaned_data.get('teaching_hours_private_school')
        teaching_hours_mscc = cleaned_data.get('teaching_hours_mscc')

        if teacher_assignment == 'Private and Makani':
            if not teaching_hours_private_school:
                self.add_error('teaching_hours_private_school', _('This field is required'))
            if not teaching_hours_mscc:
                self.add_error('teaching_hours_mscc', _('This field is required'))

        extra_coaching = cleaned_data.get('extra_coaching')
        extra_coaching_specify = cleaned_data.get('extra_coaching_specify')

        if extra_coaching == 'yes' and not extra_coaching_specify:
            self.add_error('extra_coaching_specify', _('This field is required'))


    class Meta:
        model = ALPTeacher
        fields = [
            'round',
            'school',
            'first_name',
            'father_name',
            'last_name',
            'mother_fullname',
            'sex',
            'birthdate',
            'id_type',
            'id_number',
            'nationality',
            'phone_number',
            'email',
            'subjects_provided',
            'registration_level',
            'teacher_assignment',
            'teaching_hours_private_school',
            'teaching_hours_mscc',
            'trainings',
            'years_of_experience',
            'training_sessions_attended',
            'training_date_of_completion',
            'extra_coaching',
            'extra_coaching_specify',
            'attach_file_1',
            'attach_type_1',
            'attach_short_description_1',
            'attach_file_2',
            'attach_type_2',
            'attach_short_description_2',
            'attach_file_3',
            'attach_type_3',
            'attach_short_description_3',
            'attach_file_4',
            'attach_type_4',
            'attach_short_description_4',
            'attach_file_5',
            'attach_type_5',
            'attach_short_description_5',
        ]

class ALPGradingForm(forms.ModelForm):
    class Meta:
        model = ALPGrading
        fields = ['registration', 'grading_data']

from .models import ALPGradingDefinition

class ALPGradingDynamicForm(ALPSchoolFilterMixin, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False

        # Load grading definitions
        self.grading_definitions = ALPGradingDefinition.objects.all()

        # Create dynamic fields based on definitions
        grading_data = {}
        if self.instance and self.instance.pk and self.instance.grading_data:
            grading_data = self.instance.grading_data

        layout_fields = [Div('registration', css_class='form-group col-md-12 mb-3')]

        for definition in self.grading_definitions:
            field_name = f"grade_{definition.id}"

            self.fields[field_name] = forms.IntegerField(
                label=definition.material,
                min_value=definition.min_grade,
                max_value=definition.max_grade,
                required=False,
                initial=grading_data.get(str(definition.id))
            )

            layout_fields.append(
                Div(field_name, css_class='form-group col-md-6 mb-3')
            )

        self.helper.layout = Layout(
            Div(*layout_fields, css_class='row')
        )

    def save(self, commit=True):
        instance = super().save(commit=False)

        grading_data = {}
        for definition in self.grading_definitions:
            field_name = f"grade_{definition.id}"
            val = self.cleaned_data.get(field_name)
            if val is not None:
                grading_data[str(definition.id)] = val

        instance.grading_data = grading_data
        if commit:
            instance.save()
        return instance

    class Meta:
        model = ALPGrading
        fields = ['registration']
