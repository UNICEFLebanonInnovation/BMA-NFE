# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.contrib import admin
from import_export import resources, fields
from import_export import fields
from import_export.admin import ImportExportModelAdmin

from .forms import BLNAdminForm, ABLNAdminForm, RSAdminForm, CBECEAdminForm, InclusionAdminForm, OutreachAdminForm
from .models import (
    Assessment,
    Cycle,
    Site,
    Referral,
    Disability,
    BLN,
    Bridging,
    ABLN,
    RS,
    CBECE,
    Inclusion,
    Center,
    Outreach
)


class BLNResource(resources.ModelResource):
    arabic_improvement = fields.Field(
        column_name='arabic improvement',
        attribute='arabic_improvement',
    )
    english_improvement = fields.Field(
        column_name='english_improvement',
        attribute='english_improvement',
    )
    french_improvement = fields.Field(
        column_name='french_improvement',
        attribute='french_improvement',
    )
    math_improvement = fields.Field(
        column_name='math_improvement',
        attribute='math_improvement',
    )
    assessment_improvement = fields.Field(
        column_name='assessment_improvement',
        attribute='assessment_improvement',
    )

    pre_test_arabic = fields.Field(column_name='pre test arabic')
    pre_test_foreign_language = fields.Field(column_name='pre_test_foreign_language')
    pre_test_math = fields.Field(column_name='pre_test_math')

    post_test_arabic = fields.Field(column_name='post_test_arabic')
    post_test_foreign_language = fields.Field(column_name='post_test_foreign_language')
    post_test_math = fields.Field(column_name='post_test_math')

    class Meta:
        fields = (
            'id',
            'partner__name',
            'new_registry',
            'student_outreached',
            'have_barcode',
            'outreach_barcode',
            'round__name',
            'governorate__name',
            'district__name',
            'location',
            'language',
            'student__id',
            'student__id_type',
            'student__id_number',
            'student__number',
            'student__first_name',
            'student__father_name',
            'student__last_name',
            'student__mother_fullname',
            'student__birthday_year',
            'student__birthday_month',
            'student__birthday_day',
            'student__nationality__name',
            'student__sex',
            'student__p_code',
            'disability__name',
            'internal_number',
            'comments',
            'hh_educational_level',
            'student__family_status',
            'student__have_children',
            'have_labour',
            'labours',
            'labour_hours',
            'pre_test_arabic',
            'pre_test_foreign_language',
            'pre_test_math',
            'pre_test_score',
            'post_test_arabic',
            'post_test_foreign_language',
            'post_test_math',
            'post_test_score',
            'arabic_improvement',
            'english_improvement',
            'french_improvement',
            'math_improvement',
            'assessment_improvement',
            'participation',
            'barriers',
            'learning_result',
            'created',
            'modified'
        )
        model = BLN
        export_order = fields

        def dehydrate_pre_test_arabic(self, obj):
            return obj.get_assessment_value('arabic', 'pre_test')

        def dehydrate_pre_test_foreign_language(self, obj):
            return obj.get_assessment_value('foreign_language', 'pre_test')

        def dehydrate_pre_test_math(self, obj):
            return obj.get_assessment_value('math', 'pre_test')

        def dehydrate_post_test_arabic(self, obj):
            return obj.get_assessment_value('arabic', 'post_test')

        def dehydrate_post_test_foreign_language(self, obj):
            return obj.get_assessment_value('foreign_language', 'post_test')

        def dehydrate_post_test_math(self, obj):
            return obj.get_assessment_value('math', 'post_test')


class BLNAdmin(ImportExportModelAdmin):
    resource_class = BLNResource
    form = BLNAdminForm
    # fields = '__all__'

    list_display = (
        'student',
        'governorate',
        'district',
        'partner',
        'created',
        'modified',
    )
    list_filter = (
        'round',
        'governorate',
        'district',
        'partner',
        'language',
        'student__sex',
        'student__nationality',
        'disability',
        'hh_educational_level',
        'student__family_status',
        'student__have_children',
        'have_labour',
        'labours',
        'labour_hours',
        'participation',
        'barriers',
        'learning_result',
        'created',
        'modified',
    )
    search_fields = (
        'student__first_name',
        'student__father_name',
        'student__last_name',
        'student__mother_fullname',
    )

    def get_export_formats(self):
        from student_registration.users.utils import get_default_export_formats
        return get_default_export_formats()


