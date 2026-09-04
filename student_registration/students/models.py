from __future__ import unicode_literals, absolute_import, division
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.postgres.fields import ArrayField

from model_utils import Choices
from model_utils.models import TimeStampedModel
from .utils import *
from django.core.exceptions import ValidationError
from datetime import datetime, date
from django.core.exceptions import ValidationError

class Nationality(models.Model):
    name = models.CharField(max_length=45, unique=True)
    code = models.CharField(max_length=5, null=True)
    name_en = models.CharField(max_length=45, unique=True, null=True)

    class Meta:
        ordering = ['id']
        verbose_name_plural = "Nationalities"

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name


class IDType(models.Model):
    name = models.CharField(max_length=45, unique=True)
    active = models.BooleanField(blank=True, default=False)

    class Meta:
        ordering = ['id']
        verbose_name = "ID Type"
        verbose_name_plural = 'ID Types'

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name


class Labour(models.Model):
    name = models.CharField(max_length=45, unique=True)

    class Meta:
        ordering = ['id']
        verbose_name = "Labour"

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name


class Person(TimeStampedModel):

    def clean(self):
        if self.birthday_year and self.birthday_month and self.birthday_day:
            try:
                birth_date = date(
                    int(self.birthday_year),
                    int(self.birthday_month),
                    int(self.birthday_day)
                )
            except ValueError:
                raise ValidationError({'birthday_day': 'Invalid birth date.'})

            if birth_date > date.today():
                raise ValidationError({'birthday_day': 'Birth date cannot be in the future.'})
            

    CURRENT_YEAR = datetime.now().year

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

    GENDER = Choices(
        ('Male', _('Male')),
        ('Female', _('Female')),
    )
    FAMILY_STATUS = Choices(
        ('married', _('Married')),
        ('engaged', _('Engaged')),
        ('divorced', _('Divorced')),
        ('widower', _('Widower')),
        ('single', _('Single')),
    )

    STUDENT_INCOME = Choices(
        ('', '----------'),
        ('5 USD or Less', _('5 USD or Less')),
        ('5-20 USD', _('5-20 USD')),
        ('20-50 USD', _('20-50 USD')),
        ('50-100 USD', _('50-100 USD')),
        ('More than 100 USD', _('More than 100 USD')),

    )

    first_name = models.CharField(
        max_length=64,
        db_index=True,
        blank=True, null=True,
        verbose_name=_('First name')
    )
    last_name = models.CharField(
        max_length=64,
        db_index=True,
        blank=True, null=True,
        verbose_name=_('Last name')
    )
    father_name = models.CharField(
        max_length=64,
        db_index=True,
        blank=True, null=True,
        verbose_name=_('Father name')
    )
    mother_fullname = models.CharField(
        max_length=64,
        db_index=True,
        blank=True, null=True,
        verbose_name=_('Mother fullname')
    )
    mother_firstname = models.CharField(max_length=64, blank=True, null=True)
    mother_lastname = models.CharField(max_length=64, blank=True, null=True)
    sex = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=GENDER,
        verbose_name=_('Sex')
    )
    birthday_year = models.CharField(
        max_length=4,
        blank=True,
        null=True,
        default=0,
        choices=((str(x), x) for x in range(1990, datetime.now().year)),
        verbose_name=_('Birthday year')
    )
    birthday_month = models.CharField(
        max_length=2,
        blank=True,
        null=True,
        default=0,
        choices=MONTHS,
        verbose_name=_('Birthday month')
    )
    birthday_day = models.CharField(
        max_length=2,
        blank=True,
        null=True,
        default=0,
        choices=((str(x), x) for x in range(1, 32)),
        verbose_name=_('Birthday day')
    )
    place_of_birth = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name=_('Place of birth')
    )
    family_status = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=FAMILY_STATUS,
        verbose_name=_('Family status')
    )
    have_children = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=Choices((1, _("Yes")), (0, _("No"))),
        verbose_name=_('Have children')
    )
    phone = models.CharField(max_length=64, blank=True, null=True, verbose_name=_('Phone number'))
    phone_prefix = models.CharField(max_length=10, blank=True, null=True, verbose_name=_('Phone prefix'))
    registered_in_unhcr = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=Choices((1, _("Yes")), (0, _("No"))),
        verbose_name=_('Registered in UNHCR')
    )
    id_number = models.CharField(
        max_length=45,
        db_index=True,
        blank=True, null=True,
        verbose_name=_('ID number')
    )
    id_type = models.ForeignKey(
        IDType,
        blank=True, null=True,
        verbose_name=_('ID type'),
        on_delete=models.SET_NULL,
    )
    nationality = models.ForeignKey(
        Nationality,
        blank=True, null=True,
        related_name='+',
        on_delete=models.SET_NULL,
        verbose_name=_('Nationality')
    )
    mother_nationality = models.ForeignKey(
        Nationality,
        blank=True, null=True,
        related_name='+',
        on_delete=models.SET_NULL,
        verbose_name=_('Mother nationality')
    )
    address = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Address')
    )
    p_code = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('P-code')
    )
    number = models.CharField(max_length=45, blank=True, null=True)
    unicef_id = models.CharField(max_length=45, blank=True, null=True)

    def __str__(self):
        if not self.first_name:
            return 'No name'

        return u'{} {} {}'.format(
            self.first_name,
            self.father_name,
            self.last_name,
        )

    def __unicode__(self):
        if not self.first_name:
            return 'No name'

        return u'{} {} {}'.format(
            self.first_name,
            self.father_name,
            self.last_name,
        )

    @property
    def full_name(self) -> str:
        return u'{} {} {}'.format(
            self.first_name,
            self.father_name,
            self.last_name,
        )

    def nationality_name(self):
        if self.nationality:
            return self.nationality.name

        return ''

    @property
    def nationality_name_en(self):
        if self.nationality:
            return self.nationality.name_en

        return ''

    @property
    def birthday(self):
        return u'{}/{}/{}'.format(
            self.birthday_day,
            self.birthday_month,
            self.birthday_year,
        )

    @property
    def birthdate(self):
        return u'{}-{}-{}'.format(
            self.birthday_year,
            self.birthday_month,
            self.birthday_day,
        )

    @property
    def age(self) -> int:
        return Person.get_age(self.birthday_year,self.birthday_month,self.birthday_day)

    @staticmethod
    def get_age(birthday_year, birthday_month, birthday_day):
        if birthday_year and birthday_month and birthday_day:
            today = datetime.now()
            return today.year - int(birthday_year) - ((today.month, today.day) < (int(birthday_month), int(birthday_day)))
        # if self.birthday_year:
        #     return int(self.CURRENT_YEAR)-int(self.birthday_year)
        return 0

    @property
    def phone_number(self):
        return '{}-{}'.format(self.phone_prefix, self.phone)

    class Meta:
        abstract = True

    def save(self, **kwargs):
        self.clean()

        """
        Generate unique IDs for every person
        :param kwargs:
        :return:
        """
        # if self.pk is None:
        self.number = generate_id(
            self.first_name,
            self.father_name,
            self.last_name,
            self.mother_fullname,
            self.sex,
            self.birthday_day,
            self.birthday_month,
            self.birthday_year
        )

        # self.unicef_id = generate_one_unique_id(
        #     str(self.pk),
        #     self.first_name,
        #     self.father_name,
        #     self.last_name,
        #     self.mother_fullname,
        #     self.birthdate,
        #     self.nationality_name_en(),
        #     self.sex
        # )

        super(Person, self).save(**kwargs)


