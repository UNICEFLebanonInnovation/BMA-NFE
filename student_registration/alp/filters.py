from django.db.models import Q
from django_filters import (
    FilterSet,
    CharFilter,
    ModelChoiceFilter
)
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout
from django.utils.translation import gettext_lazy as _

from .models import ALPRegistration, ALPTeacher, ALPRound, ALPProgram

class ALPRegistrationFilter(FilterSet):
    first_name = CharFilter(field_name='child__first_name', lookup_expr='icontains', label=_('Child First Name'))
    last_name = CharFilter(field_name='child__last_name', lookup_expr='icontains', label=_('Child Last Name'))
    round = ModelChoiceFilter(queryset=ALPRound.objects.all(), label=_('Round'))
    programme = ModelChoiceFilter(queryset=ALPProgram.objects.all(), label=_('Programme'))

    class Meta:
        model = ALPRegistration
        fields = ['first_name', 'last_name', 'round', 'programme']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form.helper = FormHelper()
        self.form.helper.form_method = 'get'
        self.form.helper.form_tag = False
        self.form.helper.disable_csrf = True
        self.form.helper.layout = Layout(*self.form.fields.keys())

class ALPTeacherFilter(FilterSet):
    first_name = CharFilter(lookup_expr='icontains', label=_('First Name'))
    last_name = CharFilter(lookup_expr='icontains', label=_('Last Name'))

    class Meta:
        model = ALPTeacher
        fields = ['first_name', 'last_name']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form.helper = FormHelper()
        self.form.helper.form_method = 'get'
        self.form.helper.form_tag = False
        self.form.helper.disable_csrf = True
        self.form.helper.layout = Layout(*self.form.fields.keys())
