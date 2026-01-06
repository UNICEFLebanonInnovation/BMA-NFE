# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.contrib import admin
from import_export import resources, fields
from import_export import fields
from import_export.admin import ImportExportModelAdmin
from django.utils.translation import gettext, gettext_lazy as _
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin
from .models import User, WebPushToken
from .forms import UserAdminForm
from django.contrib.admin import SimpleListFilter
from student_registration.users.templatetags.custom_tags import has_group

class UserCategoryFilter(SimpleListFilter):
    title = 'User Category'
    parameter_name = 'user_category'

    def lookups(self, request, model_admin):
        return (
            ('MSCC', 'MSCC'),
            ('YOUTH', 'YOUTH'),
            ('Dirasa', 'Dirasa'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'MSCC':
            return queryset.filter(groups__name='MSCC')
        if self.value() == 'YOUTH':
            return queryset.filter(groups__name='YOUTH')
        if self.value() == 'Dirasa':
            return queryset.exclude(groups__name__in=['MSCC', 'YOUTH'])
        return queryset


class UserResource(resources.ModelResource):
    is_active = fields.Field(column_name='is_active', attribute='is_active')
    user_category = fields.Field(column_name='user_category')

    class Meta:
        model = User
        fields = (
            'id',
            'first_name',
            'last_name',
            'username',
            'email',
            'partner__name',
            'school__name',
            'center__name',
            'partner__name',
            'is_active',
            'user_category',
        )
        export_order = fields

    def dehydrate_user_category(self, user):
        if has_group(user, 'MSCC'):
            return 'MSCC'
        if has_group(user, 'YOUTH'):
            return 'YOUTH'
        return 'Dirasa'


class UserAdmin(AuthUserAdmin, ImportExportModelAdmin):
    resource_class = UserResource
    form = UserAdminForm
    filter_horizontal = ('groups', 'user_permissions')
    list_display = (
        'username',
        'first_name',
        'last_name',
        'is_active',
        'email',
        'school',
        'center',
        'partner',
        'phone_number',
        'is_active',
        'user_category_display'
    )
    search_fields = (
        u'username',
        u'school__name',
        u'first_name',
        u'last_name',
    )
    list_filter = (
        'groups',
        'school',
        'center',
        'partner',
        'is_active',
        UserCategoryFilter
    )
    actions = (
        'activate',
        'disable',
    )

    fieldsets = (
        ('Account', {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email',
                                         'partner', 'phone_number', 'center', 'school')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')})
    )

    def user_category_display(self, obj):
        if has_group(obj, 'MSCC'):
            return 'MSCC'
        if has_group(obj, 'YOUTH'):
            return 'YOUTH'
        return 'Dirasa'
    user_category_display.short_description = 'User Category'

    def activate(self, request, queryset):
        queryset.update(is_active=True)

    def disable(self, request, queryset):
        queryset.update(is_active=False)
        return False


admin.site.register(User, UserAdmin)
admin.site.register(WebPushToken)


