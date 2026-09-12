# -*- coding: utf-8 -*-
"""Entity registry: one place describing every record type the app can sync.

Each ``EntitySpec`` says which Django model and *web form* back the entity,
how it is scoped for a user, whether it identifies a person (and therefore
goes through duplicate verification), and how the form must be instantiated
so that the push engine reproduces the website behaviour exactly.
"""
from __future__ import unicode_literals

from dataclasses import dataclass, field
from typing import Callable, Optional

from django.db.models import Q

from student_registration.users.templatetags.custom_tags import has_group

from . import access

KIND_IDENTITY = 'identity'            # registration forms creating/updating a person
KIND_FORM = 'form'                    # custom forms with save(request, instance=<pk>, registry=<pk>)
KIND_MODELFORM = 'modelform'          # standard ModelForms saved by the view
KIND_TEACHER = 'teacher'              # mscc TeacherForm (serializer backed)
KIND_NEW_ROUND = 'new_round'          # mscc NewRoundForm
KIND_BRIDGING_SUBFORM = 'bridging_subform'
KIND_SCHOOL_ACTIVITY = 'school_activity'
KIND_ATTENDANCE = 'attendance'
KIND_TEACHER_ATTENDANCE = 'teacher_attendance'


@dataclass
class EntitySpec:
    key: str
    module: str
    label: str
    model: type
    kind: str = KIND_FORM
    form_class: Optional[type] = None
    parent: Optional[str] = None
    parent_field: str = 'registration'
    identity: bool = False
    person_field: Optional[str] = None
    person_prefix: str = 'child_'
    instance_kw: str = 'instance'
    extra_kwargs: Optional[Callable] = None
    save_kwargs: Optional[Callable] = None
    scope: Optional[Callable] = None
    can_write: Optional[Callable] = None
    layout: Optional[dict] = None
    order: int = 50
    pullable: bool = True
    serialize: Optional[Callable] = None
    multiple: bool = True          # several rows per parent allowed (else edit-in-place)
    description: str = ''
    hidden_fields: tuple = field(default_factory=tuple)
    extra_fields: tuple = field(default_factory=tuple)  # POST-only inputs the view reads

    @property
    def has_modified(self):
        return any(f.name == 'modified' for f in self.model._meta.fields)


# ---------------------------------------------------------------------------
# Scope helpers (mirror the list views of the web platform)
# ---------------------------------------------------------------------------

def mscc_registration_scope(user):
    from student_registration.mscc.models import Registration
    qs = Registration.objects.all()
    round_filter = Q(round__isnull=True) | Q(round__current_year=True)
    if access.is_mscc_unicef(user):
        return qs.filter(round_filter)
    if has_group(user, 'MSCC_PARTNER') and user.partner_id:
        return qs.filter(round_filter, partner_id=user.partner_id)
    if (has_group(user, 'MSCC_CENTER') or has_group(user, 'MSCC')) and user.center_id:
        return qs.filter(round_filter, center_id=user.center_id)
    if has_group(user, 'MSCC') and user.partner_id:
        return qs.filter(round_filter, partner_id=user.partner_id)
    return qs.none()


def mscc_service_scope(model):
    def _scope(user):
        return model.objects.filter(registration__in=mscc_registration_scope(user))
    return _scope


def mscc_center_ids(user):
    from student_registration.locations.models import Center
    if access.is_mscc_unicef(user):
        return Center.objects.values_list('id', flat=True)
    if has_group(user, 'MSCC_PARTNER') and user.partner_id:
        return Center.objects.filter(partner_id=user.partner_id).values_list('id', flat=True)
    if user.center_id:
        return Center.objects.filter(id=user.center_id).values_list('id', flat=True)
    if user.partner_id:
        return Center.objects.filter(partner_id=user.partner_id).values_list('id', flat=True)
    return Center.objects.none().values_list('id', flat=True)


def mscc_teacher_scope(user):
    from student_registration.mscc.models import Teacher
    qs = Teacher.objects.all()
    if access.is_mscc_unicef(user):
        return qs
    if user.center_id:
        return qs.filter(center_id=user.center_id)
    if user.partner_id:
        return qs.filter(center__partner_id=user.partner_id)
    return qs.none()


def mscc_attendance_scope(user):
    from student_registration.attendances.models import MSCCAttendance
    return MSCCAttendance.objects.filter(center_id__in=mscc_center_ids(user))


