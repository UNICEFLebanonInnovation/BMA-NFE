# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, division
import datetime

from django.db import models
from django.conf import settings
from django.utils.translation import gettext as _
from django.db.models import JSONField
from django.contrib.postgres.fields import ArrayField

from model_utils import Choices
from model_utils.models import TimeStampedModel

from student_registration.students.models import Student, Labour, Nationality
from student_registration.locations.models import Location
from student_registration.schools.models import (
    School,
    Section,
    ClassRoom,
    CLMRound,
    EducationalLevel,
    PartnerOrganization
)


class Assessment(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    overview = models.TextField(blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    capacity = models.IntegerField(blank=True, null=True)
    assessment_form = models.URLField(blank=True, null=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name


class Cycle(models.Model):
    name = models.CharField(max_length=100)
    current_cycle = models.BooleanField(blank=True, default=False)

    class Meta:
        ordering = ['name']
        verbose_name = "Program cycle"
        verbose_name_plural = "Program cycles"

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name


class RSCycle(models.Model):
    name = models.CharField(max_length=100)
    current_cycle = models.BooleanField(blank=True, default=False)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name


class Site(models.Model):
    name = models.CharField(max_length=100)
    current_cycle = models.BooleanField(blank=True, default=False)

    class Meta:
        ordering = ['name']
        verbose_name = "Program site"
        verbose_name_plural = "Program sites"

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name


class Referral(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        ordering = ['name']
        verbose_name = "Referral"
        verbose_name_plural = "Referrals"

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name


class Disability(models.Model):
    name = models.CharField(max_length=100)
    name_en = models.CharField(max_length=145, blank=True, null=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']
        verbose_name = "Disability"
        verbose_name_plural = "Disabilities"

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name


class Center(models.Model):
    name = models.CharField(max_length=100)

    partner = models.ForeignKey(
        PartnerOrganization,
        blank=True, null=True,
        verbose_name=_('Partner'),
        related_name='+',
        on_delete=models.SET_NULL,
    )

    class Meta:
        ordering = ['name']
        verbose_name = "Site / Center"
        verbose_name_plural = "Sites / Centers"

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name


class CLM(TimeStampedModel):
    CURRENT_YEAR = datetime.datetime.now().year

    MONTHS = Choices(
        ('1', _('January')),
        ('2', _('February')),
        ('3', _('March')),
        ('4', _('April')),
        ('5', _('May')),
        ('6', _('June')),
        ('7', _('July')),
        ('8', _('August')),
        ('9', _('September')),
        ('10', _('October')),
        ('11', _('November')),
        ('12', _('December')),
    )
    LANGUAGES = Choices(
        ('arabic', _('Arabic')),
        ('english_arabic', _('English/Arabic')),
        ('french_arabic', _('French/Arabic'))
    )
    STATUS = Choices(
        'enrolled',
        'pre_test',
        'post_test'
    )
    YES_NO = Choices(
        ('', '----------'),
        ('yes', _("Yes")),
        ('no', _("No")),
    )
    YES_NO_SOMETIMES = Choices(
        ('yes', _("Yes")),
        ('no', _("No")),
        ('sometimes', _("Sometimes"))
    )
    WITH_WHO = Choices(
        ('', '----------'),
        ('child', _('Child')),
        ('caregiver', _('Caregiver')),
        ('child_and_caregiver', _('Child and caregiver'))
    )
    HOW_OFTEN = Choices(
        ('', '----------'),
        ('daily', _('Daily')),
        ('every_2_to_3_days', _('Every 2-3 days')),
        ('weekly', _('Weekly')),
        ('biweekly', _('Biweekly')),
        ('monthly', _('Monthly'))
    )
    PERCENT = Choices(
        ('hundred', _("100%")),
        ('seventy_five', _("75%")),
        ('fifty', _("50%")),
        ('twenty_five', _("25%")),
        ('less_than_twenty_five', _("Less than 25%")),
    )
    REFERRAL = Choices(
        ('from_same_ngo', _('Referral from the same NGO')),
        ('from_other_ngo', _('Referral from an other NGO')),
        ('form_official_reference',
         _('Referral from an official reference (Mukhtar, Municipality, School Director, etc.)')),
        ('from_host_community', _('Referral from the host community')),
        ('from_displaced_community', _('Referral from the displaced community')),
    )
    PARTICIPATION = Choices(
        ('', '----------'),
        ('no_absence', _('No Absence')),
        ('less_than_5days', _('Less than 5 absence days')),
        ('5_10_days', _('5 to 10 absence days')),
        ('10_15_days', _('10 to 15 absence days')),
        ('15_25_days', _('15 to 25 absence days')),
        ('more_than_25days', _('More than 25 absence days')),
    )
    BARRIERS = Choices(
        ('', '----------'),
        ('Full time job to support family financially', _('Full time job to support family financially')),
        ('seasonal_work', _('Seasonal work')),
        # ('cold_weather', _('Cold Weather')),
        # ('transportation', _('Transportation')),
        ('availablity_electronic_device', _('Availablity of Electronic Device')),
        ('internet_connectivity', _('Internet Connectivity')),
        ('sickness', _('Sickness')),
        ('security', _('Security')),
        ('family_moved', _('Family moved')),
        ('Moved back to Syria', _('Moved back to Syria')),
        ('Enrolled in formal education', _('Enrolled in formal education')),
        ('marriage engagement pregnancy', _('Marriage/Engagement/Pregnancy')),
        ('violence bullying', _('Violence/Bullying')),
        ('No interest in pursuing the programme/No value', _('No interest in pursuing the programme/No value')),
        # ('no_barriers', _('No barriers')),
        ('other', _('Other')),
    )
    HAVE_LABOUR = Choices(
        ('no', _('No')),
        ('Yes - Morning', _('Yes - Morning')),
        ('Yes - Afternoon', _('Yes - Afternoon')),
        ('Yes - All day', _('Yes - All day')),
    )
    LABOURS = Choices(
        ('', '----------'),
        ('agriculture', _('Agriculture')),
        ('building', _('Building')),
        ('manufacturing', _('Manufacturing')),
        ('retail_store', _('Retail / Store')),
        ('begging', _('Begging')),
        ('other_many_other', _('Other services')),
        # ('other', _('Other')),
    )
    LEARNING_RESULT = Choices(
        ('', _('Learning result')),
        ('graduated_next_level', _('Graduated to the next level')),
        ('graduated_next_round_same_level', _('Graduated to the next round, same level')),
        ('graduated_next_round_higher_level', _('Graduated to the next round, higher level')),
        ('graduated_to_formal_kg', _('Graduated to formal education - KG')),
        ('graduated_to_formal_level1', _('Graduated to formal education - Level 1')),
        ('referred_to_another_program', _('Referred to another program')),
        ('other', _('Other')),
        ('Referral to School Bridging Programme', _('Referral to School Bridging Programme')),
        # ('dropout', _('Dropout from school'))
    )
    REGISTRATION_LEVEL = (
        ('', '----------'),
        ('level_one', _('Level one')),
        ('level_two', _('Level two')),
        ('level_three', _('Level three')),
        ('level_four', _('Level four'))
    )

    MODALITY = Choices(
        # ('', '----------'),
        ('online', _("Online Forms")),
        ('phone', _("Phone / Whatasapp")),
        ('parents', _("Asking Parents")),
        ('offline', _("Offline(F2F)"))
    )

    SESSION_MODALITY = Choices(
        # ('', '----------'),
        ('online', _("Online via Whatsapp")),
        ('phone', _("Phone calls")),
        ('offline', _("Offline(F2F)"))
    )
    AKELIUS = Choices(
        ('child using Akelius in Center', _("child using Akelius in Center")),
        ('child using Akelius at Home', _("child using Akelius at Home")),
        ('Child is not using Akelius at all', _("Child is not using Akelius at all"))
    )
    first_attendance_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('First attendance date')
    )
    round = models.ForeignKey(
        CLMRound,
        blank=True, null=True,
        related_name='+',
        on_delete=models.SET_NULL,
        verbose_name=_('Round')
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
    location = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Location')
    )
    center = models.ForeignKey(
        Center,
        blank=True, null=True,
        related_name='+',
        on_delete=models.SET_NULL,
        verbose_name=_('Site / Center')
    )

    language = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=LANGUAGES,
        verbose_name=_('The language supported in the program')
    )
    student = models.ForeignKey(
        Student,
        blank=False, null=True,
        related_name='+',
        on_delete=models.SET_NULL,
        verbose_name=_('Student')
    )
    disability = models.ForeignKey(
        Disability,
        blank=True, null=True,
        related_name='+',
        on_delete=models.SET_NULL,
        verbose_name=_('Disability')
    )
    have_labour = ArrayField(
        models.CharField(
            choices=HAVE_LABOUR,
            max_length=50,
            blank=True,
            null=True,
        ),
        blank=True,
        null=True,
        verbose_name=_('Does the child participate in work?')
    )
    have_labour_single_selection = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=HAVE_LABOUR,
        verbose_name=_('Does the child participate in work?')
    )
    labour_weekly_income = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=Student.STUDENT_INCOME,
        verbose_name=_('What is the income of the child per week?')
    )
    labours = ArrayField(
        models.CharField(
            choices=LABOURS,
            max_length=50,
            blank=True,
            null=True,
        ),
        blank=True,
        null=True,
        verbose_name=_('What is the type of work ?')
    )
    labours_single_selection = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=LABOURS,
        verbose_name=_('What is the type of work ?')
    )
    labours_other_specify = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_(
            'Please specify(hotel, restaurant, transport, personal services such as cleaning, hair care, cooking and childcare)')
    )
    labour_hours = models.IntegerField(
        blank=True,
        null=True,
        verbose_name=_('How many hours does this child work in a day?')
    )
    hh_educational_level = models.ForeignKey(
        EducationalLevel,
        blank=True, null=True,
        related_name='+',
        on_delete=models.SET_NULL,
        verbose_name=_('What is the educational level of the mother?')
    )

    father_educational_level = models.ForeignKey(
        EducationalLevel,
        blank=True, null=True,
        related_name='+',
        on_delete=models.SET_NULL,
        verbose_name=_('What is the educational level of the father?')
    )

    status = models.CharField(max_length=50, choices=STATUS, default=STATUS.enrolled)
    pre_test = JSONField(default=dict)
    pre_test_score = models.CharField(
        max_length=45,
        blank=True,
        null=True,
        verbose_name=_('Pre-assessment')
    )
    post_test = JSONField(default=dict)
    post_test_score = models.CharField(
        max_length=45,
        blank=True,
        null=True,
        verbose_name=_('Post-assessment')
    )
    scores = JSONField(default=dict)

    participation = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=PARTICIPATION,
        verbose_name=_('Participation')
    )
    barriers = ArrayField(
        models.CharField(
            choices=BARRIERS,
            max_length=100,
            blank=True,
            null=True,
        ),
        blank=True,
        null=True,
        verbose_name=_('Barriers')
    )
    learning_result = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=LEARNING_RESULT,
        verbose_name=_('Learning result')
    )
    barriers_single = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=BARRIERS,
        verbose_name=_('The main barriers affecting the daily attendance and performance')
    )
    barriers_other = models.TextField(
        blank=True, null=True,
        verbose_name=_('Please specify')
    )

    test_done = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=(('yes', _("Yes")), ('no', _("No"))),
        verbose_name=_('test_done')
    )
    round_complete = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=(('yes', _("Yes")), ('no', _("No"))),
        verbose_name=_('Round complete')
    )
    follow_up_type = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=(
            ('none', _('----------')),
            ('Phone', _('Phone Call')),
            ('House visit', _('House Visit')),
            ('Family Visit', _('Family Visit')),
        ),
        verbose_name=_('Type of follow up')
    )

    phone_call_number = models.IntegerField(
        blank=True,
        null=True,
        verbose_name=_('Please enter the number phone calls')
    )
    house_visit_number = models.IntegerField(
        blank=True,
        null=True,
        verbose_name=_('Please enter the number of house visits')
    )
    family_visit_number = models.IntegerField(
        blank=True,
        null=True,
        verbose_name=_('Please enter the number parent visits')
    )
    phone_call_follow_up_result = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=(
            ('child back', _('Phone Call')),
            ('child transfer to difficulty center', _('Child transfer to difficulty center')),
            ('child transfer to protection', _('Child transfer to protection')),
            ('child transfer to medical', _('Child transfer to medical')),
            ('Intensive followup', _('Intensive followup')),
            ('dropout', _('Dropout')),
        ),
        verbose_name=_('Result of follow up')
    )
    house_visit_follow_up_result = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=(
            ('child back', _('Phone Call')),
            ('child transfer to difficulty center', _('Child transfer to difficulty center')),
            ('child transfer to protection', _('Child transfer to protection')),
            ('child transfer to medical', _('Child transfer to medical')),
            ('Intensive followup', _('Intensive followup')),
            ('dropout', _('Dropout')),
        ),
        verbose_name=_('Result of follow up')
    )
    family_visit_follow_up_result = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=(
            ('child back', _('Phone Call')),
            ('child transfer to difficulty center', _('Child transfer to difficulty center')),
            ('child transfer to protection', _('Child transfer to protection')),
            ('child transfer to medical', _('Child transfer to medical')),
            ('Intensive followup', _('Intensive followup')),
            ('dropout', _('Dropout')),
        ),
        verbose_name=_('Result of follow up')
    )
    cp_referral = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=(('', '----------'), ('yes', _("Yes")), ('no', _("No"))),
        verbose_name=_('CP Followup')
    )
    parent_attended_visits = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=(('yes', _("Yes")), ('no', _("No"))),
        verbose_name=_('Parents attended parents meeting')
    )
    pss_session_attended = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=(('yes', _("Yes")), ('no', _("No"))),
        verbose_name=_('Attended PSS Session')
    )
    pss_session_number = models.IntegerField(
        blank=True,
        null=True,
        verbose_name=_('PSS session number')
    )
    pss_session_modality = ArrayField(
        models.CharField(
            choices=SESSION_MODALITY,
            max_length=200,
            blank=True,
            null=True,
        ),
        blank=True,
        null=True,
        verbose_name=_('Please the modality used per each session')
    )
    pss_parent_attended = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=(
            ('', '----------'),
            ('mother', _('Mother')),
            ('father', _('Father')),
            ('other', _('Other')),
        ),
        verbose_name=_('Parents attended parents meeting')
    )
    pss_parent_attended_other = models.TextField(
        blank=True, null=True,
        verbose_name=_('Please specify')
    )
    covid_session_attended = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=(('yes', _("Yes")), ('no', _("No"))),
        verbose_name=_('Attended PSS Session')
    )
    covid_session_number = models.IntegerField(
        blank=True,
        null=True,
        verbose_name=_('PSS session number')
    )

    covid_session_modality = ArrayField(
        models.CharField(
            choices=SESSION_MODALITY,
            max_length=200,
            blank=True,
            null=True,
        ),
        blank=True,
        null=True,
        verbose_name=_('Please the modality used per each session')
    )
    covid_parent_attended = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=(
            ('', '----------'),
            ('mother', _('Mother')),
            ('father', _('Father')),
            ('other', _('Other')),
        ),
        verbose_name=_('Parents attended parents meeting')
    )
    covid_parent_attended_other = models.TextField(
        blank=True, null=True,
        verbose_name=_('Please specify')
    )

    followup_session_attended = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=(('yes', _("Yes")), ('no', _("No"))),
        verbose_name=_('Attended PSS Session')
    )
    followup_session_number = models.IntegerField(
        blank=True,
        null=True,
        verbose_name=_('PSS session number')
    )

    followup_session_modality = ArrayField(
        models.CharField(
            choices=SESSION_MODALITY,
            max_length=200,
            blank=True,
            null=True,
        ),
        blank=True,
        null=True,
        verbose_name=_('Please the modality used per each session')
    )
    followup_parent_attended = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=(
            ('', '----------'),
            ('mother', _('Mother')),
            ('father', _('Father')),
            ('other', _('Other')),
        ),
        verbose_name=_('Parents attended parents meeting')
    )
    followup_parent_attended_other = models.TextField(
        blank=True, null=True,
        verbose_name=_('Please specify')
    )
    # parent_attended = models.CharField(
    #     max_length=100,
    #     blank=True,
    #     null=True,
    #     choices=(
    #         ('', '----------'),
    #         ('mother', _('Mother')),
    #         ('father', _('Father')),
    #         ('other', _('Other')),
    #     ),
    #     verbose_name=_('Parents attended parents meeting')
    # )
    #
    # parent_attended_other = models.TextField(
    #     blank=True, null=True,
    #     verbose_name=_('Please specify')
    # )
    visits_number = models.IntegerField(
        blank=True,
        null=True,
        verbose_name=_('Please enter the number parent visits')
    )
    child_health_examed = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=(('yes', _("Yes")), ('no', _("No"))),
        verbose_name=_('"Did the child receive health exam')
    )
    child_health_concern = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=(('yes', _("Yes")), ('no', _("No"))),
        verbose_name=_('Anything to worry about')
    )
    registration_level = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=REGISTRATION_LEVEL,
        verbose_name=_('Learning result')
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
    dropout_status = models.BooleanField(blank=True, default=False)
    moved = models.BooleanField(blank=True, default=False)
    outreach_barcode = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Outreach barcode')
    )
    new_registry = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=Choices(('yes', _("Yes")), ('no', _("No"))),
        verbose_name=_('First time registered?')
    )
    student_outreached = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=Choices(('yes', _("Yes")), ('no', _("No"))),
        verbose_name=_('Student outreached?')
    )
    have_barcode = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=Choices(('yes', _("Yes")), ('no', _("No"))),
        verbose_name=_('Have barcode with him?')
    )
    registration_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('Registration date')
    )
    partner = models.ForeignKey(
        PartnerOrganization,
        blank=True, null=True,
        verbose_name=_('Partner'),
        related_name='+',
        on_delete=models.SET_NULL,
    )
    internal_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Internal number')
    )
    comments = models.TextField(
        blank=True, null=True,
        verbose_name=_('Comments')
    )
    unsuccessful_pretest_reason = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=Choices(
            ('disability', _('Disability')),
            ('enrolled and did not do the pre-test', _("Enrolled and did not do the pre-test")),
            ('enrolled in formal', _("Enrolled in formal education")),
        ),
        verbose_name=_('unsuccessful pre test reason')
    )
    unsuccessful_posttest_reason = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=Choices(
            ('disability', _('Disability')),
            ('dropout', _("Dropout from the round")),
            ('uncompleted_participation', _("Uncompleted Participation"))
        ),
        verbose_name=_('unsuccessful post test reason')
    )

    phone_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Phone number')
    )
    phone_number_confirm = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Phone number confirm')
    )
    education_status = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=Choices(
            ('out of school', _('Out of school')),
            ('enrolled in formal education but did not continue',
             _("Enrolled in formal education but did not continue")),
            ('enrolled in ABLN', _("Enrolled in ABLN")),
            ('enrolled in BLN', _("Enrolled in BLN")),
        ),
        verbose_name=_('Education status')
    )

    id_type = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=Choices(
            ('UNHCR Registered', _('UNHCR Registered')),
            ('UNHCR Recorded', _("UNHCR Recorded")),
            ('Syrian national ID', _("Syrian national ID")),
            ('Palestinian national ID', _("Palestinian national ID")),
            ('Lebanese national ID', _("Lebanese national ID")),
            ('Lebanese Extract of Record', _("Lebanese Extract of Record")),
            ('Other nationality', _("Other nationality")),
            ('Child have no ID', _("Child have no ID"))
        ),
        verbose_name=_('Child ID type')
    )

    case_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Case number')
    )
    case_number_confirm = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Case number confirm')
    )

    individual_case_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Individual Case number')
    )
    individual_case_number_confirm = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Individual Case number confirm')
    )

    recorded_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Recorded number')
    )
    recorded_number_confirm = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Recorded number confirm')
    )

    other_nationality = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name=_('Specify the nationality')
    )
    national_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Lebanese ID number ')
    )
    national_number_confirm = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Lebanese ID number confirm')
    )
    parent_extract_record = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Parent Lebanese Extract of Record')
    )
    parent_extract_record_confirm = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Parent Lebanese Extract of Record confirm')
    )

    individual_extract_record = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Lebanese Extract of Record of the child')
    )
    individual_extract_record_confirm = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Confirm Lebanese Extract of Record of the child')
    )
    syrian_national_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Syrian ID number ')
    )
    syrian_national_number_confirm = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Syrian ID number confirm')
    )
    sop_national_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Palestinian ID number ')
    )
    sop_national_number_confirm = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Palestinian ID number confirm')
    )

    source_of_identification = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=Choices(
            ('Direct outreach', _('Direct outreach')),
            ('List database', _('List database')),
            ('Referral from another NGO', _('Referral from another NGO')),
            ('Referred by CP partner', _('Referred by CP partner')),
            ('Referred by youth partner', _('Referred by youth partner')),
            ('Referral from another Municipality', _('Referral from Municipality')),
            ('Family walked in to NGO', _('Family walked in to NGO')),
            ('RIMS', _('RIMS')),
            ('Referral to School Briding Programme', _('Referral to School Briding Programme')),
            ('Other Sources', _('Other Sources')),
        ),
        verbose_name=_('Source of identification of the child')
    )
    source_of_identification_specify = models.TextField(
        blank=True, null=True,
        verbose_name=_('Please specify')
    )
    rims_case_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('RIMS Case Number')
    )
    source_of_transportation = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=Choices(
            ('Transportation provided by partner', _('Transportation provided by partner')),
            ('Walk', _('Walk')),
            ('private or parents', _('Private/Parents'))
        ),
        verbose_name=_('Source of transportation of the child')
    )

    no_child_id_confirmation = models.CharField(max_length=50, blank=True, null=True, )
    no_parent_id_confirmation = models.CharField(max_length=50, blank=True, null=True, )

    parent_id_type = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=Choices(
            ('UNHCR Registered', _('UNHCR Registered')),
            ('UNHCR Recorded', _("UNHCR Recorded")),
            ('Syrian national ID', _("Syrian national ID")),
            ('Palestinian national ID', _("Palestinian national ID")),
            ('Lebanese national ID', _("Lebanese national ID")),
            ('Parent have no ID', _("Parent have no ID"))
        ),
        verbose_name=_('Parent ID type')
    )

    parent_case_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Case number')
    )
    parent_case_number_confirm = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Case number confirm')
    )

    parent_individual_case_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Individual Case number')
    )
    parent_individual_case_number_confirm = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Individual Case number confirm')
    )

    parent_national_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Lebanese ID number ')
    )
    parent_national_number_confirm = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Lebanese ID number confirm')
    )
    parent_syrian_national_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Syrian ID number ')
    )
    parent_syrian_national_number_confirm = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Syrian ID number confirm')
    )
    parent_sop_national_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Palestinian ID number ')
    )
    parent_sop_national_number_confirm = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Palestinian ID number confirm')
    )
    parent_other_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('ID number ')
    )
    parent_other_number_confirm = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('ID number confirm')
    )
    other_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Child ID number ')
    )
    other_number_confirm = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Child ID number confirm')
    )
    referral_programme_type_1 = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=Choices(
            ('CP (PSS and/or Case Management)', _('CP (PSS and/or Case Management)')),
            ('Health', _('Health')),
            ('WASH', _('WASH')),
            ('Specialized Services', _('Specialized Services')),
            # ('ALP', _('ALP')),
            # ('BLN', _('BLN')),
            # ('Youth', _('Youth')),
            ('Other', _('Other')),
            ('No need', _('No need')),
        ),
        verbose_name=_('Programme Type')
    )
    referral_partner_1 = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name=_('School / Center')
    )
    referral_date_1 = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('Referral date')
    )
    confirmation_date_1 = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('Date when the receiving organization confirms accepting the child (or child receiving service)')
    )

    referral_programme_type_2 = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=Choices(
            ('CP (PSS and/or Case Management)', _('CP (PSS and/or Case Management)')),
            ('Health', _('Health')),
            ('WASH', _('WASH')),
            ('Specialized Services', _('Specialized Services')),
            # ('ALP', _('ALP')),
            # ('BLN', _('BLN')),
            # ('Youth', _('Youth')),
            ('Other', _('Other')),
            ('No need', _('No need')),
        ),
        verbose_name=_('Programme Type')
    )
    referral_partner_2 = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name=_('School / Center')
    )
    referral_date_2 = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('Referral date')
    )
    confirmation_date_2 = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('Date when the receiving organization confirms accepting the child (or child receiving service)')
    )

    referral_programme_type_3 = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=Choices(
            ('CP (PSS and/or Case Management)', _('CP (PSS and/or Case Management)')),
            ('Health', _('Health')),
            ('WASH', _('WASH')),
            ('Specialized Services', _('Specialized Services')),
            # ('ALP', _('ALP')),
            # ('BLN', _('BLN')),
            # ('Youth', _('Youth')),
            ('Other', _('Other')),
            ('No need', _('No need')),
        ),
        verbose_name=_('Programme Type')
    )
    referral_partner_3 = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name=_('School / Center')
    )
    referral_date_3 = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('Referral date')
    )
    confirmation_date_3 = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('Date when the receiving organization confirms accepting the child (or child receiving service)')
    )

    followup_call_reason_1 = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Reason')
    )
    followup_call_result_1 = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Results')
    )
    followup_call_date_1 = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('Call date')
    )

    followup_call_reason_2 = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Reason')
    )
    followup_call_result_2 = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Results')
    )
    followup_call_date_2 = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('Call date')
    )

    followup_visit_reason_1 = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Reason')
    )
    followup_visit_result_1 = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Results')
    )
    followup_visit_date_1 = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('Visit date')
    )

    caretaker_first_name = models.CharField(
        max_length=500,
        blank=False,
        null=True,
        verbose_name=_('Caregiver First Name')
    )
    caretaker_middle_name = models.CharField(
        max_length=500,
        blank=False,
        null=True,
        verbose_name=_('Caregiver Middle Name')
    )
    caretaker_last_name = models.CharField(
        max_length=500,
        blank=False,
        null=True,
        verbose_name=_('Caregiver Last Name')
    )
    caretaker_mother_name = models.CharField(
        max_length=500,
        blank=False,
        null=True,
        verbose_name=_('Caregiver Mother Name')
    )
    caretaker_birthday_year = models.CharField(
        max_length=4,
        blank=True,
        null=True,
        default=0,
        choices=((str(x), x) for x in range(1940, CURRENT_YEAR - 18)),
        verbose_name=_('Caregiver birthday year')
    )
    caretaker_birthday_month = models.CharField(
        max_length=2,
        blank=True,
        null=True,
        default=0,
        choices=MONTHS,
        verbose_name=_('Caregiver birthday month')
    )
    caretaker_birthday_day = models.CharField(
        max_length=2,
        blank=True,
        null=True,
        default=0,
        choices=((str(x), x) for x in range(1, 32)),
        verbose_name=_('Caregiver birthday day')
    )

    cycle_completed = models.BooleanField(blank=True, default=False, verbose_name=_('Course completed successfully'))
    enrolled_at_school = models.BooleanField(blank=True, default=False, verbose_name=_('Enrolled at School'))

    basic_stationery = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Did the child receive basic stationery?')
    )
    pss_kit = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Did the child benefit from the PSS kit?')
    )

    remote_learning = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Was the child involved in remote learning?')
    )

    remote_learning_reasons_not_engaged = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=Choices(
            ('child_relocated', _('Child relocated')),
            ('child_is_not_reachable', _('Child is not reachable')),
            ('child_did_not_fit_the_criteria', _('Child did not fit the criteria - enrolled in previous FE')),
            ('Other', _('Other')),
        ),
        verbose_name=_('what other reasons for this child not being engaged?')
    )

    reasons_not_engaged_other = models.TextField(
        blank=True, null=True,
        verbose_name=_('Please specify')
    )

    reliable_internet = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO_SOMETIMES,
        verbose_name=_('Does the family have reliable internet service in their area during remote learning?')
    )

    gender_participate = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_(
            'Did both girls and boys in the same family participate in the class and have access to the phone/device?')
    )
    gender_participate_explain = models.TextField(
        blank=True, null=True,
        verbose_name=_('Explain')
    )
    remote_learning_engagement = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=PERCENT,
        verbose_name=_('Frequency of Child Engagement in remote learning?')
    )
    meet_learning_outcomes = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=PERCENT,
        verbose_name=_('How well did the child meet the learning outcomes?')
    )
    parent_learning_support_rate = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=PERCENT,
        verbose_name=_(
            'How do you rate the parents learning support provided to the child through this Remote learning phase?')
    )
    covid_message = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_(
            'Has the child directly been reached with awareness messaging on Covid-19 and prevention measures?')
    )
    covid_message_how_often = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=HOW_OFTEN,
        verbose_name=_('How often?')
    )

    covid_parents_message = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_(
            'Has the parents directly been reached with awareness messaging on Covid-19 and prevention measures? ')
    )
    covid_parents_message_how_often = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=HOW_OFTEN,
        verbose_name=_('How often?')
    )

    follow_up_done = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Was any follow-up done to ensure messages were well received, understood and adopted?')
    )
    follow_up_done_with_who = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=WITH_WHO,
        verbose_name=_('With who child and/or caregiver?')
    )

    child_received_books = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=(('yes', _("Yes")), ('no', _("No"))),
        verbose_name=_('child received books')
    )
    child_received_printout = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=(('yes', _("Yes")), ('no', _("No"))),
        verbose_name=_('child received printout')
    )
    child_received_internet = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=(('yes', _("Yes")), ('no', _("No"))),
        verbose_name=_('child received internet')
    )
    referal_wash = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=(('yes', _("Yes")), ('no', _("No"))),
        verbose_name=_('referal wash')
    )
    referal_health = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=(('yes', _("Yes")), ('no', _("No"))),
        verbose_name=_('referal health')
    )
    referal_other = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=(('yes', _("Yes")), ('no', _("No"))),
        verbose_name=_('referal other')
    )
    referal_other_specify = models.TextField(
        blank=True, null=True,
        verbose_name=_('referal other specify')
    )

    akelius_program = ArrayField(
        models.CharField(
            choices=AKELIUS,
            max_length=200,
            blank=True,
            null=True,
        ),
        blank=True,
        null=True,
        verbose_name=_('Did the child use Akelius program')
    )

    @property
    def student_fullname(self):
        if self.student:
            return self.student.full_name
        return ''

    @property
    def student_age(self):
        if self.student:
            return self.student.age
        return 0

    @property
    def assessment_improvement(self):
        if self.pre_test and self.post_test:
            try:
                return '{}{}'.format(
                    round(((float(self.post_test_score) - float(self.pre_test_score)) /
                           float(self.pre_test_score)) * 100.0, 2), '%')
            except ZeroDivisionError:
                return 0.0
        return 0.0

    def get_absolute_url(self):
        return '/clm/edit/%d/' % self.pk

    def __str__(self):
        if self.student:
            return self.student.__str__()
        return str(self.id)

    def __unicode__(self):
        if self.student:
            return self.student.__unicode__()
        return str(self.id)

    def score(self, keys, stage):
        assessment = getattr(self, stage, 'pre_test')
        score = stage + '_score'
        marks = {key: float(assessment.get(key, 0)) for key in keys}
        total = sum(marks.values())
        setattr(self, score, total)

    def get_score_value(self, key, stage):
        assessment = getattr(self, stage, 'pre_test')
        if assessment:
            return float(assessment.get(key, 0))
        return 0

    class Meta:
        abstract = True


