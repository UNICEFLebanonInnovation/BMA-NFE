from __future__ import unicode_literals, absolute_import, division

from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils.translation import gettext as _
from django.db.models import JSONField
from django.contrib.postgres.fields import ArrayField

from model_utils import Choices
from model_utils.models import TimeStampedModel

from student_registration.child.models import Child
from student_registration.locations.models import Center
from student_registration.students.models import AttachmentType, IDType, Nationality, Training
from student_registration.schools.models import (
    School,
    PartnerOrganization
)

PACKAGE_TYPES = Choices(
    ('Core-Package', _('Core Package')),
    ('Walk-in', _('Walk-in')),
    # ('Walk-in-OOSC', _('Walk-in OOSC')),
    # ('Walk-in-In-School', _('Walk-in In School')),
)

PACKAGE_CATEGORIES = Choices(
    ('Education', 'Education'),
    ('Youth', 'Youth'),
    ('Health & Nutrition', 'Health & Nutrition'),
    ('Child Protection', 'Child Protection'),
    ('Social Protection', 'Social Protection'),
)

YES_NO = Choices(
    ('', '----------'),
    ('Yes', _("Yes")),
    ('No', _("No"))
)

AGREE_DISAGREE = Choices(
    ('Strongly Agree', _("Strongly Agree")),
    ('Agree', _("Agree")),
    ('Don\'t Agree', _("Don\'t Agree")),
    ('Strongly Disagree', _("Strongly Disagree"))
)


class Round(models.Model):
    """Program round metadata used to scope registrations for a given year."""
    YEAR_CHOICES = [(year, year) for year in range(2020, 2051)]

    name = models.CharField(max_length=45, unique=True)
    current_year = models.BooleanField(blank=True, default=False)
    year = models.PositiveSmallIntegerField(
        choices=YEAR_CHOICES,
        blank=True,
        null=True,
        verbose_name=_('Year'),
    )

    class Meta:
        ordering = ['name']
        verbose_name = "Round"

    def __str__(self):
        """Return the round display name for admin lists.

        Returns:
            str: The configured ``name`` for this round.
        """
        return self.name

    def __unicode__(self):
        """Return the unicode representation of the round name.

        Returns:
            str: Same value as :meth:`__str__` for legacy contexts.
        """
        return self.name


class RoundPartner(TimeStampedModel):
    """Association between a round and a partner organization."""
    round = models.ForeignKey(
        Round,
        related_name='partner_rounds',
        on_delete=models.CASCADE,
    )
    partner = models.ForeignKey(
        PartnerOrganization,
        related_name='rounds',
        on_delete=models.CASCADE,
    )
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)

    class Meta:
        ordering = ['round__name', 'partner__name']
        unique_together = ('round', 'partner')
        verbose_name = "Round Partner"
        verbose_name_plural = "Round Partners"

    def __str__(self):
        """Return the combined round and partner label.

        Returns:
            str: The round-partner tuple formatted as ``"<round> - <partner>"``.
        """
        return f"{self.round} - {self.partner}"

    def __unicode__(self):
        """Return the unicode representation of the round-partner mapping.

        Returns:
            str: Same value as :meth:`__str__` for legacy contexts.
        """
        return self.__str__()


class Teacher(TimeStampedModel):
    """Basic teacher profile stored for MSCC registrations."""

    GENDER = Choices(
        ('Male', _('Male')),
        ('Female', _('Female')),
    )

    first_name = models.CharField(
        max_length=64,
        db_index=True,
        blank=True,
        null=True,
        verbose_name=_('First name')
    )
    father_name = models.CharField(
        max_length=64,
        db_index=True,
        blank=True,
        null=True,
        verbose_name=_('Father name')
    )
    last_name = models.CharField(
        max_length=64,
        db_index=True,
        blank=True,
        null=True,
        verbose_name=_('Last name')
    )
    mother_fullname = models.CharField(
        max_length=64,
        db_index=True,
        blank=True,
        null=True,
        verbose_name=_('Mother full name')
    )
    sex = models.CharField(
        max_length=6,
        choices=GENDER,
        blank=True,
        null=True,
        verbose_name=_('Sex')
    )
    birthdate = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('Birth date')
    )
    id_number = models.CharField(
        max_length=45,
        db_index=True,
        blank=True,
        null=True,
        verbose_name=_('ID number')
    )
    id_type = models.ForeignKey(
        IDType,
        blank=True,
        null=True,
        verbose_name=_('ID type'),
        related_name='mscc_teachers',
        on_delete=models.SET_NULL,
    )
    nationality = models.ForeignKey(
        Nationality,
        blank=True,
        null=True,
        related_name='mscc_teachers',
        on_delete=models.SET_NULL,
        verbose_name=_('Nationality')
    )
    unicef_id = models.CharField(
        max_length=45,
        blank=True,
        null=True,
        verbose_name=_('Unicef ID')
    )

    SUBJECT_PROVIDED = (
        ('arabic', _('Arabic')),
        ('math', _('Math')),
        ('english', _('English')),
        ('french', _('French')),
        ('PSS / Counsellor', _('PSS / Counsellor')),
        ('Physical Education', _('Physical Education')),
        ('Art', _('Art')),
        ('Sciences', _('Sciences')),
        ('PSS', _('PSS')),
        ('History', _('History')),
        ('Geography', _('Geography')),
        ('Civics', _('Civics')),
        ('Computer', _('Computer')),
    )
    REGISTRATION_LEVEL = (
        ('Level one', _('Level one')),
        ('Level two', _('Level two')),
        ('Level three', _('Level three')),
        ('Level four', _('Level four')),
        ('Level five', _('Level five')),
        ('Level six', _('Level six')),
        ('level_one_pm', _('Level one PM shift')),
        ('level_two_pm', _('Level two PM shift')),
        ('level_three_pm', _('Level three PM shift')),
        ('level_four_pm', _('Level four PM shift')),
        ('level_five_pm', _('Level five PM shift')),
        ('level_six_pm', _('Level six PM shift')),
        ('grade_one', _('Grade one')),
        ('grade_two', _('Grade two')),
        ('grade_three', _('Grade three')),
        ('grade_four', _('Grade four')),
        ('grade_five', _('Grade five')),
        ('grade_six', _('Grade six')),
        ('grade_seven', _('Grade seven')),
        ('grade_eight', _('Grade eight')),
        ('grade_nine', _('Grade nine')),
    )
    TEACHER_ASSIGNMENT = Choices(
        ('Dirasa only', _('Dirasa only')),
        ('Private and Dirasa', _('Private and Dirasa')),
    )
    YES_NO = Choices(
        ('', '----------'),
        ('yes', _("Yes")),
        ('no', _("No")),
    )
    round = models.ForeignKey(
        Round,
        blank=True, null=True,
        related_name='+',
        on_delete=models.SET_NULL,
        verbose_name=_('Round')
    )
    center = models.ForeignKey(
        Center,
        blank=False, null=True,
        related_name='+',
        on_delete=models.SET_NULL,
        verbose_name=_('Center')
    )
    email = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('Email')
    )
    primary_phone_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Phone number')
    )
    subjects_provided = ArrayField(
        models.CharField(
            choices=SUBJECT_PROVIDED,
            max_length=200,
            blank=True,
            null=True,
        ),
        blank=True,
        null=True,
        verbose_name=_('Subjects provided')
    )
    registration_level = ArrayField(
        models.CharField(
            choices=REGISTRATION_LEVEL,
            max_length=200,
            blank=True,
            null=True,
        ),
        blank=True,
        null=True,
        verbose_name=_('Dirasa Grade level')
    )
    teacher_assignment = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=TEACHER_ASSIGNMENT,
        verbose_name=_('Teacher Assignment')
    )
    teaching_hours_private_school = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of teaching hours in private school')
    )
    teaching_hours_mscc = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of teaching hours in MSCC')
    )
    trainings = models.ManyToManyField(
        Training,
        blank=True,
        related_name='mscc_teachers',
        verbose_name=_('Topics of teacher training')
    )
    training_sessions_attended = models.IntegerField(
        blank=True,
        null=True,
        choices=((x, x) for x in range(0, 30)),
        verbose_name=_('Number of teacher training sessions (attended)')
    )
    extra_coaching = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Extra coaching')
    )
    extra_coaching_specify = models.TextField(
        blank=True, null=True,
        verbose_name=_('Please specify')
    )
    attach_short_description_1 = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_('Description')
    )
    attach_file_1 = models.FileField(
        upload_to='uploads/mscc_teacher',
        blank=True,
        null=True,
        verbose_name=_('Attachment'),
    )
    attach_type_1 = models.ForeignKey(
        AttachmentType,
        blank=True, null=True,
        on_delete=models.SET_NULL,
        related_name='mscc_attach_type_1',
        verbose_name=_('Type')
    )
    attach_short_description_2 = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_('Description')
    )
    attach_file_2 = models.FileField(
        upload_to='uploads/mscc_teacher',
        blank=True,
        null=True,
        verbose_name=_('Attachment'),
    )
    attach_type_2 = models.ForeignKey(
        AttachmentType,
        blank=True, null=True,
        on_delete=models.SET_NULL,
        related_name='mscc_attach_type_2',
        verbose_name=_('Type')
    )
    attach_short_description_3 = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_('Description')
    )
    attach_file_3 = models.FileField(
        upload_to='uploads/mscc_teacher',
        blank=True,
        null=True,
        verbose_name=_('Attachment'),
    )
    attach_type_3 = models.ForeignKey(
        AttachmentType,
        blank=True, null=True,
        on_delete=models.SET_NULL,
        related_name='mscc_attach_type_3',
        verbose_name=_('Type')
    )
    attach_short_description_4 = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_('Description')
    )
    attach_file_4 = models.FileField(
        upload_to='uploads/mscc_teacher',
        blank=True,
        null=True,
        verbose_name=_('Attachment'),
    )
    attach_type_4 = models.ForeignKey(
        AttachmentType,
        blank=True, null=True,
        on_delete=models.SET_NULL,
        related_name='mscc_attach_type_4',
        verbose_name=_('Type')
    )
    attach_short_description_5 = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_('Description')
    )
    attach_file_5 = models.FileField(
        upload_to='uploads/mscc_teacher',
        blank=True,
        null=True,
        verbose_name=_('Attachment'),
    )
    attach_type_5 = models.ForeignKey(
        AttachmentType,
        blank=True, null=True,
        on_delete=models.SET_NULL,
        related_name='mscc_attach_type_5',
        verbose_name=_('Type')
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=False, null=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    modified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True, null=True,
        related_name='+',
        on_delete=models.SET_NULL,
        verbose_name=_('Modified by'),
    )

    class Meta:
        verbose_name = 'MSCC Teacher'
        verbose_name_plural = 'MSCC Teachers'

