from django.db.models import Q
from django.db.utils import OperationalError, ProgrammingError

from django_filters import (
    FilterSet,
    ModelChoiceFilter,
    ChoiceFilter,
    CharFilter,
    BooleanFilter,
)
from collections import OrderedDict
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, ButtonHolder, Submit, HTML
from django import forms
from django.utils.translation import gettext_lazy as _

from student_registration.locations.models import Center, Location
from student_registration.students.models import Nationality
from .models import (
    Registration,
    EducationService,
    Round,
    Teacher,
    Packages,
)
from student_registration.child.models import Child
from student_registration.schools.models import PartnerOrganization
from student_registration.contrib.filters import RedesignFilterSet
from student_registration.users.templatetags.custom_tags import has_group

DELETED_CHOICES = [
    ('', 'All'),
    ('yes', 'Yes'),
    ('no', 'No'),
]

class PlaceholderFilterSet(FilterSet):
    """Deprecated: Base FilterSet that hides labels and uses placeholders."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form.helper = FormHelper(self.form)
        self.form.helper.form_method = "get"     # django-filter expects GET
        self.form.helper.form_class = "row g-3"
        self.form.helper.form_tag = True

        for name, field in self.form.fields.items():
            if isinstance(field.widget, (forms.TextInput, forms.NumberInput)):
                label = field.label or name.replace('_', ' ').title()
                field.widget.attrs.setdefault('placeholder', label)


class MainFilter(RedesignFilterSet):

    child__first_name = CharFilter(lookup_expr='icontains' )
    child__father_name = CharFilter(lookup_expr='icontains')
    child__last_name = CharFilter(lookup_expr='icontains')
    child__mother_fullname = CharFilter(lookup_expr='icontains')
    child__unicef_id = CharFilter(lookup_expr='icontains')
    child__gender = ChoiceFilter(choices=Child.GENDER, empty_label='Gender')
    child__nationality = ChoiceFilter(choices=Nationality.objects.values_list('id', 'name')
                                .order_by('name').distinct(), empty_label='Nationality')

    partner = ChoiceFilter(
        choices=PartnerOrganization.objects.values_list('id', 'name')
        .order_by('name').distinct(),
        empty_label='Partner',
    )
    round = ChoiceFilter(
        choices=Round.objects.filter(current_year=True).values_list('id', 'name')
        .order_by('name').distinct(),
        empty_label='Round'
    )
    programme_type = ChoiceFilter(
        choices=Packages.objects.values_list('name', 'name').order_by('name').distinct(),
        field_name='education_service__education_program',
        empty_label='Programme Type',
        method='filter_education_program',
    )

    center = ChoiceFilter(choices=Center.objects.values_list('id', 'name')
                          .order_by('name').distinct(), empty_label='Center')

    class Meta:
        model = Registration
        fields = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        user = getattr(getattr(self, 'request', None), 'user', None)
        if not user:
            return

        if user.is_staff or has_group(user, 'MSCC_UNICEF'):
            return

        if has_group(user, 'MSCC_PARTNER'):
            partner_centers = list(
                Center.objects.filter(partner_id=user.partner_id)
                    .values_list('id', 'name')
                    .order_by('name')
                    .distinct()
            ) if user.partner_id else []
            center_choices = partner_centers
            self.filters['center'].extra['choices'] = center_choices
            self.filters['center'].field.choices = center_choices
            if 'center' in self.form.fields:
                self.form.fields['center'].choices = center_choices

        if has_group(user, 'MSCC_CENTER'):
            self.filters.pop('partner', None)
            self.form.fields.pop('partner', None)
            self.filters.pop('center', None)
            self.form.fields.pop('center', None)
        elif has_group(user, 'MSCC_PARTNER'):
            self.filters.pop('partner', None)
            self.form.fields.pop('partner', None)

    def filter_education_program(self, queryset, name, value):
        return queryset.filter(education_service__education_program=value)


class FullFilter(RedesignFilterSet):

    partner = ChoiceFilter(choices=PartnerOrganization.objects.values_list('id', 'name')
                          .order_by('name').distinct(), empty_label='Partner')

    round = ChoiceFilter(
        choices=Round.objects.filter(current_year=True).values_list('id', 'name')
        .order_by('name').distinct(),
        empty_label='Round'
    )

    center = ChoiceFilter(choices=Center.objects.values_list('id', 'name')
                          .order_by('name').distinct(), empty_label='Center')

    child__first_name = CharFilter(lookup_expr='icontains')
    child__father_name = CharFilter(lookup_expr='icontains')
    child__last_name = CharFilter(lookup_expr='icontains')
    child__mother_fullname = CharFilter(lookup_expr='icontains')
    child__unicef_id = CharFilter(lookup_expr='icontains')
    child__gender = ChoiceFilter(choices=Child.GENDER, empty_label='Gender')
    child__nationality = ChoiceFilter(choices=Nationality.objects.values_list('id', 'name')
                                      .order_by('name').distinct(), empty_label='Nationality')

    programme_type = ChoiceFilter(
        choices=Packages.objects.values_list('name', 'name').order_by('name').distinct(),
        field_name='education_service__education_program',
        empty_label='Programme Type',
        method='filter_education_program',
    )


    class Meta:
        model = Registration
        fields = [
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        user = getattr(getattr(self, 'request', None), 'user', None)
        if not user:
            return

        if user.is_staff or has_group(user, 'MSCC_UNICEF'):
            return

        if has_group(user, 'MSCC_PARTNER'):
            partner_centers = list(
                Center.objects.filter(partner_id=user.partner_id)
                .values_list('id', 'name')
                .order_by('name')
                .distinct()
            ) if user.partner_id else []
            center_choices = partner_centers
            self.filters['center'].extra['choices'] = center_choices
            self.filters['center'].field.choices = center_choices
            if 'center' in self.form.fields:
                self.form.fields['center'].choices = center_choices

        if has_group(user, 'MSCC_CENTER'):
            self.filters.pop('partner', None)
            self.form.fields.pop('partner', None)
            self.filters.pop('center', None)
            self.form.fields.pop('center', None)
        elif has_group(user, 'MSCC_PARTNER'):
            self.filters.pop('partner', None)
            self.form.fields.pop('partner', None)

    def filter_education_program(self, queryset, name, value):
        return queryset.filter(education_service__education_program=value)


class TeacherFilter(RedesignFilterSet):
    NO_ROUND_OPTION = ('ALl', 'All Rounds')

    round = Round.objects.filter(current_year=True).values_list('id', 'name').order_by('name').distinct()

    center = ModelChoiceFilter(queryset=Center.objects.all(), empty_label=_('Center'))

    class Meta:
        model = Teacher
        fields = OrderedDict((
            ('first_name', ['contains']),
            ('father_name', ['contains']),
            ('last_name', ['contains']),
            ('unicef_id', ['contains']),
            ('center', ['exact']),
            ('round', ['exact']),
        ))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        user = getattr(getattr(self, 'request', None), 'user', None)
        if not user:
            return

        if user.is_staff or has_group(user, 'MSCC_UNICEF'):
            return

        if has_group(user, 'MSCC_CENTER'):
            self.filters.pop('center', None)
            self.form.fields.pop('center', None)
        elif has_group(user, 'MSCC_PARTNER') and user.partner_id:
            partner_center_qs = Center.objects.filter(partner_id=user.partner_id).order_by('name')
            self.filters['center'].queryset = partner_center_qs
            self.filters['center'].field.queryset = partner_center_qs
            if 'center' in self.form.fields:
                self.form.fields['center'].queryset = partner_center_qs
