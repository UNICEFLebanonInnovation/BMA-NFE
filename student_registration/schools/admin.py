# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals


from django.contrib import admin
from import_export import resources, fields
from import_export import fields
from import_export.admin import ImportExportModelAdmin

from .models import (
    School,
    Section,
    PartnerOrganization,
    EducationalLevel,
    CLMRound,
    PublicHolidays,
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


class PartnerOrganizationAdmin(ImportExportModelAdmin):
    filter_horizontal = ('schools', )
    search_fields = ('name', 'short_name')
    list_filter = ('active',)
    list_display = (
        'name',
        'short_name',
        'active',
    )
    fields = (
        'name',
        'short_name',
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
    )

    list_display = (
        'name',
        'current_year',
        'current_round_bridging',
    )


class EducationalLevelResource(resources.ModelResource):
    class Meta:
        model = EducationalLevel
        fields = (
            'id',
            'name',
        )
        export_order = fields


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
        )
        export_order = fields


class SchoolAdmin(ImportExportModelAdmin):
    resource_class = SchoolResource

    # Keep the centrally managed school page aligned with the profile that ALP
    # focal points see.
    fields = School.ALP_PROFILE_FIELDS
    LOCATION_TYPES_BY_FIELD = {
        'governorate': 1,
        'district': 2,
        'cadaster': 3,
    }

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        location_type_id = self.LOCATION_TYPES_BY_FIELD.get(db_field.name)
        if location_type_id is not None:
            kwargs['queryset'] = Location.objects.filter(type_id=location_type_id)

        return super(SchoolAdmin, self).formfield_for_foreignkey(
            db_field, request, **kwargs
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
    )
    search_fields = (
        'name',
        'number',
    )

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(School, SchoolAdmin)
# admin.site.register(Section, SectionAdmin)
admin.site.register(PartnerOrganization, PartnerOrganizationAdmin)
admin.site.register(EducationalLevel, EducationalLevelAdmin)
# admin.site.register(PublicHolidays)
# admin.site.register(ClubType, ClubTypeAdmin)
