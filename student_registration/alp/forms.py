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
from student_registration.locations.models import Location
from student_registration.students.widgets import CustomClearableFileInput
from student_registration.mscc.forms import MainForm
from student_registration.students.utils import generate_one_unique_id
from django.contrib import messages
from .serializers import ALPRegistrationSerializer


class ALPSchoolProfileForm(forms.ModelForm):
    """School details that an ALP school focal point may maintain."""

    provided_packages = forms.MultipleChoiceField(
        label=_('Provided Services'),
        choices=School.PROVIDED_PACKAGES,
        widget=forms.CheckboxSelectMultiple,
        required=True,
    )
    programs = forms.MultipleChoiceField(
        label=_('Education Program'),
        choices=tuple(choice for choice in School.PROGRAM if choice[0] != 'ALP'),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )
    offer_digital_learning = forms.ChoiceField(
        label=_('Does the center offer digital learning services?'),
        choices=School.YES_NO,
        required=False,
    )
    have_digital_hub = forms.ChoiceField(
        label=_('Does the center have a digital hub?'),
        choices=School.YES_NO,
        required=False,
    )
    admin_staff_number = forms.IntegerField(
        label=_('Number of Admin staff in the center'),
        min_value=0,
        required=True,
    )
    neaby_phcc = forms.CharField(
        label=_('Nearby PHCC name'),
        required=True,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['governorate'].queryset = Location.objects.filter(
            parent__isnull=True
        ).order_by('name')
        self.fields['district'].queryset = Location.objects.none()
        self.fields['cadaster'].queryset = Location.objects.none()

        governorate_id = self.data.get('governorate') if self.is_bound else None
        district_id = self.data.get('district') if self.is_bound else None
        if not self.is_bound and self.instance.pk:
            governorate_id = self.instance.governorate_id
            district_id = self.instance.district_id

        if governorate_id:
            self.fields['district'].queryset = Location.objects.filter(
                parent_id=governorate_id
            ).order_by('name')
        if district_id:
            self.fields['cadaster'].queryset = Location.objects.filter(
                parent_id=district_id
            ).order_by('name')

        self.helper = FormHelper()
        self.helper.form_action = reverse('alp:school_profile')
        self.helper.layout = Layout(
            Fieldset(
                _('School Information'),
                Div(
                    Div('number', css_class='col-md-4'),
                    Div('name', css_class='col-md-4'),
                    Div('type', css_class='col-md-4'),
                    css_class='row',
                ),
                Div(
                    Div('operating_shift', css_class='col-md-4'),
                    css_class='row',
                ),
                Div(
                    Div('director_name', css_class='col-md-4'),
                    Div('land_phone_number', css_class='col-md-4'),
                    Div('email', css_class='col-md-4'),
                    css_class='row',
                ),
            ),
            Fieldset(
                _('Location'),
                Div(
                    Div('governorate', css_class='col-md-4'),
                    Div('district', css_class='col-md-4'),
                    Div('cadaster', css_class='col-md-4'),
                    css_class='row',
                ),
                Div(
                    Div('longitude', css_class='col-md-6'),
                    Div('latitude', css_class='col-md-6'),
                    css_class='row',
                ),
            ),
            Fieldset(
                _('Provided Services & Programs'),
                Div(
                    Div('provided_packages', css_class='col-md-6 multiple-choice'),
                    Div('programs', css_class='col-md-6 multiple-choice'),
                    css_class='row',
                ),
                Div(
                    Div('offer_digital_learning', css_class='col-md-6'),
                    Div('have_digital_hub', css_class='col-md-6'),
                    css_class='row',
                ),
                Div(
                    Div('admin_staff_number', css_class='col-md-6'),
                    Div('neaby_phcc', css_class='col-md-6'),
                    css_class='row',
                ),
            ),
            FormActions(
                Submit('save', _('Save changes'), css_class='btn btn-primary'),
            ),
        )

    class Meta:
        model = School
        fields = (
            'number', 'name', 'type', 'operating_shift', 'director_name',
            'land_phone_number', 'email', 'governorate', 'district', 'cadaster',
            'longitude', 'latitude',
            'provided_packages', 'programs', 'offer_digital_learning',
            'have_digital_hub', 'admin_staff_number', 'neaby_phcc',
        )
class ALPRegistrationForm(MainForm):
    """ALP registration with the MSCC child, caregiver and ID workflow."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        route = 'alp:registration_edit' if self.instance.pk else 'alp:registration_add'
        route_kwargs = {'pk': self.instance.pk} if self.instance.pk else None
        self.helper.form_action = reverse(route, kwargs=route_kwargs)
        self.fields.pop('school', None)

    @staticmethod
    def _registration_data(request):
        """Return submitted data scoped to the school assigned to the user."""
        data = request.POST.copy()
        if not request.user.is_superuser:
            if request.user.school_id:
                data['school'] = request.user.school_id
            else:
                data.pop('school', None)
        return data

    def save(self, request=None, instance=None):
        data = self._registration_data(request)
        serializer = ALPRegistrationSerializer(
            instance, data=data
        ) if instance else ALPRegistrationSerializer(data=data)
        if not serializer.is_valid():
            messages.warning(request, serializer.errors)
            return None
        registration = serializer.save()
        registration.owner = registration.owner or request.user
        registration.modified_by = request.user
        if not registration.school_id and request.user.school_id:
            registration.school_id = request.user.school_id
        child = registration.child
        if request.FILES.get('child_photo'):
            child.photo = request.FILES['child_photo']
        child.disability_other = request.POST.get('child_disability_other', '')
        child.unicef_id = generate_one_unique_id(
            str(child.pk), child.first_name, child.father_name, child.last_name,
            child.mother_fullname, child.birthdate, child.nationality_name_en,
            child.gender,
        )
        child.save()
        registration.save()
        request.session['instance_id'] = registration.id
        messages.success(request, _('Your data has been sent successfully to the server'))
        return registration

    class Meta:
        model = ALPRegistration
        fields = MainForm.Meta.fields + (
            'school', 'round', 'programme', 'registration_date',
        )
        widgets = {'registration_date': forms.DateInput(attrs={'type': 'date'})}

class ALPTeacherForm(ALPSchoolFilterMixin, forms.ModelForm):
    round = forms.ModelChoiceField(
        queryset=ALPRound.objects.filter(current_year=True), widget=forms.Select,
        label=_('Academic year'),
        empty_label='-------',
        required=True, to_field_name='id',
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
    teacher_assignment_other = forms.CharField(
        label=_('Other teacher assignment'),
        widget=forms.TextInput,
        required=False,
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
        # Let ALPSchoolFilterMixin consume the request.  Popping it here meant
        # that the mixin never saw the user and exposed every school in the
        # ALP teacher form.
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
                    Div('round', css_class='col-md-6'),
                    css_class='row mb-3'
                ),
                Div(
                    Div('teacher_assignment', css_class='col-md-4'),
                    Div('teacher_assignment_other', css_class='col-md-4'),
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
                Div(
                    Div('attach_file_5', css_class='col-md-6'),
                    Div('attach_type_5', css_class='col-md-3'),
                    Div('attach_short_description_5', css_class='col-md-3'),
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
        teacher_assignment_other = cleaned_data.get('teacher_assignment_other')
        teaching_hours_private_school = cleaned_data.get('teaching_hours_private_school')
        teaching_hours_mscc = cleaned_data.get('teaching_hours_mscc')

        if teacher_assignment == 'ALP and private':
            if teaching_hours_private_school is None:
                self.add_error('teaching_hours_private_school', _('This field is required'))
            if teaching_hours_mscc is None:
                self.add_error('teaching_hours_mscc', _('This field is required'))

        if teacher_assignment == 'other' and not teacher_assignment_other:
            self.add_error('teacher_assignment_other', _('This field is required'))

        extra_coaching = cleaned_data.get('extra_coaching')
        extra_coaching_specify = cleaned_data.get('extra_coaching_specify')

        if extra_coaching == 'yes' and not extra_coaching_specify:
            self.add_error('extra_coaching_specify', _('This field is required'))

        return cleaned_data


    class Meta:
        model = ALPTeacher
        fields = [
            'round',
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
            'teacher_assignment_other',
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
