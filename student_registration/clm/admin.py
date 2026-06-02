# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.contrib import admin
from import_export import resources, fields
from import_export import fields
from import_export.admin import ImportExportModelAdmin

from .models import (
    Disability,
    Bridging,
    Center,
)


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


# admin.site.register(Center, CenterAdmin)
admin.site.register(Disability, DisabilityAdmin)
# admin.site.register(Bridging, BridgingAdmin)