class BridgingAdmin(admin.ModelAdmin):

    list_display = (
        'student',
        'get_unicef_id',
        'governorate',
        'district',
        'partner',
        'deleted',
        'created',
        'modified',
    )
    list_filter = (
        'round',
        'governorate',
        'district',
        'partner',
        'student__sex',
        'student__nationality',
        'disability',
        'student__family_status',
        'student__have_children',
        'have_labour',
        'created',
        'modified',
    )
    search_fields = (
        'student__first_name',
        'student__father_name',
        'student__last_name',
        'student__mother_fullname',
        'student__unicef_id',
    )

    readonly_fields = ('student_fullname_display',)

    fields = (
        'student_fullname_display',
        'deleted',
        'round',
        'governorate',
        'district',
        'cadaster',
        'partner',
        'school',
        'registration_level',
        'registration_date',
        'language',
        'internal_number',
        'disability',
        'hh_educational_level',
        'father_educational_level',
        'caretaker_birthday_year',
        'caretaker_birthday_month',
        'caretaker_birthday_day',
        'first_attendance_date',
        'child_outreach',
        'residence_type',
        'have_labour_single_selection',
        'labours_single_selection',
        'labours_other_specify',
        'labour_hours',
        'phone_number',
        'phone_number_confirm',
        'phone_owner',
        'second_phone_number',
        'second_phone_number_confirm',
        'second_phone_owner',
        'id_type',
        'case_number',
        'case_number_confirm',
        'individual_case_number',
        'individual_case_number_confirm',
        'parent_individual_case_number',
        'parent_individual_case_number_confirm',
        'recorded_number',
        'recorded_number_confirm',
        'national_number',
        'national_number_confirm',
        'syrian_national_number',
        'syrian_national_number_confirm',
        'sop_national_number',
        'sop_national_number_confirm',
        'parent_national_number',
        'parent_national_number_confirm',
        'parent_syrian_national_number',
        'parent_syrian_national_number_confirm',
        'parent_sop_national_number',
        'parent_sop_national_number_confirm',
        'parent_other_number',
        'parent_other_number_confirm',
        'other_number',
        'other_number_confirm',
        'individual_extract_record',
        'individual_extract_record_confirm',
        'no_child_id_confirmation',
        'source_of_identification',
        'rims_case_number',
        'source_of_identification_specify',
        'other_nationality',
        'education_status',
        'caretaker_first_name',
        'caretaker_middle_name',
        'caretaker_last_name',
        'caretaker_mother_name',
        'miss_school_date',
        'round_start_date',
        'main_caregiver',
        'main_caregiver_nationality',
        'other_caregiver_relationship',
        'labour_weekly_income',
        'source_of_transportation',
        'consent_parents',
        'enrolled_formal_education'

    )

    def get_unicef_id(self, obj):
        return obj.student.unicef_id
    get_unicef_id.short_description = 'Unicef ID'

    def student_fullname_display(self, obj):
        return obj.student.full_name if obj.student else "-"
    student_fullname_display.short_description = 'Student Full Name'


