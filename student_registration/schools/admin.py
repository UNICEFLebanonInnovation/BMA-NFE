# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals


from django.contrib import admin
from import_export import resources, fields
from import_export import fields
from import_export.admin import ImportExportModelAdmin

from .models import (
    School,
    EducationLevel,
    ClassLevel,
    Section,
    ClassRoom,
    PartnerOrganization,
    ALPReferMatrix,
    EducationYear,
    ALPAssignmentMatrix,
    EducationalLevel,
    Holiday,
    CLMRound,
    PublicDocument,
    Coordinator,
    Evaluation,
    PublicHolidays,
    Schl_Subject,
    ClubType
)
from student_registration.locations.models import Location

class ClubTypeResource(resources.ModelResource):
    class Meta:
        model = ClubType
        fields = (
            'id',
            'name',
        )
        export_order = ('name', )


class ClubTypeAdmin(ImportExportModelAdmin):
    resource_class = ClubTypeResource


class GovernorateFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = 'Governorate'

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'governorate'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return ((l.id, l.name) for l in Location.objects.filter(type_id=1))

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        if self.value():
            return queryset.filter(location__parent_id=self.value())
        return queryset


class SchoolTypeFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = 'School type'

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'school_type'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return (
            ('alp', 'ALP'),
            ('2ndshift', '2nd shift'),
            ('both', 'ALP & 2nd shift'),
        )

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        if not self.value():
            return queryset
        if self.value() == 'alp':
            return queryset.filter(is_alp=True)
        if self.value() == '2ndshift':
            return queryset.filter(is_2nd_shift=True)
        if self.value() == 'both':
            return queryset.filter(is_alp=True, is_2nd_shift=True)



class EducationLevelResource(resources.ModelResource):
    class Meta:
        model = EducationLevel
        fields = (
            'id',
            'name',
            'note',
        )
        export_order = ('name',)


class EducationLevelAdmin(ImportExportModelAdmin):
    resource_class = EducationLevelResource

    def get_export_formats(self):
        from student_registration.users.utils import get_default_export_formats
        return get_default_export_formats()


class ClassLevelResource(resources.ModelResource):
    class Meta:
        model = ClassLevel
        fields = (
            'id',
            'name'
        )
        export_order = ('name',)


class ClassLevelAdmin(ImportExportModelAdmin):
    resource_class = ClassLevelResource
    def get_export_formats(self):
        from student_registration.users.utils import get_default_export_formats
        return get_default_export_formats()


class SectionResource(resources.ModelResource):
    class Meta:
        model = Section
        fields = (
            'id',
            'name'
        )
        export_order = ('name',)


class SectionAdmin(ImportExportModelAdmin):
    resource_class = SectionResource

    def get_export_formats(self):
        from student_registration.users.utils import get_default_export_formats
        return get_default_export_formats()


class ClassRoomResource(resources.ModelResource):
    class Meta:
        model = ClassRoom
        fields = (
            'id',
            'name',
        )
        export_order = fields


class ClassRoomAdmin(ImportExportModelAdmin):
    resource_class = ClassRoomResource
    fields = (
        'name',
        'classroom_type',
    )
    list_display = fields

    def get_export_formats(self):
        from student_registration.users.utils import get_default_export_formats
        return get_default_export_formats()


class PartnerOrganizationAdmin(ImportExportModelAdmin):
    filter_horizontal = ('schools', )
    search_fields = ('name', 'short_name')
    list_filter = ('is_Kayany', 'is_unrwa', 'is_youth', 'active')
    list_display = (
        'name',
        'short_name',
        'is_Kayany',
        'is_unrwa',
        'is_youth',
        'active',
    )
    fields = (
        'name',
        'short_name',
        'is_Kayany',
        'is_unrwa',
        'is_youth',
        'active',
        'schools'
    )

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "schools":
            kwargs["queryset"] = School.objects.filter(is_closed=False)
        return super(PartnerOrganizationAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)

    def get_export_formats(self):
        from student_registration.users.utils import get_default_export_formats
        return get_default_export_formats()