class BLN(CLM):
    miss_school_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('miss_school_date')
    )
    LEARNING_RESULT = Choices(
        ('', _('Learning result')),
        ('graduated_to_bln_next_level', _('Graduated to the next level')),
        ('graduated_to_bln_next_round_same_level', _('Graduated to the next round, same level')),
        ('graduated_to_bln_next_round_higher_level', _('Graduated to the next round, higher level')),
        ('referred_to_alp', _('referred to ALP')),
        ('referred_public_school', _('Referred to public school')),
        ('referred_to_tvet', _('Referred to TVET')),
        ('referred_to_ybln', _('Referred to YBLN')),
        ('dropout', _('Dropout, referral not possible')),
        ('Referral to School Bridging Programme', _('Referral to School Bridging Programme')),
        ('other', _('Other')),
    )
    REGISTRATION_LEVEL = (
        ('', '----------'),
        ('level_one', _('Level one')),
        ('level_two', _('Level two')),
        ('level_three', _('Level three'))
    )
    MAIN_CAREGIVER = (
        ('', '----------'),
        ('mother', _('Mother')),
        ('father', _('Father')),
        ('other', _('Other')),
    )
    cycle = models.ForeignKey(
        Cycle,
        blank=True, null=True,
        related_name='+',
        on_delete=models.SET_NULL,
        verbose_name=_('Cycle')
    )
    referral = ArrayField(
        models.CharField(
            choices=CLM.REFERRAL,
            max_length=100,
            blank=True,
            null=True,
        ),
        blank=True,
        null=True,
        verbose_name=_('Referral')
    )

    learning_result = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=LEARNING_RESULT,
        verbose_name=_('Learning result')
    )
    learning_result_other = models.TextField(
        blank=True, null=True,
        verbose_name=_('Please specify')
    )
    first_attendance_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('First attendance date')
    )
    round_start_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('Round start date')
    )
    registration_level = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=REGISTRATION_LEVEL,
        verbose_name=_('Registration level')
    )
    main_caregiver = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=MAIN_CAREGIVER,
        verbose_name=_('Main Caregiver')
    )

    main_caregiver_nationality = models.ForeignKey(
        Nationality,
        blank=False, null=True,
        related_name='+',
        on_delete=models.SET_NULL,
        verbose_name=_('Main Caregiver Nationality')
    )
    main_caregiver_nationality_other = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name=_('specify')
    )

    other_caregiver_relationship = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name=_('Other Caregiver Relationship')
    )

    student_number_children = models.IntegerField(
        blank=True,
        null=True,
        choices=((x, x) for x in range(0, 20)),
        verbose_name=_('How many children does this child have?')
    )
    phone_owner = models.CharField(
        max_length=100,
        blank=False,
        null=True,
        choices=Choices(
            ('main_caregiver', _('Phone Main Caregiver')),
            ('family member', _('Family Member')),
            ('neighbors', _('Neighbors')),
            ('shawish', _('Shawish')),
        ),
        verbose_name=_('Phone Owner')
    )
    second_phone_owner = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=Choices(
            ('main_caregiver', _('Phone Main Caregiver')),
            ('family member', _('Family Member')),
            ('neighbors', _('Neighbors')),
            ('shawish', _('Shawish')),
        ),
        verbose_name=_('Second Phone Owner')
    )
    second_phone_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Second Phone number')
    )
    second_phone_number_confirm = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Second Phone number confirm')
    )

    source_of_identification = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=Choices(
            ('', '----------'),
            ('Referred by CP partner', _('Referred by CP partner')),
            ('Referred by youth partner', _('Referred by youth partner')),
            ('Family walked in to NGO', _('Family walked in to NGO')),
            ('Referral from another NGO', _('Referral from another NGO')),
            ('Referral from another Municipality', _('Referral from Municipality')),
            ('Direct outreach', _('Direct outreach')),
            ('List database', _('List database')),
            ('abln', _('ABLN')),
            ('RIMS', _('RIMS')),
            ('Other Sources', _('Other Sources')),
        ),
        verbose_name=_('Source of identification of the child')
    )

    def calculate_sore(self, stage):
        keys = [
            'BLN_ASSESSMENT/arabic',
            'BLN_ASSESSMENT/math',
            'BLN_ASSESSMENT/social_emotional',
            'BLN_ASSESSMENT/psychomotor',
            'BLN_ASSESSMENT/artistic',
        ]
        super(BLN, self).score(keys, stage)

    def assessment_form(self, stage, assessment_slug, callback=''):
        try:
            assessment = Assessment.objects.get(slug=assessment_slug)
            return '{form}?d[status]={status}&d[enrollment_id]={enrollment_id}&d[enrollment_model]=BLN&returnURL={callback}'.format(
                form=assessment.assessment_form,
                status=stage,
                enrollment_id=self.id,
                callback=callback
            )
        except Assessment.DoesNotExist as ex:
            return ''

    def domain_improvement(self, domain_mame):
        key = '{}/{}'.format(
            'BLN_ASSESSMENT',
            domain_mame,
        )
        try:
            if self.pre_test and self.post_test:
                return round(((float(self.post_test[key]) - float(self.pre_test[key])) /
                              20.0) * 100.0, 2)
        except Exception:
            return 0.0
        return 0.0

    def get_assessment_value(self, key, stage):
        assessment = getattr(self, stage)
        if assessment:
            key = 'BLN_ASSESSMENT/' + key
            return assessment.get(key, 0)
        return 0

    @property
    def arabic_improvement(self):
        return str(self.domain_improvement('arabic')) + '%'

    @property
    def math_improvement(self):
        return str(self.domain_improvement('math')) + '%'

    @property
    def english_improvement(self):
        return str(self.domain_improvement('english')) + '%'

    @property
    def french_improvement(self):
        return str(self.domain_improvement('french')) + '%'

    @property
    def social_emotional_improvement(self):
        return str(self.domain_improvement('social_emotional')) + '%'

    @property
    def psychomotor_improvement(self):
        return str(self.domain_improvement('psychomotor')) + '%'

    @property
    def artistic_improvement(self):
        return str(self.domain_improvement('artistic')) + '%'

    def pre_assessment_form(self):
        return self.assessment_form(stage='pre_test', assessment_slug='bln_pre_test')

    def post_assessment_form(self):
        return self.assessment_form(stage='post_test', assessment_slug='bln_post_test')

    class Meta:
        ordering = ['-id']
        verbose_name = "BLN"
        verbose_name_plural = "BLN"


