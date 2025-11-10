# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.contrib import admin
from import_export import resources, fields
from import_export import fields
from import_export.admin import ImportExportModelAdmin

from .models import (
    Location,
    LocationType,
    Center
)
from .forms import CenterAdminForm


class LocationResource(resources.ModelResource):
    class Meta:
        model = Location
        fields = (
            'id',
            'name',
            'name_en',
            'type',
            'parent__id',
            'latitude',
            'longitude',
            'p_code'
        )
        export_order = ('name', )


class LocationAdmin(ImportExportModelAdmin):
    resource_class = LocationResource
    list_display = (
        'name', 'parent'
    )

    def get_export_formats(self):
        from student_registration.users.utils import get_default_export_formats
        return get_default_export_formats()


class CenterResource(resources.ModelResource):
    class Meta:
        model = Center
        import_id_fields = ('id',)
        fields = (
            'id',
            'name',
            'partner',
            'type',
            'governorate',
            'caza',
            'cadaster',
            'longitude',
            'latitude',
            'manager_name',
            'phone_number',
            'email',
            'is_active',
            'p_code',
        )
        export_order = fields

    def before_save_instance(self, instance, using_transactions, dry_run):
        if not instance.email:
            instance.email = ''


class CenterAdmin(ImportExportModelAdmin):
    resource_class = CenterResource
    form = CenterAdminForm
    list_display = (
            'name',
            'governorate',
            'caza',
            'cadaster',
            'longitude',
            'latitude',
            'p_code',
            'type',
            'partner',
            'is_active',
    )
    list_filter = (
        'name',
        'governorate',
        'type',
        'partner',
        'is_active',
    )
    search_fields = (
        'name',
    )

    def get_export_formats(self):
        from student_registration.users.utils import get_default_export_formats
        return get_default_export_formats()


admin.site.register(Location, LocationAdmin)
admin.site.register(LocationType)
admin.site.register(Center, CenterAdmin)
