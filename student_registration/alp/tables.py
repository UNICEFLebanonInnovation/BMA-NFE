import django_tables2 as tables
from django.utils.translation import gettext as _
from django.utils.html import format_html

from .models import ALPRegistration, ALPTeacher

class ALPRegistrationTable(tables.Table):
    actions = tables.TemplateColumn(
        template_code='''
            <div class="btn-group btn-group-sm" role="group">
                <a href="{% url 'alp:child_profile' record.pk %}" class="btn btn-outline-primary" title="{% trans 'Profile' %}">
                    <i class="bi bi-person-badge"></i>
                </a>
                <a href="{% url 'alp:registration_edit' record.pk %}" class="btn btn-outline-secondary" title="{% trans 'Edit' %}">
                    <i class="bi bi-pencil"></i>
                </a>
                <a href="{% url 'alp:registration_delete' record.pk %}" class="btn btn-outline-danger" title="{% trans 'Delete' %}">
                    <i class="bi bi-trash"></i>
                </a>
            </div>
        ''',
        verbose_name=_('Actions'),
        orderable=False,
    )

    class Meta:
        model = ALPRegistration
        template_name = 'django_tables2/bootstrap5.html'
        attrs = {'class': 'table table-hover table-striped align-middle'}
        fields = ('id', 'child__first_name', 'child__last_name', 'school', 'round', 'programme', 'actions')

class ALPTeacherTable(tables.Table):
    actions = tables.TemplateColumn(
        template_code='''
            <div class="btn-group btn-group-sm" role="group">
                <a href="{% url 'alp:teacher_edit' record.pk %}" class="btn btn-outline-secondary" title="{% trans 'Edit' %}">
                    <i class="bi bi-pencil"></i>
                </a>
                <a href="{% url 'alp:teacher_delete' record.pk %}" class="btn btn-outline-danger" title="{% trans 'Delete' %}">
                    <i class="bi bi-trash"></i>
                </a>
            </div>
        ''',
        verbose_name=_('Actions'),
        orderable=False,
    )

    class Meta:
        model = ALPTeacher
        template_name = 'django_tables2/bootstrap5.html'
        attrs = {'class': 'table table-hover table-striped align-middle'}
        fields = ('first_name', 'last_name', 'phone_number', 'sex', 'school', 'actions')