class Bridging(CLM):
    YES_NO = Choices(
        ('', '----------'),
        ('yes', _("Yes")),
        ('no', _("No")),
    )
    RESIDENCE_TYPE = Choices(
        ('', _('----------')),
        ('Informal settlement', _('Informal settlement - مخيم')),
        ('House', _('House - منزل')),
        ('Collective shelter', _('Collective shelter - مجمع سكني  ')),
    )
    LEARNING_RESULT = Choices(
        ('', _('----------')),
        ('graduated_to_Bridging_next_level', _('Progress to the next Dirasa level')),
        ('graduated_to_Bridging_next_round_same_level', _('Repeat the same Dirasa level')),
        ('dropout', _('Drop out')),
        ('referred_public_school', _('Referred to formal education')),
        ('other', _('Referred to another pathway')),
    )
    SCHOOL_TYPE = Choices(
        ('', _('----------')),
        ('Public', _('Public')),
        ('Private', _('Private')),
        ('Semi-Private', _('Semi-Private'))
    )
    REGISTRATION_LEVEL = (
        ('', '----------'),
        ('level_one', _('Level one')),
        ('level_two', _('Level two')),
        ('level_three', _('Level three')),
        ('level_four', _('Level four')),
        ('level_five', _('Level five')),
        ('level_six', _('Level six')),
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
    MAIN_CAREGIVER = (
        ('', '----------'),
        ('mother', _('Mother')),
        ('father', _('Father')),
        ('other', _('Other')),
    )
    LANGUAGES = Choices(
        ('english_arabic', _('English/Arabic')),
        ('french_arabic', _('French/Arabic'))
    )

    child_outreach = models.IntegerField(blank=True, null=True)
    miss_school_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('miss_school_date')
    )
    language = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=LANGUAGES,
        verbose_name=_('The language supported in the program')
    )
    school = models.ForeignKey(
        School,
        blank=False, null=True,
        related_name='+',
        on_delete=models.SET_NULL,
        verbose_name=_('School Name')
    )
    cycle = models.ForeignKey(
        Cycle,
        blank=True, null=True,
        related_name='+',
        on_delete=models.SET_NULL,
        verbose_name=_('Cycle')
    )
    residence_type = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=RESIDENCE_TYPE,
        verbose_name=_('Residence Type')
    )
    referral = ArrayField(
        models.CharField(
            choices=CLM.REFERRAL,
            max_length=100,
            blank=True,
            null=True,
        ),
        blank=True,
        null=True,
        verbose_name=_('Referral')
    )
    learning_result = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=LEARNING_RESULT,
        verbose_name=_('Learning result')
    )
    dropout_reason = models.TextField(
        blank=True, null=True,
        verbose_name=_('Dropout reason')
    )
    learning_result_other = models.TextField(
        blank=True, null=True,
        verbose_name=_('Please Specify')
    )
    referral_school = models.TextField(
        blank=True, null=True,
        verbose_name=_('Formal Education school')
    )
    referral_school_type = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=SCHOOL_TYPE,
        verbose_name=_('School Type')
    )
    dropout_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('Dropout date')
    )
    first_attendance_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('First attendance date')
    )
    round_start_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('Round start date')
    )
    registration_level = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=REGISTRATION_LEVEL,
        verbose_name=_('Registration level')
    )
    main_caregiver = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=MAIN_CAREGIVER,
        verbose_name=_('Main Caregiver')
    )

    main_caregiver_nationality = models.ForeignKey(
        Nationality,
        blank=False, null=True,
        related_name='+',
        on_delete=models.SET_NULL,
        verbose_name=_('Main Caregiver Nationality')
    )
    main_caregiver_nationality_other = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name=_('specify')
    )

    other_caregiver_relationship = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name=_('Other Caregiver Relationship')
    )

    student_number_children = models.IntegerField(
        blank=True,
        null=True,
        choices=((x, x) for x in range(0, 20)),
        verbose_name=_('How many children does this child have?')
    )
    phone_owner = models.CharField(
        max_length=100,
        blank=False,
        null=True,
        choices=Choices(
            ('main_caregiver', _('Phone Main Caregiver')),
            ('family member', _('Family Member')),
            ('neighbors', _('Neighbors')),
            ('shawish', _('Shawish')),
        ),
        verbose_name=_('Phone Owner')
    )
    second_phone_owner = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=Choices(
            ('main_caregiver', _('Phone Main Caregiver')),
            ('family member', _('Family Member')),
            ('neighbors', _('Neighbors')),
            ('shawish', _('Shawish')),
        ),
        verbose_name=_('Second Phone Owner')
    )
    second_phone_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Second Phone number')
    )
    second_phone_number_confirm = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Second Phone number confirm')
    )
    source_of_identification = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=Choices(
            ('', '----------'),
            ('CP partner referral', _('CP partner referral')),
            ('Awarness Session', _('Awarness Session')),
            ('Child parents', _('Child parents')),
            ('From Profiling Database', _('From Profiling Database')),
            ('Referred by the municipality / Other formal sources', _('Referred by the municipality / Other formal sources')),
            ('From Displaced Community', _('From Displaced Community')),
            ('From Hosted Community', _('From Hosted Community')),
            ('From Other NGO', _('From Other NGO')),
            ('School Director', _('School Director')),
            ('RIMS', _('RIMS'))
        ),
        verbose_name=_('Source of identification of the child')
    )
    education_status = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=Choices(
            ('', '----------'),
            ('No Registered in any school before', _('Not Registered in any school before')),
            ('Was registered in BLN program', _('Was registered in BLN program')),
            ('Was registered in formal school and didnt continue',
             _('Was registered in formal school and didnt continue')),
            ('Was registered in CBECE program', _('Was registered in CBECE program')),
            ('Was registered in ALP program and didnt continue', _('Was registered in ALP program and didnt continue'))
        ),
        verbose_name=_('Education status')
    )
    community_Liaison_follow_up = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Was the community Liaison at school level involved in follow up on child absence or drop out?')
    )
    community_liaison_specify = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name=_('specify')
    )
    receiving_social_assistance = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Is the child receiving social assistance?')
    )
    receiving_transportation_support = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Is the Child Receiving Transportation Support?')
    )
    using_digital_platform = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=(
            ('', '----------'),
            ('yes_akelius)', _("Yes (Akelius)")),
            ('yes_learning_passport)', _("Yes (Learning Passport)")),
            ('no', _("No"))),
        verbose_name=_('Is the Child Using a digital platform (Akelius or  Learning Passport)')
    )
    school_contacted_caretaker = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Have the child caregivers been contacted by the School Community Laison')
    )
    discussion_topic = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name=_('Please specify what has been discussed')
    )
    have_labour_single_selection = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=CLM.HAVE_LABOUR,
        verbose_name=_('Does the child participate in work?')
    )
    consent_parents = models.FileField(
        upload_to='uploads/student',
        blank=True,
        null=True,
        verbose_name=_('Consent from parents'),
    )
    registration_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('Registration Date')
    )
    mid_test1 = JSONField(default=dict)
    mid_test2 = JSONField(default=dict)

    enrolled_formal_education = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Was this child enrolled in Formal Education last year and dropped out due to lack of documentation?')
    )
    def calculate_sore(self, stage):
        keys = [
            'Bridging_ASSESSMENT/arabic',
            'Bridging_ASSESSMENT/math',
            'Bridging_ASSESSMENT/social_emotional',
            'Bridging_ASSESSMENT/psychomotor',
            'Bridging_ASSESSMENT/artistic',
        ]
        super(Bridging, self).score(keys, stage)

    def assessment_form(self, stage, assessment_slug, callback=''):
        try:
            assessment = Assessment.objects.get(slug=assessment_slug)
            return '{form}?d[status]={status}&d[enrollment_id]={enrollment_id}&d[enrollment_model]=Bridging&returnURL={callback}'.format(
                form=assessment.assessment_form,
                status=stage,
                enrollment_id=self.id,
                callback=callback
            )
        except Assessment.DoesNotExist as ex:
            return ''

    def domain_improvement(self, domain_mame):
        key = '{}/{}'.format(
            'Bridging_ASSESSMENT',
            domain_mame,
        )
        try:
            if self.pre_test and self.post_test:
                return round(((float(self.post_test[key]) - float(self.pre_test[key])) /
                              20.0) * 100.0, 2)
        except Exception:
            return 0.0
        return 0.0

    def get_assessment_value(self, key, stage):
        assessment = getattr(self, stage)
        if assessment:
            key = 'Bridging_ASSESSMENT/' + key
            return assessment.get(key, 0)
        return 0

    @property
    def arabic_improvement(self):
        return str(self.domain_improvement('arabic')) + '%'

    @property
    def math_improvement(self):
        return str(self.domain_improvement('math')) + '%'

    @property
    def english_improvement(self):
        return str(self.domain_improvement('english')) + '%'

    @property
    def french_improvement(self):
        return str(self.domain_improvement('french')) + '%'

    @property
    def social_emotional_improvement(self):
        return str(self.domain_improvement('social_emotional')) + '%'

    @property
    def psychomotor_improvement(self):
        return str(self.domain_improvement('psychomotor')) + '%'

    @property
    def artistic_improvement(self):
        return str(self.domain_improvement('artistic')) + '%'

    def pre_assessment_form(self):
        return self.assessment_form(stage='pre_test', assessment_slug='Bridging_pre_test')

    def post_assessment_form(self):
        return self.assessment_form(stage='post_test', assessment_slug='Bridging_post_test')

    @property
    def attendance_days(self):
        return Bridging.get_attendance_days(self.student, self.round.start_date_bridging, self.round.end_date_bridging)

    @staticmethod
    def get_attendance_days(student_id, start_date, end_date):
        from student_registration.attendances.models import CLMAttendanceStudent
        if student_id and start_date and end_date:
            return CLMAttendanceStudent.objects.filter(student=student_id,
                                                       attended='yes',
                                                       attendance_day__attendance_date__range=(start_date, end_date)
                                                       ).count()
        return 0

    @property
    def total_absent_days(self):
        return Bridging.get_total_absent_days(self.student.id, self.round.id)

    @staticmethod
    def get_total_absent_days(student_id, round_id):
        result = 0
        from student_registration.attendances.models import CLMStudentTotalAttendance
        if student_id and round_id:
            attendance_days = CLMStudentTotalAttendance.objects.filter(student_id=student_id, round_id=round_id).first()
            if attendance_days:
                result = attendance_days.total_absence_days
        return result

    @property
    def max_consecutive_absence(self):
        return Bridging.get_max_consecutive_absence(self.student.id, self.round.id)

    @staticmethod
    def get_max_consecutive_absence(student_id, round_id):
        result = 0
        from django.db.models import Max
        from student_registration.attendances.models import CLMStudentAbsences

        if student_id and round_id:
            max_consecutive_absence_days = CLMStudentAbsences.objects.filter(
                student_id=student_id,
                round_id=round_id
            ).aggregate(max_consecutive=Max('consecutive_absence_days'))
            max_value = max_consecutive_absence_days.get('max_consecutive')
            if max_value is not None:
                result = max_value

        return result

    @property
    def more_than_ten_consecutive_absence(self):
        return Bridging.get_more_than_ten_consecutive_absence(self.student.id, self.round.id)

    @staticmethod
    def get_more_than_ten_consecutive_absence(student_id, round_id):
        result = False
        from student_registration.attendances.models import CLMStudentAbsences
        if student_id and round_id:
            attendance_days = CLMStudentAbsences.objects.filter(student_id=student_id, round_id=round_id, consecutive_absence_days__gte=10).exists()
            if attendance_days:
                result = True
        return result

    @property
    def period_out_school(self):
        return Bridging.get_period_out_school(self.student, self.miss_school_date, self.round.start_date_bridging)

    @staticmethod
    def get_period_out_school(student_id, miss_school_date, round_start_date):
        if student_id and miss_school_date and round_start_date:
            return (miss_school_date - round_start_date).days
        return 0

    class Meta:
        ordering = ['student__first_name', 'student__father_name', 'student__last_name']
        verbose_name = "Bridging"
        verbose_name_plural = "Bridging"


class Outreach(CLM):
    miss_school_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('miss_school_date')
    )
    LEARNING_RESULT = Choices(
        ('', _('Learning result')),
        ('graduated_to_outreach_next_level', _('Graduated to the next level')),
        ('graduated_to_outreach_next_round_same_level', _('Graduated to the next round, same level')),
        ('graduated_to_outreach_next_round_higher_level', _('Graduated to the next round, higher level')),
        ('referred_to_alp', _('referred to ALP')),
        ('referred_public_school', _('Referred to public school')),
        ('referred_to_tvet', _('Referred to TVET')),
        ('referred_to_youtreach', _('Referred to YOutreach')),
        ('dropout', _('Dropout, referral not possible')),
        ('other', _('Other')),
    )
    REGISTRATION_LEVEL = (
        ('', '----------'),
        ('level_one', _('Level one')),
        ('level_two', _('Level two')),
        ('level_three', _('Level three'))
    )
    MAIN_CAREGIVER = (
        ('', '----------'),
        ('mother', _('Mother')),
        ('father', _('Father')),
        ('other', _('Other')),
    )
    cycle = models.ForeignKey(
        Cycle,
        blank=True, null=True,
        related_name='+',
        on_delete=models.SET_NULL,
        verbose_name=_('Cycle')
    )
    referral = ArrayField(
        models.CharField(
            choices=CLM.REFERRAL,
            max_length=100,
            blank=True,
            null=True,
        ),
        blank=True,
        null=True,
        verbose_name=_('Referral')
    )

    learning_result = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=LEARNING_RESULT,
        verbose_name=_('Learning result')
    )
    learning_result_other = models.TextField(
        blank=True, null=True,
        verbose_name=_('Please specify')
    )
    first_attendance_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('First attendance date')
    )
    round_start_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('Round start date')
    )
    registration_level = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=REGISTRATION_LEVEL,
        verbose_name=_('Registration level')
    )
    main_caregiver = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=MAIN_CAREGIVER,
        verbose_name=_('Main Caregiver')
    )

    main_caregiver_nationality = models.ForeignKey(
        Nationality,
        blank=False, null=True,
        related_name='+',
        on_delete=models.SET_NULL,
        verbose_name=_('Main Caregiver Nationality')
    )
    main_caregiver_nationality_other = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name=_('specify')
    )

    other_caregiver_relationship = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name=_('Other Caregiver Relationship')
    )

    student_number_children = models.IntegerField(
        blank=True,
        null=True,
        choices=((x, x) for x in range(0, 20)),
        verbose_name=_('How many children does this child have?')
    )
    phone_owner = models.CharField(
        max_length=100,
        blank=False,
        null=True,
        choices=Choices(
            ('main_caregiver', _('Phone Main Caregiver')),
            ('family member', _('Family Member')),
            ('neighbors', _('Neighbors')),
            ('shawish', _('Shawish')),
        ),
        verbose_name=_('Phone Owner')
    )
    second_phone_owner = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=Choices(
            ('main_caregiver', _('Phone Main Caregiver')),
            ('family member', _('Family Member')),
            ('neighbors', _('Neighbors')),
            ('shawish', _('Shawish')),
        ),
        verbose_name=_('Second Phone Owner')
    )
    second_phone_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Second Phone number')
    )
    second_phone_number_confirm = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Second Phone number confirm')
    )

    source_of_identification = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=Choices(
            ('', '----------'),
            ('Referred CP partner', _('Referred CP partner')),
            ('Formal Education', _('Formal Education')),
            ('Referred YBLN', _('Referred YBLN')),
            ('Referred TEVET', _('Referred TEVET')),
            ('Other BLN (Unicef partner)', _('Other BLN (Unicef partner)')),
            ('Other ABLN (Unicef partner)', _('Other ABLN (Unicef partner)')),
            ('Other CBECE (Unicef partner)', _('Other CBECE (Unicef partner)')),
            ('Other BLN (Non-Unicef partner)', _('Other BLN (Non-Unicef partner)')),
            ('Other ABLN (Non-Unicef partner)', _('Other ABLN (Non-Unicef partner)')),
            ('Other CBECE (Non-Unicef partner)', _('Other CBECE (Non-Unicef partner)')),
            ('Referral to ALP', _('Referral to ALP')),
            ('Referral to Speciailized services (Unicef partner)', _('Referral to Speciailized services (Unicef partner)')),
            ('Referral to Speciailized services (Non-Unicef partner)', _('Referral to Speciailized services (Non-Unicef partner)')),
            ('Referral to School Briding Programme', _('Referral to School Briding Programme')),
        ),
        verbose_name=_('Source of identification of the child')
    )
    education_status = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=Choices(
            ('', '----------'),
            ('out of school', _('Out of school')),
            ('enrolled in formal education but did not continue', ("Enrolled in formal education but did not continue")),
            ('enrolled in non formal education but did not continue', ("Enrolled in non formal education but did not continue"))

        ),
        verbose_name=_('Education status')
    )

    def calculate_sore(self, stage):
        keys = [
            'Outreach_ASSESSMENT/arabic',
            'Outreach_ASSESSMENT/math',
            'Outreach_ASSESSMENT/social_emotional',
            'Outreach_ASSESSMENT/psychomotor',
            'Outreach_ASSESSMENT/artistic',
        ]
        super(Outreach, self).score(keys, stage)

    def assessment_form(self, stage, assessment_slug, callback=''):
        try:
            assessment = Assessment.objects.get(slug=assessment_slug)
            return '{form}?d[status]={status}&d[enrollment_id]={enrollment_id}&d[enrollment_model]=Outreach&returnURL={callback}'.format(
                form=assessment.assessment_form,
                status=stage,
                enrollment_id=self.id,
                callback=callback
            )
        except Assessment.DoesNotExist as ex:
            return ''

    def domain_improvement(self, domain_mame):
        key = '{}/{}'.format(
            'Outreach_ASSESSMENT',
            domain_mame,
        )
        try:
            if self.pre_test and self.post_test:
                return round(((float(self.post_test[key]) - float(self.pre_test[key])) /
                              20.0) * 100.0, 2)
        except Exception:
            return 0.0
        return 0.0

    def get_assessment_value(self, key, stage):
        assessment = getattr(self, stage)
        if assessment:
            key = 'Outreach_ASSESSMENT/' + key
            return assessment.get(key, 0)
        return 0

    @property
    def arabic_improvement(self):
        return str(self.domain_improvement('arabic')) + '%'

    @property
    def math_improvement(self):
        return str(self.domain_improvement('math')) + '%'

    @property
    def english_improvement(self):
        return str(self.domain_improvement('english')) + '%'

    @property
    def french_improvement(self):
        return str(self.domain_improvement('french')) + '%'

    @property
    def social_emotional_improvement(self):
        return str(self.domain_improvement('social_emotional')) + '%'

    @property
    def psychomotor_improvement(self):
        return str(self.domain_improvement('psychomotor')) + '%'

    @property
    def artistic_improvement(self):
        return str(self.domain_improvement('artistic')) + '%'

    def pre_assessment_form(self):
        return self.assessment_form(stage='pre_test', assessment_slug='outreach_pre_test')

    def post_assessment_form(self):
        return self.assessment_form(stage='post_test', assessment_slug='outreach_post_test')

    class Meta:
        ordering = ['-id']
        verbose_name = "Outreach"
        verbose_name_plural = "Outreach"


