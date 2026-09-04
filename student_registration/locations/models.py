from __future__ import unicode_literals, absolute_import, division

from django.db import models
from django.conf import settings
from model_utils import Choices
from model_utils.models import TimeStampedModel
from mptt.models import MPTTModel, TreeForeignKey
from django.contrib.postgres.fields import ArrayField

from django.utils.translation import gettext_lazy as _


class LocationType(models.Model):
    name = models.CharField(max_length=64, unique=True)
    name_en = models.CharField(max_length=145, blank=True, null=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Location Type'

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name


class Location(MPTTModel):

    name = models.CharField(max_length=254)
    name_en = models.CharField(max_length=254, blank=True, null=True)
    type = models.ForeignKey(
        'LocationType',
        verbose_name='Location Type',
        on_delete=models.CASCADE
    )
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    p_code = models.CharField(max_length=32, blank=True, null=True)
    parent = TreeForeignKey(
        'self', null=True, blank=True,
        related_name='children',
        db_index=True,
        on_delete=models.SET_NULL
    )

    def __str__(self):
        return self.name

    def __unicode__(self):
        # if self.type:
        #     return u'{} - {}'.format(
        #         self.name,
        #         self.type.name
        #     )
        return self.name

    class Meta:
        unique_together = ('name', 'type', 'p_code')
        ordering = ['name']
        verbose_name = 'Location'


class Center(TimeStampedModel):
    # from student_registration.schools.models import PartnerOrganization
    TYPE = Choices(
        ('Municipality', _('Municipality')),
        ('Collective Settlement', _('Collective Settlement')),
        ('Informal Settlement', _('Informal Settlement')),
        ('Welfare Center', _('Welfare Center')),
        ('Community Hub', _('Community Hub')),
    )
    PROVIDED_PACKAGES = Choices(
        ('Education', 'Education'),
        ('Youth', 'Youth'),
        ('Health & Nutrition', 'Health & Nutrition'),
        ('Child Protection', 'Child Protection'),
        ('Social Protection', 'Social Protection'),
    )
    PROGRAM = Choices(
        ('BLN', 'BLN'),
        ('ABLN', 'ABLN'),
        ('RS', 'RS'),
        ('CBECE', 'CBECE'),
        ('YBLN', 'YBLN'),
        ('YFS', 'YFS')
    )
    YES_NO = Choices(
        ('', '----------'),
        ('Yes', _("Yes")),
        ('No', _("No"))
    )
    TRUE_FALSE = Choices(
        ('', '----------'),
        ('True', _("Yes")),
        ('False', _("No")),
    )
    partner = models.ForeignKey(
        'schools.PartnerOrganization',
        blank=True, null=True,
        verbose_name=_('Partner'),
        on_delete=models.SET_NULL,
        related_name='center_partner'
    )
    name = models.CharField(max_length=100)
    governorate = models.ForeignKey(
        'Location',
        blank=True, null=True,
        related_name='+',
        on_delete=models.SET_NULL,
        verbose_name=_('Governorate')
    )
    caza = models.ForeignKey(
        'Location',
        blank=True, null=True,
        related_name='+',
        on_delete=models.SET_NULL,
        verbose_name=_('Caza')
    )
    cadaster = models.ForeignKey(
        'Location',
        blank=True, null=True,
        related_name='+',
        on_delete=models.SET_NULL,
        verbose_name=_('Cadaster')
    )
    longitude = models.FloatField(
        blank=True,
        null=True,
        verbose_name=_('Center GPS (longitude)')
    )
    latitude = models.FloatField(
        blank=True,
        null=True,
        verbose_name=_('Center GPS (latitude)')
    )
    manager_name = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Center Manager name')
    )
    phone_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Phone number')
    )
    email = models.EmailField(
        blank=True,
        null = True,
        max_length=254,
        verbose_name='Email'
    )

    type = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=TYPE,
        verbose_name=_('Type')
    )
    provided_packages = ArrayField(
        models.CharField(
            choices=PROVIDED_PACKAGES,
            max_length=200,
            blank=True,
            null=True,
        ),
        blank=True,
        null=True,
        verbose_name=_('Provided Services')
    )
    programs = ArrayField(
        models.CharField(
            choices=PROGRAM,
            max_length=200,
            blank=True,
            null=True,
        ),
        blank=True,
        null=True,
        verbose_name=_('Programs')
    )
    admin_staff_number = models.IntegerField(
        blank=True,
        null=True,
        choices=((x, x) for x in range(0, 300)),
        verbose_name=_('Number of Admin staff in the centers')
    )
    cwd_accessible = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Is the center accessible for CWD ?')
    )
    p_code = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('P-Code')
    )
    is_active = models.BooleanField(
        default=False,
        blank=True,
        null=True,
        verbose_name=_('is active')
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=False, null=True,
        related_name='+',
        on_delete=models.SET_NULL,
    )
    modified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True, null=True,
        related_name='+',
        on_delete=models.SET_NULL,
        verbose_name=_('Modified by'),
    )
    offer_digital_learning = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Does the center offer digital learning services?')
    )
    have_digital_hub = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Does the center have a digital hub?')
    )
    neaby_phcc = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name=_('Nearby PHCC name')
    )

    @property
    def total_children(self):
        from student_registration.mscc.models import Registration
        return Registration.objects.filter(center=self.id).count()

    @property
    def total_male(self):
        from student_registration.mscc.models import Registration
        return Registration.objects.filter(center=self.id, child__gender='Male').count()

    @property
    def total_female(self):
        from student_registration.mscc.models import Registration
        return Registration.objects.filter(center=self.id, child__gender='Female').count()

    @property
    def total_disability(self):
        from student_registration.mscc.models import Registration
        return Registration.objects.filter(center=self.id).exclude(child__disability__name_en='No').count()

    @property
    def total_disability_male(self):
        from student_registration.mscc.models import Registration
        return Registration.objects.filter(center=self.id, child__gender='Male').exclude(child__disability__name_en='No').count()

    @property
    def total_disability_female(self):
        from student_registration.mscc.models import Registration
        return Registration.objects.filter(center=self.id, child__gender='Female').exclude(child__disability__name_en='No').count()

    @property
    def total_lebanese(self):
        from student_registration.mscc.models import Registration
        return Registration.objects.filter(center=self.id,child__nationality__code='LEB').count()

    @property
    def total_non_lebanese(self):
        from student_registration.mscc.models import Registration
        return Registration.objects.filter(center=self.id).exclude(child__nationality__code='LEB').count()

    @property
    def total_admin_staff(self):
        return self.admin_staff_number if self.admin_staff_number is not None else 0

    @property
    def total_teachers(self):
        from student_registration.mscc.models import Teacher
        return Teacher.objects.filter(center=self.id).count()

    @property
    def total_teachers_male(self):
        from student_registration.mscc.models import Teacher
        return Teacher.objects.filter(center=self.id, sex='Male').count()

    @property
    def total_teachers_female(self):
        from student_registration.mscc.models import Teacher
        return Teacher.objects.filter(center=self.id, sex='Female').count()

    @property
    def total_staff(self):
        admin_staff = self.total_admin_staff
        teachers = self.total_teachers
        return admin_staff + teachers

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = "Center"
        verbose_name_plural = "Centers"