class Registration(TimeStampedModel):

    YES_NO = Choices(
        ('', '----------'),
        ('Yes', _("Yes")),
        ('No', _("No"))
    )

    HAVE_LABOUR = Choices(
        ('', '----------'),
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
            ('', '----------'),
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
            ('', '----------'),
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
            ('', '----------'),
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
    center = models.ForeignKey(
        Center,
        blank=True, null=True,
        related_name='+',
        on_delete=models.SET_NULL,
        verbose_name=_('Center')
    )
    child = models.ForeignKey(
        Child,
        blank=False, null=True,
        related_name='+',
        on_delete=models.SET_NULL,
        verbose_name=_('Child')
    )
    student_old = models.IntegerField(blank=True, null=True)
    partner = models.ForeignKey(
        PartnerOrganization,
        blank=True, null=True,
        verbose_name=_('Partner'),
        related_name='+',
        on_delete=models.SET_NULL,
    )
    round = models.ForeignKey(
        Round,
        blank=True, null=True,
        related_name='+',
        on_delete=models.SET_NULL,
        verbose_name=_('Round')
    )
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
        verbose_name=_('Source of referral of the child to MSCC')
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
        verbose_name=_('Packages received/to be provided to child under MSCC')
    )
    type = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('Type')
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
    deleted = models.BooleanField(blank=True, default=False)
    deleted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True, null=True,
        related_name='+',
        on_delete=models.SET_NULL,
        verbose_name=_('Deleted by'),
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

    @property
    def child_fullname(self):
        """Return the child's full name linked to the registration.

        Returns:
            str: Child full name when available, otherwise an empty string.
        """
        if self.child:
            return self.child.full_name
        return ''

    @property
    def child_age(self):
        """Return the child's age for reporting.

        Returns:
            int: Age from the related ``Child`` record or ``0`` if missing.
        """
        if self.child:
            return self.child.age
        return 0

    @property
    def child_birthday(self):
        """Expose the child's birthday for downstream consumers.

        Returns:
            date: Birthday from the related ``Child`` or ``0`` if unknown.
        """
        if self.child:
            return self.child.birthday
        return 0

    @property
    def education_program(self):
        """Fetch the most recent education program assigned to the child.

        Returns:
            str: Program code for the latest education service, otherwise ``''``.
        """
        result = ''
        program = self.education_service.all().last()
        if program:
            result = program.education_program
        return result

    @property
    def class_section(self):
        """Fetch the class section for the latest education service.

        Returns:
            str: Section name from the most recent service, otherwise ``''``.
        """
        result = ''
        program = self.education_service.all().last()
        if program:
            result = program.class_section
        return result

    @property
    def has_previous_registration(self):
        """Indicate if the child has an older MSCC registration.

        Returns:
            str: ``"Yes"`` when a previous registration exists, otherwise ``"No"``.
        """
        if hasattr(self, 'has_previous'):
            return "Yes" if self.has_previous else "No"
        previous_registration_exists = Registration.objects.filter(
            child_id=self.child.id,
            created__lt=self.created
        ).exists()
        return "Yes" if previous_registration_exists else "No"

    @property
    def total_absent_days(self):
        """Return the number of recorded absences for this registration.

        Returns:
            int: Cached ``_total_absent_days`` or the computed absence count.
        """
        if hasattr(self, '_total_absent_days'):
            return self._total_absent_days or 0
        return Registration.get_total_absent_days(self.id)

    @staticmethod
    def get_total_absent_days(registration_id):
        """Compute the total absences for the provided registration id.

        Args:
            registration_id (int): Registration identifier to check.

        Returns:
            int: Number of attendance records marked "No" for the registration.
        """
        result = 0
        from student_registration.attendances.models import MSCCAttendanceChild
        attendance_days = MSCCAttendanceChild.objects.filter(registration_id=registration_id, attended='No').count()
        if attendance_days:
            result = attendance_days
        return result

    def get_absolute_url(self):
        """Build the profile URL for this registration.

        Returns:
            str: URL for the child's profile view.
        """
        return reverse('mscc:child_profile', kwargs={'pk': self.pk})

    def __str__(self):
        """Return the child display name or registration id.

        Returns:
            str: Child string representation when linked, otherwise the id.
        """
        if self.child:
            return self.child.__str__()
        return str(self.id)

    def __unicode__(self):
        """Return the unicode representation of the child or id.

        Returns:
            str: Child unicode string when present, otherwise the id.
        """
        if self.child:
            return self.child.__unicode__()
        return str(self.id)

    class Meta:
        ordering = ['-id']
        verbose_name = "MSCC Registration"
        verbose_name_plural = "MSCC Registrations"


