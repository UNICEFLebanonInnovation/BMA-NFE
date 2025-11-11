# coding: utf-8
import django_tables2 as tables
from django.utils.translation import gettext as _

from .models import CLM, Bridging


class CommonTable(tables.Table):

    # edit_column = tables.TemplateColumn(verbose_name=_('Edit student'),
    #                                     template_name='django_tables2/edit_column.html',
    #                                     attrs={'url': ''})
    # delete_column = tables.TemplateColumn(verbose_name=_('Delete student'),
    #                                       template_name='django_tables2/delete_column.html',
    #                                       attrs={'url': ''})

    student_age = tables.Column(verbose_name=_('Age'), accessor='student.age')
    student_birthday = tables.Column(verbose_name=_('Birthday'), accessor='student.birthday')

    class Meta:
        model = CLM
        template = 'django_tables2/bootstrap.html'
        attrs = {'class': 'table table-bordered table-striped table-hover'}
        fields = (
            # 'edit_column',
            # 'delete_column',
        )


class BridgingTable(CommonTable):

    action_column = tables.TemplateColumn(verbose_name=_('Actions'), orderable=False,
                                        template_name='django_tables2/clm_action_column.html',
                                        attrs={'url_edit': '/clm/bridging-edit/',
                                               'url_delete': '/clm/bridging-delete/',
                                               'url_post_assessment': '/clm/bridging-post-assessment/',
                                               'url_mid_assessment1': '/clm/bridging-mid-assessment/',
                                               'url_mid_assessment2': '/clm/bridging-mid-assessment/',
                                               'url_followup': '/clm/bridging-followup/',
                                               'url_service': '/clm/bridging-service/',
                                               'programme': 'Bridging'})

    clm_absence_column = tables.TemplateColumn(verbose_name=_('Absence'), orderable=False,
                                                    template_name='django_tables2/clm_absence_column.html')

    clm_max_consecutive_column = tables.TemplateColumn(verbose_name=_('Max Consecutive'), orderable=False,
                                               template_name='django_tables2/clm_max_consecutive_column.html')

    class Meta:
        model = Bridging
        fields = (
            'action_column',
            'clm_absence_column',
            'clm_max_consecutive_column',
            'school.name',
            'registration_level',
            'round',
            'governorate',
            'district',
            'internal_number',
            'student.number',
            'student.unicef_id',
            'student.first_name',
            'student.father_name',
            'student.last_name',
            'student.sex',
            'student_age',
            'student_birthday',
            'student.nationality',
            'student.mother_fullname',
            'owner',
            'modified_by',
            'created',
            'modified',
        )