class RSResource(resources.ModelResource):
    arabic_reading_improvement = fields.Field(
        column_name='arabic_reading_improvement',
        attribute='arabic_reading_improvement',
    )
    pretest_result = fields.Field(
        column_name='pretest_result',
        attribute='pretest_result',
    )
    posttest_result = fields.Field(
        column_name='posttest_result',
        attribute='posttest_result',
    )
    arabic_improvement = fields.Field(
        column_name='arabic_improvement',
        attribute='arabic_improvement',
    )
    language_improvement = fields.Field(
        column_name='language_improvement',
        attribute='language_improvement',
    )
    science_improvement = fields.Field(
        column_name='science_improvement',
        attribute='science_improvement',
    )
    math_improvement = fields.Field(
        column_name='math_improvement',
        attribute='math_improvement',
    )
    academic_test_improvement = fields.Field(
        column_name='academic_test_improvement',
        attribute='academic_test_improvement',
    )
    pre_test_score = fields.Field(
        column_name='pre_test_score',
        attribute='pre_test_score',
    )
    post_test_score = fields.Field(
        column_name='post_test_score',
        attribute='post_test_score',
    )
    assessment_improvement = fields.Field(
        column_name='assessment_improvement',
        attribute='assessment_improvement',
    )
    pre_motivation_score = fields.Field(
        column_name='pre_motivation_score',
        attribute='pre_motivation_score',
    )
    post_motivation_score = fields.Field(
        column_name='post_motivation_score',
        attribute='post_motivation_score',
    )
    motivation_improvement = fields.Field(
        column_name='motivation_improvement',
        attribute='motivation_improvement',
    )
    pre_self_assessment_score = fields.Field(
        column_name='pre_self_assessment_score',
        attribute='pre_self_assessment_score',
    )
    post_self_assessment_score = fields.Field(
        column_name='post_self_assessment_score',
        attribute='post_self_assessment_score',
    )
    self_assessment_improvement = fields.Field(
        column_name='self_assessment_improvement',
        attribute='self_assessment_improvement',
    )

    class Meta:
        model = RS
        fields = (
            'id',
            'partner__name',
            'new_registry',
            'round__name',
            'type',
            'site',
            'school',
            'governorate__name',
            'district__name',
            'location',
            'language',
            'student__id',
            'student__id_type',
            'student__id_number',
            'student__number',
            'student__first_name',
            'student__father_name',
            'student__last_name',
            'student__mother_fullname',
            'student__birthday_year',
            'student__birthday_month',
            'student__birthday_day',
            'student__nationality__name',
            'student__sex',
            'student__p_code',
            'disability__name',
            'internal_number',
            'comments',
            'hh_educational_level',
            'student__family_status',
            'student__have_children',
            'have_labour',
            'labours',
            'labour_hours',
            'registered_in_school',
            'shift',
            'grade',
            'section',
            'referral',
            'pre_reading_score',
            'post_reading_score',
            'arabic_reading_improvement',
            'pretest_result',
            'posttest_result',
            'arabic_improvement',
            'language_improvement',
            'science_improvement',
            'math_improvement',
            'academic_test_improvement',
            'pre_test_score',
            'post_test_score',
            'assessment_improvement',
            'pre_motivation_score',
            'post_motivation_score',
            'motivation_improvement',
            'pre_self_assessment_score',
            'post_self_assessment_score',
            'self_assessment_improvement',
            'participation',
            'barriers',
            'learning_result',
            'created',
            'modified'
        )
        export_order = fields


class RSAdmin(ImportExportModelAdmin):
    resource_class = RSResource
    form = RSAdminForm
    # fields = '__all__'

    list_display = (
        'student',
        'governorate',
        'district',
        'partner',
        'created',
        'modified',
    )
    list_filter = (
        'round',
        'type',
        'site',
        'school',
        'governorate',
        'district',
        'partner',
        'language',
        'student__sex',
        'student__nationality',
        'disability',
        'hh_educational_level',
        'student__family_status',
        'student__have_children',
        'have_labour',
        'labours',
        'labour_hours',
        'registered_in_school',
        'shift',
        'grade',
        'section',
        'referral',
        'participation',
        'barriers',
        'learning_result',
        'created',
        'modified',
    )
    search_fields = (
        'student__first_name',
        'student__father_name',
        'student__last_name',
        'student__mother_fullname',
    )

    def get_export_formats(self):
        from student_registration.users.utils import get_default_export_formats
        return get_default_export_formats()