class EducationHistory(TimeStampedModel):

    child = models.IntegerField(blank=True, null=True)
    student_old = models.IntegerField(blank=True, null=True)
    registration_id = models.IntegerField(blank=True, null=True)

    programme_type = models.CharField(
        max_length=100,
        blank=True,
        null=True,
    )
    programme_id = models.IntegerField(blank=True, null=True)

    class Meta:
        ordering = ['-id']
        verbose_name = "Education History"
        verbose_name_plural = "Education Histories"


class ProvidedServices(models.Model):

    name = models.CharField(
        max_length=250,
        blank=False,
        null=False,
    )
    registration = models.ForeignKey(
        Registration,
        blank=False, null=True,
        related_name='+',
        on_delete=models.SET_NULL,
    )
    type = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('Type')
    )
    category = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('Category')
    )
    service_id = models.IntegerField(blank=True, null=True)
    completed = models.BooleanField(blank=True, default=False)
    required = models.BooleanField(blank=True, default=False)
    completion_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('Completion date')
    )

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['id']
        verbose_name = "Provided Service"
        verbose_name_plural = "Provided Services"


class Packages(models.Model):

    name = models.CharField(
        max_length=250,
        blank=False,
        null=False,
    )
    type = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=PACKAGE_TYPES,
        verbose_name=_('Type')
    )
    category = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=PACKAGE_CATEGORIES,
        verbose_name=_('Category')
    )
    required = models.BooleanField(blank=True, default=False)
    age = models.IntegerField(blank=True, null=True)

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['id']
        verbose_name = "Package"
        verbose_name_plural = "Packages"


class InclusionService(TimeStampedModel):

    PARENTAL_ENGAGEMENT = Choices(
        ('', '----------'),
        ('Mother Only', _('Mother Only')),
        ('Father Only', _('Father Only')),
        ('Both', _('Both')),
        ('No one', _('No one')),
        ("Haven't started yet", _("Haven't started yet")),
    )

    registration = models.ForeignKey(
        Registration,
        blank=False, null=True,
        related_name='+',
        on_delete=models.SET_NULL,
    )
    dropout = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Dropout')
    )
    parental_engagement = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=PARENTAL_ENGAGEMENT,
        verbose_name=_('Parental Engagement Curriculum')
    )

    class Meta:
        ordering = ['id']
        verbose_name = "Inclusion"
        verbose_name_plural = "Inclusions"


class DigitalService(models.Model):
    ACCESS = Choices(
        ('', '----------'),
        ('Class', _('Class')),
        ('Home', _('Home')),
        ('Class & Home', _('Class & Home')),
    )
    YES_NO_OCCASIONALLY = Choices(
        ('', '----------'),
        ('Yes', _("Yes")),
        ('No', _("No")),
        ('Occasionally', _("Occasionally"))
    )
    NOTICING_CHANGE = Choices(
        ('', '----------'),
        ('Very Likely', _('Very Likely')),
        ('Likely', _('Likely')),
        ('Neutral', _('Neutral')),
        ('Not really', _('Not really')),
    )
    registration = models.ForeignKey(
        Registration,
        blank=False, null=True,
        related_name='+',
        on_delete=models.SET_NULL,
    )
    using_akelius = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Is the child using Akelius?')
    )
    akelius_sessions_number = models.IntegerField(
        blank=True,
        null=True,
        verbose_name=_('Number of sessions per week')
    )
    akelius_access = models.CharField(
        max_length=250,
        blank=True,
        null=True,
        choices=ACCESS,
        verbose_name=_("Access during")
    )
    akelius_child_equipped = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=YES_NO_OCCASIONALLY,
        verbose_name=_('Is the child equipped at home to access the platforms (Based on Child and parents'' confirmation)')
    )
    akelius_change_literacy = models.CharField(
        max_length=250,
        blank=True,
        null=True,
        choices=NOTICING_CHANGE,
        verbose_name=_("As a teacher, are you noticing a change in motivation & output about Literacy")
    )
    akelius_change_math = models.CharField(
        max_length=250,
        blank=True,
        null=True,
        choices=NOTICING_CHANGE,
        verbose_name=_("As a teacher, are you noticing a change in motivation & output about Math")
    )
    akelius_change_learning = models.CharField(
        max_length=250,
        blank=True,
        null=True,
        choices=NOTICING_CHANGE,
        verbose_name=_("As a teacher, are you noticing a change in attitude towards learning")
    )
    using_lp = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Is the child using Learning Passport?')
    )
    lp_sessions_number = models.IntegerField(
        blank=True,
        null=True,
        verbose_name=_('Number of sessions per week')
    )
    lp_access = models.CharField(
        max_length=250,
        blank=True,
        null=True,
        choices=ACCESS,
        verbose_name=_("Access during")
    )
    lp_child_equipped = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=YES_NO_OCCASIONALLY,
        verbose_name=_(
            'Is the child equipped at home to access the platforms (Based on Child and parents'' confirmation)')
    )
    lp_change_literacy = models.CharField(
        max_length=250,
        blank=True,
        null=True,
        choices=NOTICING_CHANGE,
        verbose_name=_("As a teacher, are you noticing a change in motivation & output about Literacy")
    )
    lp_change_math = models.CharField(
        max_length=250,
        blank=True,
        null=True,
        choices=NOTICING_CHANGE,
        verbose_name=_("As a teacher, are you noticing a change in motivation & output about Math")
    )
    lp_change_learning = models.CharField(
        max_length=250,
        blank=True,
        null=True,
        choices=NOTICING_CHANGE,
        verbose_name=_("As a teacher, are you noticing a change in attitude towards learning")
    )

    class Meta:
        ordering = ['id']
        verbose_name = "Digital"
        verbose_name_plural = "Digital"


class PSSService(models.Model):

    LIVING_ARRANGEMENT = Choices(
        ('', '----------'),
        ('Unaccompanied or Separated Child', _('Unaccompanied or Separated Child')),
        ('Living with single parent/caregiver', _('Living with single parent/caregiver')),
        ('Living with Mother/women-headed Household ', _('Living with Mother/women-headed Household')),
        ('Child-headed Household', _('Child-headed Household')),
        ('Main caregiver is ill/disabled', _('Main caregiver is ill/disabled')),
    )

    CHILD_VULNERABILITY = Choices(
        ('', '----------'),
        ('Clear signs of neglect', _('Clear signs of neglect')),
        ('Clear signs of distress', _('Clear signs of distress')),
        ('Clear signs of physical maltreatment/damage and/or injuries',
         _('Clear signs of physical maltreatment/damage and/or injuries')),
    )

    OUT_SCHOOL_REASONS = Choices(
        ('', '----------'),
        ('Fear of bullying, discrimination or violence at school or on the way to school',
         _('Fear of bullying, discrimination or violence at school or on the way to school')),
        ('The child needs to work', _('The child needs to work')),
        ('The child needs to stay at home to support the family with chores',
         _('The child needs to stay at home to support the family with chores')),
        ('Disability', _('Disability')),
        ('N/A', _('N/A')),
    )
    PROTECTION_CONCERN = Choices(
        ('', '----------'),
        ('Nightmares', _('Nightmares')),
        ('Regressions', _('Regressions')),
        ('Distress', _('Distress')),
        ('Suicidal ideation', _('Suicidal ideation')),
        ('Bedwetting', _('Bedwetting')),
        ('Anger issues', _('Anger issues')),
        ('Isolation', _('Isolation')),
    )
    registration = models.ForeignKey(
        Registration,
        blank=False, null=True,
        related_name='+',
        on_delete=models.SET_NULL,
    )
    child_registered = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Is the child registered/ have birth registration?')
    )
    child_living_arrangement = models.CharField(
        max_length=250,
        blank=True,
        null=True,
        choices=LIVING_ARRANGEMENT,
        verbose_name=_("What is the child's living arrangement?")
    )
    child_vulnerability = models.CharField(
        max_length=250,
        blank=True,
        null=True,
        choices=CHILD_VULNERABILITY,
        verbose_name=_("Visible and known vulnerabilites of the child")
    )
    child_out_school_reasons = models.CharField(
        max_length=250,
        blank=True,
        null=True,
        choices=OUT_SCHOOL_REASONS,
        verbose_name=_("Reasons for a child being out of school")
    )
    caregivers_distress = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Do you feel distressed and anxious?')
    )
    caregivers_additional_parenting = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('If yes, would you like any additional parenting or psychosocial support?')
    )
    child_distress = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Are any of the children in your HH experiencing any '
                       'signs of distress or negative mental health symptoms ?')
    )
    child_additional_parenting = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('If yes, do you need additional support '
                       'for taking care or better dealing with your children?')
    )
    child_know_seek_help = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Does the child know where to seek help or support in case he is exposed to violence, abuse, or exploitation?')
    )
    child_protection_concern = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=PROTECTION_CONCERN,
        verbose_name=_('Does the facilitator identify any child protection concern or has the caregiver expressed any of the below signs on their children?')
    )

    class Meta:
        ordering = ['id']
        verbose_name = "PSS Service"
        verbose_name_plural = "PSS Services"


