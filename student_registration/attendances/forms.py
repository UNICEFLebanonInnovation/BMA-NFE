from django import forms
from dal import autocomplete
from .models import CLMAttendance
from student_registration.schools.models import (
    School,
)


class CLMAttendanceAdminForm(forms.ModelForm):

    school = forms.ModelChoiceField(
        queryset=School.objects.filter(is_closed=False),
        widget=autocomplete.ModelSelect2(url='school_autocomplete')
    )

    def __init__(self, *args, **kwargs):
        super(CLMAttendanceAdminForm, self).__init__(*args, **kwargs)

    class Meta:
        model = CLMAttendance
        fields = '__all__'
