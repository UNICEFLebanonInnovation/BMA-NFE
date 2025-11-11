from __future__ import unicode_literals, absolute_import, division

from django.conf import settings
from django.utils.translation import gettext as _
from django.db import models
from django.db.models import JSONField
from model_utils.models import TimeStampedModel
from model_utils import Choices
from student_registration.schools.models import School


class ExportHistory(TimeStampedModel):

    EXPORT_TYPE = Choices(
        ('', '----------'),
        ('Makani List', _('Makani List')),
        ('Makani Raw Attendance', _('Makani Raw Attendance')),
        ('Makani Total Attendance', _('Makani Total Attendance')),
        ('Center List', _('Center List')),
        ('Bridging Absence Raw Data', _('Bridging Absence Raw Data')),
        ('Bridging Attendance Total', _('Bridging Attendance Total')),
        ('Bridging Absence Consecutive', _('Bridging Absence Consecutive')),
        ('Teacher List', _('Teacher List')),
        ('Bridging List', _('Bridging List')),
        ('School List - Bridging', _('School List - Bridging')),
        ('School List', _('School List')),
    )
    STATUS = Choices(
        ('pending', 'Pending'),
        ('done', 'Done'),
        ('failed', 'Failed'),
    )
    export_type = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=EXPORT_TYPE,
        verbose_name=_('Export Type')
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True, null=True,
        related_name='+',
        on_delete=models.SET_NULL,
        verbose_name=_('Modified by'),
    )
    partner_name = models.CharField(
        max_length=64,
        db_index=True,
        blank=True, null=True,
        verbose_name=_('Partner name')
    )
    fields = JSONField(blank=True, null=True)
    file_format = models.CharField(max_length=10, default='csv')
    file_url = models.URLField(blank=True, null=True)
    status = models.CharField(
        max_length=10,
        choices=STATUS,
        default=STATUS.pending,
    )

    class Meta:
        ordering = ['-created']
        verbose_name = "Export History"
        verbose_name_plural = "Export History"


class UserActivity(models.Model):
    username = models.CharField(max_length=255)
    path = models.TextField()
    method = models.CharField(max_length=10)
    data = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "{} - {} {}".format(self.username, self.method, self.path)