class HealthNutritionService(TimeStampedModel):

    DEVELOPMENT_DELAYS = Choices(
        ('', '----------'),
        ('Social/Emotional', _('Social/Emotional')),
        ('Language/Communication', _('Language/Communication')),
        ('Cognitive (learning thinking, problem solving)', _('Cognitive (learning thinking, problem solving)')),
        ('Movement/Physical development', _('Movement/Physical development')),
        ('No', _('No')),
    )
    AGE_EAT_SOLID_FOOD = Choices(
        ('', '----------'),
        ('0 month', _('1 months')),
        ('1 month', _('1 months')),
        ('2 months', _('2 months')),
        ('3 months', _('3 months')),
        ('4 months', _('4 months')),
        ('5 months', _('5 months')),
        ('6 months', _('6 months')),
        ('7 months', _('7 months')),
        ('8 months', _('8 months')),
        ('9 months', _('9 months')),
        ('10 months', _('10 months')),
        ('11 months', _('11 months')),
        ('12 months', _('12 months')),
        ('13 months', _('13 months')),
        ('14 months', _('14 months')),
        ('15 months', _('15 months')),
        ('16 months', _('16 months')),
        ('17 months', _('17 months')),
        ('18 months', _('18 months')),
        ('19 months', _('19 months')),
        ('20 months', _('20 months')),
        ('21 months', _('21 months')),
        ('22 months', _('22 months')),
        ('23 months', _('23 months')),
        ('24 months', _('24 months'))
    )
    MALNUTRITION_SCREENING = Choices(
        ('', '----------'),
        ('No malnutrition screening', _('No malnutrition screening')),
        ('MAM (MUAC >11.5 and <12.5 cm)', _('MAM (MUAC >11.5 and <12.5 cm)')),
        ('SAM (MUAC <11.5 cm)', _('SAM (MUAC <11.5 cm)')),
        ('SAM with Bilateral pitting oedema  (both feet puffy)', _('SAM with Bilateral pitting oedema  (both feet puffy)')),
        ('At risk of malnutrition (MUAC 12.5-13.5 cm)', _('At risk of malnutrition (MUAC 12.5-13.5 cm)')),
    )
    registration = models.ForeignKey(
        Registration,
        blank=False, null=True,
        related_name='+',
        on_delete=models.SET_NULL
    )
    # Caregivers of children 0-5 years
    baby_breastfed = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Is the baby being Breastfed?')
    )
    # Caregivers of children 0-5 years
    infant_exclusively_breastfed = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('if yes, is it exclusively breastfeeding for infants between 0-6 months?(only brest milk no other liquids even water)')
    )
    # Caregivers of children 0-5 years
    eat_solid_food = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Did the child start to eat solid food?')
    )
    # Caregivers of children 0-5 years
    age_eat_solid_food = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=AGE_EAT_SOLID_FOOD,
        verbose_name=_('If yes, at which age ?')
    )
    # Caregivers of children 0-5 years
    immunization_record_screened = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Child immunization record screened (to check the integrated ECD milestones Cards based on the age of the child- or the national immunization Calendar)')
    )
    # Caregivers of children 0-5 years
    vaccine_missing = models.TextField(
        blank=True, null=True,
        verbose_name=_('write the name of vaccine missing')
    )
    # Caregivers of children 0-5 years
    muac_malnutrition_screening = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=MALNUTRITION_SCREENING,
        verbose_name=_('MUAC malnutrition screening ')
    )
    # Caregivers of children 0-18 years
    eating_minimum_meals = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Is the child eating 3 minimum meals per day?')
    )
    # Caregivers of children 0-18 years
    child_vaccinated = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Is the child being vaccinated as per the National vaccination calendar?')
    )
    # Caregivers of children 0-5 years
    positive_parenting = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('positive parenting and dealing with difficult children without the use of harsh punishment?')
    )
    # Caregivers of children 0-5 years
    development_delays_identified = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=DEVELOPMENT_DELAYS,
        verbose_name=_('Any delays in the development milestones  is being identified? (please to check the Integrated ECD milestones Cards based on the age of the child)')
    )
    # Caregivers of children 6-18 years
    respond_stressful_events = models.TextField(
        blank=True, null=True,
        verbose_name=_('How children of different ages respond to and understand stressful and traumatic events?')
    )
    # Caregivers of children 6-18 years
    physical_activity = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Is the child practicing physical activity at least twice a week')
    )
    # Caregivers of children 6-18 years
    accessing_reproductive_health = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('In case of a child marriage to ask if the child is accessing in reproductive health services')
    )

    # Counselling and sessions
    # Caregivers of children 0-5 years
    caregiver_counselling = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Did the caregiver receive one on one counselling?')
    )
    # Caregivers of children 0-5 years
    counselling_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('If yes (please provide session date)')
    )
    # Caregivers of children 0-5 years
    next_counselling_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('Date of Next session')
    )
    # Caregivers of children 0-5 years
    caregiver_ecd_counselling = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Did the caregiver attended ECD group counselling?')
    )
    # Caregivers of children 0-5 years
    ecd_counselling_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('If yes (please provide session date)')
    )
    # Caregivers of children 0-5 years
    next_ecd_counselling_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('Date of Next session')
    )
    # Caregivers of children 0-5 years
    child_screened_malnutrition = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Was the child screened for malnutrition using MUAC tapes?')
    )
    # Caregivers of children 0-5 years
    child_malnutrition_screening = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=MALNUTRITION_SCREENING,
        verbose_name=_('MUAC malnutrition screening ')
    )
    # Caregivers of children 0-5 years
    child_immunization_screened = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Was the child immunization record screened')
    )
    # Caregivers of children 0-5 years
    missing_vaccine = models.TextField(
        blank=True, null=True,
        verbose_name=_('if yes (please mention if any vaccine is missing)')
    )
    # Caregivers of children 6-18 years
    attended_health_nutrition_session = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Children attended health and nutrition session')
    )
    # Caregivers of children 6-18 years
    health_nutrition_session_title = models.TextField(
        blank=True, null=True,
        verbose_name=_('if yes to write the title of the session')
    )
    # Caregivers of children 0-5 years
    health_nutrition_session_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('if yes to write the date of the session')
    )

    class Meta:
        ordering = ['id']
        verbose_name = "Health & Nutrition Service"
        verbose_name_plural = "Health & Nutrition Services"