def alp_scope(model):
    def _scope(user):
        from student_registration.alp.utils import filter_by_school
        return filter_by_school(model.objects.all(), user)
    return _scope


def alp_school_scope(user):
    from student_registration.schools.models import School
    if not user.school_id:
        return School.objects.none()
    return School.objects.filter(id=user.school_id)


def clm_bridging_scope(user):
    from student_registration.clm.models import Bridging
    qs = Bridging.objects.filter(round__current_year=True)
    if has_group(user, 'CLM_BRIDGING_ALL') or user.is_staff:
        return qs
    if user.partner_id:
        qs = qs.filter(partner_id=user.partner_id)
        if user.school_id:
            qs = qs.filter(school_id=user.school_id)
        return qs
    return qs.none()


def clm_school_ids(user):
    from student_registration.schools.models import PartnerOrganization, School
    if has_group(user, 'CLM_BRIDGING_ALL') or user.is_staff:
        return School.objects.values_list('id', flat=True)
    if user.school_id:
        return School.objects.filter(id=user.school_id).values_list('id', flat=True)
    if user.partner_id:
        return (PartnerOrganization.objects.filter(id=user.partner_id)
                .values_list('schools', flat=True))
    return School.objects.none().values_list('id', flat=True)


def clm_attendance_scope(user):
    from student_registration.attendances.models import CLMAttendance
    return CLMAttendance.objects.filter(school_id__in=clm_school_ids(user))


def clm_teacher_scope(user):
    from student_registration.students.models import Teacher
    return Teacher.objects.filter(school_id__in=clm_school_ids(user))


def clm_school_activity_scope(model):
    def _scope(user):
        return model.objects.filter(school_id__in=clm_school_ids(user))
    return _scope


# ---------------------------------------------------------------------------
# Form kwargs helpers
# ---------------------------------------------------------------------------

def _age_kwargs(user, spec, payload, parent, instance):
    age = 0
    if parent is not None and getattr(parent, 'child', None) is not None:
        age = parent.child.age or 0
    return {'age': age}


def _grading_kwargs(user, spec, payload, parent, instance):
    return {
        'programme_type': payload.get('programme_type'),
        'pre_post': payload.get('pre_post') or 'pre',
    }


def _school_grading_kwargs(user, spec, payload, parent, instance):
    return {'programme_type': payload.get('programme_type')}


def _mid_assessment_kwargs(user, spec, payload, parent, instance):
    return {'number': int(payload.get('number') or 1)}


# ---------------------------------------------------------------------------
# Layout overlays (sections + conditional reveals) for the wizard forms
# ---------------------------------------------------------------------------

ID_NUMBER_FIELDS = {
    # IDType.id → fields revealed (parent/caregiver + child). Same mapping as
    # Child.id_number / caregiver_id_number and the web form JS.
    '1': ['case_number', 'case_number_confirm', 'parent_individual_case_number',
          'parent_individual_case_number_confirm', 'individual_case_number',
          'individual_case_number_confirm'],
    '2': ['recorded_number', 'recorded_number_confirm'],
    '3': ['parent_syrian_national_number', 'parent_syrian_national_number_confirm',
          'syrian_national_number', 'syrian_national_number_confirm'],
    '4': ['parent_sop_national_number', 'parent_sop_national_number_confirm',
          'sop_national_number', 'sop_national_number_confirm'],
    '5': ['parent_national_number', 'parent_national_number_confirm',
          'national_number', 'national_number_confirm'],
    '6': ['parent_other_number', 'parent_other_number_confirm',
          'other_number', 'other_number_confirm'],
    '9': ['parent_extract_record', 'parent_extract_record_confirm'],
}