class ALPReferMatrixResource(resources.ModelResource):
    class Meta:
        model = ALPReferMatrix


class ALPReferMatrixAdmin(ImportExportModelAdmin):
    resource_class = ALPReferMatrixResource
    fields = (
        'level',
        'age',
        'success_refer_to',
        'fail_refer_to',
        'success_grade',
    )
    list_display = fields

    def get_export_formats(self):
        from student_registration.users.utils import get_default_export_formats
        return get_default_export_formats()


class ALPAssignmentMatrixResource(resources.ModelResource):
    class Meta:
        model = ALPAssignmentMatrix


class ALPAssignmentMatrixAdmin(ImportExportModelAdmin):
    resource_class = ALPAssignmentMatrixResource
    fields = (
        'level',
        'range_start',
        'range_end',
        'refer_to',
        'matrix_type',
    )
    list_display = (
        'level',
        'range',
        'refer_to',
        'matrix_type',
    )

    def get_export_formats(self):
        from student_registration.users.utils import get_default_export_formats
        return get_default_export_formats()


class PublicDocumentResource(resources.ModelResource):
    class Meta:
        model = PublicDocument


class PublicDocumentAdmin(ImportExportModelAdmin):
    resource_class = PublicDocumentResource
    list_display = (
        'name',
        'file_url',
        'created',
        'modified'
    )

    def get_export_formats(self):
        from student_registration.users.utils import get_default_export_formats
        return get_default_export_formats()


class CLMRoundResource(resources.ModelResource):
    class Meta:
        model = CLMRound
        fields = (
            'id',
            'name',
        )
        export_order = fields


class CLMRoundAdmin(ImportExportModelAdmin):
    resource_class = CLMRoundResource

    fields = (
        'name',
        'current_year',
        'current_round_bridging',
        'start_date_bridging',
        'end_date_bridging',
        'start_date_bridging_edit',
        'end_date_bridging_edit',
        'current_year_inclusion',
        'current_round_inclusion',
        'start_date_inclusion',
        'end_date_inclusion',
        'start_date_inclusion_edit',
        'end_date_inclusion_edit',
    )

    list_display = (
        'name',
        'current_year',
        'current_round_bridging',
        'current_year_inclusion',
        'current_round_inclusion',
    )


class EducationalLevelResource(resources.ModelResource):
    class Meta:
        model = EducationalLevel
        fields = (
            'id',
            'name',
        )
        export_order = fields


