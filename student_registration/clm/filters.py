from django.utils.translation import gettext as _

from django_filters import (
    FilterSet,
    ModelChoiceFilter,
    ChoiceFilter,
    CharFilter,
    BooleanFilter,
)
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, ButtonHolder, Submit, HTML
from django import forms
from student_registration.locations.models import Location
from student_registration.schools.models import CLMRound, School, Section, ClassRoom
from student_registration.students.models import Nationality
from .models import (
    BLN,
    ABLN,
    RS,
    CBECE,
    Cycle,
    Disability,
    GeneralQuestionnaire,
    Outreach,
    Bridging)


class CommonFilter(FilterSet):
    round = ModelChoiceFilter(queryset=CLMRound.objects.all(), empty_label=_('Round'))
    governorate = ModelChoiceFilter(queryset=Location.objects.filter(parent__isnull=True), empty_label=_('Governorate'))
    district = ModelChoiceFilter(queryset=Location.objects.filter(parent__isnull=False), empty_label=_('District'))
    student__nationality = ModelChoiceFilter(queryset=Nationality.objects.exclude(id=9), empty_label=_('Nationality'))
    disability = ModelChoiceFilter(queryset=Disability.objects.filter(active=True), empty_label=_('Disability'))


class BLNFilter(CommonFilter):

    class Meta:
        model = BLN
        fields = {
            'round': ['exact'],
            'student__id_number': ['contains'],
            'student__number': ['contains'],
            'internal_number': ['contains'],
            'student__first_name': ['contains'],
            'student__father_name': ['contains'],
            'student__last_name': ['contains'],
            'student__mother_fullname': ['contains'],
            'student__nationality': ['exact'],
            'governorate': ['exact'],
            'district': ['exact'],
            # 'participation': ['exact'],
            'learning_result': ['exact'],
            'owner__username': ['contains'],
            'disability': ['exact'],
        }


class ABLNFilter(CommonFilter):

    class Meta:
        model = ABLN
        fields = {
            'round': ['exact'],
            'student__id_number': ['contains'],
            'student__number': ['contains'],
            'internal_number': ['contains'],
            'student__first_name': ['contains'],
            'student__father_name': ['contains'],
            'student__last_name': ['contains'],
            'student__mother_fullname': ['contains'],
            'student__nationality': ['exact'],
            'governorate': ['exact'],
            'district': ['exact'],
            'participation': ['exact'],
            'learning_result': ['exact'],
            'owner__username': ['contains'],
            'disability': ['exact'],
        }


class RSFilter(CommonFilter):
    section = ModelChoiceFilter(queryset=Section.objects.all(), empty_label=_('Section'))
    school = ModelChoiceFilter(queryset=School.objects.all(), empty_label=_('School'))
    registered_in_school = ModelChoiceFilter(queryset=School.objects.all(), empty_label=_('Registered in school'))
    grade = ModelChoiceFilter(queryset=ClassRoom.objects.all(), empty_label=_('Class'))

    class Meta:
        model = RS
        fields = {
            'round': ['exact'],
            'student__id_number': ['contains'],
            'student__number': ['contains'],
            'internal_number': ['contains'],
            'student__first_name': ['contains'],
            'student__father_name': ['contains'],
            'student__last_name': ['contains'],
            'student__mother_fullname': ['contains'],
            'student__nationality': ['exact'],
            'type': ['exact'],
            'site': ['exact'],
            'school': ['exact'],
            'governorate': ['exact'],
            'district': ['exact'],
            'registered_in_school': ['exact'],
            'shift': ['exact'],
            'grade': ['exact'],
            'section': ['exact'],
            'participation': ['exact'],
            'learning_result': ['exact'],
            'owner__username': ['contains'],
            'disability': ['exact'],
        }