REGISTRATION_SECTIONS = [
    {
        'key': 'identity', 'label': 'Identity', 'label_ar': 'الهوية',
        'fields': [
            'child_first_name', 'child_father_name', 'child_last_name', 'child_mother_fullname',
            'child_gender', 'child_birthday_year', 'child_birthday_month', 'child_birthday_day',
            'child_nationality', 'child_nationality_other', 'child_disability', 'child_disability_other',
            'child_marital_status', 'child_have_children', 'child_children_number',
            'child_have_sibling', 'child_siblings_have_disability', 'child_mother_pregnant_expecting',
            'child_living_arrangement', 'child_address', 'child_p_code', 'child_fe_unique_id',
            'partner_unique_number', 'source_of_identification', 'source_of_identification_specify',
            'cash_support_programmes', 'mscc_packages',
        ],
    },
    {
        'key': 'caregivers', 'label': 'Caregivers & household', 'label_ar': 'مقدمو الرعاية والأسرة',
        'fields': [
            'main_caregiver', 'main_caregiver_other', 'caregiver_first_name', 'caregiver_middle_name',
            'caregiver_last_name', 'caregiver_mother_name', 'main_caregiver_nationality',
            'main_caregiver_nationality_other', 'father_educational_level', 'mother_educational_level',
            'children_number_under18', 'first_phone_owner', 'first_phone_number',
            'first_phone_number_confirm', 'second_phone_owner', 'second_phone_number',
            'second_phone_number_confirm', 'id_type',
            'case_number', 'case_number_confirm', 'parent_individual_case_number',
            'parent_individual_case_number_confirm', 'individual_case_number',
            'individual_case_number_confirm', 'parent_extract_record', 'parent_extract_record_confirm',
            'recorded_number', 'recorded_number_confirm', 'parent_national_number',
            'parent_national_number_confirm', 'national_number', 'national_number_confirm',
            'parent_syrian_national_number', 'parent_syrian_national_number_confirm',
            'syrian_national_number', 'syrian_national_number_confirm', 'parent_sop_national_number',
            'parent_sop_national_number_confirm', 'sop_national_number', 'sop_national_number_confirm',
            'parent_other_number', 'parent_other_number_confirm', 'other_number', 'other_number_confirm',
        ],
    },
    {
        'key': 'labour', 'label': 'Child labour', 'label_ar': 'عمالة الأطفال',
        'fields': [
            'have_labour', 'labour_type', 'labour_type_specify', 'labour_hours',
            'labour_weekly_income', 'labour_condition',
        ],
    },
]

REGISTRATION_REVEALS = [
    {'when': {'field': 'child_nationality', 'in': ['6']}, 'show': ['child_nationality_other']},
    {'when': {'field': 'child_disability', 'label_contains': 'other'}, 'show': ['child_disability_other']},
    {'when': {'field': 'child_have_children', 'in': ['Yes']}, 'show': ['child_children_number']},
    {'when': {'field': 'main_caregiver', 'in': ['Other']}, 'show': ['main_caregiver_other']},
    {'when': {'field': 'main_caregiver_nationality', 'in': ['6']},
     'show': ['main_caregiver_nationality_other']},
    {'when': {'field': 'source_of_identification', 'in': ['Other Sources']},
     'show': ['source_of_identification_specify']},
    {'when': {'field': 'have_labour', 'not_in': ['', 'No']},
     'show': ['labour_type', 'labour_type_specify', 'labour_hours', 'labour_weekly_income', 'labour_condition']},
    {'when': {'field': 'labour_type', 'in': ['Other services']}, 'show': ['labour_type_specify']},
] + [
    {'when': {'field': 'id_type', 'in': [id_type]}, 'show': fields}
    for id_type, fields in ID_NUMBER_FIELDS.items()
]

ALP_SECTIONS = [
    {'key': 'enrolment', 'label': 'Enrolment', 'label_ar': 'التسجيل',
     'fields': ['round', 'programme', 'registration_date']},
] + REGISTRATION_SECTIONS

