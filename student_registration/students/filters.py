from django import forms
from django.utils.translation import gettext as _

import django_filters
from django_filters import FilterSet, ModelChoiceFilter,CharFilter
from django.db.models import Value, CharField, Func
from django.db.models.functions import Concat,Cast
from collections import OrderedDict
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, ButtonHolder, Submit, HTML

from student_registration.schools.models import School, CLMRound
from student_registration.students.models import Teacher


class LPAD(Func):
    function = 'LPAD'
    output_field = CharField()

class PlaceholderFilterSet(FilterSet):
    """Base FilterSet that hides labels and uses placeholders."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form.helper = FormHelper(self.form)
        self.form.helper.form_method = "get"     # django-filter expects GET
        self.form.helper.form_class = "form-inline"
        self.form.helper.form_tag = True
        # self.form.helper.add_input(Submit("submit", "Filter"))
        # self.form.helper.add_input(Rest("Rest", "Cancel"))
        all_fields = list(self.form.fields)  # -> ['type', 'partner', 'round', ...]
        self.form.helper.layout = Layout(
            *all_fields,
            ButtonHolder(
                Submit("submit", "Filter", css_class="btn btn-primary"),
                HTML(
                    '<a href="javascript:void(0);"  title="Download" class="btn btn-success download-report" onclick="teacherExport(event)">'
                    'Export'
                    '</a>'
                ),
                css_class="d-flex gap-2"  # optional: layout/spacing
            ),
        )
        for name, field in self.form.fields.items():
            label = field.label or name.replace('_', ' ').title()
            field.label = ''
            if isinstance(field.widget, (forms.TextInput, forms.NumberInput)):
                field.widget.attrs.setdefault('placeholder', label)


class TeacherFilter(PlaceholderFilterSet):
    round = ModelChoiceFilter(queryset=CLMRound.objects.filter(current_year=True).all(), empty_label=_('Round'))
    school = ModelChoiceFilter(queryset=School.objects.filter(is_closed=False), empty_label=_('School'))
    class Meta:
        model = Teacher
        fields = OrderedDict((
                ('first_name', ['contains']),
                ('father_name', ['contains']),
                ('last_name', ['contains']),
                ('unicef_id', ['contains']),
                ('school', ['exact']),
                ('round', ['exact']),
        ))


