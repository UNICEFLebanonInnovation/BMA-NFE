# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.contrib import admin
from import_export import resources, fields
from import_export.admin import ImportExportModelAdmin
import datetime

from .models import (
    Student,
    Nationality,
    IDType,
    Labour,
    Teacher,
    Training,
    AttachmentType
)


class NationalityResource(resources.ModelResource):
    class Meta:
        model = Nationality
        fields = (
            'id',
            'name',
        )
        export_order = ('name', )


class NationalityAdmin(ImportExportModelAdmin):
    resource_class = NationalityResource


class IDTypeResource(resources.ModelResource):
    class Meta:
        model = IDType
        fields = (
            'id',
            'name'
        )
        export_order = ('name', )


class IDTypeAdmin(ImportExportModelAdmin):
    resource_class = IDTypeResource

    def get_export_formats(self):
        from student_registration.users.utils import get_default_export_formats
        return get_default_export_formats()


class FromAgeFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = 'From Age'

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'from_age'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return ((l, l) for l in range(0, 100))

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        if self.value():
            now = datetime.datetime.now()
            return queryset.filter(birthday_year__lte=(now.year - int(self.value())))

        return queryset


class ToAgeFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = 'To Age'

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'to_age'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return ((l, l) for l in range(0, 100))

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        if self.value():
            now = datetime.datetime.now()
            return queryset.filter(birthday_year__gte=(now.year - int(self.value())))
        return queryset


class StudentResource(resources.ModelResource):

    class Meta:
        model = Student
        fields = (
            'first_name',
            'father_name',
            'last_name',
            'mother_fullname',
            # 'age',
            'birthday_day',
            'birthday_month',
            'birthday_year',
            'place_of_birth',
            'sex',
            'nationality',
            'mother_nationality',
            'id_type',
            'id_number',
            'unicef_id',
            'number',
            'address',
            'phone',
            'phone_prefix',
            'std_image',
            'recordnumber',
            'unhcr_family',
            'unhcr_personal',
            'is_specialneeds',
            'specialneeds',
            'specialneedsdt',
            'unhcr_family',
            'unhcr_personal',
            'is_financialsupport',
            'Financialsupport_number',
            'financialsupport',
            #'id_image',
            'unhcr_image',
            'birthdoc_image',
            'std_image',

        )
        export_order = (
            'first_name',
            'father_name',
            'last_name',
            'mother_fullname',
            # 'age',
            'birthday_day',
            'birthday_month',
            'birthday_year',
            'sex',
            'nationality',
            'mother_nationality',
            'id_type',
            'id_number',
            'unicef_id',
            'number',
            'address',
            'phone',
            'phone_prefix',
        )


class StudentAdmin(ImportExportModelAdmin):
    resource_class = StudentResource
    list_display = (
        'first_name',
        'father_name',
        'last_name',
        'mother_fullname',
        'age',
        'sex',
        'nationality',
        'mother_nationality',
        'unicef_id'

    )
    list_filter = (
        'unicef_id',
        FromAgeFilter,
        ToAgeFilter,
        'birthday_day',
        'birthday_month',
        'birthday_year',
        'sex',
        'nationality',
        'mother_nationality',
    )
    search_fields = (
        'first_name',
        'father_name',
        'last_name',
        'mother_fullname',
        'id_number',
    )

    def get_export_formats(self):
        from student_registration.users.utils import get_default_export_formats
        return get_default_export_formats()


class TeacherAdmin(ImportExportModelAdmin):
    list_display = (
        'first_name',
        'father_name',
        'last_name',
        'sex',
        'unicef_id'

    )
    list_filter = (
        'sex',
    )
    search_fields = (
        'first_name',
        'father_name',
        'last_name',
        'unicef_id',
    )


class TrainingResource(resources.ModelResource):
    class Meta:
        model = Training
        fields = (
            'id',
            'name',
        )
        export_order = ('name', )


class TrainingAdmin(ImportExportModelAdmin):
    resource_class = TrainingResource


class AttachmentTypeResource(resources.ModelResource):
    class Meta:
        model = AttachmentType
        fields = (
            'id',
            'name',
        )
        export_order = ('name', )


class AttachmentTypeAdmin(ImportExportModelAdmin):
    resource_class = AttachmentTypeResource


admin.site.register(Student, StudentAdmin)
admin.site.register(Teacher, TeacherAdmin)
admin.site.register(Nationality, NationalityAdmin)
admin.site.register(IDType, IDTypeAdmin)
admin.site.register(Labour)
admin.site.register(Training, TrainingAdmin)
admin.site.register(AttachmentType, AttachmentTypeAdmin)
