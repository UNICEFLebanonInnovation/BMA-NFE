# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, division
import datetime

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.db.models import JSONField
from django.contrib.postgres.fields import ArrayField

from model_utils import Choices
from model_utils.models import TimeStampedModel

from student_registration.students.models import Student, Nationality
from student_registration.locations.models import Location
from student_registration.schools.models import (
    School,
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
        """Return the student's full name for display.

        Returns:
            str: Full name composed by the related ``Student`` instance or an empty string when missing.
        """
        if self.student:
            return self.student.full_name
        return ''

    @property
    def student_age(self):
        """Return the student's current age.

        Returns:
            int: Age pulled from the related ``Student`` instance, or ``0`` if unavailable.
        """
        if self.student:
            return self.student.age
        return 0

    @property
    def assessment_improvement(self):
        """Calculate percentage improvement between pre and post assessments.

        Returns:
            float | str: Percentage change between ``pre_test_score`` and ``post_test_score`` or ``0.0`` when data is missing
            or invalid.
        """
        if self.pre_test and self.post_test:
            try:
                return '{}{}'.format(
                    round(((float(self.post_test_score) - float(self.pre_test_score)) /
                           float(self.pre_test_score)) * 100.0, 2), '%')
            except ZeroDivisionError:
                return 0.0
        return 0.0

    def get_absolute_url(self):
        """Resolve the edit URL for this enrollment.

        Returns:
            str: Absolute URL path pointing to the edit view for this instance.
        """
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
        """Aggregate assessment answers into a total score.

        Args:
            keys (Iterable[str]): Question keys to extract from the assessment payload.
            stage (str): Assessment stage name (e.g., ``pre_test`` or ``post_test``) used to select the stored answers.

        Returns:
            None: Updates the ``<stage>_score`` attribute in place.
        """
        assessment = getattr(self, stage, 'pre_test')
        score = stage + '_score'
        marks = {key: float(assessment.get(key, 0)) for key in keys}
        total = sum(marks.values())
        setattr(self, score, total)

    def get_score_value(self, key, stage):
        """Fetch a numeric score for a single assessment key.

        Args:
            key (str): Question identifier to read from the assessment data.
            stage (str): Assessment stage name used to select the stored answers.

        Returns:
            float: Score value for the question; returns ``0`` when data is unavailable.
        """
        assessment = getattr(self, stage, 'pre_test')
        if assessment:
            return float(assessment.get(key, 0))
        return 0

    class Meta:
        abstract = True


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
        """Compute aggregate scores for the bridging assessment.

        Args:
            stage (str): Assessment stage label (``pre_test`` or ``post_test``).

        Returns:
            None: Delegates to :py:meth:`score` to set the ``<stage>_score`` field.
        """
        keys = [
            'Bridging_ASSESSMENT/arabic',
            'Bridging_ASSESSMENT/math',
            'Bridging_ASSESSMENT/social_emotional',
            'Bridging_ASSESSMENT/psychomotor',
            'Bridging_ASSESSMENT/artistic',
        ]
        super(Bridging, self).score(keys, stage)

    def assessment_form(self, stage, assessment_slug, callback=''):
        """Generate an assessment link for a given stage.

        Args:
            stage (str): Assessment status to embed in the URL (e.g., ``pre_test``).
            assessment_slug (str): Slug of the :class:`Assessment` record to fetch the form URL.
            callback (str, optional): URL to return to after submission. Defaults to an empty string.

        Returns:
            str: Fully formed URL to launch the assessment form, or an empty string when the assessment is missing.
        """
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
        """Calculate improvement percentage for a specific learning domain.

        Args:
            domain_mame (str): Key suffix representing the domain (e.g., ``arabic`` or ``math``).

        Returns:
            float: Percentage improvement between pre- and post-test values for the domain, or ``0.0`` when unavailable.
        """
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
        """Return the stored assessment value for a given key.

        Args:
            key (str): Domain or question key without the ``Bridging_ASSESSMENT/`` prefix.
            stage (str): Assessment stage label used to select the dataset.

        Returns:
            Any: Raw value from the assessment payload, or ``0`` if not found.
        """
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
        """Build the pre-assessment form URL for the enrollment.

        Returns:
            str: URL string targeting the pre-test form.
        """
        return self.assessment_form(stage='pre_test', assessment_slug='Bridging_pre_test')

    def post_assessment_form(self):
        """Build the post-assessment form URL for the enrollment.

        Returns:
            str: URL string targeting the post-test form.
        """
        return self.assessment_form(stage='post_test', assessment_slug='Bridging_post_test')

    @property
    def attendance_days(self):
        """Count attended days for the enrollment during the round."""
        return Bridging.get_attendance_days(self.student, self.round.start_date_bridging, self.round.end_date_bridging)

    @staticmethod
    def get_attendance_days(student_id, start_date, end_date):
        """Return attended days for a student within a date range.

        Args:
            student_id (int | Student): Target student identifier or instance.
            start_date (date): Start of the attendance window.
            end_date (date): End of the attendance window.

        Returns:
            int: Number of days where the student was marked as attended.
        """
        from student_registration.attendances.models import CLMAttendanceStudent
        if student_id and start_date and end_date:
            # __iexact: the model's choices say 'yes'/'no' but every writer -
            # clm.utils and bridging/attendance.js - stores 'Yes'/'No', so an
            # exact lowercase match returned 0 attended days for every student.
            return CLMAttendanceStudent.objects.filter(student=student_id,
                                                       attended__iexact='yes',
                                                       attendance_day__attendance_date__range=(start_date, end_date)
                                                       ).count()
        return 0

    @property
    def total_absent_days(self):
        """Return total absence days recorded for the enrollment."""
        return Bridging.get_total_absent_days(self.student.id, self.round.id)

    @staticmethod
    def get_total_absent_days(student_id, round_id):
        """Fetch total absence days for a student and round combination.

        Args:
            student_id (int): Identifier of the student to query.
            round_id (int): Identifier of the round to scope results.

        Returns:
            int: Total absence day count or ``0`` when no record exists.
        """
        result = 0
        from student_registration.attendances.models import CLMStudentTotalAttendance
        if student_id and round_id:
            attendance_days = CLMStudentTotalAttendance.objects.filter(student_id=student_id, round_id=round_id).first()
            if attendance_days:
                result = attendance_days.total_absence_days
        return result

    @property
    def max_consecutive_absence(self):
        """Return the maximum consecutive absence days."""
        return Bridging.get_max_consecutive_absence(self.student.id, self.round.id)

    @staticmethod
    def get_max_consecutive_absence(student_id, round_id):
        """Determine the highest consecutive absence streak for a student.

        Args:
            student_id (int): Identifier of the student to evaluate.
            round_id (int): Identifier of the round that holds attendance records.

        Returns:
            int: Maximum number of consecutive absent days or ``0`` when none are found.
        """
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
        """Indicate if the enrollment exceeded ten consecutive absence days."""
        return Bridging.get_more_than_ten_consecutive_absence(self.student.id, self.round.id)

    @staticmethod
    def get_more_than_ten_consecutive_absence(student_id, round_id):
        """Check whether a student has ten or more consecutive absences in a round.

        Args:
            student_id (int): Identifier of the student to evaluate.
            round_id (int): Identifier of the round to scope attendance.

        Returns:
            bool: ``True`` when a streak of at least ten absences exists; otherwise ``False``.
        """
        result = False
        from student_registration.attendances.models import CLMStudentAbsences
        if student_id and round_id:
            attendance_days = CLMStudentAbsences.objects.filter(student_id=student_id, round_id=round_id, consecutive_absence_days__gte=10).exists()
            if attendance_days:
                result = True
        return result

    @property
    def period_out_school(self):
        """Return the number of days the student was out of school before the round start."""
        return Bridging.get_period_out_school(self.student, self.miss_school_date, self.round.start_date_bridging)

    @staticmethod
    def get_period_out_school(student_id, miss_school_date, round_start_date):
        """Calculate the duration out of school before enrollment.

        Args:
            student_id (int | Student): Student to measure.
            miss_school_date (date): Date when the student stopped attending school.
            round_start_date (date): Start date of the current CLM round.

        Returns:
            int: Number of days between ``miss_school_date`` and ``round_start_date`` or ``0`` when inputs are missing.
        """
        if student_id and miss_school_date and round_start_date:
            return (miss_school_date - round_start_date).days
        return 0

    class Meta:
        ordering = ['student__first_name', 'student__father_name', 'student__last_name']
        verbose_name = "Bridging"
        verbose_name_plural = "Bridging"