BRIDGING_SECTIONS = [
    {'key': 'enrolment', 'label': 'Enrolment', 'label_ar': 'التسجيل',
     'fields': ['round', 'school', 'governorate', 'district', 'cadaster', 'registration_level',
                'language', 'registration_date', 'first_attendance_date', 'round_start_date',
                'residence_type', 'internal_number', 'partner_name']},
    {'key': 'identity', 'label': 'Identity', 'label_ar': 'الهوية',
     'fields': ['student_first_name', 'student_father_name', 'student_last_name',
                'student_mother_fullname', 'student_sex', 'student_birthday_year',
                'student_birthday_month', 'student_birthday_day', 'student_nationality',
                'other_nationality', 'student_address', 'student_p_code', 'disability',
                'student_family_status', 'student_have_children', 'student_number_children',
                'education_status', 'miss_school_date', 'enrolled_formal_education',
                'source_of_identification', 'source_of_identification_specify', 'rims_case_number']},
    {'key': 'caregivers', 'label': 'Caregivers & household', 'label_ar': 'مقدمو الرعاية والأسرة',
     'fields': ['main_caregiver', 'other_caregiver_relationship', 'main_caregiver_nationality',
                'main_caregiver_nationality_other', 'caretaker_first_name', 'caretaker_middle_name',
                'caretaker_last_name', 'caretaker_mother_name', 'caretaker_birthday_year',
                'caretaker_birthday_month', 'caretaker_birthday_day', 'hh_educational_level',
                'father_educational_level', 'phone_owner', 'phone_number', 'phone_number_confirm',
                'second_phone_owner', 'second_phone_number', 'second_phone_number_confirm',
                'id_type', 'individual_case_number', 'individual_case_number_confirm',
                'recorded_number', 'recorded_number_confirm', 'national_number',
                'national_number_confirm', 'syrian_national_number', 'syrian_national_number_confirm',
                'sop_national_number', 'sop_national_number_confirm', 'other_number',
                'other_number_confirm', 'individual_extract_record',
                'individual_extract_record_confirm', 'no_child_id_confirmation']},
    {'key': 'labour', 'label': 'Child labour & support', 'label_ar': 'عمالة الأطفال والدعم',
     'fields': ['have_labour_single_selection', 'labours_single_selection', 'labours_other_specify',
                'labour_hours', 'labour_weekly_income', 'source_of_transportation', 'consent_parents']},
    {'key': 'pre_test', 'label': 'Pre-test', 'label_ar': 'الاختبار القبلي', 'fields': []},
]


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

_REGISTRY = None


def get_registry():
    """Return the ordered dict of entity specs (built lazily after app load)."""
    global _REGISTRY
    if _REGISTRY is None:
        _REGISTRY = _build_registry()
    return _REGISTRY


def get_spec(key):
    spec = get_registry().get(key)
    if spec is None:
        raise KeyError('Unknown entity "{}"'.format(key))
    return spec