class ABLN(CLM):
    miss_school_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('miss_school_date')
    )
    LEARNING_RESULT = Choices(
        ('', _('Learning result')),
        ('graduated_to_abln_next_level', _('Graduated to the ABLN next level')),
        ('graduated_to_abln_next_round_same_level', _('Graduated to the next round, same level')),
        ('graduated_to_abln_next_round_higher_level', _('Graduated to the next round, higher level')),
        ('referred_to_bln', _('Referred to BLN')),
        ('referred_to_ybln', _('Referred to YBLN')),
        ('referred_to_alp', _('Referred to ALP')),
        ('referred_to_cbt', _('Referred to CBT')),
        ('dropout', _('Dropout, referral not possible')),
        ('referred_public_school', _('Referred to public school')),
        ('referred_to_tvet', _('Referred to TVET')),
        ('Referral to School Bridging Programme', _('Referral to School Bridging Programme')),
        ('other', _('Other')),
    )
    REGISTRATION_LEVEL = (
        ('', '----------'),
        ('level_one', _('Level one')),
        ('level_two', _('Level two')),
    )

    MAIN_CAREGIVER = (
        ('', '----------'),
        ('mother', _('Mother')),
        ('father', _('Father')),
        ('other', _('Other')),
    )
    cycle = models.ForeignKey(
        Cycle,
        blank=True, null=True,
        related_name='+',
        on_delete=models.SET_NULL,
        verbose_name=_('Cycle')
    )
    referral = ArrayField(
        models.CharField(
            choices=CLM.REFERRAL,
            max_length=100,
            blank=True,
            null=True,
        ),
        blank=True,
        null=True,
        verbose_name=_('Referral')
    )

    learning_result = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=LEARNING_RESULT,
        verbose_name=_('Learning result')
    )
    learning_result_other = models.TextField(
        blank=True, null=True,
        verbose_name=_('Please specify')
    )
    first_attendance_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('First attendance date')
    )
    round_start_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('Round start date')
    )
    registration_level = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=REGISTRATION_LEVEL,
        verbose_name=_('Registration level')
    )
    main_caregiver = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=MAIN_CAREGIVER,
        verbose_name=_('Main Caregiver')
    )

    main_caregiver_nationality = models.ForeignKey(
        Nationality,
        blank=False, null=True,
        related_name='+',
        on_delete=models.SET_NULL,
        verbose_name=_('Main Caregiver Nationality')
    )
    main_caregiver_nationality_other = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name=_('specify')
    )
    other_caregiver_relationship = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name=_('Other Caregiver Relationship')
    )
    student_number_children = models.IntegerField(
        blank=True,
        null=True,
        choices=((x, x) for x in range(0, 20)),
        verbose_name=_('How many children does this child have?')
    )
    phone_owner = models.CharField(
        max_length=100,
        blank=False,
        null=True,
        choices=Choices(
            ('main_caregiver', _('Phone Main Caregiver')),
            ('family member', _('Family Member')),
            ('neighbors', _('Neighbors')),
            ('shawish', _('Shawish')),
        ),
        verbose_name=_('Phone Owner')
    )
    second_phone_owner = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=Choices(
            ('main_caregiver', _('Phone Main Caregiver')),
            ('family member', _('Family Member')),
            ('neighbors', _('Neighbors')),
            ('shawish', _('Shawish')),
        ),
        verbose_name=_('Second Phone Owner')
    )
    second_phone_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Second Phone number')
    )
    second_phone_number_confirm = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Second Phone number confirm')
    )

    source_of_identification = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=Choices(
            ('', '----------'),
            ('Referred by CP partner', _('Referred by CP partner')),
            ('Referred by youth partner', _('Referred by youth partner')),
            ('Family walked in to NGO', _('Family walked in to NGO')),
            ('Referral from another NGO', _('Referral from another NGO')),
            ('Referral from another Municipality', _('Referral from Municipality')),
            ('Direct outreach', _('Direct outreach')),
            ('List database', _('List database')),
            ('RIMS', _('RIMS')),
            ('Other Sources', _('Other Sources')),
            # ('bln', _('BLN'))
        ),
        verbose_name=_('Source of identification of the child')
    )

    def calculate_sore(self, stage):
        keys = [
            'ABLN_ASSESSMENT/arabic',
            'ABLN_ASSESSMENT/math',
            'ABLN_ASSESSMENT/social_emotional',
            'ABLN_ASSESSMENT/psychomotor',
            'ABLN_ASSESSMENT/artistic',
        ]
        super(ABLN, self).score(keys, stage)

    def assessment_form(self, stage, assessment_slug, callback=''):
        try:
            assessment = Assessment.objects.get(slug=assessment_slug)
            return '{form}?d[status]={status}&d[enrollment_id]={enrollment_id}&d[enrollment_model]=ABLN&returnURL={callback}'.format(
                form=assessment.assessment_form,
                status=stage,
                enrollment_id=self.id,
                callback=callback
            )
        except Assessment.DoesNotExist as ex:
            return ''

    def domain_improvement(self, domain_mame):
        key = '{}/{}'.format(
            'ABLN_ASSESSMENT',
            domain_mame,
        )
        try:
            if self.pre_test and self.post_test:
                return round(((float(self.post_test[key]) - float(self.pre_test[key])) /
                              20.0) * 100.0, 2)
        except Exception:
            return 0.0
        return 0.0

    def get_assessment_value(self, key, stage):
        assessment = getattr(self, stage)
        if assessment:
            key = 'ABLN_ASSESSMENT/' + key
            return assessment.get(key, 0)
        return 0

    @property
    def arabic_improvement(self):
        return str(self.domain_improvement('arabic')) + '%'

    @property
    def math_improvement(self):
        return str(self.domain_improvement('math')) + '%'

    @property
    def english_improvement(self):
        return str(self.domain_improvement('english')) + '%'

    @property
    def french_improvement(self):
        return str(self.domain_improvement('french')) + '%'

    @property
    def social_emotional_improvement(self):
        return str(self.domain_improvement('social_emotional')) + '%'

    @property
    def psychomotor_improvement(self):
        return str(self.domain_improvement('psychomotor')) + '%'

    @property
    def artistic_improvement(self):
        return str(self.domain_improvement('artistic')) + '%'

    def pre_assessment_form(self):
        return self.assessment_form(stage='pre_test', assessment_slug='abln_pre_test')

    def post_assessment_form(self):
        return self.assessment_form(stage='post_test', assessment_slug='abln_post_test')

    class Meta:
        ordering = ['-id']
        verbose_name = "ABLN"
        verbose_name_plural = "ABLN"


class RS(CLM):
    MUAC = Choices(
        ('', _('MUAC')),
        ('1', _('< 11.5 CM (severe malnutrition)')),
        ('2', _('< 12.5 CM (moderate malnutrition)')),
    )
    # SITES = Choices(
    #     ('', _('Program site')),
    #     ('in_school', _('Inside the school')),
    #     ('out_school', _('Outside the school')),
    # )

    # LEARNING_RESULT = Choices(
    #     ('', _('Learning result')),
    #     ('repeat_level', _('Yes')),
    #     ('graduated_next_level', _('No'))
    # )
    LEARNING_RESULT = Choices(
        ('', '----------'),
        ('graduated_to_rs_next_round_higher_level', _('Progress to FE higher grade next year')),
        ('graduated_to_rs_next_round_same_level', _('Repeat same grade next year')),
        ('referred_alp', _('Referred to ALP')),
        ('graduated_to_tvet', _('Referred to TVET')),
        ('other', _('Other')),
    )
    MAIN_CAREGIVER = (
        ('', '----------'),
        ('mother', _('Mother')),
        ('father', _('Father')),
        ('other', _('Other')),
    )
    SCHOOL_SHIFTS = Choices(
        ('', _('----------')),
        ('first', _('First shift')),
        ('second', _('Second shift')),
    )
    TYPES = Choices(
        ('', _('Program type')),
        ('homework_support', _('Homework Support')),
        ('remedial_support', _('Remedial Support')),
    )
    SITES = Choices(
        ('', _('Program site')),
        ('in_school', _('Inside the school')),
        ('out_school', _('Outside the school')),
    )
    REFER_SEASON = Choices(
        ('academic', _('Academic')),
        ('absence', _('Absence'))
    )
    GRADE_LEVEL = Choices(
        ('grade1', _('Grade 1')),
        ('grade2', _('Grade 2')),
        ('grade3', _('Grade 3')),
        ('grade4', _('Grade 4')),
        ('grade5', _('Grade 5')),
        ('grade6', _('Grade 6')),
        ('grade7', _('Grade 7')),
        ('grade8', _('Grade 8')),
        ('grade9', _('Grade 9'))
    )

    SOURCE_JOIN_FE = Choices(
        ('ALP', _('ALP')),
        ('Prep-ECE', _('Prep - ECE')),
        ('ABLN', ('ABLN')),
        ('CBECE', _('CBECE')),
        ('BLN', ('BLN')),
        ('YBLN', _('YBLN')),
        ('FE_outside_lebanon', _('FE outside Lebanon')),
        ('FE__lebanon', _('FE Lebanon')),
    )
    # YEAR_REGISTRATION = Choices(
    #     ('year_1_2020', _('Year 1-2020')),
    #     ('year_2_2020', _("Year 2-2021")),
    # )
    education_status = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=Choices(
            ('', '----------'),
            ('out of school', _('Out of school')),
            ('enrolled in formal education but did not continue',
             _("Enrolled in formal education but did not continue")),
            ('enrolled in CBECE', _("Enrolled in CBECE")),
        ),
        verbose_name=_('Education status')
    )
    type = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=TYPES,
        verbose_name=_('Program type')
    )
    cycle = models.ForeignKey(
        Cycle,
        blank=True, null=True,
        related_name='+',
        on_delete=models.SET_NULL,
        verbose_name=_('Cycle')
    )
    site = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=SITES,
        verbose_name=_('Program site')
    )
    school = models.ForeignKey(
        School,
        blank=False, null=True,
        related_name='+',
        on_delete=models.SET_NULL,
        verbose_name=_('Attending in school')
    )
    registered_in_school = models.TextField(
        blank=True, null=True,
        verbose_name=_('School of Enrollment')
    )

    shift = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=SCHOOL_SHIFTS,
        verbose_name=_('Shift')
    )
    grade = models.ForeignKey(
        ClassRoom,
        blank=True, null=True,
        related_name='+',
        on_delete=models.SET_NULL,
        verbose_name=_('Class')
    )
    referral = ArrayField(
        models.CharField(
            choices=CLM.REFERRAL,
            max_length=100,
            blank=True,
            null=True,
        ),
        blank=True,
        null=True,
        verbose_name=_('Where was the child referred?')
    )
    child_muac = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=MUAC,
        verbose_name=_('Child MUAC')
    )
    pre_test_arabic = models.IntegerField(
        blank=True,
        null=True,
        choices=((x, x) for x in range(0, 21)),
        verbose_name=_('Arabic')
    )
    pre_test_language = models.FloatField(
        blank=True,
        null=True,
        choices=((x, x) for x in range(0, 21)),
        verbose_name=_('Foreign Language')
    )
    pre_test_math = models.FloatField(
        blank=True,
        null=True,
        choices=((x, x) for x in range(0, 21)),
        verbose_name=_('Math')
    )
    pre_test_science = models.FloatField(
        blank=True,
        null=True,
        choices=((x, x) for x in range(0, 21)),
        verbose_name=_('Science')
    )
    post_test_arabic = models.FloatField(
        blank=True,
        null=True,
        choices=((x, x) for x in range(0, 21)),
        verbose_name=_('Science')
    )
    post_test_language = models.FloatField(
        blank=True,
        null=True,
        choices=((x, x) for x in range(0, 21)),
        verbose_name=_('Science')
    )
    post_test_math = models.FloatField(
        blank=True,
        null=True,
        choices=((x, x) for x in range(0, 21)),
        verbose_name=_('Science')
    )
    post_test_science = models.FloatField(
        blank=True,
        null=True,
        choices=((x, x) for x in range(0, 21)),
        verbose_name=_('Science')
    )

    pre_reading = JSONField(default=dict)
    pre_reading_score = models.CharField(
        max_length=45,
        blank=True,
        null=True,
        verbose_name=_('Arabic reading - Pre')
    )
    post_reading = JSONField(default=dict)
    post_reading_score = models.CharField(
        max_length=45,
        blank=True,
        null=True,
        verbose_name=_('Arabic reading - Post')
    )

    pre_self_assessment = JSONField(default=dict)
    pre_self_assessment_score = models.CharField(
        max_length=45,
        blank=True,
        null=True,
        verbose_name=_('Self-assessment - Pre')
    )
    post_self_assessment = JSONField(default=dict)
    post_self_assessment_score = models.CharField(
        max_length=45,
        blank=True,
        null=True,
        verbose_name=_('Self-assessment - Post')
    )

    pre_motivation = JSONField(default=dict)
    pre_motivation_score = models.CharField(
        max_length=45,
        blank=True,
        null=True,
        verbose_name=_('Motivation - Pre')
    )
    post_motivation = JSONField(default=dict)
    post_motivation_score = models.CharField(
        max_length=45,
        blank=True,
        null=True,
        verbose_name=_('Motivation - Post')
    )
    learning_result = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=LEARNING_RESULT,
        verbose_name=_('Learning result')
    )
    learning_result_other = models.TextField(
        blank=True, null=True,
        verbose_name=_('Please specify')
    )
    section = models.ForeignKey(
        Section,
        blank=True, null=True,
        related_name='+',
        on_delete=models.SET_NULL,
        verbose_name=_('Section')
    )
    final_grade = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        blank=True, null=True,
        # help_text='/80'
    )
    miss_school = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=(('yes', _("Yes")), ('no', _("No"))),
        verbose_name=_('Miss school?')
    )
    miss_school_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('miss_school_date')
    )
    round_start_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('Round start date')
    )
    main_caregiver = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=MAIN_CAREGIVER,
        verbose_name=_('Main Caregiver')
    )
    main_caregiver_nationality = models.ForeignKey(
        Nationality,
        blank=False, null=True,
        related_name='+',
        on_delete=models.SET_NULL,
        verbose_name=_('Main Caregiver Nationality')
    )

    other_caregiver_relationship = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name=_('Other Caregiver Relationship')
    )

    student_number_children = models.IntegerField(
        blank=True,
        null=True,
        choices=((x, x) for x in range(0, 20)),
        verbose_name=_('How many children does this child have?')
    )
    phone_owner = models.CharField(
        max_length=100,
        blank=False,
        null=True,
        choices=Choices(
            ('main_caregiver', _('Phone Main Caregiver')),
            ('family member', _('Family Member')),
            ('neighbors', _('Neighbors')),
            ('shawish', _('Shawish')),
        ),
        verbose_name=_('Phone Owner')
    )
    second_phone_owner = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=Choices(
            ('main_caregiver', _('Phone Main Caregiver')),
            ('family member', _('Family Member')),
            ('neighbors', _('Neighbors')),
            ('shawish', _('Shawish')),
        ),
        verbose_name=_('Second Phone Owner')
    )
    second_phone_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Second Phone number')
    )
    second_phone_number_confirm = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Second Phone number confirm')
    )
    source_of_identification = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=Choices(
            ('', '----------'),
            ('Referral from school directors', _('Referral from school directors')),
            ('From Profiling Database (MEHE)', _('From Profiling Database (MEHE)')),
            ('RIMS', _('RIMS')),
            ('Other Sources', _('Other Sources')),
        ),
        verbose_name=_('Source of identification of the child')
    )
    grade_level = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=GRADE_LEVEL,
        verbose_name=_('What was the child education level when first joining formal education in lebanon')
    )
    source_join_fe = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=SOURCE_JOIN_FE,
        verbose_name=_('From where did the child first come to join  FE')
    )
    # year_registration = models.CharField(
    #     max_length=100,
    #     blank=True,
    #     null=True,
    #     choices= YEAR_REGISTRATION ,
    #     verbose_name=_('Year of registration')
    # )
    grade_registration = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=Choices(
            ('', '----------'),
            ('1', _('1')),
            ('2', _('2')),
            ('3', _('3')),
            ('4', _('4')),
            ('5', _('5')),
            ('6', _('6')),
            ('7', _('7')),
            ('8', _('8')),
            ('9', _('9')),
        ),
        verbose_name=_('Grade of registeration')
    )


    class Meta:
        ordering = ['-id']
        verbose_name = "RS"
        verbose_name_plural = "RS"

    @property
    def pretest_total(self):
        try:
            return self.pre_test_arabic + self.pre_test_language + self.pre_test_math + self.pre_test_science
        except TypeError:
            return 0

    @property
    def pretest_result(self):
        return '{}/{}'.format(
            str(self.pretest_total),
            '80'
        )

    @property
    def posttest_total(self):
        try:
            return self.post_test_arabic + self.post_test_language + self.post_test_math + self.post_test_science
        except TypeError:
            return 0

    @property
    def posttest_result(self):
        return '{}/{}'.format(
            str(self.posttest_total),
            '80'
        )

    @property
    def academic_test_improvement(self):
        if self.pretest_total and self.posttest_total:
            try:
                return '{}{}'.format(
                    round((float(self.posttest_total) - float(self.pretest_total)) /
                          float(self.pretest_total) * 100.0, 2),
                    '%')
            except ZeroDivisionError:
                return 0.0
        return 0

    @property
    def self_assessment_improvement(self):
        if self.pre_self_assessment and self.post_self_assessment:
            try:
                return '{}{}'.format(
                    round(((float(self.post_self_assessment_score) - float(self.pre_self_assessment_score)) /
                           float(self.pre_self_assessment_score)) * 100.0, 2),
                    '%')
            except ZeroDivisionError:
                return 0.0
        return 0.0

    @property
    def motivation_improvement(self):
        if self.pre_motivation and self.post_motivation:
            try:
                return '{}{}'.format(
                    round(((float(self.post_motivation_score) - float(self.pre_motivation_score)) /
                           float(self.pre_motivation_score)) * 100.0, 2),
                    '%')
            except ZeroDivisionError:
                return 0.0
        return 0.0

    @property
    def arabic_reading_improvement(self):
        if self.pre_reading_score and self.post_reading_score:
            try:
                return self.pre_reading_score - self.post_reading_score
            except Exception:
                return 0
        return 0

    def assessment_form(self, stage, assessment_slug, callback=''):
        try:
            assessment = Assessment.objects.get(slug=assessment_slug)
            return '{form}?d[status]={status}&d[enrollment_id]={enrollment_id}&d[enrollment_model]=RS&returnURL={callback}'.format(
                form=assessment.assessment_form,
                status=stage,
                enrollment_id=self.id,
                callback=callback
            )
        except Assessment.DoesNotExist:
            return ''

    @property
    def pre_assessment_form(self):
        return self.assessment_form(stage='pre_test', assessment_slug='rs_pre_test')

    @property
    def post_assessment_form(self):
        return self.assessment_form(stage='post_test', assessment_slug='rs_post_test')

    def domain_improvement(self, domain_mame):
        pre_test = getattr(self, 'pre_test_' + domain_mame)
        post_test = getattr(self, 'post_test_' + domain_mame)
        if pre_test and post_test:
            try:
                return round(((float(post_test) - float(pre_test)) /
                              float(pre_test)) * 100.0, 2)
            except ZeroDivisionError:
                return 0.0
        return 0.0

    @property
    def arabic_improvement(self):
        return str(self.domain_improvement('arabic')) + '%'

    @property
    def math_improvement(self):
        return str(self.domain_improvement('math')) + '%'

    @property
    def language_improvement(self):
        return str(self.domain_improvement('language')) + '%'

    @property
    def science_improvement(self):
        return str(self.domain_improvement('science')) + '%'

    def get_assessment_value(self, key, stage):
        assessment = getattr(self, stage)
        if assessment:
            key = 'RS_ASSESSMENT/' + key
            return assessment.get(key, 0)
        return 0

    def calculate_score(self, stage):
        keys = []
        if stage in ['pre_test', 'post_test']:
            keys = [
                # 'RS_ASSESSMENT_0/FL0',
                'RS_ASSESSMENT/FL1',
                'RS_ASSESSMENT/FL2',
                'RS_ASSESSMENT/FL3',
                'RS_ASSESSMENT/FL4',
            ]
        elif stage in ['pre_reading', 'post_reading']:
            keys = [
                'RS_ASSESSMENT/FL1',
            ]
        elif stage in ['pre_motivation', 'post_motivation']:
            keys = [
                'RS_ASSESSMENT/FL5',
                'RS_ASSESSMENT/FL6',
                'RS_ASSESSMENT/FL7',
                'RS_ASSESSMENT/FL8',
            ]
        elif stage in ['pre_self_assessment', 'post_self_assessment']:
            keys = [
                'SELF_ASSESSMENT/assessment_1',
                'SELF_ASSESSMENT/assessment_2',
                'SELF_ASSESSMENT/assessment_3',
                'SELF_ASSESSMENT/assessment_4',
                'SELF_ASSESSMENT/assessment_5',
                'SELF_ASSESSMENT/assessment_6',
                'SELF_ASSESSMENT/assessment_7',
                'SELF_ASSESSMENT/assessment_8',
                'SELF_ASSESSMENT/assessment_9',
                'SELF_ASSESSMENT/assessment_10',
                'SELF_ASSESSMENT/assessment_11',
                'SELF_ASSESSMENT/assessment_12',
                'SELF_ASSESSMENT/assessment_13',
                'SELF_ASSESSMENT/assessment_14',
            ]
        super(RS, self).score(keys, stage)