class HealthNutritionReferral(TimeStampedModel):

    DEVELOPMENT_DELAYS = Choices(
        ('', '----------'),
        ('Primary Health care center', _('Primary Health care center')),
        ('Dispensary', _('Dispensary')),
        ('Hospital', _('Hospital')),
        ('Private clinic', _('Private clinic')),
        ('Organization', _('Organization')),
    )
    MALNUTRITION_TREATMENT_CENTER = Choices(
        ('', '----------'),
        ('MAM', _('MAM')),
        ('SAM', _('SAM')),
        ('At Risk of Malnutrition', _('At Risk of Malnutrition')),
        ('To Supplementary Feeding PHCC', _('To Supplementary Feeding PHCC')),
        ('To Treatment Center/ PHCC', _('To Treatment Center/ PHCC')),
        ('To Hospital', _('To Hospital')),
        ('To Organization', _('To Organization')),
    )
    registration = models.ForeignKey(
        Registration,
        blank=False, null=True,
        related_name='+',
        on_delete=models.SET_NULL
    )
    referred_development_delays = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Was the child Referred for any observed developmental delays as per the milestones cards to?')
    )
    development_delays = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=DEVELOPMENT_DELAYS,
        verbose_name=_('if yes, please select')
    )
    referred_malnutrition = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Was the child Referred for malnutrition treatment center?')
    )
    malnutrition_treatment_center = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=MALNUTRITION_TREATMENT_CENTER,
        verbose_name=_('if yes, please select')
    )
    referred_anc_pnc = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Was a Pregnant lactating women/child referred  for ANC and PNC follow up  and to receive MMS (multivitamins) to PHC?')
    )
    phc_center = models.TextField(
        blank=True, null=True,
        verbose_name=_('If yes (please add name the PHC center)')
    )
    women_child_referred_iycf = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Was a Pregnant lactating women/child with challenges on breastfeeding referred to IYCF specialists?')
    )
    women_child_referred_organization = models.TextField(
        blank=True, null=True,
        verbose_name=_('If yes (please add name of organization referred tor)')
    )
    infant_child_referred_iycf = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Was a Children aged 6months to 59months with challenges on infant and young child feeding practice refeered to IYCF specialists and to receive Micronutrient supplements?')
    )
    infant_child_referred_organization = models.TextField(
        blank=True, null=True,
        verbose_name=_('If yes (please add name of organization referred to)')
    )

    class Meta:
        ordering = ['id']
        verbose_name = "Health & Nutrition Referral"
        verbose_name_plural = "Health & Nutrition Referrals"


class EducationService(TimeStampedModel):

    EDUCATION_STATUS = Choices(
        ('', '----------'),
        ('Never registered in any formal school before', _('Never registered in any formal school before')),
        ('Was registered in formal school but didn\'t continue',
         _('Was registered in formal school but didn\'t continue')),
        ('Was registered in non formal program and was referred to MSCC',
         _('Was registered in non formal program and was referred to MSCC')),
        ('Was registered in non formal program but didn\'t continue',
         _('Was registered in non formal program but didn\'t continue')),
        ('Was enrolled in TVET Programs', _('Was enrolled in TVET Programs')),
        ('Was Registered in Formal Education but not attending',
         _('Was Registered in Formal Education but not attending')),
        ('Currently registered in Formal Education school', _('Currently registered in Formal Education school')),
        ('Currently registered in Formal Education school but not attending', _('Currently registered in Formal Education school but not attending')),
        ('No', _('No')),
    )
    DROPOUT_PROGRAM = Choices(
        ('', '----------'),
        ('Was registered in CBECE level 1-2', _('Was registered in CBECE level 1-2')),
        ('Was registered in BLN program', _('Was registered in BLN program')),
        ('Was registered in ALP program and didn\'t continue', _('Was registered in ALP program and didn\'t continue')),
        ('Was enrolled in Dirasa', _('Was enrolled in Dirasa')),
        ('Other', _('Other')),
    )
    EDUCATION_PROGRAM = Choices(
        ('BLN Level 1', _('BLN Level 1')),
        ('BLN Level 2', _('BLN Level 2')),
        ('BLN Level 3', _('BLN Level 3')),
        ('BLN Catch-up', _('BLN Catch-up')),
        ('ABLN Level 1', _('ABLN Level 1')),
        ('ABLN Level 2', _('ABLN Level 2')),
        ('ABLN Catch-up', _('ABLN Catch-up')),
        ('YBLN Level 1', _('YBLN Level 1')),
        ('YBLN Level 2', _('YBLN Level 2')),
        ('YBLN Catch-up', _('YBLN Catch-up')),
        ('YFS Level 1', _('YFS Level 1')),
        ('YFS Level 2', _('YFS Level 2')),
        ('YFS Level 1 - RS Grade 9', _('YFS Level 1 - RS Grade 9')),
        ('YFS Level 2 - RS Grade 9', _('YFS Level 2 - RS Grade 9')),
        ('CBECE Level 1', _('CBECE Level 1')),
        ('CBECE Level 2', _('CBECE Level 2')),
        ('CBECE Level 3', _('CBECE Level 3')),
        ('CBECE Catch-up', _('CBECE Catch-up')),
        ('RS Grade 1', _('RS Grade 1')),
        ('RS Grade 2', _('RS Grade 2')),
        ('RS Grade 3', _('RS Grade 3')),
        ('RS Grade 4', _('RS Grade 4')),
        ('RS Grade 5', _('RS Grade 5')),
        ('RS Grade 6', _('RS Grade 6')),
        ('RS Grade 7', _('RS Grade 7')),
        ('RS Grade 8', _('RS Grade 8')),
        ('RS Grade 9', _('RS Grade 9')),
        ('ECD', _('ECD')),
    )
    YOUTH_PROGRAM = Choices(
        ('YBLN Level 1', _('YBLN Level 1')),
        ('YBLN Level 2', _('YBLN Level 2')),
        ('YFS Level 1', _('YFS Level 1')),
        ('YFS Level 2', _('YFS Level 2')),
        ('YFS Level 1 - RS Grade 9', _('YFS Level 1 - RS Grade 9')),
        ('YFS Level 2 - RS Grade 9', _('YFS Level 2 - RS Grade 9')),
    )
    CLASS_SECTION = Choices(
        ('', '----------'),
        ('A', _('A')),
        ('B', _('B')),
        ('C', _('C')),
        ('D', _('D')),
        ('E', _('E')),
        ('F', _('F')),
        ('G', _('G')),
        ('H', _('H')),
        ('I', _('I')),
        ('J', _('J')),
        ('K', _('K')),
        ('L', _('L')),
        ('M', _('M')),
        ('N', _('N')),
        ('O', _('O')),
        ('P', _('P')),
        ('Q', _('Q')),
        ('R', _('R')),
        ('S', _('S')),
        ('T', _('T')),
        ('U', _('U')),
        ('V', _('V')),
        ('W', _('W')),
        ('X', _('X')),
        ('Y', _('Y')),
        ('Z', _('Z')),
    )
    CATCH_UP_REGISTERED = Choices(
        ('', '----------'),
        ('Yes-New Comers programme', _('Yes-New Comers programme')),
        ('Yes-Undocumented programme', _('Yes-Undocumented programme'))
    )
    registration = models.ForeignKey(
        Registration,
        blank=False, null=True,
        related_name='education_service',
        on_delete=models.SET_NULL
    )
    education_status = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        choices=EDUCATION_STATUS,
        verbose_name=_('Child\'s educational level when registering for the round')
    )
    dropout_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('Please Specify dropout date from school')
    )
    education_program = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        choices=EDUCATION_PROGRAM,
        verbose_name=_('Education Program')
    )
    catch_up_registered = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        choices=CATCH_UP_REGISTERED,
        verbose_name=_('Is the child registered in catch-up program')
    )
    class_section = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=CLASS_SECTION,
        verbose_name=_('Class Section')
    )
    # @todo not sure about this field
    registration_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('Date of registration in the round')
    )

    round = models.ForeignKey(
        Round,
        blank=True, null=True,
        related_name='+',
        on_delete=models.SET_NULL,
        verbose_name=_('Round')
    )

    class Meta:
        ordering = ['id']
        verbose_name = "Education Service"
        verbose_name_plural = "Education Services"


