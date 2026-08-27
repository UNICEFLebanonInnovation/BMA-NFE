from __future__ import unicode_literals

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from model_utils import Choices
from model_utils.models import TimeStampedModel
from django.db.models import JSONField
from django.contrib.postgres.fields import ArrayField

from student_registration.schools.models import School
from student_registration.child.models import Child

class ALPRound(models.Model):
    name = models.CharField(max_length=45, unique=True, verbose_name=_('Round Name'))
    current_year = models.BooleanField(blank=True, default=False, verbose_name=_('Current Year'))

    class Meta:
        ordering = ['name']
        verbose_name = _("ALP Round")
        verbose_name_plural = _("ALP Rounds")

    def __str__(self):
        return self.name

class ALPProgram(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name=_('Program Name'))

    class Meta:
        ordering = ['name']
        verbose_name = _("ALP Program")
        verbose_name_plural = _("ALP Programs")

    def __str__(self):
        return self.name

class ALPTeacher(TimeStampedModel):
    GENDER = Choices(
        ('Male', _('Male')),
        ('Female', _('Female')),
    )

    first_name = models.CharField(max_length=64, db_index=True, blank=True, null=True, verbose_name=_('First name'))
    father_name = models.CharField(max_length=64, db_index=True, blank=True, null=True, verbose_name=_('Father name'))
    last_name = models.CharField(max_length=64, db_index=True, blank=True, null=True, verbose_name=_('Last name'))
    phone_number = models.CharField(max_length=20, db_index=True, blank=True, null=True, verbose_name=_('Phone Number'))
    sex = models.CharField(max_length=6, choices=GENDER, blank=True, null=True, verbose_name=_('Sex'))
    school = models.ForeignKey(School, blank=False, null=True, related_name='+', on_delete=models.SET_NULL, verbose_name=_('School'))
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, blank=False, null=True, related_name='+', on_delete=models.SET_NULL)

    class Meta:
        ordering = ['-created']
        verbose_name = _("ALP Teacher")
        verbose_name_plural = _("ALP Teachers")

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class ALPRegistration(TimeStampedModel):
    YES_NO = Choices(('', _('----------')), ('Yes', _("Yes")), ('No', _("No")))

    school = models.ForeignKey(School, blank=True, null=True, related_name='+', on_delete=models.SET_NULL, verbose_name=_('School'))
    child = models.ForeignKey(Child, blank=False, null=True, related_name='+', on_delete=models.SET_NULL, verbose_name=_('Child'))
    round = models.ForeignKey(ALPRound, blank=True, null=True, related_name='+', on_delete=models.SET_NULL, verbose_name=_('Round'))
    programme = models.ForeignKey(ALPProgram, blank=True, null=True, related_name='+', on_delete=models.SET_NULL, verbose_name=_('Programme'))

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, blank=False, null=True, related_name='+', on_delete=models.SET_NULL)
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, related_name='+', on_delete=models.SET_NULL, verbose_name=_('Modified by'))

    class Meta:
        ordering = ['-created']
        verbose_name = _("ALP Registration")
        verbose_name_plural = _("ALP Registrations")

    def __str__(self):
        return f"Registration {self.id} for {self.child}"

class ALPGrading(TimeStampedModel):
    registration = models.ForeignKey(ALPRegistration, blank=False, null=True, related_name='+', on_delete=models.SET_NULL, verbose_name=_('Registration'))
    grading_data = JSONField(default=dict, verbose_name=_('Grading Data'))
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, blank=False, null=True, related_name='+', on_delete=models.SET_NULL)

    class Meta:
        ordering = ['-created']
        verbose_name = _("ALP Grading")
        verbose_name_plural = _("ALP Gradings")

class ALPGradingDefinition(models.Model):
    material = models.CharField(max_length=100, verbose_name=_('Material'))
    min_grade = models.IntegerField(verbose_name=_('Min Grade'))
    max_grade = models.IntegerField(verbose_name=_('Max Grade'))

    class Meta:
        ordering = ['material']
        verbose_name = _("ALP Grading Definition")
        verbose_name_plural = _("ALP Grading Definitions")

    def __str__(self):
        return self.material

class ALPTeacherAttendance(TimeStampedModel):
    teacher = models.ForeignKey(ALPTeacher, blank=False, null=True, related_name='+', on_delete=models.SET_NULL, verbose_name=_('Teacher'))
    date = models.DateField(blank=True, null=True, verbose_name=_('Attendance Date'))
    status = models.CharField(max_length=20, choices=[('Present', _('Present')), ('Absent', _('Absent'))], blank=True, null=True, verbose_name=_('Status'))
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, blank=False, null=True, related_name='+', on_delete=models.SET_NULL)

    class Meta:
        ordering = ['-date']
        verbose_name = _("ALP Teacher Attendance")
        verbose_name_plural = _("ALP Teacher Attendances")

class ALPAttendance(TimeStampedModel):
    SHIFT = Choices(('', _('----------')), ('Morning shift', _('Morning shift')), ('Afternoon shift', _('Afternoon shift')))

    registration = models.ForeignKey(ALPRegistration, blank=False, null=True, related_name='+', on_delete=models.SET_NULL, verbose_name=_('Registration'))
    date = models.DateField(blank=True, null=True, verbose_name=_('Attendance Date'))
    status = models.CharField(max_length=20, choices=[('Present', _('Present')), ('Absent', _('Absent'))], blank=True, null=True, verbose_name=_('Status'))
    shift = models.CharField(max_length=50, choices=SHIFT, blank=True, null=True, verbose_name=_('Operating Shift'))
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, blank=False, null=True, related_name='+', on_delete=models.SET_NULL)

    class Meta:
        ordering = ['-date']
        verbose_name = _("ALP Attendance")
        verbose_name_plural = _("ALP Attendances")
