from django import forms
from django_filters import FilterSet
from crispy_forms.helper import FormHelper

class RedesignFilterSet(FilterSet):
    """Base FilterSet for the modern redesign."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.build_helper()

    def build_helper(self):
        """Build the crispy helper from the form's current fields.

        FormHelper snapshots a layout when it is constructed, so a subclass that
        drops a field afterwards - as the role-scoped filters do with `partner`
        and `center` - leaves the removed name in the layout. crispy then logs
        "Could not resolve form field" and silently renders nothing for it.
        Subclasses that remove fields must call this again once they are done.
        """
        self.form.helper = FormHelper(self.form)
        self.form.helper.form_method = "get"
        self.form.helper.form_tag = False
        self.form.helper.disable_csrf = True

        for name, field in self.form.fields.items():
            field.widget.attrs.update({'class': 'form-control mb-3'})
            if isinstance(field.widget, forms.Select):
                field.widget.attrs.update({'class': 'form-select mb-3'})
