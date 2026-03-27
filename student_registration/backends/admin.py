# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.contrib import admin
from django.urls import path
from django.db.models import Count
from django.template.response import TemplateResponse

from import_export import resources, fields
from import_export.admin import ImportExportModelAdmin
from .models import ExportHistory, UserActivity


class ExportHistoryAdmin(admin.ModelAdmin):

    change_list_template = 'admin/export_history_change_list.html'

    list_display = (
        'export_type',
        'status',
        'created_by',
        'partner_name',
        'created',
        'modified',
    )
    list_filter = (
        'export_type',
        'partner_name',
    )
    search_fields = (
        'created_by__username',
    )
    list_select_related = ('created_by',)

    def get_urls(self):
        urls = super().get_urls()
        extra_urls = [
            path('dashboard/', self.admin_site.admin_view(self.dashboard_view), name='exporthistory_dashboard'),
        ]
        return extra_urls + urls

    def dashboard_view(self, request):
        queryset = ExportHistory.objects.all()

        export_stats = list(queryset.values('export_type').annotate(count=Count('id')).order_by('-count'))
        partner_stats = list(queryset.values('partner_name').annotate(count=Count('id')).order_by('-count'))

        # Determine the most frequently exported data fields based on 'fields' JSON
        field_stats = {}
        for record in queryset.exclude(fields__isnull=True).exclude(fields=''):
            if isinstance(record.fields, dict):
                for key in record.fields.keys():
                    field_stats[key] = field_stats.get(key, 0) + 1

        sorted_field_stats = sorted([{'field': k, 'count': v} for k, v in field_stats.items()], key=lambda x: x['count'], reverse=True)[:15]

        context = dict(
            self.admin_site.each_context(request),
            title='Export History Dashboard',
            export_stats=export_stats,
            partner_stats=partner_stats,
            field_stats=sorted_field_stats,
            total=queryset.count(),
        )
        return TemplateResponse(request, 'admin/export_history_dashboard.html', context)


class UserActivityAdmin(admin.ModelAdmin):

    change_list_template = 'admin/user_activity_change_list.html'

    list_display = (
        'username',
        'path',
        'method',
        'data',
        'timestamp',
    )
    list_filter = (
        'method',
    )
    search_fields = (
        'username',
        'path'

    )

    def get_urls(self):
        urls = super().get_urls()
        extra_urls = [
            path('dashboard/', self.admin_site.admin_view(self.dashboard_view), name='useractivity_dashboard'),
        ]
        return extra_urls + urls

    def dashboard_view(self, request):
        queryset = UserActivity.objects.all()

        method_stats = list(queryset.values('method').annotate(count=Count('id')).order_by('-count'))
        top_paths = list(queryset.values('path').annotate(count=Count('id')).order_by('-count')[:10])

        context = dict(
            self.admin_site.each_context(request),
            title='User Activity Dashboard',
            method_stats=method_stats,
            top_paths=top_paths,
            total=queryset.count(),
        )
        return TemplateResponse(request, 'admin/user_activity_dashboard.html', context)



admin.site.register(ExportHistory, ExportHistoryAdmin)
admin.site.register(UserActivity, UserActivityAdmin)