class CBECEResource(resources.ModelResource):
    pre_test_score = fields.Field(
        column_name='pre_test_score',
        attribute='pre_test_score',
    )
    post_test_score = fields.Field(
        column_name='post_test_score',
        attribute='post_test_score',
    )
    art_improvement = fields.Field(
        column_name='art_improvement',
        attribute='art_improvement',
    )
    cognitive_improvement = fields.Field(
        column_name='cognitive_improvement',
        attribute='cognitive_improvement',
    )
    social_improvement = fields.Field(
        column_name='social_improvement',
        attribute='social_improvement',
    )
    psycho_improvement = fields.Field(
        column_name='psycho_improvement',
        attribute='psycho_improvement',
    )
    artistic_improvement = fields.Field(
        column_name='artistic_improvement',
        attribute='artistic_improvement',
    )
    assessment_improvement = fields.Field(
        column_name='assessment_improvement',
        attribute='assessment_improvement',
    )

    pre_test_LanguageArtDomain = fields.Field(column_name='pre_test_LanguageArtDomain')
    pre_test_CognitiveDomian = fields.Field(column_name='pre_test_CognitiveDomian')
    pre_test_ScienceDomain = fields.Field(column_name='pre_test_ScienceDomain')
    pre_test_SocialEmotionalDomain = fields.Field(column_name='pre_test_SocialEmotionalDomain')
    pre_test_PsychomotorDomain = fields.Field(column_name='pre_test_PsychomotorDomain')
    pre_test_ArtisticDomain = fields.Field(column_name='pre_test_ArtisticDomain')

    post_test_LanguageArtDomain = fields.Field(column_name='post_test_LanguageArtDomain')
    post_test_CognitiveDomian = fields.Field(column_name='post_test_CognitiveDomian')
    post_test_ScienceDomain = fields.Field(column_name='post_test_ScienceDomain')
    post_test_SocialEmotionalDomain = fields.Field(column_name='post_test_SocialEmotionalDomain')
    post_test_PsychomotorDomain = fields.Field(column_name='post_test_PsychomotorDomain')
    post_test_ArtisticDomain = fields.Field(column_name='post_test_ArtisticDomain')

    class Meta:
        model = CBECE
        fields = (
            'id',
            'partner__name',
            'new_registry',
            'student_outreached',
            'have_barcode',
            'outreach_barcode',
            'round__name',
            'cycle',
            'site',
            'school',
            'governorate__name',
            'district__name',
            'location',
            'language',
            'referral',
            'student__id',
            'student__id_type',
            'student__id_number',
            'student__number',
            'student__first_name',
            'student__father_name',
            'student__last_name',
            'student__mother_fullname',
            'student__birthday_year',
            'student__birthday_month',
            'student__birthday_day',
            'student__nationality__name',
            'student__sex',
            'student__p_code',
            'disability__name',
            'internal_number',
            'comments',
            'child_muac',
            'hh_educational_level',
            'have_labour',
            'labours',
            'labour_hours',
            'pre_test_LanguageArtDomain',
            'pre_test_CognitiveDomian',
            'pre_test_ScienceDomain',
            'pre_test_SocialEmotionalDomain',
            'pre_test_PsychomotorDomain',
            'pre_test_ArtisticDomain',
            'pre_test_score',
            'post_test_LanguageArtDomain',
            'post_test_CognitiveDomian',
            'post_test_ScienceDomain',
            'post_test_SocialEmotionalDomain',
            'post_test_PsychomotorDomain',
            'post_test_ArtisticDomain',
            'post_test_score',
            'art_improvement',
            'cognitive_improvement',
            'social_improvement',
            'psycho_improvement',
            'artistic_improvement',
            'assessment_improvement',
            'participation',
            'barriers',
            'learning_result',
            'created',
            'modified'
        )
        export_order = fields

        def dehydrate_pre_test_LanguageArtDomain(self, obj):
            return obj.get_assessment_value('LanguageArtDomain', 'pre_test')

        def dehydrate_pre_test_CognitiveDomian(self, obj):
            return obj.get_assessment_value('CognitiveDomian', 'pre_test')

        def dehydrate_pre_test_ScienceDomain(self, obj):
            return obj.get_assessment_value('ScienceDomain', 'pre_test')

        def dehydrate_pre_test_SocialEmotionalDomain(self, obj):
            return obj.get_assessment_value('SocialEmotionalDomain', 'pre_test')

        def dehydrate_pre_test_PsychomotorDomain(self, obj):
            return obj.get_assessment_value('PsychomotorDomain', 'pre_test')

        def dehydrate_pre_test_ArtisticDomain(self, obj):
            return obj.get_assessment_value('ArtisticDomain', 'pre_test')

        def dehydrate_post_test_LanguageArtDomain(self, obj):
            return obj.get_assessment_value('LanguageArtDomain', 'post_test')

        def dehydrate_post_test_CognitiveDomian(self, obj):
            return obj.get_assessment_value('CognitiveDomian', 'post_test')

        def dehydrate_post_test_ScienceDomain(self, obj):
            return obj.get_assessment_value('ScienceDomain', 'post_test')

        def dehydrate_post_test_SocialEmotionalDomain(self, obj):
            return obj.get_assessment_value('SocialEmotionalDomain', 'post_test')

        def dehydrate_post_test_PsychomotorDomain(self, obj):
            return obj.get_assessment_value('PsychomotorDomain', 'post_test')

        def dehydrate_post_test_ArtisticDomain(self, obj):
            return obj.get_assessment_value('ArtisticDomain', 'post_test')


