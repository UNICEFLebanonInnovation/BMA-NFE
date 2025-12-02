from __future__ import unicode_literals, absolute_import, division

from django.conf import settings
from django.utils.translation import gettext as _
from django.db import models
from django.db.models import JSONField
from model_utils.models import TimeStampedModel
from model_utils import Choices
from student_registration.schools.models import School


class ExportHistory(TimeStampedModel):
    """
    Stores metadata about user-triggered export jobs.

    Parameters
    ----------
    export_type : str
        Human-readable export category chosen from ``EXPORT_TYPE`` options.
    created_by : User
        The user who initiated the export operation; can be null if the user was deleted.
    partner_name : str
        Optional partner or organization name to further describe the export source.
    fields : dict
        JSON payload that records the fields or filters used to build the export.
    file_format : str
        The format of the generated file (e.g., ``csv`` or ``xlsx``).
    file_url : str
        The download URL for the generated export file.
    status : str
        Current processing status pulled from ``STATUS`` choices.

    Returns
    -------
    ExportHistory
        A timestamped record describing a single export job.
    """

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
    """
    Captures basic request information for auditing purposes.

    Parameters
    ----------
    username : str
        Username associated with the request.
    path : str
        The URL path requested by the user.
    method : str
        HTTP method used in the request (e.g., ``GET`` or ``POST``).
    data : str
        Serialized request payload including metadata such as IP address and user agent.
    timestamp : datetime
        Automatically recorded creation time for the audit entry.

    Returns
    -------
    UserActivity
        A model instance representing a logged request.
    """

    username = models.CharField(max_length=255)
    path = models.TextField()
    method = models.CharField(max_length=10)
    data = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """
        Render a concise, human-readable description of the logged activity.

        Parameters
        ----------
        self : UserActivity
            The current audit record instance.

        Returns
        -------
        str
            A formatted string showing the username, HTTP method, and request path.
        """

        return "{} - {} {}".format(self.username, self.method, self.path)