class Student(Person):

    pass


class Training(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        ordering = ['name']
        verbose_name = "Topics of teacher training"

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name


class AttachmentType(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        ordering = ['name']
        verbose_name = "Attachment Type"

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name


class Teacher(Person):
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
        'schools.CLMRound',
        blank=True, null=True,
        related_name='+',
        on_delete=models.SET_NULL,
        verbose_name=_('Round')
    )
    school = models.ForeignKey(
        'schools.School',
        blank=False, null=True,
        related_name='+',
        on_delete=models.SET_NULL,
        verbose_name=_('School')
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
    teaching_hours_dirasa = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Number of teaching hours in Dirasa')
    )
    years_of_experience = models.IntegerField(
        blank=True, null=True,
        verbose_name=_('Years of experience in NFE/FE')
    )
    trainings = models.ManyToManyField(
        Training,
        blank=True,
        verbose_name=_('Topics of teacher training')
    )
    training_sessions_attended = models.IntegerField(
        blank=True,
        null=True,
        choices=((x, x) for x in range(0, 30)),
        verbose_name=_('Number of teacher training sessions (attended)')
    )
    training_date_of_completion = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('Date of completion of the listed training')
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
        upload_to='uploads/teacher',
        blank=True,
        null=True,
        verbose_name=_('Attachment'),
        # validators=[validate_file_size]
    )
    attach_type_1 = models.ForeignKey(
        AttachmentType,
        blank=True, null=True,
        on_delete=models.SET_NULL,
        related_name='attach_type_1',
        verbose_name=_('Type')
    )
    attach_short_description_2 = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_('Description')
    )
    attach_file_2 = models.FileField(
        upload_to='uploads/teacher',
        blank=True,
        null=True,
        verbose_name=_('Attachment'),
    )
    attach_type_2 = models.ForeignKey(
        AttachmentType,
        blank=True, null=True,
        on_delete=models.SET_NULL,
        related_name='attach_type_2',
        verbose_name=_('Type')
    )
    attach_short_description_3 = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_('Description')
    )
    attach_file_3 = models.FileField(
        upload_to='uploads/teacher',
        blank=True,
        null=True,
        verbose_name=_('Attachment'),
    )
    attach_type_3 = models.ForeignKey(
        AttachmentType,
        blank=True, null=True,
        on_delete=models.SET_NULL,
        related_name='attach_type_3',
        verbose_name=_('Type')
    )
    attach_short_description_4 = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_('Description')
    )
    attach_file_4 = models.FileField(
        upload_to='uploads/teacher',
        blank=True,
        null=True,
        verbose_name=_('Attachment'),
    )
    attach_type_4 = models.ForeignKey(
        AttachmentType,
        blank=True, null=True,
        on_delete=models.SET_NULL,
        related_name='attach_type_4',
        verbose_name=_('Type')
    )
    attach_short_description_5 = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_('Description')
    )
    attach_file_5 = models.FileField(
        upload_to='uploads/teacher',
        blank=True,
        null=True,
        verbose_name=_('Attachment'),
    )
    attach_type_5 = models.ForeignKey(
        AttachmentType,
        blank=True, null=True,
        on_delete=models.SET_NULL,
        related_name='attach_type_5',
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
