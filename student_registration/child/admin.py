# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from .models import Child


class ChildAdmin(admin.ModelAdmin):

    list_display = (
        'first_name',
        'father_name',
        'last_name',
        'mother_fullname',
        'nationality',
        'birthday_year',
        'disability',
        'marital_status',
        'unicef_id',
        'created',
        'modified',
    )
    list_filter = (
        'nationality',
        'birthday_year',
        'p_code',
        'disability',
        'marital_status',
        'number',
        'created',
        'modified',
    )
    search_fields = (
        'first_name',
        'father_name',
        'last_name',
    )


admin.site.register(Child, ChildAdmin)
