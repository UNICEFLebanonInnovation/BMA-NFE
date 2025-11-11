# coding: utf-8
import django_tables2 as tables
from django.utils.translation import gettext as _
from django.urls import reverse
from django.utils.html import format_html

from .models import Registration


class BootstrapTable(tables.Table):

    class Meta:
        model = Registration
        template = 'django_tables2/bootstrap4.html'
        attrs = {'class': 'table table-bordered table-striped table-hover'}


class CommonTable(tables.Table):
    child_age = tables.Column(
        verbose_name=_('Age'),
        orderable=False,
    )
    child_birthday = tables.Column(
        verbose_name=_('Birthday'),
        orderable=False,
    )
    education_program = tables.Column(
        verbose_name=_('Education Program'),
        orderable=False,
    )
    class_section = tables.Column(
        verbose_name=_('Section'),
        orderable=False,
    )
    has_previous_registration = tables.Column(
        verbose_name=_('Has Previous Registration'),
        orderable=False,
    )

    # child_unicef_id = tables.Column(
    #     verbose_name=_('UNICEF ID'),
    #     orderable=False,
    # )

    class Meta:
        model = Registration
        template = 'django_tables2/bootstrap4.html'
        fields = ()

    def render_child_age(self, record):
        return record.child.age

    def render_child_birthday(self, record):
        return record.child.birthday

    def render_education_program(self, record):
        return record.education_program

    def render_class_section(self, record):
        return record.class_section

    def render_has_previous_registration(self, record):
        return record.has_previous_registration

    def render_child_unicef_id(self, record):
        url = reverse('mscc:child_profile', kwargs={'pk': record.id})
        return format_html('<a href="{}" target="_blank">{}</a>', url, record.child.unicef_id)


class MainTable(CommonTable):
    action_column = tables.TemplateColumn(
        verbose_name=_('Actions'),
        orderable=False,
        template_name='django_tables2/mscc/action_column.html'
    )
    type_column = tables.TemplateColumn(verbose_name=_('Type'), orderable=False,
                                        template_name='django_tables2/mscc/type_column.html')
    absence_column = tables.TemplateColumn(verbose_name=_('Total Absence'), orderable=False,
                                       template_name='django_tables2/mscc/absence_column.html')


    # center_type = tables.Column(verbose_name=_('Center Type'), accessor='center.type')
    # governorate = tables.Column(verbose_name=_('Governorate'), accessor='center.governorate')
    # caza = tables.Column(verbose_name=_('Caza'), accessor='center.caza')
    # cadaster = tables.Column(verbose_name=_('Cadaster'), accessor='center.cadaster')

    class Meta:
        model = Registration
        fields = (
            'action_column',
            'type_column',
            'absence_column',
            'round',
            'child.number',
            'child.unicef_id',
            # 'child_unicef_id',
            'child.first_name',
            'child.father_name',
            'child.last_name',
            'child.mother_fullname',
            'child.gender',
            'child_age',
            'child_birthday',
            'child.nationality',
            'education_program',
            'class_section',
            'partner_unique_number',
            'has_previous_registration',
            # 'center',
            # 'center_type',
            # 'governorate',
            # 'caza',
            # 'cadaster',
            'owner',
            'modified_by',
        )


class FullTable(CommonTable):
    action_column = tables.TemplateColumn(
        verbose_name=_('Actions'),
        orderable=False,
        template_name='django_tables2/mscc/action_column.html'
    )
    type_column = tables.TemplateColumn(verbose_name=_('Type'), orderable=False,
                                        template_name='django_tables2/mscc/type_column.html')
    absence_column = tables.TemplateColumn(verbose_name=_('Total Absence'), orderable=False,
                                       template_name='django_tables2/mscc/absence_column.html')
    center_type = tables.Column(verbose_name=_('Center Type'), accessor='center.type')
    governorate = tables.Column(verbose_name=_('Governorate'), accessor='center.governorate')
    caza = tables.Column(verbose_name=_('Caza'), accessor='center.caza')
    cadaster = tables.Column(verbose_name=_('Cadaster'), accessor='center.cadaster')

    class Meta:
        model = Registration
        fields = (
            'action_column',
            'type_column',
            'absence_column',
            'round',
            'child.number',
            'child.unicef_id',
            # 'child_unicef_id',
            'child.first_name',
            'child.father_name',
            'child.last_name',
            'child.mother_fullname',
            'child.gender',
            'child_age',
            'child_birthday',
            'child.nationality',
            'education_program',
            'class_section',
            'partner_unique_number',
            'partner',
            'center',
            'center_type',
            'governorate',
            'caza',
            'cadaster',
            'has_previous_registration',
            'owner',
            'modified_by'
        )


class PartnerTable(CommonTable):
    action_column = tables.TemplateColumn(
        verbose_name=_('Actions'),
        orderable=False,
        template_name='django_tables2/mscc/action_column.html'
    )
    type_column = tables.TemplateColumn(verbose_name=_('Type'), orderable=False,
                                        template_name='django_tables2/mscc/type_column.html')
    absence_column = tables.TemplateColumn(verbose_name=_('Total Absence'), orderable=False,
                                       template_name='django_tables2/mscc/absence_column.html')
    center_type = tables.Column(verbose_name=_('Center Type'), accessor='center.type')
    governorate = tables.Column(verbose_name=_('Governorate'), accessor='center.governorate')
    caza = tables.Column(verbose_name=_('Caza'), accessor='center.caza')
    cadaster = tables.Column(verbose_name=_('Cadaster'), accessor='center.cadaster')

    class Meta:
        model = Registration
        fields = (
            'action_column',
            'type_column',
            'absence_column',
            'round',
            'child.number',
            'child.unicef_id',
            # 'child_unicef_id',
            'child.first_name',
            'child.father_name',
            'child.last_name',
            'child.mother_fullname',
            'child.gender',
            'child_age',
            'child_birthday',
            'child.nationality',
            'education_program',
            'class_section',
            'partner_unique_number',
            'center',
            'center_type',
            'governorate',
            'caza',
            'cadaster',
            'has_previous_registration',
            'owner',
            'modified_by'
        )


class YouthMainTable(CommonTable):
    action_column = tables.TemplateColumn(
        verbose_name=_('Actions'),
        orderable=False,
        template_name='django_tables2/mscc/action_column.html'
    )

    class Meta:
        model = Registration
        fields = (
            'action_column',
            'child.number',
            'child.unicef_id',
            # 'child_unicef_id',
            'child.first_name',
            'child.father_name',
            'child.last_name',
            'child.mother_fullname',
            'child.gender',
            'child_age',
            'child_birthday',
            'child.nationality',
            # 'center',
            # 'center_type',
            # 'governorate',
            # 'caza',
            # 'cadaster',
        )
