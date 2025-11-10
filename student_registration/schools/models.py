from __future__ import unicode_literals, absolute_import, division
from django.conf import settings
from django.db import models
from model_utils import Choices
from model_utils.models import TimeStampedModel
from django.utils.translation import gettext as _
from django.contrib.postgres.fields import ArrayField
from student_registration.staffs.models import Bank


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
    bank_Base1 = models.ForeignKey(
        Bank,
        blank=True, null=True,
        related_name='+',
        on_delete=models.SET_NULL,
        verbose_name=_('Bank'),
    )
    branch_base1 = models.CharField(
        max_length=60,
        blank=True,
        null=True,
        verbose_name=_('Branch')
    )
    iban_base1 = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('IBAN LL')
    )
    bank_Base2 = models.ForeignKey(
        Bank,
        blank=True, null=True,
        related_name='+',
        on_delete=models.SET_NULL,
        verbose_name=_('Bank'),
    )
    branch_base2 = models.CharField(
        max_length=60,
        blank=True,
        null=True,
        verbose_name=_('Branch')
    )
    iban_base2 = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('IBAN $')
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
    benefit_wfp_service = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Is the school benefiting from WFP services?')
    )
    wfp_service_type = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=WFP_SERVICE_TYPE,
        verbose_name=_('Service Type?')
    )
    is_unrwa = models.BooleanField(blank=True, default=False)

    class Meta:
        ordering = ['number']

    def attendances_2ndshift(self):
        qs = self.attendances.filter(
            education_year__current_year=True,
            school_type='2nd-shift'
        )
        if self.academic_year_start:
            qs = qs.filter(
                attendance_date__gte=self.academic_year_start
            )
        return qs

    def attendances_alp(self):
        return self.attendances.filter(
            alp_round__current_round=True,
            school_type='ALP'
        )

    @property
    def total_attendances_days_2ndshift(self):
        qs = self.attendances_2ndshift()
        return qs.count()

    @property
    def total_attendances_days_2ndshift_open(self):
        qs = self.attendances_2ndshift()
        return qs.exclude(close_reason__isnull=False).count()

    @property
    def total_attendances_days_alp(self):
        return self.attendances_alp().count()

    @property
    def total_attendances_days_alp_open(self):
        qs = self.attendances_alp()
        return qs.exclude(close_reason__isnull=False).count()

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
    def total_registered(self):
        from student_registration.enrollments.models import Enrollment
        return Enrollment.objects.filter(
            education_year__current_year=True, disabled=False,
            school_id=self.id
        ).count()

    @property
    def total_registered_bridging(self):
        from student_registration.clm.models import Bridging
        return Bridging.objects.all().count()

    @property
    def total_registered_2ndshift(self):
        from student_registration.enrollments.models import Enrollment
        return Enrollment.objects.filter(
            education_year__current_year=True, moved=False, dropout_status=False,
            school_id=self.id
        ).count()

    @property
    def total_registered_2ndshift_male(self):
        from student_registration.enrollments.models import Enrollment
        return Enrollment.objects.filter(
            education_year__current_year=True,
            school_id=self.id,
            student__sex='Male'
        ).count()

    @property
    def total_registered_2ndshift_female(self):
        from student_registration.enrollments.models import Enrollment
        return Enrollment.objects.filter(
            education_year__current_year=True,
            school_id=self.id,
            student__sex='Female'
        ).count()

    @property
    def total_registered_alp(self):
        from student_registration.alp.models import Outreach
        return Outreach.objects.filter(
            alp_round__current_round=True,
            registered_in_level__isnull=False,
            school_id=self.id
        ).count()

    @property
    def total_registered_alp_male(self):
        from student_registration.alp.models import Outreach
        return Outreach.objects.filter(
            alp_round__current_round=True,
            registered_in_level__isnull=False,
            school_id=self.id,
            student__sex='Male'
        ).count()

    @property
    def total_registered_alp_female(self):
        from student_registration.alp.models import Outreach
        return Outreach.objects.filter(
            alp_round__current_round=True,
            registered_in_level__isnull=False,
            school_id=self.id,
            student__sex='Female'
        ).count()

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