class EvaluationResource(resources.ModelResource):

    class Meta:
        model = Evaluation
        fields = (
            'owner',
            'school',
            'school__location',
            'school__number',
            'school__name',
            'total_teaching_days',
            'total_teaching_days_tillnow',
            'implemented_de',
            'reasons_no_de',
            'challenges_de',
            'steps_de',
            'evaluate_steps_de',
            'other_notes_de',

            'c1_eng_completed',
            'c1_eng_completed_de',
            'c1_eng_remaining_de',
            'c1_fr_completed',
            'c1_fr_completed_de',
            'c1_fr_remaining_de',
            'c1_math_completed',
            'c1_math_completed_de',
            'c1_math_remaining_de',
            'c1_sc_completed',
            'c1_sc_completed_de',
            'c1_sc_remaining_de',
            'c1_ara_completed',
            'c1_ara_completed_de',
            'c1_ara_remaining_de',
            'c1_civic_completed',
            'c1_civic_completed_de',
            'c1_civic_remaining_de',
            'c1_geo_completed',
            'c1_geo_completed_de',
            'c1_geo_remaining_de',

            'c2_eng_completed',
            'c2_eng_completed_de',
            'c2_eng_remaining_de',
            'c2_fr_completed',
            'c2_fr_completed_de',
            'c2_fr_remaining_de',
            'c2_math_completed',
            'c2_math_completed_de',
            'c2_math_remaining_de',
            'c2_sc_completed',
            'c2_sc_completed_de',
            'c2_sc_remaining_de',
            'c2_ara_completed',
            'c2_ara_completed_de',
            'c2_ara_remaining_de',
            'c2_civic_completed',
            'c2_civic_completed_de',
            'c2_civic_remaining_de',
            'c2_geo_completed',
            'c2_geo_completed_de',
            'c2_geo_remaining_de',
            'implemented_de_2',
            'reasons_no_de_2',
            'challenges_de_2',
            'steps_de_2',
            'evaluate_steps_de_2',
            'implemented_de_3',
            'reasons_no_de_3',
            'challenges_de_3',
            'steps_de_3',
            'evaluate_steps_de_3',

            'c3_eng_completed',
            'c3_eng_completed_de',
            'c3_eng_remaining_de',
            'c3_fr_completed',
            'c3_fr_completed_de',
            'c3_fr_remaining_de',
            'c3_math_completed',
            'c3_math_completed_de',
            'c3_math_remaining_de',
            'c3_sc_completed',
            'c3_sc_completed_de',
            'c3_sc_remaining_de',
            'c3_ara_completed',
            'c3_ara_completed_de',
            'c3_ara_remaining_de',
            'c3_civic_completed',
            'c3_civic_completed_de',
            'c3_civic_remaining_de',
            'c3_geo_completed',
            'c3_geo_completed_de',
            'c3_geo_remaining_de',

            'implemented_de_3',
            'reasons_no_de_3',
            'challenges_de_3',
            'steps_de_3',
            'evaluate_steps_de_3',

            'c4_eng_completed',
            'c4_eng_completed_de',
            'c4_eng_remaining_de',
            'c4_fr_completed',
            'c4_fr_completed_de',
            'c4_fr_remaining_de',
            'c4_math_completed',
            'c4_math_completed_de',
            'c4_math_remaining_de',
            'c4_sc_completed',
            'c4_sc_completed_de',
            'c4_sc_remaining_de',
            'c4_ara_completed',
            'c4_ara_completed_de',
            'c4_ara_remaining_de',
            'c4_civic_completed',
            'c4_civic_completed_de',
            'c4_civic_remaining_de',
            'c4_geo_completed',
            'c4_geo_completed_de',
            'c4_geo_remaining_de',

            'c5_eng_completed',
            'c5_eng_completed_de',
            'c5_eng_remaining_de',
            'c5_fr_completed',
            'c5_fr_completed_de',
            'c5_fr_remaining_de',
            'c5_math_completed',
            'c5_math_completed_de',
            'c5_math_remaining_de',
            'c5_sc_completed',
            'c5_sc_completed_de',
            'c5_sc_remaining_de',
            'c5_ara_completed',
            'c5_ara_completed_de',
            'c5_ara_remaining_de',
            'c5_civic_completed',
            'c5_civic_completed_de',
            'c5_civic_remaining_de',
            'c5_geo_completed',
            'c5_geo_completed_de',
            'c5_geo_remaining_de',

            'c6_eng_completed',
            'c6_eng_completed_de',
            'c6_eng_remaining_de',
            'c6_fr_completed',
            'c6_fr_completed_de',
            'c6_fr_remaining_de',
            'c6_math_completed',
            'c6_math_completed_de',
            'c6_math_remaining_de',
            'c6_sc_completed',
            'c6_sc_completed_de',
            'c6_sc_remaining_de',
            'c6_ara_completed',
            'c6_ara_completed_de',
            'c6_ara_remaining_de',
            'c6_civic_completed',
            'c6_civic_completed_de',
            'c6_civic_remaining_de',
            'c6_geo_completed',
            'c6_geo_completed_de',
            'c6_geo_remaining_de',

            'c7_eng_completed',
            'c7_eng_completed_de',
            'c7_eng_remaining_de',
            'c7_fr_completed',
            'c7_fr_completed_de',
            'c7_fr_remaining_de',
            'c7_math_completed',
            'c7_math_completed_de',
            'c7_math_remaining_de',
            'c7_sc_completed',
            'c7_sc_completed_de',
            'c7_sc_remaining_de',
            'c7_ara_completed',
            'c7_ara_completed_de',
            'c7_ara_remaining_de',
            'c7_civic_completed',
            'c7_civic_completed_de',
            'c7_civic_remaining_de',
            'c7_geo_completed',
            'c7_geo_completed_de',
            'c7_geo_remaining_de',

            'c8_eng_completed',
            'c8_eng_completed_de',
            'c8_eng_remaining_de',
            'c8_fr_completed',
            'c8_fr_completed_de',
            'c8_fr_remaining_de',
            'c8_math_completed',
            'c8_math_completed_de',
            'c8_math_remaining_de',
            'c8_sc_completed',
            'c8_sc_completed_de',
            'c8_sc_remaining_de',
            'c8_ara_completed',
            'c8_ara_completed_de',
            'c8_ara_remaining_de',
            'c8_civic_completed',
            'c8_civic_completed_de',
            'c8_civic_remaining_de',
            'c8_geo_completed',
            'c8_geo_completed_de',
            'c8_geo_remaining_de',

            'c9_eng_completed',
            'c9_eng_completed_de',
            'c9_eng_remaining_de',
            'c9_fr_completed',
            'c9_fr_completed_de',
            'c9_fr_remaining_de',
            'c9_math_completed',
            'c9_math_completed_de',
            'c9_math_remaining_de',
            'c9_sc_completed',
            'c9_sc_completed_de',
            'c9_sc_remaining_de',
            'c9_ara_completed',
            'c9_ara_completed_de',
            'c9_ara_remaining_de',
            'c9_civic_completed',
            'c9_civic_completed_de',
            'c9_civic_remaining_de',
            'c9_geo_completed',
            'c9_geo_completed_de',
            'c9_geo_remaining_de',

            'cprep_eng_completed',
            'cprep_eng_completed_de',
            'cprep_eng_remaining_de',
            'cprep_fr_completed',
            'cprep_fr_completed_de',
            'cprep_fr_remaining_de',
            'cprep_math_completed',
            'cprep_math_completed_de',
            'cprep_math_remaining_de',
            'cprep_sc_completed',
            'cprep_sc_completed_de',
            'cprep_sc_remaining_de',
            'cprep_ara_completed',
            'cprep_ara_completed_de',
            'cprep_ara_remaining_de',
            'cprep_civic_completed',
            'cprep_civic_completed_de',
            'cprep_civic_remaining_de',
            'cprep_geo_completed',
            'cprep_geo_completed_de',
            'cprep_geo_remaining_de',
            'c9_total_std',
            'c9_total_std_de',
            'implemented_de_9',
            'reasons_no_de_9',
            'challenges_de_9',
            'steps_de_9',
            'evaluate_steps_de_9',
            'implemented_de_prep',
            'reasons_no_de_prep',
            'challenges_de_prep',
            'steps_de_prep',
            'evaluate_steps_de_prep',
            'c9_total_teachers',
            'c9_total_teachers_de',


        )
        list_display = fields

        export_order = fields


