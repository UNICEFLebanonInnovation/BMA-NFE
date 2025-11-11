from __future__ import unicode_literals, absolute_import, division
from django.conf import settings
from django.db import models
from model_utils import Choices
from model_utils.models import TimeStampedModel
from django.utils.translation import gettext as _
from django.contrib.postgres.fields import ArrayField


class Coordinator(models.Model):
    name = models.CharField(max_length=200, unique=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Coordinator'

    def __str__(self):
        return self.name

    def __unicode__(self):
            return self.name


class PublicHolidays(models.Model):
    holiday = models.DateField(
        unique=True,
        verbose_name=_('Public holidays')
    )

    def __str__(self):
        return self.holiday.strftime("%m/%d/%Y")

    def __unicode__(self):
        return self.holiday.strftime("%m/%d/%Y")


class School(TimeStampedModel):
    from student_registration.locations.models import Location
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
    YES_NO = Choices(
        ('', '----------'),
        ('yes', _("Yes")),
        ('no', _("No")),
    )
    TRUE_FALSE = Choices(
        ('', '----------'),
        ('True', _("Yes")),
        ('False', _("No")),
    )
    TYPE = Choices(
        ('', '----------'),
        ('Private School', _("Private School")),
        ('Private Free School', _("Private Free School")),
    )
    DAYS_OF_THE_WEEK = Choices(
        ('Monday', _('Monday')),
        ('Tuesday', _('Tuesday')),
        ('Wednesday', _('Wednesday')),
        ('Thursday', _('Thursday')),
        ('Friday', _('Friday')),
        ('Saturday', _('Saturday')),
        ('Sunday', _('Sunday')),
    )
    WFP_SERVICE_TYPE = Choices(
        ('', '----------'),
        ('Community Kitchen', _("Community Kitchen")),
        ('School Snacks', _("School Snacks")),
    )
    number = models.CharField(
        max_length=45,
        unique=True,
        verbose_name=_('School CERD Number')
    )
    type = models.CharField(
        blank=True, null=True, max_length=100,
        choices=TYPE,
    )
    name = models.CharField(
        max_length=255,
        verbose_name=_('School name')
    )
    director_name = models.CharField(
        max_length=100,
        blank=True, null=True,
        verbose_name=_('School director name')
    )
    land_phone_number = models.CharField(
        max_length=100,
        blank=True, null=True,
        verbose_name=_('School land phone number')
    )
    email = models.CharField(
        max_length=100,
        blank=True, null=True,
        verbose_name=_('School email')
    )
    governorate = models.ForeignKey(
        Location,
        blank=True, null=True,
        related_name='+',
        on_delete=models.SET_NULL,
        verbose_name=_('Governorate')
    )
    district = models.ForeignKey(
        Location,
        blank=True, null=True,
        related_name='+',
        on_delete=models.SET_NULL,
        verbose_name=_('District')
    )
    cadaster = models.ForeignKey(
        Location,
        blank=True, null=True,
        related_name='+',
        on_delete=models.SET_NULL,
        verbose_name=_('Cadaster')
    )
    longitude = models.FloatField(
        blank=True,
        null=True,
        verbose_name=_('School GPS (longitude)')
    )
    latitude = models.FloatField(
        blank=True,
        null=True,
        verbose_name=_('School GPS (latitude)')
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
        verbose_name=_('Grade level')
    )
    school_capacity = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('School capacity')
    )
    empty_building = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Available empty building/closed campus')
    )
    number_children = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Total Number of children enrolled (excluding Dirasa)')
    )
    number_children_male = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Total Number of children enrolled (male)')
    )
    number_children_female = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Total Number of children enrolled (female)')
    )
    number_children_lebanese = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Total Number of children enrolled (Lebanese)')
    )
    number_children_non_lebanese = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Total Number of children enrolled (non Lebanese)')
    )
    number_children_sbp = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Total Number of children enrolled (Dirasa only)')
    )
    number_children_male_sbp = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Total Number of children enrolled (male, Dirasa only)')
    )
    number_children_female_sbp = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Total Number of children enrolled (female, Dirasa only)')
    )
    number_children_lebanese_sbp = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Total Number of children enrolled (Lebanese, Dirasa only)')
    )
    number_children_non_lebanese_sbp = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Total Number of children enrolled (non Lebanese, Dirasa only)')
    )
    CWD_accessible = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Is the school accessible for CWD?')
    )
    internet_available = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Availability of Internet')
    )
    digital_learning_programme = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Does the school have a digital learning programme?')
    )
    school_digital_capacity = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of devices')
    )
    is_first_shift = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('School is 1st shift?')
    )
    weekend = models.CharField(
        max_length=100,
        blank=True, null=True,
        choices=Choices(
            ('Friday', _('Friday')),
            ('Saturday', _('Saturday')),
        ),
        verbose_name=_('School weekends')
    )
    working_days = ArrayField(
        models.CharField(
            choices=DAYS_OF_THE_WEEK,
            max_length=100,
            blank=True,
            null=True,
        ),
        blank=True,
        null=True,
        verbose_name=_('Working Days')
    )
    academic_year_start = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('School year start date')
    )
    academic_year_end = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('School year end date')
    )
    receive_supplies = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Did the school receive school supplies/stationery')
    )
    number_dirasa_children_disability = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Total number of Children With Disability (Dirasa only)')
    )
    number_total_children_disability = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Total number of Children With Disability (Excluding Dirasa)')
    )
    academic_year_exam_end = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('Exam end date')
    )
    director_phone_number = models.CharField(
        max_length=100,
        blank=True, null=True,
        verbose_name=_('School land phone number')
    )
    fax_number = models.CharField(
        max_length=100,
        blank=True, null=True,
        verbose_name=_('School fax number')
    )
    certified_foreign_language = models.CharField(
        max_length=100,
        blank=True, null=True,
        choices=Choices(
            ('French', _('French')),
            ('English', _('English')),
            ('French & English', _('French & English'))
        ),
        verbose_name=_('Certified foreign language')
    )
    comments = models.TextField(
        blank=True, null=True,
        verbose_name=_('Comments')
    )
    it_name = models.CharField(
        max_length=100,
        blank=True, null=True,
        verbose_name=_('School IT name')
    )
    it_phone_number = models.CharField(
        max_length=100,
        blank=True, null=True,
        verbose_name=_('School IT phone number')
    )
    coordinator = models.ForeignKey(
        Coordinator,
        blank=True, null=True,
        verbose_name=_('coordinator'),
        related_name='+',
        on_delete=models.SET_NULL,
    )
    is_2nd_shift = models.BooleanField(
        blank=True,
        default=False,
        verbose_name=_('School is 2nd shift?')
    )
    number_students_2nd_shift = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Expected number of students in 2nd shift')
    )
    is_alp = models.BooleanField(
        blank=True,
        default=False,
        verbose_name=_('School is ALP?')
    )
    number_students_alp = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Expected number of students in ALP')
    )
    attendance_range = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Attendance day range')
    )
    attendance_from_beginning = models.BooleanField(
        blank=True,
        default=False,
        verbose_name=_('Start attendance from the beginning')
    )
    location = models.ForeignKey(
        Location,
        blank=False, null=True,
        verbose_name=_('School location'),
        related_name='+',
        on_delete=models.SET_NULL,
    )
    is_bma = models.BooleanField(
        default=True,
        blank=True,
        verbose_name=_('BMA school')
    )
    is_closed = models.BooleanField(
        default=False,
        blank=True,
        verbose_name=_('is closed')
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

    class Meta:
        ordering = ['number']

    @property
    def location_name(self):
        if self.location:
            return self.location.name
        return ''

    @property
    def location_parent_name(self):
        if self.location and self.location.parent:
            return self.location.parent.name
        return ''

    @property
    def total_registered_bridging(self):
        from student_registration.clm.models import Bridging
        return Bridging.objects.all().count()

    @property
    def have_academic_year_dates(self):
        if not self.academic_year_start \
           or not self.academic_year_end \
           or not self.academic_year_exam_end:
            return False
        return True

    def __unicode__(self):
        return u'{} - {}'.format(self.number, self.name)

    def __str__(self):
        return self.name


class ClubType(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        ordering = ['name']
        verbose_name = "Club Type"

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name


class Club(TimeStampedModel):
    school = models.ForeignKey(
        'School',
        verbose_name=_('school'),
        related_name='+',
        on_delete=models.CASCADE,
    )
    club_name = models.CharField(
        max_length=50,
        blank=True, null=True,
        verbose_name=_('Club Name')
    )
    number_clubs = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of Clubs')
    )
    club_type = models.ForeignKey(
        'ClubType',
        blank=True, null=True,
        related_name='+',
        on_delete=models.SET_NULL,
        verbose_name=_('Club Type')
    )
    number_children = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Total Number of Children')
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


class Meeting(TimeStampedModel):
    school = models.ForeignKey(
        'School',
        verbose_name=_('school'),
        related_name='+',
        on_delete=models.CASCADE,
    )
    meeting_name = models.CharField(
        max_length=50,
        blank=True, null=True,
        verbose_name=_('Meeting Name')
    )
    meeting_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('Meeting Date')
    )
    number_participants = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of Participants')
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
        verbose_name=_('Modified by'),
        on_delete=models.SET_NULL,
    )