class EducationLevel(models.Model):
    name = models.CharField(max_length=45, unique=True)
    note = models.IntegerField(blank=True, null=True)
    with_math = models.BooleanField(blank=True, default=False)
    with_science = models.BooleanField(blank=True, default=False)
    with_arabic = models.BooleanField(blank=True, default=False)
    with_language = models.BooleanField(blank=True, default=False)
    coefficient_score = models.FloatField(blank=True, null=True)
    new_calculation = models.BooleanField(blank=True, default=False)

    @property
    def sum_subjects(self):
        sum_subject = 0
        if self.with_math:
            sum_subject += 1
        if self.with_science:
            sum_subject += 1
        if self.with_arabic:
            sum_subject += 1
        if self.with_language:
            sum_subject += 1
        return sum_subject

    class Meta:
        ordering = ['id']
        verbose_name = "ALP Level"

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name


class ClassLevel(models.Model):
    name = models.CharField(max_length=45, unique=True)

    class Meta:
        ordering = ['id']
        verbose_name = "ALP Result"

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


class ClassRoom(models.Model):
    name = models.CharField(max_length=45, unique=True)
    classroom_type = models.CharField(
        blank=True, null=True, max_length=2,
        choices=Choices(
            ('PV', _('Private School')),
            ('PU', _('Public School')),
        ),
    )

    class Meta:
        ordering = ['id']
        verbose_name = "Formal Education Level"

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name


class CLMRound(models.Model):

    name = models.CharField(max_length=45, unique=True)
    current_year = models.BooleanField(blank=True, default=False)
    current_year_inclusion = models.BooleanField(blank=True, default=False)

    current_round_bln = models.BooleanField(blank=True, default=False)
    current_round_abln = models.BooleanField(blank=True, default=False)
    current_round_cbece = models.BooleanField(blank=True, default=False)
    current_round_inclusion = models.BooleanField(blank=True, default=False)
    current_round_rs = models.BooleanField(blank=True, default=False)
    current_round_outreach = models.BooleanField(blank=True, default=False)
    current_round_bridging = models.BooleanField(blank=True, default=False)

    start_date_bln = models.DateField(blank=True, null=True)
    end_date_bln = models.DateField(blank=True, null=True)
    start_date_bln_edit = models.DateField(blank=True, null=True)
    end_date_bln_edit = models.DateField(blank=True, null=True)

    start_date_abln = models.DateField(blank=True, null=True)
    end_date_abln = models.DateField(blank=True, null=True)
    start_date_abln_edit = models.DateField(blank=True, null=True)
    end_date_abln_edit = models.DateField(blank=True, null=True)

    start_date_cbece = models.DateField(blank=True, null=True)
    end_date_cbece = models.DateField(blank=True, null=True)
    start_date_cbece_edit = models.DateField(blank=True, null=True)
    end_date_cbece_edit = models.DateField(blank=True, null=True)

    start_date_inclusion = models.DateField(blank=True, null=True)
    end_date_inclusion = models.DateField(blank=True, null=True)
    start_date_inclusion_edit = models.DateField(blank=True, null=True)
    end_date_inclusion_edit = models.DateField(blank=True, null=True)

    start_date_rs = models.DateField(blank=True, null=True)
    end_date_rs = models.DateField(blank=True, null=True)
    start_date_rs_edit = models.DateField(blank=True, null=True)
    end_date_rs_edit = models.DateField(blank=True, null=True)

    start_date_outreach = models.DateField(blank=True, null=True)
    end_date_outreach = models.DateField(blank=True, null=True)
    start_date_outreach_edit = models.DateField(blank=True, null=True)
    end_date_outreach_edit = models.DateField(blank=True, null=True)

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
    is_Kayany = models.BooleanField(blank=True, default=False)
    is_unrwa = models.BooleanField(blank=True, default=False)
    is_youth = models.BooleanField(blank=True, default=False)

    bln_round = models.ForeignKey(
        'CLMRound',
        blank=True, null=True,
        related_name='+',
        on_delete=models.SET_NULL,
        verbose_name=_('BLN current round')
    )
    rs_round = models.ForeignKey(
        'CLMRound',
        blank=True, null=True,
        related_name='+',
        on_delete=models.SET_NULL,
        verbose_name=_('RS current round')
    )
    cbece_round = models.ForeignKey(
        'CLMRound',
        blank=True, null=True,
        related_name='+',
        on_delete=models.SET_NULL,
        verbose_name=_('CB-ECE current round')
    )

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