class CBECEAdmin(ImportExportModelAdmin):
    resource_class = CBECEResource
    form = CBECEAdminForm
    # fields = '__all__'

    list_display = (
        'student',
        'governorate',
        'district',
        'partner',
        'created',
        'modified',
    )
    list_filter = (
        'round',
        'cycle',
        'site',
        'school',
        'governorate',
        'district',
        'partner',
        'language',
        'student__sex',
        'student__nationality',
        'disability',
        'child_muac',
        'hh_educational_level',
        'student__family_status',
        'student__have_children',
        'have_labour',
        'labours',
        'labour_hours',
        'participation',
        'barriers',
        'learning_result',
        'created',
        'modified',
    )
    search_fields = (
        'student__first_name',
        'student__father_name',
        'student__last_name',
        'student__mother_fullname',
    )

    def get_export_formats(self):
        from student_registration.users.utils import get_default_export_formats
        return get_default_export_formats()


class ABLNResource(resources.ModelResource):
    arabic_improvement = fields.Field(
        column_name='arabic improvement',
        attribute='arabic_improvement',
    )
    english_improvement = fields.Field(
        column_name='english_improvement',
        attribute='english_improvement',
    )
    french_improvement = fields.Field(
        column_name='french_improvement',
        attribute='french_improvement',
    )
    math_improvement = fields.Field(
        column_name='math_improvement',
        attribute='math_improvement',
    )
    assessment_improvement = fields.Field(
        column_name='assessment_improvement',
        attribute='assessment_improvement',
    )

    pre_test_arabic = fields.Field(column_name='pre test arabic')
    pre_test_foreign_language = fields.Field(column_name='pre_test_foreign_language')
    pre_test_math = fields.Field(column_name='pre_test_math')

    post_test_arabic = fields.Field(column_name='post_test_arabic')
    post_test_foreign_language = fields.Field(column_name='post_test_foreign_language')
    post_test_math = fields.Field(column_name='post_test_math')

    class Meta:
        fields = (
            'id',
            'partner__name',
            'new_registry',
            'student_outreached',
            'have_barcode',
            'outreach_barcode',
            'round__name',
            'governorate__name',
            'district__name',
            'location',
            'language',
            'student__id',
            'student__id_type',
            'student__id_number',
            'student__number',
            'student__first_name',
            'student__father_name',
            'student__last_name',
            'student__mother_fullname',
            'student__birthday_year',
            'student__birthday_month',
            'student__birthday_day',
            'student__nationality__name',
            'student__sex',
            'student__p_code',
            'disability__name',
            'internal_number',
            'comments',
            'hh_educational_level',
            'student__family_status',
            'student__have_children',
            'have_labour',
            'labours',
            'labour_hours',
            'pre_test_arabic',
            'pre_test_foreign_language',
            'pre_test_math',
            'pre_test_score',
            'post_test_arabic',
            'post_test_foreign_language',
            'post_test_math',
            'post_test_score',
            'arabic_improvement',
            'english_improvement',
            'french_improvement',
            'math_improvement',
            'assessment_improvement',
            'participation',
            'barriers',
            'learning_result',
            'created',
            'modified'
        )
        model = ABLN
        export_order = fields

        def dehydrate_pre_test_arabic(self, obj):
            return obj.get_assessment_value('arabic', 'pre_test')

        def dehydrate_pre_test_foreign_language(self, obj):
            return obj.get_assessment_value('foreign_language', 'pre_test')

        def dehydrate_pre_test_math(self, obj):
            return obj.get_assessment_value('math', 'pre_test')

        def dehydrate_post_test_arabic(self, obj):
            return obj.get_assessment_value('arabic', 'post_test')

        def dehydrate_post_test_foreign_language(self, obj):
            return obj.get_assessment_value('foreign_language', 'post_test')

        def dehydrate_post_test_math(self, obj):
            return obj.get_assessment_value('math', 'post_test')