class EvaluationAdmin(ImportExportModelAdmin):
    resource_class = EvaluationResource
    class Meta:
        model = Evaluation
        list_filter = (
            'school',
            'school__location',
            'school__number',
            'school__name',
        )


class EducationalLevelAdmin(ImportExportModelAdmin):
    resource_class = EducationalLevelResource


class SchoolResource(resources.ModelResource):
    district = fields.Field(column_name='District')
    governorate = fields.Field(column_name='Governorate')

    class Meta:
        model = School
        fields = (
            'id',
            'number',
            'name',
            'director_name',
            'land_phone_number',
            'email',
            'governorate',
            'district',
            'cadaster',
            'longitude',
            'latitude',
            'registration_level',
            'school_capacity',
            'empty_building',
            'number_children',
            'number_children_male',
            'number_children_female',
            'number_children_lebanese',
            'number_children_non_lebanese',
            'number_children_sbp',
            'number_children_male_sbp',
            'number_children_female_sbp',
            'number_children_lebanese_sbp',
            'number_children_non_lebanese_sbp',
            'CWD_accessible',
            'internet_available',
            'school_digital_capacity',
            'is_first_shift',
            'working_days',
            'academic_year_start',
            'academic_year_end',
            'receive_supplies',
            'number_dirasa_children_disability',
            'number_total_children_disability',
            'is_closed',
        )
        export_order = fields

    # def dehydrate_district(self, obj):
    #     if obj.location:
    #         return obj.location.name
    #     return ''
    #
    # def dehydrate_governorate(self, obj):
    #     if obj.location and obj.location.parent:
    #         return obj.location.parent.name
    #     return ''