class ALPReferMatrix(models.Model):
    level = models.ForeignKey(
        'EducationLevel',
        blank=True, null=True,
        related_name='+',
        on_delete=models.SET_NULL,
    )
    success_refer_to = models.ForeignKey(
        'ClassLevel',
        blank=True, null=True,
        on_delete=models.SET_NULL,
        related_name='success_refer_to',
    )
    fail_refer_to = models.ForeignKey(
        'ClassLevel',
        blank=True, null=True,
        on_delete=models.SET_NULL,
        related_name='fail_refer_to',
    )
    age = models.IntegerField(blank=True, null=True)
    success_grade = models.IntegerField(blank=True, null=True)

    class Meta:
        ordering = ['id']
        verbose_name = "ALP Post-test Refer Matrix"

    def __str__(self):
        return self.name

    def __unicode__(self):
        return str(self.id)


class EducationYear(models.Model):
    name = models.CharField(max_length=100, unique=True)
    current_year = models.BooleanField(blank=True, default=False)

    class Meta:
        ordering = ['name']
        verbose_name = "Education Year"

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name


class ALPAssignmentMatrix(models.Model):
    MATRIX_TYPE =(
        ('O', _('Old')),
        ('N', _('New')),
    )
    level = models.ForeignKey(
        'EducationLevel',
        blank=True, null=True,
        related_name='+',
        on_delete=models.SET_NULL,
    )
    refer_to = models.ForeignKey(
        'EducationLevel',
        blank=True, null=True,
        on_delete=models.SET_NULL,
        related_name='refer_to',
    )

    range_start = models.FloatField(blank=True, null=True)
    range_end = models.FloatField(blank=True, null=True)
    matrix_type = models.CharField(blank=True, null=True, max_length=1, choices=MATRIX_TYPE)

    @property
    def range(self):
        return "{}-{}".format(self.range_start, self.range_end)

    class Meta:
        ordering = ['id']
        verbose_name = "ALP Pre-test Refer Matrix"

    def __str__(self):
        return self.name

    def __unicode__(self):
        return str(self.id)


class EducationalLevel(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ['id']

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


class PublicDocument(TimeStampedModel):

    name = models.CharField(max_length=100)
    overview = models.TextField(blank=True, null=True)
    file_url = models.URLField(blank=True, null=True)

    class Meta:
        ordering = ['created']

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name


class Setup(models.Model):
    staff_seq = models.IntegerField(
        blank=True, null=True)


class class_section(TimeStampedModel):

    school = models.ForeignKey(
        'School',
        verbose_name=_('school'),
        related_name='+',
        on_delete=models.CASCADE,
    )
    classroom = models.ForeignKey(
        'ClassRoom',
        blank=True, null=True,
        verbose_name=_('class'),
        related_name='+',
        on_delete=models.SET_NULL,
    )
    section = models.ForeignKey(
        'Section',
        blank=True, null=True,
        verbose_name=_('section'),
        related_name='+',
        on_delete=models.SET_NULL,
    )
    closed_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('Closed Date')
    )
    is_closed = models.BooleanField(
        blank=True,
        default=False,
        verbose_name=_('is closed')
    )
    school_type = models.CharField(
        max_length=15,
        blank=True, null=True,
        verbose_name=_('school type')
    )
    education_year = models.ForeignKey(
        'EducationYear',
        blank=True, null=True,
        related_name='+',
        on_delete=models.SET_NULL,
        verbose_name=_('Education year')
    )


