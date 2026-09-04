import django_tables2 as tables
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html

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

from .models import ALPAttendance, ALPTeacherAttendance

class ALPAttendanceTable(tables.Table):
    actions = tables.TemplateColumn(
        template_name='django_tables2/alp/attendance_actions.html',
        verbose_name=_('Actions'),
        orderable=False,
    )

    class Meta:
        model = ALPAttendance
        template_name = 'django_tables2/bootstrap5.html'
        attrs = {'class': 'table table-hover table-striped align-middle'}
        fields = ('registration', 'date', 'status', 'shift', 'actions')

class ALPTeacherAttendanceTable(tables.Table):
    actions = tables.TemplateColumn(
        template_name='django_tables2/alp/teacher_attendance_actions.html',
        verbose_name=_('Actions'),
        orderable=False,
    )

    class Meta:
        model = ALPTeacherAttendance
        template_name = 'django_tables2/bootstrap5.html'
        attrs = {'class': 'table table-hover table-striped align-middle'}
        fields = ('teacher', 'date', 'status', 'actions')