# @todo to be reviewed
class EducationRSService(TimeStampedModel):

    REGISTRATION_LEVEL = Choices(
        ('', '----------'),
        ('Level one', _('Level one')),
        ('Level two', _('Level two')),
        ('Level three', _('Level three')),
        ('Level four', _('Level four')),
        ('Level five', _('Level five')),
        ('Level six', _('Level six'))
    )
    SUPPORT_NEEDED = Choices(
        ('Foreign Languages', _('Foreign Languages')),
        ('Arabic', _('Arabic')),
        ('Math', _('Math')),
        ('Sciences', _('Sciences')),
    )
    SCHOOL_SHIFTS = Choices(
        ('', _('----------')),
        ('First shift', _('First shift')),
        ('Second shift', _('Second shift')),
    )
    registration = models.ForeignKey(
        Registration,
        blank=False, null=True,
        related_name='+',
        on_delete=models.SET_NULL,
    )
    school = models.ForeignKey(
        School,
        blank=False, null=True,
        related_name='+',
        on_delete=models.SET_NULL,
        verbose_name=_('Name of public School')
    )
    foreign_language_grade = models.IntegerField(
        blank=True,
        null=True,
        choices=((x, x) for x in range(0, 100)),
        verbose_name=_('Foreign Language\'s grade')
    )
    arabic_grade = models.IntegerField(
        blank=True,
        null=True,
        choices=((x, x) for x in range(0, 100)),
        verbose_name=_('Arabic grade')
    )
    math_grade = models.IntegerField(
        blank=True,
        null=True,
        choices=((x, x) for x in range(0, 100)),
        verbose_name=_('Math grade')
    )
    sciences_grade = models.IntegerField(
        blank=True,
        null=True,
        choices=((x, x) for x in range(0, 100)),
        verbose_name=_('Sciences grade')
    )
    shift = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=SCHOOL_SHIFTS,
        verbose_name=_('First or Second shift schools')
    )
    grade_level = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=REGISTRATION_LEVEL,
        verbose_name=_('Grade level')
    )
    support_needed = ArrayField(
        models.CharField(
            choices=SUPPORT_NEEDED,
            max_length=100,
            blank=True,
            null=True,
        ),
        blank=True,
        null=True,
        verbose_name=_('Needed support')
    )

    class Meta:
        ordering = ['id']
        verbose_name = "Education RS Service"
        verbose_name_plural = "Education RS Services"


# @todo to be removed
class EducationAssessment(TimeStampedModel):
    MODALITY = Choices(
        ('', '----------'),
        ('Online Forms', _('Online Forms')),
        ('Phone call/WhatsApp', _('Phone call/WhatsApp')),
        ('Asking Parents', _('Asking Parents')),
        ('Offline (F2F)', _('Offline (F2F)'))
    )
    PARTICIPATION = Choices(
        ('', '----------'),
        ('No Absence', _('No Absence')),
        ('Absence for less than 5 days/equivlant remote learning sessions',
         _('Absence for less than 5 days/equivlant remote learning sessions')),
        ('Absence for 5-10 days /equivlant remote learning sessions',
         _('Absence for 5-10 days /equivlant remote learning sessions')),
        ('Absence for 10-15 days /equivlant remote learning sessions',
         _('Absence for 10-15 days /equivlant remote learning sessions')),
        ('Absence for 15-25 days /equivlant remote learning sessions',
         _('Absence for 15-25 days /equivlant remote learning sessions')),
        ('Absence for more than 25 days / equivlant remote learning sessions',
         _('Absence for more than 25 days / equivlant remote learning sessions')),
    )
    BARRIERS = Choices(
        ('', '----------'),
        ('Working Full-time to support family', _('Working Full-time to support family')),
        ('Availability of Electronic Device', _('Availability of Electronic Device')),
        ('Sickness', _('Sickness')),
        ('Family changed address in Lebanon', _('Family changed address in Lebanon')),
        ('Marriage/engagement', _('Marriage/engagement')),
        ('No barriers', _('No barriers')),
        ('Enrolled in Formal Education', _('Enrolled in Formal Education')),
        ('Seasonal Work', _('Seasonal Work')),
        ('Internet Connectivity', _('Internet Connectivity')),
        ('Security Concerns', _('Security Concerns')),
        ('Family moved back to Syria', _('Family moved back to Syria')),
        ('No Interest in pursuing programme', _('No Interest in pursuing programme')),
        ('Violence and Bullying', _('Violence and Bullying')),
        ('Other', _('Other')),
    )
    registration = models.ForeignKey(
        Registration,
        blank=False, null=True,
        related_name='+',
        on_delete=models.SET_NULL,
    )
    pre_attended_arabic = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Did the Child Undertake Arabic Language Development Assessment')
    )
    pre_modality_arabic = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=MODALITY,
        verbose_name=_('Modality')
    )
    pre_arabic_grade = models.IntegerField(
        blank=True,
        null=True,
        verbose_name=_('Grade')
    )
    pre_attended_language = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Did the Child Undertake Foreign Language Development Assessment')
    )
    pre_modality_language = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=MODALITY,
        verbose_name=_('Modality')
    )
    pre_language_grade = models.IntegerField(
        blank=True,
        null=True,
        verbose_name=_('Grade')
    )
    pre_attended_math = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Did the Child Undertake Cognitive Development - Mathematics test')
    )
    pre_modality_math = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=MODALITY,
        verbose_name=_('Modality')
    )
    pre_math_grade = models.IntegerField(
        blank=True,
        null=True,
        verbose_name=_('Grade')
    )
    participation = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=PARTICIPATION,
        verbose_name=_('Child Level of participation / Absence')
    )
    barriers = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=BARRIERS,
        verbose_name=_('The main barriers affecting the child\'s '
                       'daily attendance/participation, performance, or causing drop-out')
    )
    barriers_other = models.TextField(
        blank=True, null=True,
        verbose_name=_('Please specify')
    )
    post_test_done = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Did the child undertake the Post tests?')
    )
    school_year_completed = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Did the child fully complete the school year?')
    )
    post_attended_arabic = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Did the Child Undertake Arabic Language Development Assessment')
    )
    post_modality_arabic = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=MODALITY,
        verbose_name=_('Modality')
    )
    post_arabic_grade = models.IntegerField(
        blank=True,
        null=True,
        verbose_name=_('Grade')
    )
    post_attended_language = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Did the Child Undertake Foreign Language Development Assessment')
    )
    post_modality_language = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=MODALITY,
        verbose_name=_('Modality')
    )
    post_language_grade = models.IntegerField(
        blank=True,
        null=True,
        verbose_name=_('Grade')
    )
    post_attended_math = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Did the Child Undertake Cognitive Development - Mathematics test')
    )
    post_modality_math = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=MODALITY,
        verbose_name=_('Modality')
    )
    post_math_grade = models.IntegerField(
        blank=True,
        null=True,
        verbose_name=_('Grade')
    )

    @property
    def arabic_improvement(self):
        if self.pre_arabic_grade and self.post_arabic_grade:
            try:
                return '{}{}'.format(
                    round(((float(self.post_arabic_grade) - float(self.pre_arabic_grade)) /
                           float(self.pre_arabic_grade)) * 100.0, 2), '%')
            except ZeroDivisionError:
                return 0.0
        return 0.0

    @property
    def math_improvement(self):
        if self.pre_math_grade and self.post_math_grade:
            try:
                return '{}{}'.format(
                    round(((float(self.post_math_grade) - float(self.pre_math_grade)) /
                           float(self.pre_math_grade)) * 100.0, 2), '%')
            except ZeroDivisionError:
                return 0.0
        return 0.0

    @property
    def language_improvement(self):
        if self.pre_language_grade and self.post_language_grade:
            try:
                return '{}{}'.format(
                    round(((float(self.post_language_grade) - float(self.pre_language_grade)) /
                           float(self.pre_language_grade)) * 100.0, 2), '%')
            except ZeroDivisionError:
                return 0.0
        return 0.0

    class Meta:
        ordering = ['id']
        verbose_name = "Education Assessment"
        verbose_name_plural = "Education Assessments"


