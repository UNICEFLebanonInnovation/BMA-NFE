# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.contrib import admin
from import_export import resources, fields
from import_export import fields
from import_export.admin import ImportExportModelAdmin

from .models import *


class PackagesResource(resources.ModelResource):
    class Meta:
        model = Packages
        fields = (
            'id',
            'name',
            'type',
            'age',
            'category'
        )
        export_order = ('name', )


class PackagesAdmin(ImportExportModelAdmin):
    resource_class = PackagesResource
    list_display = (
        'id',
        'name',
        'type',
        'age',
        'category'
    )
    list_filter = (
        'name',
        'type',
        'age',
        'category'
    )


class ProvidedServicesResource(resources.ModelResource):
    class Meta:
        model = ProvidedServices
        fields = (
            'id',
            'name',
            'type',
            'category',
            'registration',
            'completed',
            'required',
            'completion_date',
        )
        export_order = ('name', )


class ProvidedServicesAdmin(ImportExportModelAdmin):
    resource_class = ProvidedServicesResource
    list_display = (
        'id',
        'name',
        'type',
        'category',
        'registration',
        'completion_date',
        'completed',
        'required',
    )
    list_filter = (
        'name',
        'type',
        'category',
    )
    search_fields = (
        'registration__child__first_name',
        'registration__child__father_name',
        'registration__child__last_name',
    )


