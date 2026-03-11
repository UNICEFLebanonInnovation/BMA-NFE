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
)
from student_registration.child.models import Child
from student_registration.schools.models import PartnerOrganization
from student_registration.contrib.filters import RedesignFilterSet

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
    NO_ROUND_OPTION = ('no_round', 'No Round')

    child__first_name = CharFilter(lookup_expr='icontains' )
    child__father_name = CharFilter(lookup_expr='icontains')
    child__last_name = CharFilter(lookup_expr='icontains')
    child__mother_fullname = CharFilter(lookup_expr='icontains')
    child__number = CharFilter(lookup_expr='icontains')
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
        empty_label='Round',
        method='filter_round'
    )
    programme_type = ChoiceFilter(choices=EducationService.EDUCATION_PROGRAM,
                                  field_name='education_service__education_program',
                                  empty_label='Programme Type', method='filter_education_program')
    child__first_phone_number = CharFilter(lookup_expr='icontains')
    child__second_phone_number = CharFilter(lookup_expr='icontains')
    center = ChoiceFilter(choices=Center.objects.values_list('id', 'name')
                          .order_by('name').distinct(), empty_label='Center')
    center__governorate = ChoiceFilter(choices=Location.objects.filter(parent__isnull=True).values_list('id', 'name')
                                       .order_by('name').distinct(), empty_label='Governorate')
    center__caza = ChoiceFilter(choices=Location.objects.filter(parent__isnull=False, type=2).values_list('id', 'name')
                                .order_by('name').distinct(), empty_label='Caza')
    center__cadaster = ChoiceFilter(
        choices=Location.objects.filter(parent__isnull=False, type=3).values_list('id', 'name')
        .order_by('name').distinct(), empty_label='Cadaster')

    class Meta:
        model = Registration
        fields = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._populate_round_choices()

    def filter_round(self, queryset, name, value):
        if value == 'no_round':
            return queryset.filter(round__isnull=True)
        return queryset.filter(**{name: value})

    def filter_education_program(self, queryset, name, value):
        return queryset.filter(education_service__education_program=value)

    def _populate_round_choices(self):
        try:
            round_choices = list(
                Round.objects.values_list('id', 'name').order_by('name').distinct()
            )
        except (ProgrammingError, OperationalError):
            round_choices = []
        self.filters['round'].extra['choices'] = [self.NO_ROUND_OPTION] + round_choices


class FullFilter(RedesignFilterSet):
    NO_ROUND_OPTION = ('no_round', 'No Round')

    partner = ChoiceFilter(choices=PartnerOrganization.objects.values_list('id', 'name')
                          .order_by('name').distinct(), empty_label='Partner')

    round = ChoiceFilter(
        empty_label='Round',
        method='filter_round'
    )

    center = ChoiceFilter(choices=Center.objects.values_list('id', 'name')
                          .order_by('name').distinct(), empty_label='Center')
    center__governorate = ChoiceFilter(choices=Location.objects.filter(parent__isnull=True).values_list('id', 'name')
                                       .order_by('name').distinct(), empty_label='Governorate')
    center__caza = ChoiceFilter(choices=Location.objects.filter(parent__isnull=False, type=2).values_list('id', 'name')
                                .order_by('name').distinct(), empty_label='Caza')
    center__cadaster = ChoiceFilter(choices=Location.objects.filter(parent__isnull=False, type=3).values_list('id', 'name')
                                    .order_by('name').distinct(), empty_label='Cadaster')

    child__first_name = CharFilter(lookup_expr='icontains')
    child__father_name = CharFilter(lookup_expr='icontains')
    child__last_name = CharFilter(lookup_expr='icontains')
    child__mother_fullname = CharFilter(lookup_expr='icontains')
    child__number = CharFilter(lookup_expr='icontains')
    child__unicef_id = CharFilter(lookup_expr='icontains')
    child__gender = ChoiceFilter(choices=Child.GENDER, empty_label='Gender')
    child__nationality = ChoiceFilter(choices=Nationality.objects.values_list('id', 'name')
                                      .order_by('name').distinct(), empty_label='Nationality')
    programme_type = ChoiceFilter(choices=EducationService.EDUCATION_PROGRAM,
                                  field_name='education_service__education_program',
                                  empty_label='Programme Type', method='filter_education_program')

    child__first_phone_number = CharFilter(lookup_expr='icontains')
    child__second_phone_number = CharFilter(lookup_expr='icontains')

    class Meta:
        model = Registration
        fields = [
        ]


class TeacherFilter(RedesignFilterSet):
    NO_ROUND_OPTION = ('no_round', 'No Round')

    round = ModelChoiceFilter(queryset=Round.objects.filter(current_year=True).all(), empty_label=_('Round'))
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
        self._populate_round_choices()

    def filter_round(self, queryset, name, value):
        if value == 'no_round':
            return queryset.filter(round__isnull=True)
        return queryset.filter(**{name: value})

    def filter_education_program(self, queryset, name, value):
        return queryset.filter(education_service__education_program=value)

    def _populate_round_choices(self):
        try:
            round_choices = list(
                Round.objects.values_list('id', 'name').order_by('name').distinct()
            )
        except (ProgrammingError, OperationalError):
            round_choices = []
        self.filters['round'].extra['choices'] = [self.NO_ROUND_OPTION] + round_choices
