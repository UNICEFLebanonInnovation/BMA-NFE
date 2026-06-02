from __future__ import unicode_literals, absolute_import, division

from django.utils.translation import gettext as _
from django import forms
from django.urls import reverse
from datetime import date
from django.contrib import messages
from crispy_forms.helper import FormHelper
from crispy_forms.bootstrap import (
    FormActions,
    InlineCheckboxes
)
from crispy_forms.layout import Layout, Fieldset, Button, Submit, Div, Field, HTML, Reset
from student_registration.students.models import (
    Student,
    Teacher,
    Training,
    AttachmentType
)
from student_registration.schools.models import (
    School,
    PartnerOrganization,
    CLMRound
)

from student_registration.students.serializers import (
    TeacherSerializer
)

from student_registration.users.templatetags.custom_tags import has_group


from django.utils.safestring import mark_safe

from django.forms.widgets import ClearableFileInput


class AdminFileWidget(forms.FileInput):
    """
    A FileField Widget that shows its current value if it has one.
    """
    def __init__(self, attrs={}):
        super(AdminFileWidget, self).__init__(attrs)

    def render(self, name, value, attrs=None):
        output = []
        if value and hasattr(value, "url"):
            output.append('%s <a target="_blank" href="%s">%s</a> <br />%s ' % \
                (_('Currently:'), value.url, value, _('Change:')))
        output.append(super(AdminFileWidget, self).render(name, value, attrs))
        return mark_safe(u''.join(output))


class StudentEnrollmentForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(StudentEnrollmentForm, self).__init__(*args, **kwargs)
    
    def clean(self):
        cleaned_data = super(StudentEnrollmentForm, self).clean()

        birthday_year = cleaned_data.get('birthday_year')
        birthday_month = cleaned_data.get('birthday_month')
        birthday_day = cleaned_data.get('birthday_day')

        # Validate birthday only if all parts are present
        if birthday_year and birthday_month and birthday_day:
            try:
                birth_date = date(
                    int(birthday_year),
                    int(birthday_month),
                    int(birthday_day)
                )
            except (ValueError, TypeError):
                self.add_error('birthday_day', 'Invalid birth date.')
                return cleaned_data

            if birth_date > date.today():
                self.add_error('birthday_year', 'Birth date cannot be after today.')

        return cleaned_data

    class Meta:
        model = Student
        fields = (
            'first_name',
            'father_name',
            'last_name',
            'mother_fullname',
            'sex',
            'birthday_year',
            'birthday_month',
            'birthday_day',
            'nationality',
            'mother_nationality',
            'id_type',
            'id_number',
            'phone',
            'phone_prefix',
            'address',
            'number',
            'unicef_id'
        )


class CustomClearableFileInput(ClearableFileInput):
    template_name = 'students/clearable_file_input.html'