class EducationProgrammeAssessment(TimeStampedModel):

    registration = models.ForeignKey(
        Registration,
        blank=False, null=True,
        related_name='+',
        on_delete=models.SET_NULL,
    )
    pre_test = JSONField(default=dict)
    post_test = JSONField(default=dict)
    school_test = JSONField(default=dict)
    programme_type = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('Education Programme Type')
    )

    class Meta:
        ordering = ['id']
        verbose_name = "Education Programme Assessment"
        verbose_name_plural = "Education Programme Assessments"


class YouthKitService(TimeStampedModel):

    VOLUNTEERING = Choices(
        ('', '----------'),
        ('Outreach', _('Outreach')),
        ('Data entry', _('Data entry')),
        ('Admin work', _('Admin work')),
        ('Awareness raising sessions', _('Awareness raising sessions')),
        ('Empowerment and leadership', _('Empowerment and leadership')),
        ('Other', _('Other')),
    )
    TRAINING_MATERIAL = Choices(
        ('', '----------'),
        ('Printed workbook', _('Printed workbook')),
        ('Tablets', _('Tablets')),
        ('Access to digital content (learning Passport) ', _('Access to digital content (learning Passport)')),
        ('Other', _('Other')),
    )
    FUTURE_PATH = Choices(
        ('', '----------'),
        ('Transition to FE', _('Transition to FE')),
        ('Repeat the school year', _('Repeat the school year')),
        ('Refer to a UNICEF Youth Programme (skills training, CBT, GIL)',
         _('Refer to a UNICEF Youth Programme (skills training, CBT, GIL)')),
        ('Transition to TVET', _('Transition to TVET')),
        ('Internship or volunteering opportunity', _('Internship or volunteering opportunity')),
    )
    ATTENDANCE = Choices(
        ('', '----------'),
        ('Full attendance', _('Full attendance')),
        ('Absence for less than 5 days', _('Absence for less than 5 days')),
        ('Absence for more than 5 days', _('Absence for more than 5 days')),
        ('Dropout', _('Dropout')),
    )

    registration = models.ForeignKey(
        Registration,
        blank=False, null=True,
        related_name='+',
        on_delete=models.SET_NULL,
    )
    # For Youth
    volunteering_experience = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Does the adolescent have any volunteering experience?')
    )
    previous_community_initiative = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Was the adolescent part of any previous community based initiative?')
    )
    enrollment_reason = models.CharField(
        max_length=300,
        blank=True,
        null=True,
        verbose_name=_('What is the reason for the adolescent enrollment in the programme?')
    )
    pre_tests_administered = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Were pre-tests administered to assess adolescents level?')
    )
    # Youth Assessment
    test_diagnostic_done = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Did the adolescent undertake any Post Diagnostic tests?')
    )
    receive_passing_grade = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Did the adolescent receive a passing grade for the tests?')
    )
    life_skills_completed = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Did the adolescent complete the life skills package?')
    )
    participate_volunteering = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Did the adolescent participate in any volunteering '
                       'opportunity during the course of the program?')
    )
    volunteering_specify = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        choices=VOLUNTEERING ,
        verbose_name=_('Please specify the volunteering opportunity')
    )
    social_course = models.CharField(
            max_length=10,
            blank=True,
            null=True,
            choices=YES_NO,
            verbose_name=_('Did the adolescent benefit from any social innovation/entrepreneurship course?')
    )
    yfs_course_completed = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Did the adolescent complete the YFS course?')
    )
    training_material = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        choices=TRAINING_MATERIAL,
        verbose_name=_('What training material was provided?')
    )
    future_path = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        choices=FUTURE_PATH,
        verbose_name=_('What is the recommended future path for the adolescent?')
    )
    participate_community_initiatives = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Did the adolescent participate/come up in community based initiatives?')
    )
    community_initiatives_specify = models.TextField(
        blank=True, null=True,
        verbose_name=_('What is the initiative?')
    )
    adolescent_attendance = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        choices=ATTENDANCE,
        verbose_name=_('Adolescent attendance')
    )
    adolescent_dropout_reason = models.TextField(
        blank=True, null=True,
        verbose_name=_('Reason for dropout')
    )
    adolescent_dropout_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('Dropout Date')
    )
    youth_trained_mental_health = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Is the youth trained on Mental health?')
    )

    class Meta:
        ordering = ['id']
        verbose_name = "Youth Kit Service"
        verbose_name_plural = "Youth Kit Services"


class YouthService(TimeStampedModel):

    TYPE = Choices(
        ('', '----------'),
        ('Maharati', _('Maharati')),
        ('GIL', _('GIL')),
    )
    registration = models.ForeignKey(
        Registration,
        blank=False, null=True,
        related_name='+',
        on_delete=models.SET_NULL,
    )

    service_type = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        choices=TYPE,
        verbose_name=_('Service Type')
    )

    service_values = JSONField(default=dict)

    class Meta:
        ordering = ['id']
        verbose_name = "Youth Service"
        verbose_name_plural = "Youth Services"


class FollowUpService(TimeStampedModel):

    FOLLOW_UP_TYPE = Choices(
        ('', _('----------')),
        ('Phone call', _('Phone call')),
        ('Home Visits', _('Home Visits')),
        ('Caregiver visited the center', _('Caregiver visited the center')),
    )
    FOLLOW_UP_RESULT = Choices(
        ('', '----------'),
        ('Child returned to program', _('Child returned to program')),
        ('Child referred to specialized services', _('Child referred to specialized services')),
        ('Child referred to CP', _('Child referred to CP')),
        ('Child referred to Health programme', _('Child referred to Health programme')),
        ('Follow-up with parents', _('Follow-up with parents')),
        ('Dropout/No Interest', _('Dropout/No Interest')),
    )
    MEETING_TYPE = Choices(
        ('', '----------'),
        ('PSS Session', _('PSS Session')),
        ('COVID health awareness session', _('COVID health awareness session')),
    )
    SESSION_MODALITY = Choices(
        ('', '----------'),
        ('Online via WhatsApp', _("Online via WhatsApp")),
        ('Phone calls', _("Phone calls")),
        ('Offline (F2F)', _("Offline (F2F)"))
    )
    CAREGIVER = Choices(
        ('', '----------'),
        ('Mother Only', _('Mother Only')),
        ('Father Only', _('Father Only')),
        ('Mother & Father', _('Mother & Father')),
        ('Other', _('Other')),
    )

    registration = models.ForeignKey(
        Registration,
        blank=False, null=True,
        related_name='+',
        on_delete=models.SET_NULL,
    )
    follow_up_type = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=FOLLOW_UP_TYPE,
        verbose_name=_('In case of absence, type of Follow-up done')
    )
    follow_up_number = models.IntegerField(
        blank=True,
        null=True,
        verbose_name=_('Number')
    )
    follow_up_result = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=FOLLOW_UP_RESULT,
        verbose_name=_('Result of follow up')
    )
    dropout_reason = models.TextField(
        blank=True, null=True,
        verbose_name=_('Reason for dropout')
    )
    dropout_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('Dropout Date')
    )
    parent_attended_meeting = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Did the child\'s caregiver attend parent meeting/engagment sessions')
    )
    meeting_type = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=MEETING_TYPE,
        verbose_name=_('Please indicate the types of meeting')
    )
    meeting_number = models.IntegerField(
        blank=True,
        null=True,
        verbose_name=_('Number of sessions attended')
    )
    meeting_modality = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        choices=SESSION_MODALITY,
        verbose_name=_('Please the modality used per each session')
    )
    caregiver_attended = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=CAREGIVER,
        verbose_name=_('Who attended the meetings')
    )
    caregiver_attended_other = models.TextField(
        blank=True, null=True,
        verbose_name=_('Please specify')
    )
    pfss_sessions = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Did they undertake FPSS sessions')
    )
    pfss_sessions_number = models.IntegerField(
        blank=True,
        null=True,
        default= 0,
        verbose_name=_('Number number of sessions')
    )
    class Meta:
        ordering = ['id']
        verbose_name = "Follow Up Service"
        verbose_name_plural = "Follow Up Services"