class ABLNAdmin(ImportExportModelAdmin):
    resource_class = ABLNResource
    form = ABLNAdminForm
    # fields = '__all__'

    list_display = (
        'student',
        'governorate',
        'district',
        'partner',
        'created',
        'modified',
    )
    list_filter = (
        'round',
        'governorate',
        'district',
        'partner',
        'language',
        'student__sex',
        'student__nationality',
        'disability',
        'hh_educational_level',
        'student__family_status',
        'student__have_children',
        'have_labour',
        'labours',
        'labour_hours',
        'participation',
        'barriers',
        'learning_result',
        'created',
        'modified',
    )
    search_fields = (
        'student__first_name',
        'student__father_name',
        'student__last_name',
        'student__mother_fullname',
    )

    def get_export_formats(self):
        from student_registration.users.utils import get_default_export_formats
        return get_default_export_formats()


class DisabilityResource(resources.ModelResource):
    class Meta:
        model = Disability
        fields = (
            'id',
            'name',
            'name_en',
        )
        export_order = fields


class DisabilityAdmin(ImportExportModelAdmin):
    resource_class = DisabilityResource


class InclusionResource(resources.ModelResource):
    arabic_improvement = fields.Field(
        column_name='arabic improvement',
        attribute='arabic_improvement',
    )
    english_improvement = fields.Field(
        column_name='english_improvement',
        attribute='english_improvement',
    )
    french_improvement = fields.Field(
        column_name='french_improvement',
        attribute='french_improvement',
    )
    math_improvement = fields.Field(
        column_name='math_improvement',
        attribute='math_improvement',
    )
    assessment_improvement = fields.Field(
        column_name='assessment_improvement',
        attribute='assessment_improvement',
    )

    pre_test_arabic = fields.Field(column_name='pre test arabic')
    pre_test_foreign_language = fields.Field(column_name='pre_test_foreign_language')
    pre_test_math = fields.Field(column_name='pre_test_math')

    post_test_arabic = fields.Field(column_name='post_test_arabic')
    post_test_foreign_language = fields.Field(column_name='post_test_foreign_language')
    post_test_math = fields.Field(column_name='post_test_math')

    class Meta:
        fields = (
            'id',
            'partner__name',
            'new_registry',
            'student_outreached',
            'have_barcode',
            'outreach_barcode',
            'round__name',
            'governorate__name',
            'district__name',
            'location',
            'language',
            'student__id',
            'student__id_type',
            'student__id_number',
            'student__number',
            'student__first_name',
            'student__father_name',
            'student__last_name',
            'student__mother_fullname',
            'student__birthday_year',
            'student__birthday_month',
            'student__birthday_day',
            'student__nationality__name',
            'student__sex',
            'student__p_code',
            'disability__name',
            'internal_number',
            'comments',
            'hh_educational_level',
            'student__family_status',
            'student__have_children',
            'have_labour',
            'labours',
            'labour_hours',
            'pre_test_arabic',
            'pre_test_foreign_language',
            'pre_test_math',
            'pre_test_score',
            'post_test_arabic',
            'post_test_foreign_language',
            'post_test_math',
            'post_test_score',
            'arabic_improvement',
            'english_improvement',
            'french_improvement',
            'math_improvement',
            'assessment_improvement',
            'participation',
            'barriers',
            'learning_result',
            'created',
            'modified'
        )
        model = Inclusion
        export_order = fields

        def dehydrate_pre_test_arabic(self, obj):
            return obj.get_assessment_value('arabic', 'pre_test')

        def dehydrate_pre_test_foreign_language(self, obj):
            return obj.get_assessment_value('foreign_language', 'pre_test')

        def dehydrate_pre_test_math(self, obj):
            return obj.get_assessment_value('math', 'pre_test')

        def dehydrate_post_test_arabic(self, obj):
            return obj.get_assessment_value('arabic', 'post_test')

        def dehydrate_post_test_foreign_language(self, obj):
            return obj.get_assessment_value('foreign_language', 'post_test')

        def dehydrate_post_test_math(self, obj):
            return obj.get_assessment_value('math', 'post_test')