class TeacherForm(forms.ModelForm):
    round = forms.ModelChoiceField(
        queryset=CLMRound.objects.filter(current_round_bridging=True), widget=forms.Select,
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
    sex = forms.ChoiceField(
        label=_("Gender"),
        widget=forms.Select, required=False,
        choices=(
            ('', '----------'),
            ('Male', _('Male')),
            ('Female', _('Female')),
        )
    )
    primary_phone_number = forms.RegexField(
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
        choices=Teacher.SUBJECT_PROVIDED,
        widget=forms.CheckboxSelectMultiple,
        required=True
    )
    registration_level = forms.MultipleChoiceField(
        label=_('Grade level'),
        choices=Teacher.REGISTRATION_LEVEL,
        widget=forms.CheckboxSelectMultiple,
        required=True
    )
    teacher_assignment = forms.ChoiceField(
        label=_('Teacher Assignment'),
        widget=forms.Select,
        required=False,
        choices=Teacher.TEACHER_ASSIGNMENT,
    )
    teaching_hours_private_school = forms.IntegerField(
        label=_('Number of teaching hours in private school'),
        widget=forms.TextInput, required=False
    )
    teaching_hours_dirasa = forms.IntegerField(
        label=_('Number of teaching hours in Dirasa'),
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
        choices=Teacher.YES_NO,
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
        super(TeacherForm, self).__init__(*args, **kwargs)
        is_Kayany = False
        if self.request.user.partner:
            is_Kayany = self.request.user.partner.is_Kayany
        choices = list()
        subject_choices = list()
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

            subject_choices.append(('arabic', _('Arabic')))
            subject_choices.append(('math', _('Math')))
            subject_choices.append(('english', _('English')))
            subject_choices.append(('french', _('French')))
            subject_choices.append(('PSS / Counsellor', _('PSS / Counsellor')))
            subject_choices.append(('Physical Education', _('Physical Education')))
            subject_choices.append(('Art', _('Art')))
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

            subject_choices.append(('arabic', _('Arabic')))
            subject_choices.append(('math', _('Math')))
            subject_choices.append(('english', _('English')))
            subject_choices.append(('Sciences', _('Sciences')))
            subject_choices.append(('PSS', _('PSS')))
            subject_choices.append(('History', _('History')))
            subject_choices.append(('Geography', _('Geography')))
            subject_choices.append(('Civics', _('Civics')))
            subject_choices.append(('Computer', _('Computer')))

        self.fields['registration_level'].choices = choices
        self.fields['subjects_provided'].choices = subject_choices

        instance = kwargs['instance'] if 'instance' in kwargs else ''
        form_action = reverse('students:teacher_add')

        if instance:
            form_action = reverse('students:teacher_edit', kwargs={'pk': instance.id})
        self.helper = FormHelper()
        self.helper.form_show_labels = True
        self.helper.form_action = form_action

        self.helper.layout = Layout(
            Div(
                Div(
                    HTML('<span class="badge-form badge-pill">1</span>'),
                    Div('school', css_class='col-md-3'),
                    HTML('<span class="badge-form badge-pill">2</span>'),
                    Div('round', css_class='col-md-3'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<span class="badge-form badge-pill">2</span>'),
                    Div('first_name', css_class='col-md-3'),
                    HTML('<span class="badge-form badge-pill">3</span>'),
                    Div('father_name', css_class='col-md-3'),
                    HTML('<span class="badge-form badge-pill">4</span>'),
                    Div('last_name', css_class='col-md-3'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<span class="badge-form badge-pill">5</span>'),
                    Div('sex', css_class='col-md-3'),
                    HTML('<span class="badge-form badge-pill">6</span>'),
                    Div('primary_phone_number', css_class='col-md-3'),
                    HTML('<span class="badge-form badge-pill">7</span>'),
                    Div('email', css_class='col-md-3'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<span class="badge-form badge-pill">8</span>'),
                    Div('subjects_provided', css_class='col-md-3 multiple-choice'),
                    HTML('<span class="badge-form badge-pill">9</span>'),
                    Div('registration_level', css_class='col-md-3 multiple-choice'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<span class="badge-form-2 badge-pill">10</span>'),
                    Div('teacher_assignment', css_class='col-md-3 multiple-choice'),
                    HTML('<span class="badge-form-2 badge-pill" id="span_teaching_hours_private_school">11</span>'),
                    Div('teaching_hours_private_school', css_class='col-md-3'),
                    HTML('<span class="badge-form-2 badge-pill" id="span_teaching_hours_dirasa">12</span>'),
                    Div('teaching_hours_dirasa', css_class='col-md-3'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<span class="badge-form-2 badge-pill">13</span>'),
                    Div('trainings', css_class='col-md-3 multiple-choice'),
                    HTML('<span class="badge-form-2 badge-pill">14</span>'),
                    Div('training_sessions_attended', css_class='col-md-3'),
                    HTML('<span class="badge-form-2 badge-pill">15</span>'),
                    Div('training_date_of_completion', css_class='col-md-3'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<span class="badge-form-2 badge-pill">16</span>'),
                    Div('years_of_experience', css_class='col-md-3'),
                    HTML('<span class="badge-form-2 badge-pill">17</span>'),
                    Div('extra_coaching', css_class='col-md-3'),
                    HTML('<span class="badge-form-2 badge-pill" id="span_extra_coaching_specify">17</span>'),
                    Div('extra_coaching_specify', css_class='col-md-3'),
                    css_class='row card-body',
                ),
                css_id='step-1'
            ),
            Div(
                Div(
                    HTML('<span class="badge-form badge-pill">1</span>'),
                    Div('attach_file_1', css_class='col-md-4'),
                    HTML('<span class="badge-form badge-pill">2</span>'),
                    Div('attach_type_1', css_class='col-md-2'),
                    HTML('<span class="badge-form badge-pill">3</span>'),
                    Div('attach_short_description_1', css_class='col-md-4'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<span class="badge-form badge-pill">4</span>'),
                    Div('attach_file_2', css_class='col-md-4'),
                    HTML('<span class="badge-form badge-pill">5</span>'),
                    Div('attach_type_2', css_class='col-md-2'),
                    HTML('<span class="badge-form badge-pill">6</span>'),
                    Div('attach_short_description_2', css_class='col-md-4'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<span class="badge-form badge-pill">6</span>'),
                    Div('attach_file_3', css_class='col-md-4'),
                    HTML('<span class="badge-form badge-pill">8</span>'),
                    Div('attach_type_3', css_class='col-md-2'),
                    HTML('<span class="badge-form badge-pill">9</span>'),
                    Div('attach_short_description_3', css_class='col-md-4'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<span class="badge-form-2 badge-pill">10</span>'),
                    Div('attach_file_4', css_class='col-md-4'),
                    HTML('<span class="badge-form-2 badge-pill">11</span>'),
                    Div('attach_type_4', css_class='col-md-2'),
                    HTML('<span class="badge-form-2 badge-pill">12</span>'),
                    Div('attach_short_description_4', css_class='col-md-4'),
                    css_class='row card-body',
                ),
                Div(
                    HTML('<span class="badge-form-2 badge-pill">13</span>'),
                    Div('attach_file_5', css_class='col-md-4'),
                    HTML('<span class="badge-form-2 badge-pill">14</span>'),
                    Div('attach_type_5', css_class='col-md-2'),
                    HTML('<span class="badge-form-2 badge-pill">15</span>'),
                    Div('attach_short_description_5', css_class='col-md-4'),
                    css_class='row card-body',
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

    def save(self, request=None, instance=None, serializer=None):
        from student_registration.students.utils import generate_one_unique_id
        if instance:
            data = request.POST.copy()
            data.update(request.FILES)
            serializer = TeacherSerializer(instance, data=data)
            if serializer.is_valid():
                instance = serializer.update(validated_data=serializer.validated_data, instance=instance)

                new_file_1 = request.FILES.get('attach_file_1', False)
                if new_file_1:
                    instance.attach_file_1 = new_file_1

                new_file_2 = request.FILES.get('attach_file_2', False)
                if new_file_2:
                    instance.attach_file_2 = new_file_2

                new_file_3 = request.FILES.get('attach_file_3', False)
                if new_file_3:
                    instance.attach_file_3 = new_file_3

                new_file_4 = request.FILES.get('attach_file_4', False)
                if new_file_4:
                    instance.attach_file_4 = new_file_4

                new_file_5 = request.FILES.get('attach_file_5', False)
                if new_file_5:
                    instance.attach_file_5 = new_file_5

                instance.modified_by = request.user
                instance.save()
                messages.success(request, _('Your data has been sent successfully to the server'))
            else:
                messages.warning(request, serializer.errors)
        else:
            data = request.POST.copy()
            data.update(request.FILES)
            serializer = TeacherSerializer(data=data)
            if serializer.is_valid():
                instance = serializer.create(validated_data=serializer.validated_data)

                new_file_1 = request.FILES.get('attach_file_1', False)
                if new_file_1:
                    instance.attach_file_1 = new_file_1

                new_file_2 = request.FILES.get('attach_file_2', False)
                if new_file_2:
                    instance.attach_file_2 = new_file_2

                new_file_3 = request.FILES.get('attach_file_3', False)
                if new_file_3:
                    instance.attach_file_3 = new_file_3

                new_file_4 = request.FILES.get('attach_file_4', False)
                if new_file_4:
                    instance.attach_file_4 = new_file_4

                new_file_5 = request.FILES.get('attach_file_5', False)
                if new_file_5:
                    instance.attach_file_5 = new_file_5

                instance.owner = request.user
                instance.modified_by = request.user
                instance.save()
                request.session['instance_id'] = instance.id
                messages.success(request, _('Your data has been sent successfully to the server'))
            else:
                messages.warning(request, serializer.errors)

        if instance:
            instance.unicef_id = generate_one_unique_id(
                str(instance.pk),
                instance.first_name,
                instance.father_name,
                instance.last_name,
                'hala',
                '2000-01-01',
                'lebanese',
                instance.sex
            )
            instance.save()

    def clean(self):
        cleaned_data = super(TeacherForm, self).clean()
        teacher_assignment = cleaned_data.get("teacher_assignment")
        teaching_hours_private_school = cleaned_data.get("teaching_hours_private_school")
        teaching_hours_dirasa = cleaned_data.get("teaching_hours_dirasa")
        if teacher_assignment == 'Private and Dirasa':
            if not teaching_hours_private_school:
                self.add_error('teaching_hours_private_school', 'This field is required')
            if not teaching_hours_dirasa:
                self.add_error('teaching_hours_dirasa', 'This field is required')

        extra_coaching = cleaned_data.get("extra_coaching")
        extra_coaching_specify = cleaned_data.get("extra_coaching")

        if extra_coaching == 'Yes':
            if not extra_coaching_specify:
                self.add_error('extra_coaching_specify', 'This field is required')


    class Meta:
        model = Teacher
        fields = (
            'id',
            'round',
            'first_name',
            'father_name',
            'last_name',
            'sex',
            'primary_phone_number',
            'school',
            'email',
            'subjects_provided',
            'registration_level',
            'teacher_assignment',
            'teaching_hours_private_school',
            'teaching_hours_dirasa',
            'trainings',
            'years_of_experience',
            'training_sessions_attended',
            'training_date_of_completion',
            'extra_coaching',
            'extra_coaching_specify',
            'attach_short_description_1',
            'attach_file_1',
            'attach_type_1',
            'attach_short_description_2',
            'attach_file_2',
            'attach_type_2',
            'attach_short_description_3',
            'attach_file_3',
            'attach_type_3',
            'attach_short_description_4',
            'attach_file_4',
            'attach_type_4',
            'attach_short_description_5',
            'attach_file_5',
            'attach_type_5',
        )