class SchoolAdmin(ImportExportModelAdmin):
    resource_class = SchoolResource

    fields = (
            'number',
            'name',
            'is_closed',
            'is_bma',
            'is_unrwa',
            'director_name',
            'land_phone_number',
            'email',
            'governorate',
            'district',
            'cadaster',
            'longitude',
            'latitude',
            'registration_level',
            'school_capacity',
            'empty_building',
            'number_children',
            'number_children_male',
            'number_children_female',
            'number_children_lebanese',
            'number_children_non_lebanese',
            'number_children_sbp',
            'number_children_male_sbp',
            'number_children_female_sbp',
            'number_children_lebanese_sbp',
            'number_children_non_lebanese_sbp',
            'CWD_accessible',
            'internet_available',
            'school_digital_capacity',
            'is_first_shift',
            'working_days',
            'academic_year_start',
            'academic_year_end',
            'receive_supplies',
            'number_dirasa_children_disability',
            'number_total_children_disability',
    )
    list_display = (
        'id',
        'number',
        'name',
        'director_name',
        'land_phone_number',
        'email',
        'governorate',
        'district',
        'is_closed',
        'is_bma',
        'is_unrwa',
    )
    search_fields = (
        'name',
        'number',
    )
    list_filter = ('is_closed', 'is_bma','is_unrwa',)

    def has_delete_permission(self, request, obj=None):
        return False

    # actions = []
    # list_filter = (
    #     GovernorateFilter,
    #     'location',
    #     'is_closed',
    # )
    # date_hierarchy = 'academic_year_start'

    # actions = ('open_attendance_90_days', 'open_attendance_60_days',
    #            'open_attendance_30_days', 'open_attendance_20_days',
    #            'open_attendance_10_days', 'open_attendance_from_beginning',
    #            'close_attendance_from_beginning', )

    # def open_attendance_90_days(self, request, queryset):
    #     queryset.update(attendance_range=90)
    #
    # def open_attendance_60_days(self, request, queryset):
    #     queryset.update(attendance_range=60)
    #
    # def open_attendance_30_days(self, request, queryset):
    #     queryset.update(attendance_range=30)
    #
    # def open_attendance_20_days(self, request, queryset):
    #     queryset.update(attendance_range=20)
    #
    # def open_attendance_10_days(self, request, queryset):
    #     queryset.update(attendance_range=10)
    #
    # def open_attendance_from_beginning(self, request, queryset):
    #     queryset.update(attendance_from_beginning=True)
    #
    # def close_attendance_from_beginning(self, request, queryset):
    #     queryset.update(attendance_from_beginning=False)

    # def get_export_formats(self):
    #     from student_registration.users.utils import get_default_export_formats
    #     return get_default_export_formats()


admin.site.register(School, SchoolAdmin)
# admin.site.register(EducationLevel, EducationLevelAdmin)
# admin.site.register(ClassLevel, ClassLevelAdmin)
admin.site.register(Section, SectionAdmin)
# admin.site.register(ClassRoom, ClassRoomAdmin)
admin.site.register(PartnerOrganization, PartnerOrganizationAdmin)
# admin.site.register(ALPReferMatrix, ALPReferMatrixAdmin)
# admin.site.register(EducationYear)
# admin.site.register(Holiday)
admin.site.register(CLMRound, CLMRoundAdmin)
# admin.site.register(PublicDocument, PublicDocumentAdmin)
admin.site.register(EducationalLevel, EducationalLevelAdmin)
# admin.site.register(ALPAssignmentMatrix, ALPAssignmentMatrixAdmin)
# admin.site.register(Coordinator)
# admin.site.register(Schl_Subject)
# admin.site.register(Evaluation, EvaluationAdmin)
admin.site.register(PublicHolidays)
admin.site.register(ClubType, ClubTypeAdmin)