class Evaluation(TimeStampedModel):
    YES_NO = Choices(
        ('yes', _("Yes")),
        ('no', _("No")),
    )
    school = models.ForeignKey(
        'School',
        blank=False, null=True,
        related_name='+',
        on_delete=models.SET_NULL,
        verbose_name=_('School')
    )
    education_year = models.ForeignKey(
        'EducationYear',
        blank=True, null=True,
        related_name='+',
        on_delete=models.SET_NULL,
        verbose_name=_('Education year')
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=False, null=True,
        related_name='+',
        on_delete=models.SET_NULL,
        verbose_name=_('Created by')
    )
    total_teaching_days = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Teaching days completed since the beginning of the school year till the end of february'),
        default=0,
        choices=((x, x) for x in range(0, 365))
    )
    total_teaching_days_tillnow = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Teaching days from the beginning of march till now'),
        default=0,
        choices=((x, x) for x in range(0, 365))
    )

    implemented_de = models.CharField(
        blank=True,  default='no',
        max_length=3,
        choices=YES_NO,
        verbose_name=_('Have you implemented distance education ?')
    )
    reasons_no_de = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Determine the reasons')
    )
    challenges_de = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('The challenges that you faced during distance education')
    )
    steps_de = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('What are the steps followed in distance education')
    )
    evaluate_steps_de = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Evaluate the steps followed in distance education')
    )

    implemented_de_2 = models.CharField(
        blank=True,  default='no',
        max_length=3,
        choices=YES_NO,
        verbose_name=_('Have you implemented distance education ?')
    )
    reasons_no_de_2 = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Determine the reasons')
    )
    challenges_de_2 = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('The challenges that you faced during distance education')
    )
    steps_de_2 = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('What are the steps followed in distance education')
    )
    evaluate_steps_de_2 = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Evaluate the steps followed in distance education')
    )

    implemented_de_3 = models.CharField(
        blank=True,  default='no',
        max_length=3,
        choices=YES_NO,
        verbose_name=_('Have you implemented distance education ?')
    )
    reasons_no_de_3 = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Determine the reasons')
    )
    challenges_de_3 = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('The challenges that you faced during distance education')
    )
    steps_de_3 = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('What are the steps followed in distance education')
    )
    evaluate_steps_de_3 = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Evaluate the steps followed in distance education')
    )
    other_notes_de = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Comments')
    )

    c2_eng_completed = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('The number of lessons completed till february'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c2_eng_completed_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons accomplished through distance education in march'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c2_eng_remaining_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons remaining'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c2_fr_completed = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('The number of lessons completed till february'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c2_fr_completed_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons accomplished through distance education in march'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c2_fr_remaining_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons remaining'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c2_math_completed = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('The number of lessons completed till february'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c2_math_completed_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons accomplished through distance education in march'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c2_math_remaining_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons remaining'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c2_sc_completed = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('The number of lessons completed till february'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c2_sc_completed_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons accomplished through distance education in march'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c2_sc_remaining_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons remaining'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c2_ara_completed = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('The number of lessons completed till february'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c2_ara_completed_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons accomplished through distance education in march'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c2_ara_remaining_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons remaining'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c2_civic_completed = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('The number of lessons completed till february'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c2_civic_completed_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons accomplished through distance education in march'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c2_civic_remaining_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons remaining'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c2_geo_completed = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('The number of lessons completed till february'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c2_geo_completed_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons accomplished through distance education in march'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c2_geo_remaining_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons remaining'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )

    c3_eng_completed = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('The number of lessons completed till february'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c3_eng_completed_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons accomplished through distance education in march'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c3_eng_remaining_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons remaining'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c3_fr_completed = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('The number of lessons completed till february'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c3_fr_completed_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons accomplished through distance education in march'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c3_fr_remaining_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons remaining'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c3_math_completed = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('The number of lessons completed till february'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c3_math_completed_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons accomplished through distance education in march'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c3_math_remaining_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons remaining'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c3_sc_completed = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('The number of lessons completed till february'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c3_sc_completed_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons accomplished through distance education in march'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c3_sc_remaining_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons remaining'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c3_ara_completed = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('The number of lessons completed till february'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c3_ara_completed_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons accomplished through distance education in march'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c3_ara_remaining_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons remaining'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c3_civic_completed = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('The number of lessons completed till february'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c3_civic_completed_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons accomplished through distance education in march'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c3_civic_remaining_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons remaining'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c3_geo_completed = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('The number of lessons completed till february'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c3_geo_completed_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons accomplished through distance education in march'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c3_geo_remaining_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons remaining'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c4_eng_completed = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('The number of lessons completed till february'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c4_eng_completed_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons accomplished through distance education in march'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c4_eng_remaining_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons remaining'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c4_fr_completed = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('The number of lessons completed till february'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c4_fr_completed_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons accomplished through distance education in march'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c4_fr_remaining_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons remaining'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c4_math_completed = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('The number of lessons completed till february'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c4_math_completed_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons accomplished through distance education in march'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c4_math_remaining_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons remaining'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c4_sc_completed = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('The number of lessons completed till february'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c4_sc_completed_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons accomplished through distance education in march'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c4_sc_remaining_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons remaining'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c4_ara_completed = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('The number of lessons completed till february'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c4_ara_completed_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons accomplished through distance education in march'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c4_ara_remaining_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons remaining'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c4_civic_completed = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('The number of lessons completed till february'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c4_civic_completed_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons accomplished through distance education in march'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c4_civic_remaining_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons remaining'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c4_geo_completed = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('The number of lessons completed till february'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c4_geo_completed_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons accomplished through distance education in march'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c4_geo_remaining_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons remaining'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c5_eng_completed = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('The number of lessons completed till february'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c5_eng_completed_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons accomplished through distance education in march'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c5_eng_remaining_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons remaining'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c5_fr_completed = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('The number of lessons completed till february'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c5_fr_completed_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons accomplished through distance education in march'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c5_fr_remaining_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons remaining'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c5_math_completed = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('The number of lessons completed till february'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c5_math_completed_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons accomplished through distance education in march'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c5_math_remaining_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons remaining'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c5_sc_completed = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('The number of lessons completed till february'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c5_sc_completed_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons accomplished through distance education in march'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c5_sc_remaining_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons remaining'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c5_ara_completed = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('The number of lessons completed till february'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c5_ara_completed_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons accomplished through distance education in march'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c5_ara_remaining_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons remaining'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c5_civic_completed = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('The number of lessons completed till february'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c5_civic_completed_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons accomplished through distance education in march'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c5_civic_remaining_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons remaining'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c5_geo_completed = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('The number of lessons completed till february'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c5_geo_completed_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons accomplished through distance education in march'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c5_geo_remaining_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons remaining'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c1_eng_completed = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('The number of lessons completed till february'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c1_eng_completed_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons accomplished through distance education in march'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c1_eng_remaining_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons remaining'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c1_fr_completed = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('The number of lessons completed till february'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c1_fr_completed_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons accomplished through distance education in march'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c1_fr_remaining_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons remaining'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c1_math_completed = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('The number of lessons completed till february'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c1_math_completed_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons accomplished through distance education in march'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c1_math_remaining_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons remaining'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c1_sc_completed = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('The number of lessons completed till february'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c1_sc_completed_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons accomplished through distance education in march'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c1_sc_remaining_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons remaining'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c1_ara_completed = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('The number of lessons completed till february'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c1_ara_completed_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons accomplished through distance education in march'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c1_ara_remaining_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons remaining'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c1_civic_completed = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('The number of lessons completed till february'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c1_civic_completed_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons accomplished through distance education in march'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c1_civic_remaining_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons remaining'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c1_geo_completed = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('The number of lessons completed till february'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c1_geo_completed_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons accomplished through distance education in march'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c1_geo_remaining_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons remaining'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c6_eng_completed = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('The number of lessons completed till february'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c6_eng_completed_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons accomplished through distance education in march'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c6_eng_remaining_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons remaining'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c6_fr_completed = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('The number of lessons completed till february'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c6_fr_completed_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons accomplished through distance education in march'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c6_fr_remaining_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons remaining'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c6_math_completed = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('The number of lessons completed till february'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c6_math_completed_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons accomplished through distance education in march'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c6_math_remaining_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons remaining'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c6_sc_completed = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('The number of lessons completed till february'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c6_sc_completed_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons accomplished through distance education in march'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c6_sc_remaining_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons remaining'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c6_ara_completed = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('The number of lessons completed till february'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c6_ara_completed_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons accomplished through distance education in march'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c6_ara_remaining_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons remaining'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c6_civic_completed = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('The number of lessons completed till february'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c6_civic_completed_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons accomplished through distance education in march'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c6_civic_remaining_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons remaining'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c6_geo_completed = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('The number of lessons completed till february'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c6_geo_completed_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons accomplished through distance education in march'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c6_geo_remaining_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons remaining'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    cprep_eng_completed = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('The number of lessons completed till february'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    cprep_eng_completed_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons accomplished through distance education in march'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    cprep_eng_remaining_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons remaining'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    cprep_fr_completed = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('The number of lessons completed till february'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    cprep_fr_completed_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons accomplished through distance education in march'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    cprep_fr_remaining_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons remaining'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    cprep_math_completed = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('The number of lessons completed till february'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    cprep_math_completed_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons accomplished through distance education in march'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    cprep_math_remaining_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons remaining'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    cprep_sc_completed = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('The number of lessons completed till february'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    cprep_sc_completed_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons accomplished through distance education in march'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    cprep_sc_remaining_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons remaining'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    cprep_ara_completed = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('The number of lessons completed till february'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    cprep_ara_completed_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons accomplished through distance education in march'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    cprep_ara_remaining_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons remaining'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    cprep_civic_completed = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('The number of lessons completed till february'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    cprep_civic_completed_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons accomplished through distance education in march'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    cprep_civic_remaining_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons remaining'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    cprep_geo_completed = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('The number of lessons completed till february'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    cprep_geo_completed_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons accomplished through distance education in march'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    cprep_geo_remaining_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons remaining'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c7_eng_completed = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('The number of lessons completed till february'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c7_eng_completed_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons accomplished through distance education in march'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c7_eng_remaining_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons remaining'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c7_fr_completed = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('The number of lessons completed till february'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c7_fr_completed_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons accomplished through distance education in march'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c7_fr_remaining_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons remaining'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c7_math_completed = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('The number of lessons completed till february'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c7_math_completed_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons accomplished through distance education in march'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c7_math_remaining_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons remaining'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c7_sc_completed = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('The number of lessons completed till february'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c7_sc_completed_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons accomplished through distance education in march'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c7_sc_remaining_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons remaining'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c7_ara_completed = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('The number of lessons completed till february'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c7_ara_completed_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons accomplished through distance education in march'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c7_ara_remaining_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons remaining'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c7_civic_completed = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('The number of lessons completed till february'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c7_civic_completed_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons accomplished through distance education in march'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c7_civic_remaining_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons remaining'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c7_geo_completed = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('The number of lessons completed till february'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c7_geo_completed_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons accomplished through distance education in march'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c7_geo_remaining_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons remaining'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c7_his_completed = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('The number of lessons completed till february'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c7_his_completed_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons accomplished through distance education in march'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c7_his_remaining_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons remaining'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c7_phy_completed = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('The number of lessons completed till february'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c7_phy_completed_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons accomplished through distance education in march'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c7_phy_remaining_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons remaining'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c7_che_completed = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('The number of lessons completed till february'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c7_che_completed_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons accomplished through distance education in march'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c7_che_remaining_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons remaining'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c8_eng_completed = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('The number of lessons completed till february'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c8_eng_completed_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons accomplished through distance education in march'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c8_eng_remaining_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons remaining'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c8_fr_completed = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('The number of lessons completed till february'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c8_fr_completed_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons accomplished through distance education in march'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c8_fr_remaining_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons remaining'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c8_math_completed = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('The number of lessons completed till february'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c8_math_completed_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons accomplished through distance education in march'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c8_math_remaining_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons remaining'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c8_sc_completed = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('The number of lessons completed till february'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c8_sc_completed_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons accomplished through distance education in march'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c8_sc_remaining_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons remaining'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c8_ara_completed = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('The number of lessons completed till february'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c8_ara_completed_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons accomplished through distance education in march'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c8_ara_remaining_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons remaining'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c8_civic_completed = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('The number of lessons completed till february'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c8_civic_completed_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons accomplished through distance education in march'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c8_civic_remaining_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons remaining'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c8_geo_completed = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('The number of lessons completed till february'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c8_geo_completed_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons accomplished through distance education in march'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c8_geo_remaining_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons remaining'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c8_his_completed = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('The number of lessons completed till february'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c8_his_completed_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons accomplished through distance education in march'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c8_his_remaining_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons remaining'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c8_phy_completed = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('The number of lessons completed till february'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c8_phy_completed_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons accomplished through distance education in march'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c8_phy_remaining_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons remaining'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c8_che_completed = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('The number of lessons completed till february'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c8_che_completed_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons accomplished through distance education in march'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c8_che_remaining_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons remaining'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c9_eng_completed = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('The number of lessons completed till february'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c9_eng_completed_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons accomplished through distance education in march'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c9_eng_remaining_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons remaining'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c9_fr_completed = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('The number of lessons completed till february'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c9_fr_completed_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons accomplished through distance education in march'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c9_fr_remaining_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons remaining'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c9_math_completed = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('The number of lessons completed till february'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c9_math_completed_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons accomplished through distance education in march'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c9_math_remaining_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons remaining'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c9_sc_completed = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('The number of lessons completed till february'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c9_sc_completed_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons accomplished through distance education in march'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c9_sc_remaining_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons remaining'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c9_ara_completed = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('The number of lessons completed till february'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c9_ara_completed_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons accomplished through distance education in march'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c9_ara_remaining_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons remaining'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c9_civic_completed = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('The number of lessons completed till february'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c9_civic_completed_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons accomplished through distance education in march'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c9_civic_remaining_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons remaining'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c9_geo_completed = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('The number of lessons completed till february'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c9_geo_completed_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons accomplished through distance education in march'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c9_geo_remaining_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons remaining'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c9_his_completed = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('The number of lessons completed till february'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c9_his_completed_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons accomplished through distance education in march'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c9_his_remaining_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons remaining'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c9_phy_completed = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('The number of lessons completed till february'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c9_phy_completed_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons accomplished through distance education in march'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c9_phy_remaining_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons remaining'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c9_che_completed = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('The number of lessons completed till february'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c9_che_completed_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons accomplished through distance education in march'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c9_che_remaining_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of lessons remaining'),
        default=0,
        choices=((x, x) for x in range(0, 100))
    )
    c9_total_std = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Total of students'),
        default=0,
        choices=((x, x) for x in range(0, 50))
    )
    c9_total_std_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Total of students they follow distance education'),
        default=0,
        choices=((x, x) for x in range(0, 50))
    )

    implemented_de_9 = models.CharField(
        blank=True,  default='no',
        max_length=3,
        choices=YES_NO,
        verbose_name=_('Have you implemented distance education ?')
    )
    reasons_no_de_9 = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Determine the reasons')
    )
    challenges_de_9 = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('The challenges that you faced during distance education')
    )
    steps_de_9 = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('What are the steps followed in distance education')
    )
    evaluate_steps_de_9 = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Evaluate the steps followed in distance education')
    )

    implemented_de_prep = models.CharField(
        blank=True,  default='no',
        max_length=3,
        choices=YES_NO,
        verbose_name=_('Have you implemented distance education ?')
    )
    reasons_no_de_prep = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Determine the reasons')
    )
    challenges_de_prep = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('The challenges that you faced during distance education')
    )
    steps_de_prep = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('What are the steps followed in distance education')
    )
    evaluate_steps_de_prep = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Evaluate the steps followed in distance education')
    )

    c9_total_teachers = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Total of teachers'),
        default=0,
        choices=((x, x) for x in range(0, 50))
    )
    c9_total_teachers_de = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of teachers who have committed to distance education'),
        default=0,
        choices=((x, x) for x in range(0, 50))
    )

    def __str__(self):
        return self.name

    def __unicode__(self):
            return self.school.name


class Schl_Subject(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=_('Subject')
    )

    class Meta:
        verbose_name_plural = "Subjects"

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name


class Schl_Survey(TimeStampedModel):
    school = models.ForeignKey(
        School,
        blank=True, null=True,
        verbose_name=_('School'),
        related_name='+',
        on_delete=models.SET_NULL,
    )
    classroom = models.ForeignKey(
        ClassRoom,
        blank=True, null=True,
        verbose_name=_('Class'),
        related_name='+',
        on_delete=models.SET_NULL,
    )
    schl_subject = models.ForeignKey(
        Schl_Subject,
        blank=True, null=True,
        verbose_name=_('Course'),
        related_name='+',
        on_delete=models.SET_NULL,
    )
    teachingdays_tillfeb = models.IntegerField(
        blank=True, null=True,
    )
    teachingdays_frommars = models.IntegerField(
        blank=True, null=True,
    )
    teachingdays_remaining = models.IntegerField(
        blank=True, null=True,
    )


class Schl_Survey_Class(TimeStampedModel):
    school = models.ForeignKey(
        School,
        blank=True, null=True,
        verbose_name=_('School'),
        related_name='+',
        on_delete=models.SET_NULL,
    )
    classroom = models.ForeignKey(
        ClassRoom,
        blank=True, null=True,
        verbose_name=_('Class'),
        related_name='+',
        on_delete=models.SET_NULL,
    )
    de_implemented = models.BooleanField(
        blank=True,
        default=False,
        verbose_name=_('Distance education implemented ?')
    )
    de_usedmethod_1 = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('The methods used during the distance education plan')
    )
    de_challenge_1 = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('The challenges during the distance education plan')
    )
    de_negativenotes_1 = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('The negative notes ')
    )
    de_positivenotes_1 = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('The negative notes ')
    )
    de_interactedstudents_1 = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('The number of interacted students  ')
    )

    de_usedmethod_2 = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('The methods used during the distance education plan')
    )
    de_challenge_2 = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('The challenges during the distance education plan')
    )
    de_negativenotes_2 = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('The negative notes ')
    )
    de_positivenotes_2 = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('The negative notes ')
    )
    de_interactedstudents_2 = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('The number of interacted students  ')
    )

    de_usedmethod_3 = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('The methods used during the distance education plan')
    )
    de_challenge_3 = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('The challenges during the distance education plan')
    )
    de_negativenotes_3 = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('The negative notes ')
    )
    de_positivenotes_3 = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('The negative notes ')
    )
    de_interactedstudents_3 = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('The number of interacted students  ')
    )

    de_usedmethod_4 = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('The methods used during the distance education plan')
    )
    de_challenge_4 = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('The challenges during the distance education plan')
    )
    de_negativenotes_4 = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('The negative notes ')
    )
    de_positivenotes_4 = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('The negative notes ')
    )
    de_interactedstudents_4 = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('The number of interacted students  ')
    )

    de_usedmethod_5 = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('The methods used during the distance education plan')
    )
    de_challenge_5 = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('The challenges during the distance education plan')
    )
    de_negativenotes_5 = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('The negative notes ')
    )
    de_positivenotes_5 = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('The negative notes ')
    )
    de_interactedstudents_5 = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('The number of interacted students  ')
    )

    de_usedmethod_6 = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('The methods used during the distance education plan')
    )
    de_challenge_6 = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('The challenges during the distance education plan')
    )
    de_negativenotes_6 = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('The negative notes ')
    )
    de_positivenotes_6 = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('The negative notes ')
    )
    de_interactedstudents_6 = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('The number of interacted students  ')
    )

    de_usedmethod_7 = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('The methods used during the distance education plan')
    )
    de_challenge_7 = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('The challenges during the distance education plan')
    )
    de_negativenotes_7 = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('The negative notes ')
    )
    de_positivenotes_7 = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('The negative notes ')
    )
    de_interactedstudents_7 = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('The number of interacted students  ')
    )

    de_usedmethod_8 = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('The methods used during the distance education plan')
    )
    de_challenge_8 = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('The challenges during the distance education plan')
    )
    de_negativenotes_8 = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('The negative notes ')
    )
    de_positivenotes_8 = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('The negative notes ')
    )
    de_interactedstudents_8 = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('The number of interacted students  ')
    )
    nbstudents = models.IntegerField(
        blank=True, null=True,
    )

    de_nbstudents = models.IntegerField(
        blank=True, null=True,
    )
    nbteachers = models.IntegerField(
        blank=True, null=True,
    )
    de_nbteachers = models.IntegerField(
        blank=True, null=True,
    )