class CBECE(CLM):
    MUAC = Choices(
        ('', _('MUAC')),
        ('1', _('< 11.5 CM (severe malnutrition)')),
        ('2', _('< 12.5 CM (moderate malnutrition)')),
    )
    SITES = Choices(
        ('', _('Program site')),
        ('in_school', _('Inside the school')),
        ('out_school', _('Outside the school')),
    )
    LEARNING_RESULT = Choices(
        ('', '----------'),
        ('graduated_to_cbece_next_level', _('Graduated to the next level')),
        ('graduated_to_cbece_next_round_same_level', _('Graduated to the next round, same level')),
        ('graduated_to_cbece_next_round_higher_level', _('Graduated to the next round, higher level round 3')),
        ('referred_to_alp', _('referred to ALP')),
        ('referred_public_school', _('Referred to public school grade 1')),
        ('referred_to_tvet', _('Referred to TVET')),
        ('referred_to_ycbece', _('Referred to YCBECE')),
        ('dropout', _('Dropout, referral not possible')),
        ('Referral to School Bridging Programme', _('Referral to School Bridging Programme')),
        ('other', _('Other')),
    )
    REGISTRATION_LEVEL = (
        ('', '----------'),
        ('level_two', _('Level two')),
        ('level_three', _('Level three'))
    )
    MAIN_CAREGIVER = (
        ('', '----------'),
        ('mother', _('Mother')),
        ('father', _('Father')),
        ('other', _('Other')),
    )

    education_status = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=Choices(
            ('', '----------'),
            ('out of school', _('Out of school')),
            ('enrolled in formal education but did not continue',
             _("Enrolled in formal education but did not continue")),
            ('enrolled in CBECE', _("Enrolled in CBECE")),
        ),
        verbose_name=_('Education status')
    )
    cycle = models.ForeignKey(
        Cycle,
        blank=True, null=True,
        related_name='+',
        on_delete=models.SET_NULL,
        verbose_name=_('Cycle')
    )
    site = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=SITES,
        verbose_name=_('Program site')
    )
    school = models.ForeignKey(
        School,
        blank=False, null=True,
        related_name='+',
        on_delete=models.SET_NULL,
        verbose_name=_('Attending in school')
    )
    referral = ArrayField(
        models.CharField(
            choices=CLM.REFERRAL,
            max_length=100,
            blank=True,
            null=True,
        ),
        blank=True,
        null=True,
        verbose_name=_('Where was the child referred?')
    )
    child_muac = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=MUAC,
        verbose_name=_('Child MUAC')
    )
    pre_test_arabic = models.IntegerField(
        blank=True,
        null=True,
        choices=((x, x) for x in range(0, 21)),
        verbose_name=_('Arabic')
    )
    pre_test_language = models.FloatField(
        blank=True,
        null=True,
        choices=((x, x) for x in range(0, 21)),
        verbose_name=_('Foreign Language')
    )
    pre_test_math = models.FloatField(
        blank=True,
        null=True,
        choices=((x, x) for x in range(0, 21)),
        verbose_name=_('Math')
    )
    pre_test_science = models.FloatField(
        blank=True,
        null=True,
        choices=((x, x) for x in range(0, 21)),
        verbose_name=_('Science')
    )

    learning_result = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=LEARNING_RESULT,
        verbose_name=_('Learning result')
    )
    learning_result_other = models.TextField(
        blank=True, null=True,
        verbose_name=_('Please specify')
    )
    final_grade = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        blank=True, null=True,
        # help_text='/80'
    )
    miss_school_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('miss_school_date')
    )
    first_attendance_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('First attendance date')
    )
    round_start_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('Round start date')
    )
    registration_level = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=REGISTRATION_LEVEL,
        verbose_name=_('Registration level')
    )
    main_caregiver = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=MAIN_CAREGIVER,
        verbose_name=_('Main Caregiver')
    )
    main_caregiver_nationality = models.ForeignKey(
        Nationality,
        blank=False, null=True,
        related_name='+',
        on_delete=models.SET_NULL,
        verbose_name=_('Main Caregiver Nationality')
    )

    other_caregiver_relationship = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name=_('Other Caregiver Relationship')
    )

    student_number_children = models.IntegerField(
        blank=True,
        null=True,
        choices=((x, x) for x in range(0, 20)),
        verbose_name=_('How many children does this child have?')
    )
    phone_owner = models.CharField(
        max_length=100,
        blank=False,
        null=True,
        choices=Choices(
            ('main_caregiver', _('Phone Main Caregiver')),
            ('family member', _('Family Member')),
            ('neighbors', _('Neighbors')),
            ('shawish', _('Shawish')),
        ),
        verbose_name=_('Phone Owner')
    )
    second_phone_owner = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=Choices(
            ('main_caregiver', _('Phone Main Caregiver')),
            ('family member', _('Family Member')),
            ('neighbors', _('Neighbors')),
            ('shawish', _('Shawish')),
        ),
        verbose_name=_('Second Phone Owner')
    )
    second_phone_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Second Phone number')
    )
    second_phone_number_confirm = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Second Phone number confirm')
    )
    source_of_identification = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=Choices(
            ('', '----------'),
            ('Referred by CP partner', _('Referred by CP partner')),
            ('Family walked in to NGO', _('Family walked in to NGO')),
            ('Referral from another NGO', _('Referral from another NGO')),
            ('Referral from another Municipality', _('Referral from Municipality')),
            ('Direct outreach', _('Direct outreach')),
            ('List database', _('List database')),
            ('From hosted community', _('From hosted community')),
            ('From displaced community', _('From displaced community')),
            ('RIMS', _('RIMS')),
            ('Other Sources', _('Other Sources')),
        ),
        verbose_name=_('Source of identification of the child')
    )
    mid_test_done = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=(('yes', _("Yes")), ('no', _("No"))),
        verbose_name=_('test_done')
    )
    mid_test = JSONField(default=dict)

    main_caregiver_nationality_other = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name=_('specify')
    )

    # def calculate_sore(self, stage):
    #     keys = [
    #         'CBECE_ASSESSMENT/LanguageArtDomain',
    #         'CBECE_ASSESSMENT/CognitiveDomian',
    #         'CBECE_ASSESSMENT/ScienceDomain',
    #         'CBECE_ASSESSMENT/SocialEmotionalDomain',
    #         'CBECE_ASSESSMENT/PsychomotorDomain',
    #         'CBECE_ASSESSMENT/ArtisticDomain',
    #     ]

    def assessment_form(self, stage, assessment_slug, callback=''):
        try:
            assessment = Assessment.objects.get(slug=assessment_slug)
            return '{form}?d[status]={status}&d[programmecycle]={programmecycle}&d[enrollment_id]={enrollment_id}&d[enrollment_model]=CBECE&returnURL={callback}'.format(
                form=assessment.assessment_form,
                status=stage,
                programmecycle=self.cycle_id,
                enrollment_id=self.id,
                callback=callback
            )
        except Assessment.DoesNotExist:
            return ''

    def domain_improvement(self, domain_mame):
        if not self.cycle_id:
            return 0.0
        if not self.pre_test or not self.post_test:
            return 0.0
        program_cycle = str(self.cycle_id)
        key = '{}/{}{}'.format(
            'CBECE_ASSESSMENT',
            domain_mame,
            program_cycle
        )
        if key in self.pre_test and key in self.post_test:
            try:
                return round(((float(self.post_test[key]) - float(self.pre_test[key])) /
                              float(self.pre_test[key])) * 100.0, 2)
            except ZeroDivisionError:
                return 0.0
        return 0.0

    def get_assessment_value(self, key, stage):
        assessment = getattr(self, stage)
        program_cycle = str(self.cycle_id)
        if assessment:
            key = 'CBECE_ASSESSMENT/{}{}'.format(key, program_cycle)
            return assessment.get(key, 0)
        return 0

    @property
    def pre_assessment_form(self):
        return self.assessment_form(stage='pre_test', assessment_slug='cbece_pre_test')

    @property
    def post_assessment_form(self):
        return self.assessment_form(stage='post_test', assessment_slug='cbece_post_test')

    @property
    def mid_assessment_form(self):
        return self.assessment_form(stage='mid_test', assessment_slug='cbece_mid_test')

    @property
    def art_improvement(self):
        return str(self.domain_improvement('LanguageArtDomain')) + '%'

    @property
    def science_improvement(self):
        return str(self.domain_improvement('ScienceDomain')) + '%'

    @property
    def cognitive_improvement(self):
        return str(self.domain_improvement('CognitiveDomian')) + '%'

    @property
    def social_improvement(self):
        return str(self.domain_improvement('SocialEmotionalDomain')) + '%'

    @property
    def psycho_improvement(self):
        return str(self.domain_improvement('PsychomotorDomain')) + '%'

    @property
    def artistic_improvement(self):
        return str(self.domain_improvement('ArtisticDomain')) + '%'

    def calculate_score(self, stage):
        program_cycle = str(self.cycle_id)
        keys = [
            'CBECE_ASSESSMENT/LanguageArtDomain' + program_cycle,
            'CBECE_ASSESSMENT/CognitiveDomian' + program_cycle,
            'CBECE_ASSESSMENT/ScienceDomain' + program_cycle,
            'CBECE_ASSESSMENT/SocialEmotionalDomain' + program_cycle,
            'CBECE_ASSESSMENT/PsychomotorDomain' + program_cycle,
            'CBECE_ASSESSMENT/ArtisticDomain' + program_cycle,
        ]
        super(CBECE, self).score(keys, stage)

        self.scores = {
            'pre_LanguageArtDomain': self.get_score_value('CBECE_ASSESSMENT/LanguageArtDomain' + program_cycle,
                                                          'pre_test'),
            'pre_CognitiveDomain': self.get_score_value(
                'CBECE_ASSESSMENT/CognitiveDomian' + program_cycle,
                'pre_test'),
            'pre_ScienceDomain': self.get_score_value(
                'CBECE_ASSESSMENT/ScienceDomain' + program_cycle,
                'pre_test'),
            'pre_SocialEmotionalDomain': self.get_score_value('CBECE_ASSESSMENT/SocialEmotionalDomain' + program_cycle,
                                                              'pre_test'),
            'pre_PsychomotorDomain': self.get_score_value('CBECE_ASSESSMENT/PsychomotorDomain' + program_cycle,
                                                          'pre_test'),
            'pre_ArtisticDomain': self.get_score_value('CBECE_ASSESSMENT/ArtisticDomain' + program_cycle, 'pre_test'),

            'post_LanguageArtDomain': self.get_score_value('CBECE_ASSESSMENT/LanguageArtDomain' + program_cycle,
                                                           'post_test'),
            'post_CognitiveDomain': self.get_score_value(
                'CBECE_ASSESSMENT/CognitiveDomian' + program_cycle,
                'post_test'),
            'post_ScienceDomain': self.get_score_value(
                'CBECE_ASSESSMENT/ScienceDomain' + program_cycle,
                'pre_test'),
            'post_SocialEmotionalDomain': self.get_score_value('CBECE_ASSESSMENT/SocialEmotionalDomain' + program_cycle,
                                                               'post_test'),
            'post_PsychomotorDomain': self.get_score_value('CBECE_ASSESSMENT/PsychomotorDomain' + program_cycle,
                                                           'post_test'),
            'post_ArtisticDomain': self.get_score_value('CBECE_ASSESSMENT/ArtisticDomain' + program_cycle, 'post_test'),
        }

    class Meta:
        ordering = ['-id']
        verbose_name = "CB-ECE"
        verbose_name_plural = "CB-ECE"