class Referral(TimeStampedModel):

    REFERRED_SERVICE = Choices(
        ('', '----------'),
        ('No', _('No')),
        ('CP', _('CP')),
        ('Wash', _('Wash')),
        ('Health', _('Health')),
        ('Youth', _('Youth')),
        ('Other', _('Other')),
    )
    LEARNING_PATH = Choices(
        ('', '----------'),
        ('Transition to Dirasa', _('Transition to Dirasa')),
        ('Repeat same level in next  school year', _('Repeat same level in next  school year')),
        ('Progress to FE', _('Progress to FE')),
        ('Referred to Specialized Education', _('Referred to Specialized Education')),
        ('Referred to TVET', _('Referred to TVET')),
        ('Drop out', _('Drop out')),
        ('Referred to YBLN', _('Referred to YBLN')),
        ('Referred to CBECE Higher Level in next school year', _('Referred to CBECE Higher Level in next school year')),
        ('Progress to  Higher Level  in next school year', _('Progress to  Higher Level  in next school year')),
    )

    registration = models.ForeignKey(
        Registration,
        blank=False, null=True,
        related_name='+',
        on_delete=models.SET_NULL,
    )
    referred_formal_education = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Was the child referred to formal education (Grade 1)?')
    )
    referred_school = models.ForeignKey(
        School,
        blank=False, null=True,
        related_name='+',
        on_delete=models.SET_NULL,
        verbose_name=_('Name of the School referred to')
    )
    receive_needed_material = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Did the child receive all needed materials and resources (Stationery, Books, Learning bundle)?')
    )
    referred_service = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=REFERRED_SERVICE,
        verbose_name=_('Was the child referred to a service?')
    )
    referred_service_other = models.TextField(
        blank=True, null=True,
        verbose_name=_('Please specify')
    )
    recommended_learning_path = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=LEARNING_PATH,
        verbose_name=_('Based on the overall score, what is the recommended learning path/outcome?')
    )
    dropout_date = models.DateField(blank=True, null=True)

    class Meta:
        ordering = ['id']
        verbose_name = "Referral"
        verbose_name_plural = "Referrals"


class YouthAssessment(TimeStampedModel):
    VOLUNTEERING_OPPORTUNITY = Choices(
        ('', '----------'),
        ('Outreach', _('Outreach')),
        ('Data entry', _('Data entry')),
        ('Admin work', _('Admin work')),
        ('Awareness raising sessions', _('Awareness raising sessions')),
        ('Empowerment and leadership', _('Empowerment and leadership')),
        ('Other', _('Other')),
    )
    TRAINING_MATERIAL = Choices(
        ('', '----------'),
        ('Printed workbook', _('Printed workbook')),
        ('Tablets', _('Tablets')),
        ('Access to digital content (learning Passport)', _('Access to digital content (learning Passport)')),
        ('Other', _('Other')),
    )
    FUTURE_PATH = Choices(
        ('', '----------'),
        ('Transition to FE', _('Transition to FE')),
        ('Repeat the school year', _('Repeat the school year')),
        ('Refer to a UNICEF Youth Programme (skills tranining, CBT, GIL...)', _('Refer to a UNICEF Youth Programme (skills tranining, CBT, GIL...)')),
        ('Transition to TVET', _('Transition to TVET')),
        ('Internship or volunteering opportunity', _('Internship or volunteering opportunity')),
    )
    ATTENDANCE = Choices(
        ('', '----------'),
        ('Full attendance', _('Full attendance')),
        ('Absence for less than 5 days', _('Absence for less than 5 days')),
        ('Absence for more than 5 days', _('Absence for more than 5 days')),
        ('Dropout', _('Dropout')),
    )
    registration = models.ForeignKey(
        Registration,
        blank=False, null=True,
        related_name='+',
        on_delete=models.SET_NULL,
    )
    undertake_post_diagnostic = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Did the adolescent undertake any Post Diagnotic tests?')
    )
    receive_passing_grade = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Did the adolescent receive a passing grade for the tests?')
    )
    complete_life_skills = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Did the adolescent complete the life skills package?')
    )
    participate_volunteering = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Did the adolescent participate in any volunteering opportunity during the course of the program?')
    )
    volunteering_opportunity = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=VOLUNTEERING_OPPORTUNITY,
        verbose_name=_('Is yes, please specify the volunteering opportunity')
    )
    benefit_innovation_course = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Did the adolescent benefit from any social innovation/entrepreneurship course?')
    )
    compelete_yfs_course = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Did the adolescent complete the YFS course?')
    )
    training_material = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=TRAINING_MATERIAL,
        verbose_name=_('What training material was provided?')
    )
    future_path = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        choices=FUTURE_PATH,
        verbose_name=_('What is the recommended future path for the adolescent?')
    )
    participate_community_initiatives = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Did the adolescent participate/come up in community based initiatives?')
    )
    attendance = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=ATTENDANCE,
        verbose_name=_('Adolescent attendance')
    )
    class Meta:
        ordering = ['id']
        verbose_name = "Youth Assessment"
        verbose_name_plural = "Youth Assessments"


class YouthReferral(TimeStampedModel):

    registration = models.ForeignKey(
        Registration,
        blank=False, null=True,
        related_name='+',
        on_delete=models.SET_NULL,
    )
    refer_tvet = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Did the partner refer youth who are above 18 to the TVET centers')
    )
    refer_innovation = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Did the partner refer youth who are above 18 to the  innovation hubs GIL?')
    )
    class Meta:
        ordering = ['id']
        verbose_name = "Youth Referral"
        verbose_name_plural = "Youth Referrals"


class Recreational(TimeStampedModel):

    registration = models.ForeignKey(
        Registration,
        blank=False, null=True,
        related_name='+',
        on_delete=models.SET_NULL,
    )
    assessment = JSONField(default=dict)

    class Meta:
        ordering = ['id']
        verbose_name = "Recreational"
        verbose_name_plural = "Recreational"


class LegoService(TimeStampedModel):

    registration = models.ForeignKey(
        Registration,
        blank=False, null=True,
        related_name='+',
        on_delete=models.SET_NULL,
    )
    participating_lego_sessions = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Is the child participating in CBPSS LEGO sessions?')
    )
    participating_education_sessions = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Is the child participating in Education sessions supported by LEGO activities?')
    )
    participating_lego_play_sessions = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Is the child participating in LEGO free-play sessions?')
    )

    class Meta:
        ordering = ['id']
        verbose_name = "LEGO"
        verbose_name_plural = "LEGO"