class CBECEFilter(CommonFilter):
    school = ModelChoiceFilter(queryset=School.objects.all(), empty_label=_('School'))
    cycle = ModelChoiceFilter(queryset=Cycle.objects.all(), empty_label=_('Cycle'))

    class Meta:
        model = CBECE
        fields = {
            'round': ['exact'],
            'student__id_number': ['contains'],
            'student__number': ['contains'],
            'internal_number': ['contains'],
            'student__first_name': ['contains'],
            'student__father_name': ['contains'],
            'student__last_name': ['contains'],
            'student__mother_fullname': ['contains'],
            'student__nationality': ['exact'],
            'cycle': ['exact'],
            'site': ['exact'],
            'school': ['exact'],
            'governorate': ['exact'],
            'district': ['exact'],
            'participation': ['exact'],
            'learning_result': ['exact'],
            'owner__username': ['contains'],
            'disability': ['exact'],
        }


class GeneralQuestionnaireFilter(CommonFilter):

    class Meta:
        model = GeneralQuestionnaire
        fields = {
            'facilitator_full_name': ['contains'],
        }


class OutreachFilter(CommonFilter):

    class Meta:
        model = Outreach
        fields = {
            'round': ['exact'],
            'student__id_number': ['contains'],
            'student__number': ['contains'],
            'internal_number': ['contains'],
            'student__first_name': ['contains'],
            'student__father_name': ['contains'],
            'student__last_name': ['contains'],
            'student__mother_fullname': ['contains'],
            'student__nationality': ['exact'],
            'governorate': ['exact'],
            'district': ['exact'],
            # 'participation': ['exact'],
            'learning_result': ['exact'],
            'owner__username': ['contains'],
            'disability': ['exact'],
        }


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
            ButtonHolder(Submit("submit", "Filter", css_class="btn btn-primary"),
                         HTML('<a href="javascript:void(0);"  title="Download" class="btn btn-success download-report" onclick="checkRoundBeforeExport(event)">Export</a>')
            )
        )
        for name, field in self.form.fields.items():
            label = field.label or name.replace('_', ' ').title()
            field.label = ''
            if isinstance(field.widget, (forms.TextInput, forms.NumberInput)):
                field.widget.attrs.setdefault('placeholder', label)


class BridgingFilter(PlaceholderFilterSet):

    round = ModelChoiceFilter(queryset=CLMRound.objects.filter(current_year=True).all(), empty_label=_('Round'))
    governorate = ModelChoiceFilter(queryset=Location.objects.filter(parent__isnull=True), empty_label=_('Governorate'))
    district = ModelChoiceFilter(queryset=Location.objects.filter(parent__isnull=False), empty_label=_('District'))
    student__nationality = ModelChoiceFilter(queryset=Nationality.objects.exclude(id=9), empty_label=_('Nationality'))
    disability = ModelChoiceFilter(queryset=Disability.objects.filter(active=True), empty_label=_('Disability'))
    learning_result = ChoiceFilter(choices=Bridging.LEARNING_RESULT, empty_label='Learning Result')

    student__first_name = CharFilter(lookup_expr='icontains')
    student__father_name = CharFilter(lookup_expr='icontains')
    student__last_name = CharFilter(lookup_expr='icontains')
    student__mother_fullname = CharFilter(lookup_expr='icontains')
    student__id_number = CharFilter(lookup_expr='icontains')
    student__number = CharFilter(lookup_expr='icontains')
    student__unicef_id = CharFilter(lookup_expr='icontains')
    internal_number = CharFilter(lookup_expr='icontains')
    phone_number = CharFilter(lookup_expr='icontains')
    second_phone_number = CharFilter(lookup_expr='icontains')
    owner__username = CharFilter(lookup_expr='icontains')

    class Meta:
        model = Bridging
        fields = [
            'round',
            'governorate',
            'district',
            'student__first_name',
            'student__father_name',
            'student__last_name',
            'student__mother_fullname',
            'student__id_number',
            'student__number',
            'student__unicef_id',
            'internal_number',
            'student__nationality',
            'disability',
            'phone_number',
            'second_phone_number',
            'learning_result',
            'owner__username'
        ]


class AttendanceFilter(CommonFilter):

    class Meta:
        model = Bridging
        fields = {
        }
