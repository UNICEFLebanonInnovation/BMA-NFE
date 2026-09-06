import django_tables2 as tables
from django.utils.translation import gettext as _

from .models import ALPRegistration, ALPTeacher


class ALPRegistrationTable(tables.Table):
    actions = tables.TemplateColumn(
        template_name='django_tables2/alp/registration_actions.html',
        verbose_name=_('Actions'),
        orderable=False,
    )

    class Meta:
        model = ALPRegistration
        template_name = 'django_tables2/bootstrap5.html'
        attrs = {'class': 'table table-hover table-striped align-middle'}
        fields = ('actions', 'id', 'child__first_name', 'child__last_name', 'school', 'round', 'programme')


class ALPTeacherTable(tables.Table):
    actions = tables.TemplateColumn(
        template_name='django_tables2/alp/teacher_actions.html',
        verbose_name=_('Actions'),
        orderable=False,
    )

    class Meta:
        model = ALPTeacher
        template_name = 'django_tables2/bootstrap5.html'
        attrs = {'class': 'table table-hover table-striped align-middle'}
        fields = ('first_name', 'last_name', 'phone_number', 'sex', 'school', 'actions')
