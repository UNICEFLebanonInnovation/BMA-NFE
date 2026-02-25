from django.utils.translation import gettext_lazy as _
from django import forms
from django_filters import (
    FilterSet,
    ModelChoiceFilter,
    ChoiceFilter,
    CharFilter
)
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, ButtonHolder, Submit, HTML
from model_utils import Choices
from .models import (
    Center,
    Location
)
from student_registration.contrib.filters import RedesignFilterSet

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
                    '<a href="#" title="Download" class="btn btn-success download-center-report">'
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


class CenterFilter(RedesignFilterSet):
    TRUE_FALSE = Choices(
        ('True', _("Yes")),
        ('False', _("No")),
    )
    name = CharFilter(lookup_expr='icontains' )
    governorate = ModelChoiceFilter(queryset=Location.objects.filter(parent__isnull=True), empty_label=_('Governorate'))
    is_active = ChoiceFilter(
        choices=TRUE_FALSE,
        empty_label=_('Center is active'),
        label=_('Is Active'),
        method='filter_is_active'
    )

    class Meta:
        model = Center
        fields = [
            'name',
            'type',
            'governorate',

        ]

    def filter_is_active(self, queryset, name, value):
        if value == 'True':
            return queryset.filter(is_active=True)
        elif value == 'False':
            return queryset.filter(is_active=False)
        return queryset