class RegistrationAdmin(admin.ModelAdmin):
    list_display = (
        'child',
        'get_unicef_id',
        'partner',
        'center',
        'round',
        'created',
        'modified',
    )
    list_select_related = (
        'child',
        'partner',
        'center',
        'round',
    )
    list_filter = (
        'child__mother_fullname',
        'child__gender',
        'child__nationality',
        'child__disability',
        'child__marital_status',
        'child__have_children',
        'have_labour',
        'partner',
        'center',
        'round', 
        'created',
        'modified',
    )
    search_fields = (
        'child__first_name',
        'child__father_name',
        'child__last_name',
        'child__unicef_id',
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('child', 'partner', 'center', 'round').filter(deleted=False)

    def get_unicef_id(self, obj):
        return obj.child.unicef_id
    get_unicef_id.short_description = 'Unicef ID'

class EducationHistoryAdmin(admin.ModelAdmin):

    list_display = (
        'registration_id',
        'child',
        'student_old',
        'programme_type',
        'created',
        'modified',
    )
    list_filter = (
        'created',
        'modified',
    )


class InclusionServiceAdmin(admin.ModelAdmin):

    list_display = (
        'registration',
        'dropout',
        'parental_engagement',
        'created',
        'modified',
    )
    list_filter = (
        'dropout',
        'parental_engagement',
        'created',
        'modified',
    )
    search_fields = (
        'registration__child__first_name',
        'registration__child__father_name',
        'registration__child__last_name',
    )


class DigitalServiceAdmin(admin.ModelAdmin):

    list_display = (
        'registration',
        'using_akelius',
        'akelius_sessions_number',
        'akelius_access',
        'akelius_child_equipped',
        'akelius_change_literacy',
        'akelius_change_math',
        'akelius_change_learning',
        'using_lp',
        'lp_sessions_number',
        'lp_access',
        'lp_child_equipped',
        'lp_change_literacy',
        'lp_change_math',
        'lp_change_learning',
    )
    list_filter = (
        'using_akelius',
        'using_lp',
    )
    search_fields = (
        'registration__child__first_name',
        'registration__child__father_name',
        'registration__child__last_name',
    )


class PSSServiceAdmin(admin.ModelAdmin):

    list_display = (
        'registration',
        'child_registered',
        'child_living_arrangement',
        'child_vulnerability',
        'child_out_school_reasons',
        'caregivers_distress',
        'caregivers_additional_parenting',
        'child_distress',
        'child_additional_parenting',
    )
    list_filter = (
        'child_registered',
    )
    search_fields = (
        'registration__child__first_name',
        'registration__child__father_name',
        'registration__child__last_name',
    )


class HealthNutritionServiceAdmin(admin.ModelAdmin):

    list_display = (
        'registration',
        'baby_breastfed',
        'eat_solid_food',
        'immunization_record_screened',
        'muac_malnutrition_screening',
        'eating_minimum_meals',
        'child_vaccinated',
        'positive_parenting',
        'development_delays_identified',
        'respond_stressful_events',
    )
    search_fields = (
        'registration__child__first_name',
        'registration__child__father_name',
        'registration__child__last_name',
    )


class HealthNutritionReferralAdmin(admin.ModelAdmin):
    list_display = (
        'registration',
        'referred_development_delays',
        'development_delays',
        'referred_malnutrition',
        'malnutrition_treatment_center',
        'referred_anc_pnc',
        'phc_center',
        'women_child_referred_iycf',
        'women_child_referred_organization',
        'infant_child_referred_iycf',
        'infant_child_referred_organization',
    )
    list_filter = (
        'referred_development_delays',
        'referred_malnutrition',
        'referred_anc_pnc',

    )
    search_fields = (
        'registration__child__first_name',
        'registration__child__father_name',
        'registration__child__last_name',
    )


class EducationServiceAdmin(admin.ModelAdmin):
    list_display = (
        'registration',
        'education_status',
        'dropout_date',
        'education_program',
    )
    list_filter = (
        'education_status',
        'education_program',

    )
    search_fields = (
        'registration__child__first_name',
        'registration__child__father_name',
        'registration__child__last_name',
    )


class EducationRSServiceAdmin(admin.ModelAdmin):

    list_display = (
        'registration',
        'school',
        'foreign_language_grade',
        'arabic_grade',
        'math_grade',
        'sciences_grade',
        'shift',
        'grade_level',
        'support_needed',
    )
    search_fields = (
        'registration__child__first_name',
        'registration__child__father_name',
        'registration__child__last_name',
    )


class EducationProgrammeAssessmentAdmin(admin.ModelAdmin):

    list_display = (
        'registration',
        'programme_type',
    )
    search_fields = (
        'registration__child__first_name',
        'registration__child__father_name',
        'registration__child__last_name',
    )


class YouthKitServiceAdmin(admin.ModelAdmin):
    list_display = (
        'registration',
        'volunteering_experience',
        'previous_community_initiative',
        'enrollment_reason',
        'pre_tests_administered',
        'test_diagnostic_done',
        'receive_passing_grade',
        'life_skills_completed',
        'participate_volunteering',
        'volunteering_specify',
        'social_course',
        'yfs_course_completed',
        'training_material',
        'future_path',
        'participate_community_initiatives',
        'community_initiatives_specify',
        'adolescent_attendance',
        'adolescent_dropout_reason',
        'adolescent_dropout_date',
        'youth_trained_mental_health',
    )

    search_fields = (
        'registration__child__first_name',
        'registration__child__father_name',
        'registration__child__last_name',
    )


class FollowUpServiceAdmin(admin.ModelAdmin):
    list_display = (
        'registration',
        'follow_up_type',
        'follow_up_number',
        'follow_up_result',
        'dropout_reason',
        'dropout_date',
        'parent_attended_meeting',
        'meeting_type',
        'meeting_number',
        'meeting_modality',
        'caregiver_attended',
        'caregiver_attended_other',
    )

    search_fields = (
        'registration__child__first_name',
        'registration__child__father_name',
        'registration__child__last_name',
    )


class ReferralAdmin(admin.ModelAdmin):
    list_display = (
        'registration',
        'referred_formal_education',
        'referred_school',
        'receive_needed_material',
        'referred_service',
        'referred_service_other',
        'recommended_learning_path',
    )

    search_fields = (
        'registration__child__first_name',
        'registration__child__father_name',
        'registration__child__last_name',
    )


class YouthAssessmentAdmin(admin.ModelAdmin):
    list_display = (
        'registration',
        'undertake_post_diagnostic',
        'receive_passing_grade',
        'complete_life_skills',
        'participate_volunteering',
        'volunteering_opportunity',
        'benefit_innovation_course',
        'compelete_yfs_course',
        'training_material',
        'future_path',
        'participate_community_initiatives',
        'attendance'
    )

    search_fields = (
        'registration__child__first_name',
        'registration__child__father_name',
        'registration__child__last_name',
    )


class YouthReferralAdmin(admin.ModelAdmin):
    list_display = (
        'registration',
        'refer_tvet',
        'refer_innovation'
    )

    search_fields = (
        'registration__child__first_name',
        'registration__child__father_name',
        'registration__child__last_name',
    )


class RecreationalAdmin(admin.ModelAdmin):
    list_display = (
        'registration',
    )

    search_fields = (
        'registration__child__first_name',
        'registration__child__father_name',
        'registration__child__last_name',
    )


class RoundPartnerInline(admin.TabularInline):
    model = RoundPartner
    extra = 1
    fields = (
        'partner',
        'start_date',
        'end_date',
    )


class RoundAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'current_year',
        'year',
    )

    search_fields = (
        'name',
    )

    list_filter = (
        'current_year',
        'year',
    )

    inlines = (RoundPartnerInline,)


admin.site.register(Registration, RegistrationAdmin)
admin.site.register(EducationHistory, EducationHistoryAdmin)
admin.site.register(ProvidedServices, ProvidedServicesAdmin)
admin.site.register(Packages, PackagesAdmin)
admin.site.register(InclusionService, InclusionServiceAdmin)
admin.site.register(DigitalService, DigitalServiceAdmin)
admin.site.register(PSSService, PSSServiceAdmin)
admin.site.register(HealthNutritionService, HealthNutritionServiceAdmin)
admin.site.register(HealthNutritionReferral, HealthNutritionReferralAdmin)
admin.site.register(EducationService, EducationServiceAdmin)
admin.site.register(EducationRSService, EducationRSServiceAdmin)
admin.site.register(EducationProgrammeAssessment, EducationProgrammeAssessmentAdmin)
admin.site.register(YouthKitService, YouthKitServiceAdmin)
admin.site.register(FollowUpService, FollowUpServiceAdmin)
admin.site.register(Referral, ReferralAdmin)
admin.site.register(YouthAssessment, YouthAssessmentAdmin)
admin.site.register(YouthReferral, YouthReferralAdmin)
admin.site.register(Recreational, RecreationalAdmin)
admin.site.register(Round, RoundAdmin)
