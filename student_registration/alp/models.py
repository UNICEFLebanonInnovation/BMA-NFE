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
    YES_NO = Choices(
        ('', _('----------')),
        ('Yes', _("Yes")),
        ('No', _("No"))
    )

    HAVE_LABOUR = Choices(
        ('', _('----------')),
            ('No', _('No')),
            ('Yes - Morning', _('Yes - Morning')),
            ('Yes - Afternoon', _('Yes - Afternoon')),
            ('Yes - Full Day', _('Yes - Full day')),
            ('Yes - Night Shift', _('Yes - Night Shift')),
            ('Yes - Morning & Night Shift', _('Yes - Morning & Night Shift')),
            ('Yes - Afternoon & Night Shift', _('Yes - Afternoon & Night Shift')),
            ('Yes - Full Day & Night Shift', _('Yes - Full Day & Night Shift')),
    )
    LABOURS = Choices(
            ('', _('----------')),
            ('Agriculture', _('Agriculture')),
            ('Construction', _('Construction')),
            ('Manufacturing', _('Manufacturing')),
            ('Retail / Store', _('Retail / Store')),
            ('Street Connected Work - includes vending and begging', _('Street Connected Work - includes vending and begging')),
            ('Household chores (includes domestic works and caring for siblings or their caregivers)',
             _('Household chores (includes domestic works and caring for siblings or their caregivers)')),
            ('Mechanic shop', _('Mechanic shop')),
            ('Other services', _('Other services')),
            ('Domestic work at other houses', _('Domestic work at other houses')),
            ('In street connected work', _('In street connected work')),
            ('Money exchange', _('Money exchange')),
    )
    LABOUR_INCOME = Choices(
            ('', _('----------')),
            ('5 USD or Less', _('5 USD or Less')),
            ('5-20 USD', _('5-20 USD')),
            ('20-50 USD', _('20-50 USD')),
            ('50-100 USD', _('50-100 USD')),
            ('More than 100 USD', _('More than 100 USD')),
    )
    LABOUR_CONDITION = Choices(
            ('Carry heavy loads', _('Carry heavy loads')),
            ('Works in extreme cold, heat or humidity', _('Works in extreme cold, heat or humidity')),
            ('Exposed to dust, fume or gas', _('Exposed to dust, fume or gas')),
            ('Maneuvers dangerous tools such as knives or operating heavy machinery', _('Maneuvers dangerous tools such as knives or operating heavy machinery')),
            ('Required to work with chemicals, such as pesticides, glues and similar, or explosives', _('Required to work with chemicals, such as pesticides, glues and similar, or explosives')),
            ('Stating exposed to fumes (including argile and cigarettes)  and gas', _('Stating exposed to fumes (including argile and cigarettes)  and gas')),
            ('Loud noise or vibration', _('Loud noise or vibration')),
            ('Exposed to any other work condition that are bad for his/her health and safety', _('Exposed to any other work condition that are bad for his/her health and safety')),
    )
    IDENTIFICATION_SOURCE = Choices(
            ('', _('----------')),
            ('Dirassa', _('Dirassa')),
            ('Awareness Session', _('Awareness Session')),
            ('Child\'s parents', _('Child\'s parents')),
            ('From Hosted Community', _('From Hosted Community')),
            ('Sector Partners referral (CP, Education, Health, Wash, Youth, Palestenian program...) ',
             _('Sector Partners referral (CP, Education, Health, Wash, Youth, Palestenian program...) ')),
            ('From Profiling Database', _('From Profiling Database')),
            ('From Other NGO', _('From Other NGO')),
            ('From Displaced Community', _('From Displaced Community')),
            ('Referred by the municipality/Other formal sources', _('Referred by the municipality/Other formal sources')),
            ('Other Sources', _('Other Sources')),
    )
    CASH_SUPPORT_PROGRAMMES = Choices(
            ('None', _('None')),
            ('Haddi', _('Haddi')),
            ('Education Cash assistance', _('Education Cash assistance')),
            ('UNHCR cash assistance', _('UNHCR cash assistance')),
            ('WFP cash assistance', _('WFP cash assistance')),
    )
    MSCC_PACKAGES = Choices(
        ('Early Childhood  Development', _('Early Childhood  Development')),
        ('Education', _('Education')),
        ('Child Protection/Psychosocial support', _('Child Protection/Psychosocial support')),
        ('Youth Empowerment and engagement', _('Youth Empowerment and engagement')),
        ('Health and Nutrition', _('Health and Nutrition')),
        ('Parental and Caregiver Support', _('Parental and Caregiver Support')),
        ('Social Cash Assistance', _('Social Cash Assistance')),
    )

    school = models.ForeignKey(School, blank=True, null=True, related_name='+', on_delete=models.SET_NULL, verbose_name=_('School'))
    child = models.ForeignKey(Child, blank=False, null=True, related_name='+', on_delete=models.SET_NULL, verbose_name=_('Child'))
    round = models.ForeignKey(ALPRound, blank=True, null=True, related_name='+', on_delete=models.SET_NULL, verbose_name=_('Round'))
    programme = models.ForeignKey(ALPProgram, blank=True, null=True, related_name='+', on_delete=models.SET_NULL, verbose_name=_('Programme'))

    student_old = models.IntegerField(blank=True, null=True, verbose_name=_('Student old'))
    have_labour = models.CharField(
        max_length=100,
        choices=HAVE_LABOUR,
        blank=True,
        null=True,
        verbose_name=_('Does the child participate in work?')
    )
    labour_type = models.CharField(
        max_length=100,
        choices=LABOURS,
        blank=True,
        null=True,
        verbose_name=_('What is the type of work?')
    )
    labour_type_specify = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('Please specify (hotel, restaurant, transport, personal '
                       'services such as cleaning, hair care, cooking and childcare)')
    )
    labour_hours = models.IntegerField(
        blank=True,
        null=True,
        default= 0,
        verbose_name=_('Number of working hours/week ')
    )
    labour_weekly_income = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=LABOUR_INCOME,
        verbose_name=_('What is the income of the child per week?')
    )
    labour_condition = ArrayField(
        models.CharField(
            choices=LABOUR_CONDITION,
            max_length=100,
            blank=True,
            null=True,
        ),
        blank=True,
        null=True,
        verbose_name=_('What is the work condition that the child is exposed to?')
    )
    source_of_identification = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=IDENTIFICATION_SOURCE,
        verbose_name=_('Source of referral of the child')
    )
    source_of_identification_specify = models.TextField(
        blank=True, null=True,
        verbose_name=_('please specify')
    )
    cash_support_programmes = ArrayField(
        models.CharField(
            choices=CASH_SUPPORT_PROGRAMMES,
            max_length=100,
            blank=True,
            null=True,
        ),
        blank=True,
        null=True,
        verbose_name=_('Cash support programmes that child is already benefiting from')
    )
    mscc_packages = ArrayField(
        models.CharField(
            choices=MSCC_PACKAGES,
            max_length=100,
            blank=True,
            null=True,
        ),
        blank=True,
        null=True,
        verbose_name=_('Packages received/to be provided to child under')
    )
    type = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('Type')
    )

    registration_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('Registration date')
    )
    partner_unique_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Partner unique child number')
    )

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, blank=False, null=True, related_name='+', on_delete=models.SET_NULL, verbose_name=_('Owner'))
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, related_name='+', on_delete=models.SET_NULL, verbose_name=_('Modified by'))
    deleted = models.BooleanField(blank=True, default=False, verbose_name=_('Deleted'))
    deleted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True, null=True,
        related_name='+',
        on_delete=models.SET_NULL,
        verbose_name=_('Deleted by'),
    )

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
