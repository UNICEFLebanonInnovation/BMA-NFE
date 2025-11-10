from __future__ import unicode_literals, absolute_import, division

from django.db import models
from django.conf import settings
from model_utils import Choices
from model_utils.models import TimeStampedModel
from mptt.models import MPTTModel, TreeForeignKey
from django.contrib.postgres.fields import ArrayField

from django.utils.translation import gettext as _


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


class ActivityInfoLocation(MPTTModel):

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
        return self.name

    class Meta:
        unique_together = ('name', 'type', 'p_code')
        ordering = ['name']


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
    def total_program_staff(self):
        return ProgramStaff.objects.filter(center=self.id).count()

    @property
    def total_staff(self):
        admin_staff = self.total_admin_staff
        program_staff = self.total_program_staff
        return admin_staff + program_staff

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = "Center"
        verbose_name_plural = "Centers"


class ProgramStaff(TimeStampedModel):

    GENDER = Choices(
        ('Male', _('Male')),
        ('Female', _('Female')),
    )
    SUBJECT = Choices(
        ('Education', _('Education')),
        ('Child Protection', _('Child Protection')),
        ('Health and Nutrition', _('Health and Nutrition')),
        ('Youth', _('Youth')),
        ('Digital', _('Digital')),
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
    TOPICS = Choices(
        ('PSEA', 'PSEA'),
        ('Digital', 'Digital'),
        ('Classroom management', 'Classroom management'),
        ('SEL', 'SEL'),
        ('Inclusion', 'Inclusion'),
        ('Safe identification and referral', 'Safe identification and referral'),
        ('Psychological first aid', 'Psychological first aid')
    )
    center = models.ForeignKey(
        'Center',
        blank=True, null=True,
        verbose_name=_('Center'),
        on_delete=models.SET_NULL,
    )
    facilitator_name = models.CharField(
        max_length=200,
        verbose_name='Facilitator Name'
    )
    phone_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Phone Number')
    )
    email = models.EmailField(blank=True, max_length=254, verbose_name='Email')
    gender = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=GENDER,
        verbose_name=_('Gender')
    )
    subject = ArrayField(
        models.CharField(
            choices=SUBJECT,
            max_length=200,
            blank=True,
            null=True,
        ),
        blank=True,
        null=True,
        verbose_name=_('Subject')
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
        verbose_name=_('Education Program')
    )
    weekly_hours_taught = models.IntegerField(
        blank = True,
        null = True,
        choices = ((x, x) for x in range(0, 300)),
        verbose_name = _('Number of Hours Taught Per Week')
    )
    attendance_training = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Facilitator Attendance to training ?')
    )
    training_topics = ArrayField(
        models.CharField(
            choices=TOPICS,
            max_length=200,
            blank=True,
            null=True,
        ),
        blank=True,
        null=True,
        verbose_name=_('Topics of facilitator training')
    )
    attach_cv = models.FileField(
        upload_to='uploads/program_staff',
        blank=True,
        null=True,
        verbose_name=_('CV Attachment'),
    )
    attach_diploma = models.FileField(
        upload_to='uploads/program_staff',
        blank=True,
        null=True,
        verbose_name=_('Diploma Attachment'),
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

    def __str__(self):
        return self.facilitator_name

    def __unicode__(self):
        return self.facilitator_name

    class Meta:
        ordering = ['facilitator_name']
        verbose_name = "ProgramStaff"
        verbose_name_plural = "ProgramStaffs"
