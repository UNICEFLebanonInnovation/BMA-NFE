from django import forms
from django_filters import FilterSet
from crispy_forms.helper import FormHelper

class RedesignFilterSet(FilterSet):
    """Base FilterSet for the modern redesign."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form.helper = FormHelper(self.form)
        self.form.helper.form_method = "get"
        self.form.helper.form_tag = False
        self.form.helper.disable_csrf = True

        for name, field in self.form.fields.items():
            field.widget.attrs.update({'class': 'form-control mb-3'})
            if isinstance(field.widget, forms.Select):
                field.widget.attrs.update({'class': 'form-select mb-3'})