class SelfPerceptionGrades(models.Model):
    enrollment = models.ForeignKey(
        RS,
        blank=True, null=True,
        related_name='+',
        on_delete=models.SET_NULL,
        verbose_name=_('Enrollment')
    )
    assessment_type = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Assessment type')
    )
    assessment_date = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_('Assessment date')
    )
    answers = JSONField(
        blank=True,
        null=True,
        default=dict,
        verbose_name=_('Assessment answers')
    )

    class Meta:
        ordering = ['id']
        verbose_name = "Child perception grade"
        verbose_name_plural = "Child perception grades"

    def __unicode__(self):
        return self.enrollment

    def __str__(self):
        return self.enrollment


class Inclusion(TimeStampedModel):
    CURRENT_YEAR = datetime.datetime.now().year

    MONTHS = Choices(
        ('1', _('January')),
        ('2', _('February')),
        ('3', _('March')),
        ('4', _('April')),
        ('5', _('May')),
        ('6', _('June')),
        ('7', _('July')),
        ('8', _('August')),
        ('9', _('September')),
        ('10', _('October')),
        ('11', _('November')),
        ('12', _('December')),
    )
    YES_NO = Choices(
        ('', '----------'),
        ('yes', _("Yes")),
        ('no', _("No")),
    )
    PARTICIPATION = Choices(
        ('', '----------'),
        ('no_absence', _('No Absence')),
        ('less_than_3days', _('Less than 3 absence days')),
        ('3_7_days', _('3 to 7 absence days')),
        ('7_12_days', _('7 to 12 absence days')),
        ('more_than_12days', _('More than 12 absence days')),
    )
    BARRIERS = Choices(
        ('', '----------'),
        ('Full time job to support family financially', _('Full time job to support family financially')),
        ('seasonal_work', _('Seasonal work')),
        ('cold_weather', _('Cold Weather')),
        ('sickness', _('Sickness')),
        ('security', _('Security')),
        ('family moved', _('Family moved')),
        ('Moved back to Syria', _('Moved back to Syria')),
        ('Enrolled in formal education', _('Enrolled in formal education')),
        ('marriage engagement pregnancy', _('Marriage/Engagement/Pregnancy')),
        ('violence bullying', _('Violence/Bullying')),
        ('No interest in pursuing the programme/No value', _('No interest in pursuing the programme/No value')),
    )
    HAVE_LABOUR = Choices(
        ('no', _('No')),
        ('yes_morning', _('Yes - Morning')),
        ('yes_afternoon', _('Yes - Afternoon')),
        ('yes_all_day', _('Yes - All day')),
    )
    LABOURS = Choices(
        ('', '----------'),
        ('agriculture', _('Agriculture')),
        ('building', _('Building')),
        ('manufacturing', _('Manufacturing')),
        ('retail_store', _('Retail / Store')),
        ('begging', _('Begging')),
        ('other_many_other', _(
            'Other services (hotel, restaurant, transport, personal services such as cleaning, hair care, cooking and childcare)')),
        # ('other', _('Other')),
    )
    LEARNING_RESULT = Choices(
        ('graduated_to_abln_next_round_same_level', _('Graduated to the next round, same level')),
        ('graduated_to_abln_next_round_higher_level', _('Graduated to the next round, higher level')),
        ('referred_to_bln', _('Referred to BLN')),
        ('referred_to_ybln', _('Referred to YBLN')),
        # ('referred_to_alp', _('Referred to ALP')),
        ('referred_to_cbt', _('Referred to CBT')),
        ('other', _('Other')),
    )
    MAIN_CAREGIVER = (
        ('', '----------'),
        ('mother', _('Mother')),
        ('father', _('Father')),
        ('other', _('Other')),
    )

    source_of_identification = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=Choices(
            ('Direct outreach', _('Direct outreach')),
            ('List database', _('List database')),
            ('Referral from another NGO', _('Referral from another NGO')),
            ('Referred by CP partner', _('Referred by CP partner')),
            ('Referred by youth partner', _('Referred by youth partner')),
            ('Referral from another Municipality', _('Referral from Municipality')),
            ('Family walked in to NGO', _('Family walked in to NGO')),
            ('from abln', _('FROM ABLN')),
            ('from bln', _('FROM BLN')),
            ('from cbece', _('FROM CBECE')),
            ('ocha', _('OCHA')),
            ('non unicef', _('Non - UNICEF')),
            ('RIMS', _('RIMS')),
        ),
        verbose_name=_('Source of identification of the child')
    )
    rims_case_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('RIMS Case Number')
    )
    first_attendance_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('First attendance date')
    )
    round = models.ForeignKey(
        CLMRound,
        blank=True, null=True,
        related_name='+',
        on_delete=models.SET_NULL,
        verbose_name=_('Round')
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
    location = models.CharField(
        max_length=250,
        blank=True,
        null=True,
        verbose_name=_('Location')
    )
    student = models.ForeignKey(
        Student,
        blank=False, null=True,
        related_name='+',
        on_delete=models.SET_NULL,
        verbose_name=_('Student')
    )
    disability = models.ForeignKey(
        Disability,
        blank=True, null=True,
        related_name='+',
        on_delete=models.SET_NULL,
        verbose_name=_('Disability')
    )
    have_labour = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=HAVE_LABOUR,
        verbose_name=_('Does the child participate in work?')
    )
    labour_type = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=LABOURS,
        verbose_name=_('What is the type of work ?')
    )
    participation = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=PARTICIPATION,
        verbose_name=_('Participation')
    )
    learning_result = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=LEARNING_RESULT,
        verbose_name=_('Learning result')
    )
    barriers = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=BARRIERS,
        verbose_name=_('The main barriers affecting the daily attendance and performance')
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
    registration_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('Registration date')
    )
    partner = models.ForeignKey(
        PartnerOrganization,
        on_delete=models.SET_NULL,
        blank=True, null=True,
        verbose_name=_('Partner'),
        related_name='+'
    )
    internal_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Internal number')
    )
    comments = models.TextField(
        blank=True, null=True,
        verbose_name=_('Comments')
    )
    phone_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Phone number')
    )
    phone_number_confirm = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Phone number confirm')
    )

    phone_owner = models.CharField(
        max_length=100,
        blank=False,
        null=True,
        choices=Choices(
            ('main_caregiver', _('Phone Main Caregiver')),
            ('family member', _('Family Member')),
            ('neighbors', _('Neighbors')),
            ('shawish', _('Shawish')),
        ),
        verbose_name=_('Phone Owner')
    )
    second_phone_owner = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=Choices(
            ('main_caregiver', _('Phone Main Caregiver')),
            ('family member', _('Family Member')),
            ('neighbors', _('Neighbors')),
            ('shawish', _('Shawish')),
        ),
        verbose_name=_('Second Phone Owner')
    )
    second_phone_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Second Phone number')
    )
    second_phone_number_confirm = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Second Phone number confirm')
    )

    education_status = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=Choices(
            ('out of school', _('Out of school')),
            ('enrolled in formal education but did not continue',
             _("Enrolled in formal education but did not continue")),
            ('enrolled in ABLN', _("Enrolled in ABLN")),
        ),
        verbose_name=_('Education status')
    )

    id_type = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=Choices(
            ('UNHCR Registered', _('UNHCR Registered')),
            ('UNHCR Recorded', _("UNHCR Recorded")),
            ('Syrian national ID', _("Syrian national ID")),
            ('Palestinian national ID', _("Palestinian national ID")),
            ('Lebanese national ID', _("Lebanese national ID")),
            ('Other nationality', _("Other nationality")),
            ('Child have no ID', _("Child have no ID"))
        ),
        verbose_name=_('Child ID type')
    )

    case_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Case number')
    )
    case_number_confirm = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Case number confirm')
    )

    individual_case_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Individual Case number')
    )
    individual_case_number_confirm = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Individual Case number confirm')
    )

    recorded_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Recorded number')
    )
    recorded_number_confirm = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Recorded number confirm')
    )

    other_nationality = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name=_('Specify the nationality')
    )

    national_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Lebanese ID number ')
    )
    national_number_confirm = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Lebanese ID number confirm')
    )
    syrian_national_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Syrian ID number ')
    )
    syrian_national_number_confirm = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Syrian ID number confirm')
    )
    sop_national_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Palestinian ID number ')
    )
    sop_national_number_confirm = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Palestinian ID number confirm')
    )
    no_child_id_confirmation = models.CharField(max_length=50, blank=True, null=True, )
    no_parent_id_confirmation = models.CharField(max_length=50, blank=True, null=True, )

    parent_case_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Case number')
    )
    parent_case_number_confirm = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Case number confirm')
    )

    parent_individual_case_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Individual Case number')
    )
    parent_individual_case_number_confirm = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Individual Case number confirm')
    )

    parent_national_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Lebanese ID number ')
    )
    parent_national_number_confirm = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Lebanese ID number confirm')
    )
    parent_syrian_national_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Syrian ID number ')
    )
    parent_syrian_national_number_confirm = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Syrian ID number confirm')
    )
    parent_sop_national_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Palestinian ID number ')
    )
    parent_sop_national_number_confirm = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Palestinian ID number confirm')
    )
    parent_other_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('ID number ')
    )
    parent_other_number_confirm = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('ID number confirm')
    )
    other_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Child ID number ')
    )
    other_number_confirm = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Child ID number confirm')
    )
    main_caregiver = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=MAIN_CAREGIVER,
        verbose_name=_('Main Caregiver')
    )

    main_caregiver_nationality = models.ForeignKey(
        Nationality,
        blank=False, null=True,
        related_name='+',
        on_delete=models.SET_NULL,
        verbose_name=_('Main Caregiver Nationality')
    )

    other_caregiver_relationship = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name=_('Other Caregiver Relationship')
    )

    caretaker_first_name = models.CharField(
        max_length=500,
        blank=False,
        null=True,
        verbose_name=_('Caregiver First Name')
    )
    caretaker_middle_name = models.CharField(
        max_length=500,
        blank=False,
        null=True,
        verbose_name=_('Caregiver Middle Name')
    )
    caretaker_last_name = models.CharField(
        max_length=500,
        blank=False,
        null=True,
        verbose_name=_('Caregiver Last Name')
    )
    caretaker_mother_name = models.CharField(
        max_length=500,
        blank=False,
        null=True,
        verbose_name=_('Caregiver Mother Name')
    )
    caretaker_birthday_year = models.CharField(
        max_length=4,
        blank=True,
        null=True,
        default=0,
        choices=((str(x), x) for x in range(1940, CURRENT_YEAR - 18)),
        verbose_name=_('Caregiver birthday year')
    )
    caretaker_birthday_month = models.CharField(
        max_length=2,
        blank=True,
        null=True,
        default=0,
        choices=MONTHS,
        verbose_name=_('Caregiver birthday month')
    )
    caretaker_birthday_day = models.CharField(
        max_length=2,
        blank=True,
        null=True,
        default=0,
        choices=((str(x), x) for x in range(1, 32)),
        verbose_name=_('Caregiver birthday day')
    )

    referral_programme_type_1 = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=Choices(
            ('CP (PSS and/or Case Management)', _('CP (PSS and/or Case Management)')),
            ('Health', _('Health')),
            ('WASH', _('WASH')),
            ('Specialized Services', _('Specialized Services')),
            ('Other', _('Other')),
            ('No need', _('No need')),
        ),
        verbose_name=_('Programme Type')
    )
    referral_partner_1 = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name=_('School / Center')
    )
    referral_date_1 = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('Referral date')
    )
    confirmation_date_1 = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('Date when the receiving organization confirms accepting the child (or child receiving service)')
    )

    referral_programme_type_2 = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=Choices(
            ('CP (PSS and/or Case Management)', _('CP (PSS and/or Case Management)')),
            ('Health', _('Health')),
            ('WASH', _('WASH')),
            ('Specialized Services', _('Specialized Services')),
            ('Other', _('Other')),
            ('No need', _('No need')),
        ),
        verbose_name=_('Programme Type')
    )
    referral_partner_2 = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name=_('School / Center')
    )
    referral_date_2 = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('Referral date')
    )
    confirmation_date_2 = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('Date when the receiving organization confirms accepting the child (or child receiving service)')
    )

    referral_programme_type_3 = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=Choices(
            ('CP (PSS and/or Case Management)', _('CP (PSS and/or Case Management)')),
            ('Health', _('Health')),
            ('WASH', _('WASH')),
            ('Specialized Services', _('Specialized Services')),
            ('Other', _('Other')),
            ('No need', _('No need')),
        ),
        verbose_name=_('Programme Type')
    )
    referral_partner_3 = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name=_('School / Center')
    )
    referral_date_3 = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('Referral date')
    )
    confirmation_date_3 = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('Date when the receiving organization confirms accepting the child (or child receiving service)')
    )
    additional_comments = models.TextField(
        blank=True, null=True,
        verbose_name=_('Comments')
    )
    child_dropout = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Has the child dropped out of the program?')
    )

    child_dropout_specify = models.TextField(
        blank=True, null=True,
        verbose_name=_('Please specify')
    )

    caregiver_trained_parental_engagement = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=Choices(
            ('', '----------'),
            ('Mother Only', _('Mother Only')),
            ('Father Only', _('Father Only')),
            ('Both Mother and Father', _('Both Mother and Father')),
            ('None', _('None')),
            ('Other', _('Other')),
            ('Not begun yet', _('Not begun yet')),
        ),
        verbose_name=_('Have the Caregivers been trained on the Parental Engagement Curriculum? ')
    )
    @property
    def student_fullname(self):
        if self.student:
            return self.student.full_name
        return ''

    @property
    def student_age(self):
        if self.student:
            return self.student.age
        return 0

    def get_absolute_url(self):
        return '/inclusion/edit/%d/' % self.pk

    def __unicode__(self):
        if self.student:
            return self.student.__unicode__()
        return str(self.id)

    def __str__(self):
        if self.student:
            return self.student.__str__()
        return str(self.id)

    class Meta:
        ordering = ['id']
        verbose_name = "Disability specialized"
        verbose_name_plural = "Disability specialized"