class CommunityInitiative(TimeStampedModel):
    school = models.ForeignKey(
        'School',
        verbose_name=_('school'),
        related_name='+',
        on_delete=models.CASCADE,
    )
    community_group_name = models.CharField(
        max_length=150,
        blank=True, null=True,
        verbose_name=_('Community Group Name')
    )
    number_initiatives = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of Initiatives')
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


class HealthVisit(TimeStampedModel):
    school = models.ForeignKey(
        'School',
        verbose_name=_('school'),
        related_name='+',
        on_delete=models.CASCADE,
    )
    focal_point_name = models.CharField(
        max_length=50,
        blank=True, null=True,
        verbose_name=_('Health Focal Point Name')
    )
    number_visits = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of Visits')
    )
    date_first_visit = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('Date of First Visit')
    )
    date_last_visit = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('Date of Last Visit')
    )
    summary = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Summary')
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


class EducationalLevel(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name


class Section(models.Model):
    name = models.CharField(max_length=45, unique=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name


class CLMRound(models.Model):

    name = models.CharField(max_length=45, unique=True)
    current_year = models.BooleanField(blank=True, default=False)
    current_round_bridging = models.BooleanField(blank=True, default=False)

    start_date_bridging = models.DateField(blank=True, null=True)
    end_date_bridging = models.DateField(blank=True, null=True)
    start_date_bridging_edit = models.DateField(blank=True, null=True)
    end_date_bridging_edit = models.DateField(blank=True, null=True)

    class Meta:
        ordering = ['name']
        verbose_name = "CLM Round"

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name


class PartnerOrganization(models.Model):

    name = models.CharField(max_length=100, unique=True)
    schools = models.ManyToManyField('School', related_name='partner_schools', blank=True)
    short_name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('Short Name')
    )
    monitoring_evaluation_focal_point_name = models.CharField(
        blank=True,
        null=True,
        max_length=100,
        verbose_name=_('Monitoring and Evaluation Focal Point Name')
    )
    monitoring_evaluation_focal_point_phone = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('Monitoring and Evaluation Focal Point Phone')
    )
    monitoring_evaluation_focal_point_email = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('Monitoring and Evaluation Focal Point Email')
    )
    program_manager_focal_point_name = models.CharField(
        blank=True,
        null=True,
        max_length=100,
        verbose_name=_('Program Manager Focal Point Name')
    )
    program_manager_focal_point_phone = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('Program Manager Focal Point Phone')
    )
    program_manager_focal_point_email = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('Program Manager Focal Point Email')
    )
    active = models.BooleanField(blank=True, default=False)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name


class Holiday(models.Model):
    name = models.CharField(max_length=100, unique=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name

