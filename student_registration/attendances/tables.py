# coding: utf-8
import django_tables2 as tables
from django.utils.translation import gettext as _

from .models import CLMAttendance, CLMAttendanceStudent
from student_registration.clm.models import Bridging


class BootstrapTable(tables.Table):
    class Meta:
        model = CLMAttendance
        template = 'django_tables2/bootstrap.html'
        attrs = {'class': 'table table-bordered table-striped table-hover'}


class CommonTable(tables.Table):

    class Meta:
        model = Bridging
        template = 'django_tables2/bootstrap.html'
        fields = (
        )


class CLMAttendanceStudentTable(CommonTable):
    class Meta:
        model = Bridging
        fields = (
            'student.full_name',
        )