class ABLN_FC(TimeStampedModel):
    YES_NO = Choices(
        ('', '----------'),
        ('yes', _("Yes")),
        ('no', _("No")),
    )
    ACTIVITIES_REPORTED = Choices(
        ('reading', _('Reading')),
        ('writing', _('Writing')),
        ('oral_communication', _('Oral Communication')),
        ('group_work', _('Group Work')),
        ('individual_tasks', _('Individual tasks')),
        ('other', _('Other'))
    )
    SHARE_EXPECTATIONS_REASON = Choices(
        ('', '----------'),
        ('lack_connectivity', _('Lack of internet connectivity')),
        ('parents_not_interested', _('Parents are not interested in programme')),
        ('phone_not_available', _('Phone is not available at home')),
        ('parents_at_work', _('Parents at work')),
        ('parents_not_vailable', _('Parents are not available')),
        ('parents_low_literacy_level', _('Parents low literacy level')),
        ('other', _('Other'))
    )
    OBJECTIVES_VERIFIED = Choices(
        ('Video_photos', _('Video, photos')),
        ('followed_by_phone_calls', _('Followed by phone calls')),
        ('voice_messages', _('Voice messages')),
        ('other', _('Other')),
    )
    INDEPENDENTLY_EVALUATION = Choices(
        ('', '----------'),
        ('excellent', _('Excellent')),
        ('good', _('Good')),
        ('needs_support', _('Needs support')),
    )
    COMPLETE_PRINTED_PACKAGE = Choices(
        ('', '----------'),
        ('yes', _("Yes")),
        ('no', _("No")),
        ('not_required', _('Not required')),
    )
    SESSIONS_PARTICIPATED = Choices(
        ('', '----------'),
        ('participating_in_all_session', _("Participating in all session")),
        ('participating_in_some_session', _("Participating in some session")),
        ('not_participating_at_all', _('Not participating at all')),
    )
    FC_TYPE = Choices(
        ('pre-arabic', 'Pre Arabic'),
        ('pre-math', _("Pre Math")),
        ('post-arabic', _("Post Arabic")),
        ('post-math', _('Post Math')),
        ('arabic', _("Arabic")),
        ('math', _('Math')),
    )
    LESSON_MODALITY = Choices(
        ('', '----------'),
        ('Online', _('Online')),
        ('Present', _('Present')),
        ('Blended', _('Blended')),
    )
    STEPS_ACQUIRE_COMPETENCY = Choices(
        ('', '----------'),
        ('Re-explain', _("Re-explain")),
        ('Extra Howmework', _("Extra Howmework")),
        ('other', _('Other')),
    )
    enrollment = models.ForeignKey(
        ABLN,
        blank=True, null=True,
        related_name='+',
        on_delete=models.SET_NULL,
        verbose_name=_('Enrollment')
    )
    fc_type = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=FC_TYPE,
        verbose_name=_('FC Type')
    )
    facilitator_name = models.TextField(
        blank=True, null=True,
        verbose_name=_('Facilitator name')
    )
    subject_taught = models.TextField(
        blank=True, null=True,
        verbose_name=_('Subject taught')
    )
    date_of_monitoring = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('Date of monitoring')
    )
    materials_needed_available = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Did the child have these learning materials available for the lesson?')
    )
    attend_lesson = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Did the child attend the scheduled lesson?')
    )
    child_interact_teacher = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Did the child interact with the teacher during the session?')
    )
    child_interact_friends = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Did the child interact With peers?')
    )
    child_clear_responses = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Did the child provide clear responses?')
    )
    child_ask_questions = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Did the child ask questions?')
    )
    child_acquire_competency = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Did the child acquire the targeted competency?')
    )
    child_show_improvement = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Does the child show improvement in achieving the targeted competency?')
    )
    child_expected_work_independently = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Was the child expected to work independently during the lesson?')
    )
    work_independently_evaluation = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=INDEPENDENTLY_EVALUATION,
        verbose_name=_('How do you rate child performance for the current lesson:?')
    )
    complete_printed_package = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=COMPLETE_PRINTED_PACKAGE,
        verbose_name=_('Did the child complete the printed package for the Week?')
    )
    sessions_participated = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=SESSIONS_PARTICIPATED,
        verbose_name=_('How many session did this child participate in online classes this week?')
    )
    not_participating_reason = models.TextField(
        blank=True, null=True,
        verbose_name=_('not participating reason')
    )
    e_recharge_card_provided = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Was the child provided with E-Recharge cards ?')
    )
    action_to_taken = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_(
            'Any specific actions to be taken with this child before the next lesson for better participation')
    )
    action_to_taken_specify = models.TextField(
        blank=True, null=True,
        verbose_name=_('Explain')
    )
    child_needs_pss = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Does the child have any PSS/ wellbeing needs?')
    )
    child_cant_access_resources = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_(
            'Did you notice that this child did not have access to the device or resources needed to complete the lesson requirements?')
    )
    homework_after_lesson = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Was there any homework given after the lesson?')
    )
    parents_supporting_student = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Were parents supporting the student through this lesson? ')
    )
    targeted_competencies = models.TextField(
        blank=True, null=True,
        verbose_name=_('Targeted Competencies')
    )

    activities_reported = ArrayField(
        models.CharField(
            choices=ACTIVITIES_REPORTED,
            max_length=100,
            blank=True,
            null=True,
        ),
        blank=True,
        null=True,
        verbose_name=_('Activities Reported')
    )
    activities_reported_other = models.TextField(
        blank=True, null=True,
        verbose_name=_('Please specify')
    )
    share_expectations = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Did you share with the child caregiver the expectations for weekly engagement in learning?')
    )
    share_expectations_no_reason = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=SHARE_EXPECTATIONS_REASON,
        verbose_name=_('If no, why not?')
    )
    share_expectations_other_reason = models.TextField(
        blank=True, null=True,
        verbose_name=_('if Other explain')
    )
    completed_tasks = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Did the child complete the required tasks later?')
    )
    meet_objectives = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Did the child meet the current lesson objectives?')
    )
    meet_objectives_verified = ArrayField(
        models.CharField(
            choices=OBJECTIVES_VERIFIED,
            max_length=100,
            blank=True,
            null=True,
        ),
        blank=True,
        null=True,
        verbose_name=_('Explain how was this verified?')
    )
    objectives_verified_specify = models.TextField(
        blank=True, null=True,
        verbose_name=_('Please specify')
    )
    additional_notes = models.TextField(
        blank=True, null=True,
        verbose_name=_('Additional notes/ specific challenges/ follow up action/ referrals etc.')
    )
    lesson_modality = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=LESSON_MODALITY,
        verbose_name=_('Lesson Modality')
    )
    steps_acquire_competency = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=STEPS_ACQUIRE_COMPETENCY,
        verbose_name=_('Steps to help the child acquire the targeted competency')
    )

    steps_acquire_competency_other = models.TextField(
        blank=True, null=True,
        verbose_name=_('Please specify')
    )


    class Meta:
        ordering = ['-id']
        verbose_name = "FC"
        verbose_name_plural = "FC"


class BLN_FC(TimeStampedModel):
    YES_NO = Choices(
        ('', '----------'),
        ('yes', _("Yes")),
        ('no', _("No")),
    )
    ACTIVITIES_REPORTED = Choices(
        ('reading', _('Reading')),
        ('writing', _('Writing')),
        ('oral_communication', _('Oral Communication')),
        ('group_work', _('Group Work')),
        ('individual_tasks', _('Individual tasks')),
        ('other', _('Other'))
    )
    SHARE_EXPECTATIONS_REASON = Choices(
        ('', '----------'),
        ('lack_connectivity', _('Lack of internet connectivity')),
        ('parents_not_interested', _('Parents are not interested in programme')),
        ('phone_not_available', _('Phone is not available at home')),
        ('parents_at_work', _('Parents at work')),
        ('parents_not_vailable', _('Parents are not available')),
        ('parents_low_literacy_level', _('Parents low literacy level')),
        ('other', _('Other'))
    )
    OBJECTIVES_VERIFIED = Choices(
        ('Video_photos', _('Video, photos')),
        ('followed_by_phone_calls', _('Followed by phone calls')),
        ('voice_messages', _('Voice messages')),
        ('other', _('Other')),
    )
    INDEPENDENTLY_EVALUATION = Choices(
        ('', '----------'),
        ('excellent', _('Excellent')),
        ('good', _('Good')),
        ('needs_support', _('Needs support')),
    )
    COMPLETE_PRINTED_PACKAGE = Choices(
        ('', '----------'),
        ('yes', _("Yes")),
        ('no', _("No")),
        ('not_required', _('Not required')),
    )
    SESSIONS_PARTICIPATED = Choices(
        ('', '----------'),
        ('participating_in_all_session', _("Participating in all session")),
        ('participating_in_some_session', _("Participating in some session")),
        ('not_participating_at_all', _('Not participating at all')),
    )
    FC_TYPE = Choices(
        ('pre-arabic', _("Pre Arabic")),
        ('pre-math', _("Pre Math")),
        ('pre-language', _("Pre Language")),
        ('post-arabic', _("Post Arabic")),
        ('post-math', _("Post Math")),
        ('post-language', _("Post Language")),
        ('arabic', _("Arabic")),
        ('language', _("Language")),
        ('math', _("Math")),
    )
    LESSON_MODALITY = Choices(
        ('', '----------'),
        ('Online', _('Online')),
        ('Present', _('Present')),
        ('Blended', _('Blended')),
    )
    STEPS_ACQUIRE_COMPETENCY = Choices(
        ('', '----------'),
        ('Re-explain', _("Re-explain")),
        ('Extra Howmework', _("Extra Howmework")),
        ('other', _('Other')),
    )
    enrollment = models.ForeignKey(
        BLN,
        blank=True, null=True,
        related_name='+',
        on_delete=models.SET_NULL,
        verbose_name=_('Enrollment')
    )
    fc_type = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=FC_TYPE,
        verbose_name=_('FC Type')
    )
    facilitator_name = models.TextField(
        blank=True, null=True,
        verbose_name=_('Facilitator name')
    )
    subject_taught = models.TextField(
        blank=True, null=True,
        verbose_name=_('Subject taught')
    )
    date_of_monitoring = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('Date of monitoring')
    )
    materials_needed_available = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Did the child have these learning materials available for the lesson?')
    )
    attend_lesson = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Did the child attend the scheduled lesson?')
    )
    child_interact_teacher = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Did the child interact with the teacher during the session?')
    )
    child_interact_friends = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Did the child interact With peers?')
    )
    child_clear_responses = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Did the child provide clear responses?')
    )
    child_ask_questions = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Did the child ask questions?')
    )
    child_acquire_competency = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Did the child acquire the targeted competency?')
    )
    child_show_improvement = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Does the child show improvement in achieving the targeted competency?')
    )
    child_expected_work_independently = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Was the child expected to work independently during the lesson?')
    )
    work_independently_evaluation = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=INDEPENDENTLY_EVALUATION,
        verbose_name=_('How do you rate child performance for the current lesson:?')
    )
    complete_printed_package = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=COMPLETE_PRINTED_PACKAGE,
        verbose_name=_('Did the child complete the printed package for the Week?')
    )
    sessions_participated = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=SESSIONS_PARTICIPATED,
        verbose_name=_('How many session did this child participate in online classes this week?')
    )
    not_participating_reason = models.TextField(
        blank=True, null=True,
        verbose_name=_('not participating reason')
    )
    e_recharge_card_provided = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Was the child provided with E-Recharge cards ?')
    )
    action_to_taken = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_(
            'Any specific actions to be taken with this child before the next lesson for better participation')
    )
    action_to_taken_specify = models.TextField(
        blank=True, null=True,
        verbose_name=_('Explain')
    )
    child_needs_pss = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Does the child have any PSS/ wellbeing needs?')
    )
    child_cant_access_resources = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_(
            'Did you notice that this child did not have access to the device or resources needed to complete the lesson requirements?')
    )
    homework_after_lesson = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Was there any homework given after the lesson?')
    )
    parents_supporting_student = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Were parents supporting the student through this lesson? ')
    )
    targeted_competencies = models.TextField(
        blank=True, null=True,
        verbose_name=_('Targeted Competencies')
    )

    activities_reported = ArrayField(
        models.CharField(
            choices=ACTIVITIES_REPORTED,
            max_length=100,
            blank=True,
            null=True,
        ),
        blank=True,
        null=True,
        verbose_name=_('Activities Reported')
    )
    activities_reported_other = models.TextField(
        blank=True, null=True,
        verbose_name=_('Please specify')
    )
    share_expectations = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Did you share with the child caregiver the expectations for weekly engagement in learning?')
    )
    share_expectations_no_reason = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=SHARE_EXPECTATIONS_REASON,
        verbose_name=_('If no, why not?')
    )
    share_expectations_other_reason = models.TextField(
        blank=True, null=True,
        verbose_name=_('if Other explain')
    )
    completed_tasks = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Did the child complete the required tasks later?')
    )
    meet_objectives = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Did the child meet the current lesson objectives?')
    )
    meet_objectives_verified = ArrayField(
        models.CharField(
            choices=OBJECTIVES_VERIFIED,
            max_length=100,
            blank=True,
            null=True,
        ),
        blank=True,
        null=True,
        verbose_name=_('Explain how was this verified?')
    )
    objectives_verified_specify = models.TextField(
        blank=True, null=True,
        verbose_name=_('Please specify')
    )
    additional_notes = models.TextField(
        blank=True, null=True,
        verbose_name=_('Additional notes/ specific challenges/ follow up action/ referrals etc.')
    )
    lesson_modality = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=LESSON_MODALITY,
        verbose_name=_('Lesson Modality')
    )
    steps_acquire_competency = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=STEPS_ACQUIRE_COMPETENCY,
        verbose_name=_('Steps to help the child acquire the targeted competency')
    )
    steps_acquire_competency_other = models.TextField(
        blank=True, null=True,
        verbose_name=_('Please specify')
    )
    class Meta:
        ordering = ['-id']
        verbose_name = "FC"
        verbose_name_plural = "FC"


class RS_FC(TimeStampedModel):
    YES_NO = Choices(
        ('', '----------'),
        ('yes', _("Yes")),
        ('no', _("No")),
    )
    ACTIVITIES_REPORTED = Choices(
        ('reading', _('Reading')),
        ('writing', _('Writing')),
        ('oral_communication', _('Oral Communication')),
        ('group_work', _('Group Work')),
        ('individual_tasks', _('Individual tasks')),
        ('other', _('Other'))
    )
    SHARE_EXPECTATIONS_REASON = Choices(
        ('', '----------'),
        ('lack_connectivity', _('Lack of internet connectivity')),
        ('parents_not_interested', _('Parents are not interested in programme')),
        ('phone_not_available', _('Phone is not available at home')),
        ('parents_at_work', _('Parents at work')),
        ('parents_not_vailable', _('Parents are not available')),
        ('parents_low_literacy_level', _('Parents low literacy level')),
        ('other', _('Other'))
    )
    OBJECTIVES_VERIFIED = Choices(
        ('Video_photos', _('Video, photos')),
        ('followed_by_phone_calls', _('Followed by phone calls')),
        ('voice_messages', _('Voice messages')),
        ('other', _('Other')),
    )
    INDEPENDENTLY_EVALUATION = Choices(
        ('', '----------'),
        ('excellent', _('Excellent')),
        ('good', _('Good')),
        ('needs_support', _('Needs support')),
    )
    COMPLETE_PRINTED_PACKAGE = Choices(
        ('', '----------'),
        ('yes', _("Yes")),
        ('no', _("No")),
        ('not_required', _('Not required')),
    )
    SESSIONS_PARTICIPATED = Choices(
        ('', '----------'),
        ('participating_in_all_session', _("Participating in all session")),
        ('participating_in_some_session', _("Participating in some session")),
        ('not_participating_at_all', _('Not participating at all')),
    )
    FC_TYPE = Choices(
        ('pre-arabic', _("Pre Arabic")),
        ('pre-math', _("Pre Math")),
        ('pre-language', _("Pre Language")),
        ('pre-science', _("Pre Science")),
        ('pre-biology', _("Pre Biology")),
        ('pre-chemistry', _("Pre Chemistry")),
        ('pre-physics', _("Pre Physics")),
        ('post-arabic', _("Post Arabic")),
        ('post-math', _("Post Math")),
        ('post-language', _("Post Language")),
        ('post-science', _("Post Science")),
        ('post-biology', _("Post Biology")),
        ('post-chemistry', _("Post Chemistry")),
        ('post-physics', _("Post Physics")),
        ('arabic', _("Arabic")),
        ('language', _("Language")),
        ('math', _("Math")),
        ('science', _("Science")),
        ('biology', _("Biology")),
        ('chemistry', _("Chemistry")),
        ('physics', _("Physics")),
    )
    LESSON_MODALITY = Choices(
        ('', '----------'),
        ('Online', _('Online')),
        ('Present', _('Present')),
        ('Blended', _('Blended')),
    )
    STEPS_ACQUIRE_COMPETENCY = Choices(
        ('', '----------'),
        ('Re-explain', _("Re-explain")),
        ('Extra Howmework', _("Extra Howmework")),
        ('other', _('Other')),
    )
    enrollment = models.ForeignKey(
        RS,
        blank=True, null=True,
        related_name='+',
        on_delete=models.SET_NULL,
        verbose_name=_('Enrollment')
    )
    fc_type = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=FC_TYPE,
        verbose_name=_('FC Type')
    )
    facilitator_name = models.TextField(
        blank=True, null=True,
        verbose_name=_('Facilitator name')
    )
    subject_taught = models.TextField(
        blank=True, null=True,
        verbose_name=_('Subject taught')
    )
    date_of_monitoring = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('Date of monitoring')
    )
    materials_needed_available = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Did the child have these learning materials available for the lesson?')
    )
    attend_lesson = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Did the child attend the scheduled lesson?')
    )
    child_interact_teacher = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Did the child interact with the teacher during the session?')
    )
    child_interact_friends = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Did the child interact With peers?')
    )
    child_clear_responses = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Did the child provide clear responses?')
    )
    child_ask_questions = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Did the child ask questions?')
    )
    child_acquire_competency = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Did the child acquire the targeted competency?')
    )
    child_show_improvement = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Does the child show improvement in achieving the targeted competency?')
    )
    child_expected_work_independently = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Was the child expected to work independently during the lesson?')
    )
    work_independently_evaluation = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=INDEPENDENTLY_EVALUATION,
        verbose_name=_('How do you rate child performance for the current lesson:?')
    )
    complete_printed_package = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=COMPLETE_PRINTED_PACKAGE,
        verbose_name=_('Did the child complete the printed package for the Week?')
    )
    sessions_participated = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=SESSIONS_PARTICIPATED,
        verbose_name=_('How many session did this child participate in online classes this week?')
    )
    not_participating_reason = models.TextField(
        blank=True, null=True,
        verbose_name=_('not participating reason')
    )
    e_recharge_card_provided = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Was the child provided with E-Recharge cards ?')
    )
    action_to_taken = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_(
            'Any specific actions to be taken with this child before the next lesson for better participation')
    )
    action_to_taken_specify = models.TextField(
        blank=True, null=True,
        verbose_name=_('Explain')
    )
    child_needs_pss = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Does the child have any PSS/ wellbeing needs?')
    )
    child_cant_access_resources = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_(
            'Did you notice that this child did not have access to the device or resources needed to complete the lesson requirements?')
    )
    homework_after_lesson = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Was there any homework given after the lesson?')
    )
    parents_supporting_student = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Were parents supporting the student through this lesson? ')
    )
    targeted_competencies = models.TextField(
        blank=True, null=True,
        verbose_name=_('Targeted Competencies')
    )

    activities_reported = ArrayField(
        models.CharField(
            choices=ACTIVITIES_REPORTED,
            max_length=100,
            blank=True,
            null=True,
        ),
        blank=True,
        null=True,
        verbose_name=_('Activities Reported')
    )
    activities_reported_other = models.TextField(
        blank=True, null=True,
        verbose_name=_('Please specify')
    )
    share_expectations = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Did you share with the child caregiver the expectations for weekly engagement in learning?')
    )
    share_expectations_no_reason = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=SHARE_EXPECTATIONS_REASON,
        verbose_name=_('If no, why not?')
    )
    share_expectations_other_reason = models.TextField(
        blank=True, null=True,
        verbose_name=_('if Other explain')
    )
    completed_tasks = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Did the child complete the required tasks later?')
    )
    meet_objectives = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Did the child meet the current lesson objectives?')
    )
    meet_objectives_verified = ArrayField(
        models.CharField(
            choices=OBJECTIVES_VERIFIED,
            max_length=100,
            blank=True,
            null=True,
        ),
        blank=True,
        null=True,
        verbose_name=_('Explain how was this verified?')
    )
    objectives_verified_specify = models.TextField(
        blank=True, null=True,
        verbose_name=_('Please specify')
    )
    additional_notes = models.TextField(
        blank=True, null=True,
        verbose_name=_('Additional notes/ specific challenges/ follow up action/ referrals etc.')
    )
    lesson_modality = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=LESSON_MODALITY,
        verbose_name=_('Lesson Modality')
    )
    steps_acquire_competency = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=STEPS_ACQUIRE_COMPETENCY,
        verbose_name=_('Steps to help the child acquire the targeted competency')
    )

    steps_acquire_competency_other = models.TextField(
        blank=True, null=True,
        verbose_name=_('Please specify')
    )
    class Meta:
        ordering = ['-id']
        verbose_name = "FC"
        verbose_name_plural = "FC"


