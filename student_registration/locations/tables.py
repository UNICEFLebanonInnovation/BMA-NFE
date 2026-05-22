# coding: utf-8
import django_tables2 as tables
from django.utils.translation import gettext as _

from .models import Center


class BootstrapTable(tables.Table):

    class Meta:
        model = Center
        template = 'django_tables2/bootstrap5.html'
        attrs = {'class': 'table table-hover'}


class CenterTable(tables.Table):
    profile_column = tables.TemplateColumn(verbose_name=_('Actions'), orderable=False,
                                        template_name='django_tables2/location/center_profile_column.html',
                                        attrs={'url': '/locations/center-profile/'})
    class Meta:
        model = Center
        template = 'django_tables2/bootstrap5.html'
        attrs = {'class': 'table table-hover'}
        fields = (
            'profile_column',
            'name',
            'partner',
            'governorate',
            'caza',
            'cadaster',
            'longitude',
            'latitude',
            'manager_name',
            'phone_number',
            'email',
            'type',
            'owner_name',
            'modified_by_name',)

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user and not (user.is_staff or user.groups.filter(name='MSCC_UNICEF').exists()):
            self.exclude = tuple(set(self.exclude + ('partner',)))
