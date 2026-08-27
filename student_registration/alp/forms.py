from django import forms
from .models import ALPRegistration, ALPTeacher, ALPGrading
from student_registration.child.models import Child

class ALPRegistrationForm(forms.ModelForm):
    class Meta:
        model = ALPRegistration
        fields = ['child', 'school', 'round', 'programme']

class ALPTeacherForm(forms.ModelForm):
    class Meta:
        model = ALPTeacher
        fields = ['first_name', 'father_name', 'last_name', 'phone_number', 'sex', 'school']

class ALPGradingForm(forms.ModelForm):
    class Meta:
        model = ALPGrading
        fields = ['registration', 'grading_data']