class CBECE_FC(TimeStampedModel):
    YES_NO = Choices(
        ('', '----------'),
        ('yes', _("Yes")),
        ('no', _("No")),
    )
    ACTIVITIES_REPORTED = Choices(
        ('reading', _('Reading')),
        ('writing', _('Writing')),
        ('oral_communication', _('Oral Communication')),
        ('group_work', _('Group Work')),
        ('individual_tasks', _('Individual tasks')),
        ('other', _('Other'))
    )
    SHARE_EXPECTATIONS_REASON = Choices(
        ('', '----------'),
        ('lack_connectivity', _('Lack of internet connectivity')),
        ('parents_not_interested', _('Parents are not interested in programme')),
        ('phone_not_available', _('Phone is not available at home')),
        ('parents_at_work', _('Parents at work')),
        ('parents_not_vailable', _('Parents are not available')),
        ('parents_low_literacy_level', _('Parents low literacy level')),
        ('other', _('Other'))
    )
    OBJECTIVES_VERIFIED = Choices(
        ('Video_photos', _('Video, photos')),
        ('followed_by_phone_calls', _('Followed by phone calls')),
        ('voice_messages', _('Voice messages')),
        ('other', _('Other')),
    )
    INDEPENDENTLY_EVALUATION = Choices(
        ('', '----------'),
        ('excellent', _('Excellent')),
        ('good', _('Good')),
        ('needs_support', _('Needs support')),
    )
    COMPLETE_PRINTED_PACKAGE = Choices(
        ('', '----------'),
        ('yes', _("Yes")),
        ('no', _("No")),
        ('not_required', _('Not required')),
    )
    SESSIONS_PARTICIPATED = Choices(
        ('', '----------'),
        ('participating_in_all_session', _("Participating in all session")),
        ('participating_in_some_session', _("Participating in some session")),
        ('not_participating_at_all', _('Not participating at all')),
    )
    FC_TYPE = Choices(
        ('pre-arabic', _("Pre Arabic")),
        ('pre-math', _("Pre Math")),
        ('pre-language', _("Pre Language")),
        ('post-arabic', _("Post Arabic")),
        ('post-math', _("Post Math")),
        ('post-language', _("Post Language")),
        ('arabic', _("Arabic")),
        ('language', _("Language")),
        ('math', _("Math")),
    )
    LESSON_MODALITY = Choices(
        ('', '----------'),
        ('Online', _('Online')),
        ('Present', _('Present')),
        ('Blended', _('Blended')),
    )
    STEPS_ACQUIRE_COMPETENCY = Choices(
        ('', '----------'),
        ('Re-explain', _("Re-explain")),
        ('Extra Howmework', _("Extra Howmework")),
        ('other', _('Other')),
    )
    enrollment = models.ForeignKey(
        CBECE,
        blank=True, null=True,
        related_name='+',
        on_delete=models.SET_NULL,
        verbose_name=_('Enrollment')
    )
    fc_type = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=FC_TYPE,
        verbose_name=_('FC Type')
    )
    facilitator_name = models.TextField(
        blank=True, null=True,
        verbose_name=_('Facilitator name')
    )
    subject_taught = models.TextField(
        blank=True, null=True,
        verbose_name=_('Subject taught')
    )
    date_of_monitoring = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('Date of monitoring')
    )
    materials_needed_available = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Did the child have these learning materials available for the lesson?')
    )
    attend_lesson = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Did the child attend the scheduled lesson?')
    )
    child_interact_teacher = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Did the child interact with the teacher during the session?')
    )
    child_interact_friends = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Did the child interact With peers?')
    )
    child_clear_responses = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Did the child provide clear responses?')
    )
    child_ask_questions = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Did the child ask questions?')
    )
    child_acquire_competency = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Did the child acquire the targeted competency?')
    )
    child_show_improvement = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Does the child show improvement in achieving the targeted competency?')
    )
    child_expected_work_independently = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Was the child expected to work independently during the lesson?')
    )
    work_independently_evaluation = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=INDEPENDENTLY_EVALUATION,
        verbose_name=_('How do you rate child performance for the current lesson:?')
    )
    complete_printed_package = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=COMPLETE_PRINTED_PACKAGE,
        verbose_name=_('Did the child complete the printed package for the Week?')
    )
    sessions_participated = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=SESSIONS_PARTICIPATED,
        verbose_name=_('How many session did this child participate in online classes this week?')
    )
    not_participating_reason = models.TextField(
        blank=True, null=True,
        verbose_name=_('not participating reason')
    )
    e_recharge_card_provided = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Was the child provided with E-Recharge cards ?')
    )
    action_to_taken = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_(
            'Any specific actions to be taken with this child before the next lesson for better participation')
    )
    action_to_taken_specify = models.TextField(
        blank=True, null=True,
        verbose_name=_('Explain')
    )
    child_needs_pss = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Does the child have any PSS/ wellbeing needs?')
    )
    child_cant_access_resources = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_(
            'Did you notice that this child did not have access to the device or resources needed to complete the lesson requirements?')
    )
    homework_after_lesson = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Was there any homework given after the lesson?')
    )
    parents_supporting_student = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Were parents supporting the student through this lesson? ')
    )
    targeted_competencies = models.TextField(
        blank=True, null=True,
        verbose_name=_('Targeted Competencies')
    )

    activities_reported = ArrayField(
        models.CharField(
            choices=ACTIVITIES_REPORTED,
            max_length=100,
            blank=True,
            null=True,
        ),
        blank=True,
        null=True,
        verbose_name=_('Activities Reported')
    )
    activities_reported_other = models.TextField(
        blank=True, null=True,
        verbose_name=_('Please specify')
    )
    share_expectations = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Did you share with the child caregiver the expectations for weekly engagement in learning?')
    )
    share_expectations_no_reason = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=SHARE_EXPECTATIONS_REASON,
        verbose_name=_('If no, why not?')
    )
    share_expectations_other_reason = models.TextField(
        blank=True, null=True,
        verbose_name=_('if Other explain')
    )
    completed_tasks = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Did the child complete the required tasks later?')
    )
    meet_objectives = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Did the child meet the current lesson objectives?')
    )
    meet_objectives_verified = ArrayField(
        models.CharField(
            choices=OBJECTIVES_VERIFIED,
            max_length=100,
            blank=True,
            null=True,
        ),
        blank=True,
        null=True,
        verbose_name=_('Explain how was this verified?')
    )
    objectives_verified_specify = models.TextField(
        blank=True, null=True,
        verbose_name=_('Please specify')
    )
    additional_notes = models.TextField(
        blank=True, null=True,
        verbose_name=_('Additional notes/ specific challenges/ follow up action/ referrals etc.')
    )
    lesson_modality = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=LESSON_MODALITY,
        verbose_name=_('Lesson Modality')
    )
    steps_acquire_competency = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=STEPS_ACQUIRE_COMPETENCY,
        verbose_name=_('Steps to help the child acquire the targeted competency')
    )

    steps_acquire_competency_other = models.TextField(
        blank=True, null=True,
        verbose_name=_('Please specify')
    )
    class Meta:
        ordering = ['-id']
        verbose_name = "FC"
        verbose_name_plural = "FC"


class GeneralQuestionnaire(TimeStampedModel):
    GENDER = Choices(
        ('Male', _('Male')),
        ('Female', _('Female')),
    )
    YES_NO = Choices(
        (1, _("Yes")),
        (0, _("No"))
    )
    PROGRAMME_LEVEL_GRADE = Choices(
        ('CBECE Level 3', _("CBECE Level 3")),
        ('BLN Level 1', _("BLN Level 1")),
        ('BLN Level 2', _("BLN Level 2")),
        ('BLN Level 3', _("BLN Level 3")),
        ('ABLN Level 1', _("ABLN Level 1")),
        ('ABLN Level 2', _("ABLN Level 2")),
        ('RS grade (6,7,8,9)', _("RS grade (6,7,8,9)")),
    )
    RESOURCE_TYPE = Choices(
        ('Hi-tech/online', _('Hi-tech/online')),
        ('Low-tech/offline', _('Low-tech/offline')),
        ('Hybrid Approach (combination of Both High and Low Tech)',
         _('Hybrid Approach (combination of Both High and Low Tech)'))
    )

    SOURCE_OF_CONTENT = Choices(
        ('Learning passport', _('Learning passport')),
        ('Akelius Digital Lanaguage Course', _('Akelius Digital Lanaguage Course')),
        ('Youtube Videos', _('Youtube Videos')),
        ('Other', _('Other'))
    )
    ONLINE_PLATFORM_USED = Choices(
        ('WhatsApp', _('WhatsApp')),
        ('Zoom', _('Zoom')),
        ('Skype', _('Skype')),
        ('Teams', _('Teams')),
        ('Other', _('Other'))
    )
    REMOTE_LEARNING_PER_WEEK = Choices(
        ('One time per week', _('One time per week')),
        ('2 times per week', _('2 times per week')),
        ('3 times per week', _('3 times per week')),
        ('4 times per week', _('4 times per week')),
        ('5 times per week', _('5 times per week'))
    )
    REMOTE_LEARNING_DURATION = Choices(
        ('Less than 15 minutes', _('Less than 15 minutes')),
        ('15-30 minutes', _('15-30 minutes')),
        ('30-45 minutes', _('30-45 minutes')),
        ('45-60 minutes', _('45-60 minutes')),
    )

    OFFLINE_MATERIALS_USED = Choices(
        ('Printed materials', _('Printed materials')),
        ('Regulated textbooks', _('Regulated textbooks')),
        ('Other', _('Other')),
    )
    ENGAGE_CHILD_HOW = Choices(
        ('Phone calls', _('Phone calls')),
        ('Home visits', _('Home visits')),
        ('Other', _('Other')),
    )
    OFFLINE_ENGAGE_CHILD_FREQUENCY = Choices(
        ('One time per week', _('One time per week')),
        ('2 times per week', _('2 times per week')),
        ('Other', _('Other'))
    )
    HOW_CHILD_ASSESSED = Choices(
        ('In writing', _('In writing')),
        ('Orally', _('Orally')),
        ('Other', _('Other'))
    )
    CHILD_ASSESSED_WRITING = Choices(
        ('Test shared by photo, whatsapp', _('Test shared by photo, whatsapp')),
        ('Worksheet filled at home and collected for correction', _('Worksheet filled at home and collected for correction')),
        ('Online Short test google forms, etc', _('Online Short test google forms, etc'))
    )
    CHILD_ASSESSED_ORALLY = Choices(
        ('Response via whatsapp voice messages', _('Response via whatsapp voice messages')),
        ('Answering teacher questions', _('Answering teachers questions')),
        ('Video recorded and shared', _('Video recorded and shared')),
        ('Parents responses over the phone', _('Parents responses over the phone'))
    )
    RESOURCES_USED_REASONS = Choices(
        ('not available', _('not available')),
        ('Not culturally appropriate', _('Not culturally appropriate')),
        ('Other', _('Other'))
    )
    RECEIVED_COVID_INFO_HOW = Choices(
        ('WhatsApp group', _('WhatsApp group')),
        ('Hard copy', _('Hard copy')),
        ('Discussion', _('Discussion'))
    )
    RECEIVED_COVID_INFO_HOW_OFTEN = Choices(
        ('once per week', _('once per week')),
        ('twice per week', _('Hard copy')),
        ('once per month', _('once per month')),
        ('twice per month', _('twice per month')),
        ('other', _('other'))
    )
    facilitator_full_name = models.TextField(
        blank=True, null=True,
        verbose_name=_('Facilitator Full Name')
    )
    subject = models.TextField(
        blank=True, null=True,
        verbose_name=_('Subject')
    )
    activities_reported_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('Activities Reported Date')
    )
    gender = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=GENDER,
        verbose_name=_('Gender')
    )
    Organization = models.TextField(
        blank=True, null=True,
        verbose_name=_('Organization')
    )
    programme_level_grade = ArrayField(
        models.CharField(
            choices=PROGRAMME_LEVEL_GRADE,
            max_length=50,
            blank=True,
            null=True,
        ),
        blank=True,
        null=True,
        verbose_name=_('Programme Level/Grade')
    )

    lessons_follow_blended = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Do your lessons follow a blended approach, using online and offline learning?')
    )
    lessons_follow_blended_explain = models.TextField(
        blank=True, null=True,
        verbose_name=_('Explain')
    )
    girls_attending = models.IntegerField(
        blank=True,
        null=True,
        verbose_name=_('Number of Girls attendeding this Group/Class?')
    )
    boys_attending = models.IntegerField(
        blank=True,
        null=True,
        verbose_name=_('Number of Boys attendeding this Group/Class?')
    )
    engage_parents_caregivers = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Did you engage with parents/caregivers to prepare them for their role during this round?')
    )
    resource_type = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=RESOURCE_TYPE,
        verbose_name=_('Type of Resources used')
    )
    content_source_used = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=SOURCE_OF_CONTENT,
        verbose_name=_('What source of content do you use ?')
    )
    content_source_other_specify = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('Please specify')
    )

    online_platform_use = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Do you use online platforms to implement remote learning')
    )
    online_platform_used = ArrayField(
        models.CharField(
            choices=ONLINE_PLATFORM_USED,
            max_length=50,
            blank=True,
            null=True,
        ),
        blank=True,
        null=True,
        verbose_name=_('what online platforms do you use to implement remote learning')
    )
    online_platform_other_specify = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('Please specify')
    )
    remote_learning_per_week = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=REMOTE_LEARNING_PER_WEEK,
        verbose_name=_('Number of times per week')
    )
    remote_learning_duration = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=REMOTE_LEARNING_DURATION,
        verbose_name=_('How long are the remote learning sessions generally?')
    )
    children_provided_guidlines = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Were the children provided with the neccassary guidelines and login information?')
    )
    offline_materials_used = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=OFFLINE_MATERIALS_USED,
        verbose_name=_(' what materials were used? ')
    )
    offline_materials_other_specify = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('Please specify')
    )
    engage_child_how = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=ENGAGE_CHILD_HOW,
        verbose_name=_('How do you engage with the child')
    )
    engage_child_other_specify = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('Please specify')
    )
    offline_engage_child_frequency = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=OFFLINE_ENGAGE_CHILD_FREQUENCY,
        verbose_name=_('Number of times per week')
    )
    offline_engage_child_frequency_specify = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('Please specify')
    )

    how_child_assessed = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=HOW_CHILD_ASSESSED,
        verbose_name=_('How was the child assessed on achieving the targeted competency/ies?')
    )
    child_assessed_writing = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=CHILD_ASSESSED_WRITING,
        verbose_name=_('In writing')
    )
    child_assessed_orally = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=CHILD_ASSESSED_ORALLY,
        verbose_name=_('Orally')
    )
    how_child_assessed_specify = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('Please specify')
    )
    resources_used_represent_participants = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Do the stories, resources, videos, examples and other resources used represent both men/boys and women/girls as active participants? ')
    )
    resources_used_reasons = ArrayField(
            models.CharField(
                choices=RESOURCES_USED_REASONS,
                max_length=50,
                blank=True,
                null=True,
            ),
            blank=True,
            null=True,
            verbose_name=_('Reasons')
    )
    resources_used_other_specify = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('Please specify')
    )

    teacher_equal_participation = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Does the teacher ensure equal participation of girls and boys?')
    )
    women_included_learning_materials = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Are women included as role models, leaders and historical figures in learning materials?')
    )
    boys_girls_family_paticipate = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Did both girls and boys in the same family participate in the class and have access to the phone/ device/resources? ')
    )
    child_receive_covid_information = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Did the child receive any information on COVID-19 awareness and preventive measures (including vaccine)')
    )
    child_receive_covid_information_how = ArrayField(
            models.CharField(
                choices=RECEIVED_COVID_INFO_HOW,
                max_length=50,
                blank=True,
                null=True,
            ),
            blank=True,
            null=True,
            verbose_name=_('How was it received')
    )
    child_receive_covid_information_how_often = ArrayField(
            models.CharField(
                choices=RECEIVED_COVID_INFO_HOW_OFTEN,
                max_length=50,
                blank=True,
                null=True,
            ),
            blank=True,
            null=True,
            verbose_name=_('How often')
    )
    child_receive_covid_information_specify = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('Be more specific about what was discussed')
    )
    parents_receive_covid_information = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Did the child receive any information on COVID-19 awareness and preventive measures (including vaccine)')
    )
    parents_receive_covid_information_how = ArrayField(
            models.CharField(
                choices=RECEIVED_COVID_INFO_HOW,
                max_length=50,
                blank=True,
                null=True,
            ),
            blank=True,
            null=True,
            verbose_name=_('How was it received')
    )
    parents_receive_covid_information_how_often = ArrayField(
            models.CharField(
                choices=RECEIVED_COVID_INFO_HOW_OFTEN,
                max_length=50,
                blank=True,
                null=True,
            ),
            blank=True,
            null=True,
            verbose_name=_('How often')
    )
    child_family_covid_challenges = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Do you think that the child and/or his/her family have any issues/challenges related to COVID-19')
    )
    child_family_covid_challenges_specify = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('Please explain')
    )

    def get_absolute_url(self):
        return '/general_questionnaire/edit/%d/' % self.pk


    # def __unicode__(self):
    #     if self.student:
    #         return self.student.__unicode__()
    #     return str(self.id)

    class Meta:
        ordering = ['id']
        verbose_name = "General Questionnaire"
        verbose_name_plural = "General Questionnaire"