class InclusionAdmin(ImportExportModelAdmin):
    resource_class = InclusionResource
    form = InclusionAdminForm
    # fields = '__all__'

    list_display = (
        'student',
        'governorate',
        'district',
        'partner',
        'created',
        'modified',
    )
    list_filter = (
        'round',
        'governorate',
        'district',
        'partner',
        'student__sex',
        'student__nationality',
        'disability',
        'student__family_status',
        'student__have_children',
        'have_labour',
        'participation',
        'barriers',
        'learning_result',
        'created',
        'modified',
    )
    search_fields = (
        'student__first_name',
        'student__father_name',
        'student__last_name',
        'student__mother_fullname',
    )

    def get_export_formats(self):
        from student_registration.users.utils import get_default_export_formats
        return get_default_export_formats()


class CenterResource(resources.ModelResource):
    class Meta:
        model = Center
        fields = (
            'id',
            'name',
        )
        export_order = fields


class CenterAdmin(ImportExportModelAdmin):
    resource_class = CenterResource


class OutreachResource(resources.ModelResource):
    class Meta:
        fields = (
            'id',
            'partner__name',
            'new_registry',
            'round__name',
            'governorate__name',
            'district__name',
            'location',
            'language',
            'student__id',
            'student__id_type',
            'student__id_number',
            'student__number',
            'student__first_name',
            'student__father_name',
            'student__last_name',
            'student__mother_fullname',
            'student__birthday_year',
            'student__birthday_month',
            'student__birthday_day',
            'student__nationality__name',
            'student__sex',
            'student__p_code',
            'disability__name',
            'internal_number',
            'comments',
            'hh_educational_level',
            'student__family_status',
            'student__have_children',
            'have_labour',
            'labours',
            'labour_hours',
            'participation',
            'barriers',
            'learning_result',
            'created',
            'modified'
        )
        model = Outreach
        export_order = fields


class OutreachAdmin(ImportExportModelAdmin):
    resource_class = OutreachResource
    form = OutreachAdminForm
    # fields = '__all__'

    list_display = (
        'student',
        'governorate',
        'district',
        'partner',
        'created',
        'modified',
    )
    list_filter = (
        'round',
        'governorate',
        'district',
        'partner',
        'language',
        'student__sex',
        'student__nationality',
        'disability',
        'hh_educational_level',
        'student__family_status',
        'student__have_children',
        'have_labour',
        'labours',
        'labour_hours',
        'participation',
        'barriers',
        'learning_result',
        'created',
        'modified',
    )
    search_fields = (
        'student__first_name',
        'student__father_name',
        'student__last_name',
        'student__mother_fullname',
    )

    def get_export_formats(self):
        from student_registration.users.utils import get_default_export_formats
        return get_default_export_formats()


# admin.site.register(Assessment)
# admin.site.register(Cycle)
# admin.site.register(Site)
admin.site.register(Center, CenterAdmin)
# admin.site.register(Referral)
admin.site.register(Disability, DisabilityAdmin)
# admin.site.register(BLN, BLNAdmin)
admin.site.register(Bridging, BridgingAdmin)
# admin.site.register(ABLN, ABLNAdmin)
# admin.site.register(RS, RSAdmin)
# admin.site.register(CBECE, CBECEAdmin)
admin.site.register(Inclusion, InclusionAdmin)
# admin.site.register(Outreach, OutreachAdmin)