def _build_registry():
    from student_registration.alp import forms as alp_forms
    from student_registration.alp.models import (
        ALPAttendance, ALPGrading, ALPRegistration, ALPTeacher, ALPTeacherAttendance,
    )
    from student_registration.attendances.models import CLMAttendance, MSCCAttendance
    from student_registration.clm import bridging_forms
    from student_registration.clm.models import Bridging
    from student_registration.mscc import education_form, forms as mscc_forms, services_form
    from student_registration.mscc.models import (
        DigitalService, EducationAssessment, EducationProgrammeAssessment, EducationRSService,
        EducationService, FollowUpService, HealthNutritionReferral, HealthNutritionService,
        InclusionService, LegoService, PSSService, Recreational, Referral, Registration, Teacher,
        YouthAssessment, YouthKitService, YouthReferral, YouthService,
    )
    from student_registration.schools import forms as school_forms
    from student_registration.schools.models import (
        Club, CommunityInitiative, HealthVisit, Meeting, School,
    )
    from student_registration.students.models import Teacher as CLMTeacher

    specs = []

    # ---------------------------------------------------------------- MSCC
    specs.append(EntitySpec(
        key='mscc.registration', module='mscc', label='Registration', model=Registration,
        kind=KIND_IDENTITY, form_class=mscc_forms.MainForm, identity=True, person_field='child',
        scope=mscc_registration_scope, can_write=access.mscc_can_edit, order=10,
        layout={'sections': REGISTRATION_SECTIONS, 'reveals': REGISTRATION_REVEALS,
                'wizard': True, 'confirm_fields': ['first_phone_number', 'second_phone_number']},
        description='Child registration at a Makani centre (child + registration).',
        hidden_fields=('student_old',),
    ))
    specs.append(EntitySpec(
        key='mscc.new_round', module='mscc', label='New round', model=EducationService,
        kind=KIND_NEW_ROUND, form_class=education_form.NewRoundForm, parent='mscc.registration',
        scope=None, can_write=access.mscc_can_edit, order=20, pullable=False,
        description='Re-enrol an existing child in a new round (creates a new registration).',
    ))

    mscc_services = [
        ('mscc.education_service', 'Education service', EducationService,
         education_form.EducationServiceForm, None, True),
        ('mscc.education_rs_service', 'Education RS service', EducationRSService,
         education_form.EducationRSServiceForm, None, True),
        ('mscc.diagnostic_assessment', 'Diagnostic assessment', EducationAssessment,
         education_form.DiagnosticAssessmentForm, None, True),
        ('mscc.education_assessment', 'Education assessment', EducationAssessment,
         education_form.EducationAssessmentForm, None, True),
        ('mscc.education_grading', 'Education grading', EducationProgrammeAssessment,
         education_form.EducationGradingForm, _grading_kwargs, True),
        ('mscc.youth_scoring', 'Youth scoring', EducationProgrammeAssessment,
         education_form.YouthScoringForm, _grading_kwargs, True),
        ('mscc.school_grading', 'School grading', EducationProgrammeAssessment,
         education_form.EducationSchoolGradingForm, _school_grading_kwargs, True),
        ('mscc.pss', 'PSS service', PSSService, services_form.PSSServiceForm, None, False),
        ('mscc.inclusion', 'Inclusion', InclusionService, services_form.InclusionServiceForm, None, False),
        ('mscc.digital', 'Digital learning', DigitalService, services_form.DigitalServiceForm, None, False),
        ('mscc.health_nutrition', 'Health & nutrition', HealthNutritionService,
         services_form.HealthNutritionServiceForm, _age_kwargs, False),
        ('mscc.health_nutrition_referral', 'Health & nutrition referral', HealthNutritionReferral,
         services_form.HealthNutritionReferralForm, None, False),
        ('mscc.youth_kit', 'Youth kit', YouthKitService, services_form.YouthKitServiceForm, None, False),
        ('mscc.youth_maharati', 'Youth Maharati', YouthService,
         services_form.YouthServiceMaharatiForm, None, True),
        ('mscc.youth_gil', 'Youth GIL', YouthService, services_form.YouthServiceGilForm, None, True),
        ('mscc.youth_assessment', 'Youth assessment', YouthAssessment,
         services_form.YouthAssessmentForm, None, False),
        ('mscc.youth_referral', 'Youth referral', YouthReferral, services_form.YouthReferralForm, None, False),
        ('mscc.follow_up', 'Follow-up', FollowUpService, services_form.FollowUpServiceForm, None, True),
        ('mscc.recreational', 'Recreational', Recreational, services_form.RecreationalForm, None, False),
        ('mscc.lego', 'LEGO', LegoService, services_form.LegoServiceForm, _age_kwargs, False),
    ]
    for key, label, model, form_class, extra, multiple in mscc_services:
        specs.append(EntitySpec(
            key=key, module='mscc', label=label, model=model, kind=KIND_FORM,
            form_class=form_class, parent='mscc.registration', extra_kwargs=extra,
            scope=mscc_service_scope(model), can_write=access.mscc_can_edit, order=30,
            multiple=multiple,
        ))
    specs.append(EntitySpec(
        key='mscc.referral', module='mscc', label='Referral', model=Referral, kind=KIND_FORM,
        form_class=mscc_forms.ReferralForm, parent='mscc.registration', instance_kw='pk',
        scope=mscc_service_scope(Referral), can_write=access.mscc_can_edit, order=30, multiple=False,
    ))
    # EducationRSServiceForm also takes the instance as ``pk``.
    for spec in specs:
        if spec.key == 'mscc.education_rs_service':
            spec.instance_kw = 'pk'

    specs.append(EntitySpec(
        key='mscc.teacher', module='mscc', label='Teacher', model=Teacher, kind=KIND_TEACHER,
        form_class=mscc_forms.TeacherForm, scope=mscc_teacher_scope,
        can_write=access.mscc_can_manage_teachers, order=10,
    ))
    specs.append(EntitySpec(
        key='mscc.attendance_day', module='mscc', label='Attendance day', model=MSCCAttendance,
        kind=KIND_ATTENDANCE, scope=mscc_attendance_scope, can_write=access.mscc_can_attend, order=40,
    ))

    # ----------------------------------------------------------------- ALP
    specs.append(EntitySpec(
        key='alp.registration', module='alp', label='ALP registration', model=ALPRegistration,
        kind=KIND_IDENTITY, form_class=alp_forms.ALPRegistrationForm, identity=True,
        person_field='child', scope=alp_scope(ALPRegistration), can_write=access.alp_can_write,
        order=10, layout={'sections': ALP_SECTIONS, 'reveals': REGISTRATION_REVEALS, 'wizard': True,
                          'confirm_fields': ['first_phone_number', 'second_phone_number']},
        hidden_fields=('student_old',),
    ))
    specs.append(EntitySpec(
        key='alp.teacher', module='alp', label='ALP teacher', model=ALPTeacher, kind=KIND_MODELFORM,
        form_class=alp_forms.ALPTeacherForm, scope=alp_scope(ALPTeacher),
        can_write=access.alp_can_write, order=10,
    ))
    specs.append(EntitySpec(
        key='alp.grading', module='alp', label='ALP grading', model=ALPGrading, kind=KIND_MODELFORM,
        form_class=alp_forms.ALPGradingDynamicForm, parent='alp.registration',
        scope=alp_scope(ALPGrading), can_write=access.alp_can_write, order=30,
    ))
    specs.append(EntitySpec(
        key='alp.school_profile', module='alp', label='School profile', model=School,
        kind=KIND_MODELFORM, form_class=alp_forms.ALPSchoolProfileForm, scope=alp_school_scope,
        can_write=access.alp_can_write, order=10, multiple=False,
    ))
    specs.append(EntitySpec(
        key='alp.attendance_day', module='alp', label='ALP attendance day', model=ALPAttendance,
        kind=KIND_ATTENDANCE, scope=alp_scope(ALPAttendance), can_write=access.alp_can_write, order=40,
    ))
    specs.append(EntitySpec(
        key='alp.teacher_attendance_day', module='alp', label='ALP teacher attendance',
        model=ALPTeacherAttendance, kind=KIND_TEACHER_ATTENDANCE,
        scope=alp_scope(ALPTeacherAttendance), can_write=access.alp_can_write, order=40,
    ))

    # ----------------------------------------------------------------- CLM
    specs.append(EntitySpec(
        key='clm.bridging', module='clm', label='Bridging registration', model=Bridging,
        kind=KIND_IDENTITY, form_class=bridging_forms.BridgingForm, identity=True,
        person_field='student', person_prefix='student_', scope=clm_bridging_scope,
        can_write=access.clm_can_register, order=10,
        layout={'sections': BRIDGING_SECTIONS, 'wizard': True,
                'confirm_fields': ['phone_number', 'second_phone_number']},
        hidden_fields=('student_id', 'enrollment_id'),
    ))
    for key, label, form_class, extra in [
        ('clm.bridging_assessment', 'Bridging post-assessment', bridging_forms.BridgingAssessmentForm, None),
        ('clm.bridging_mid_assessment', 'Bridging mid-assessment',
         bridging_forms.BridgingMidAssessmentForm, _mid_assessment_kwargs),
        ('clm.bridging_followup', 'Bridging follow-up', bridging_forms.BridgingFollowupForm, None),
        ('clm.bridging_service', 'Bridging services', bridging_forms.BridgingServiceForm, None),
    ]:
        specs.append(EntitySpec(
            key=key, module='clm', label=label, model=Bridging, kind=KIND_BRIDGING_SUBFORM,
            form_class=form_class, parent='clm.bridging', extra_kwargs=extra, pullable=False,
            scope=None, can_write=access.clm_can_register, order=30, multiple=False,
        ))
    specs.append(EntitySpec(
        key='clm.teacher', module='clm', label='Teacher', model=CLMTeacher, kind=KIND_MODELFORM,
        form_class=None, scope=clm_teacher_scope, can_write=access.clm_can_manage_teachers, order=10,
    ))
    for key, label, model, form_class in [
        ('clm.club', 'Club', Club, school_forms.ClubForm),
        ('clm.meeting', 'Meeting', Meeting, school_forms.MeetingForm),
        ('clm.community_initiative', 'Community initiative', CommunityInitiative,
         school_forms.CommunityInitiativeForm),
        ('clm.health_visit', 'Health visit', HealthVisit, school_forms.HealthVisitForm),
    ]:
        specs.append(EntitySpec(
            key=key, module='clm', label=label, model=model, kind=KIND_SCHOOL_ACTIVITY,
            form_class=form_class, scope=clm_school_activity_scope(model),
            can_write=access.clm_can_register, order=20,
        ))
    specs.append(EntitySpec(
        key='clm.attendance_day', module='clm', label='Bridging attendance day', model=CLMAttendance,
        kind=KIND_ATTENDANCE, scope=clm_attendance_scope, can_write=access.clm_can_attend, order=40,
    ))

    return {spec.key: spec for spec in specs}


def specs_for_user(user):
    """Entities the user can see (module enabled)."""
    caps = access.module_capabilities(user)
    return [spec for spec in get_registry().values() if caps[spec.module]['enabled']]
