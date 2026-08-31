from __future__ import unicode_literals

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from model_utils import Choices
from model_utils.models import TimeStampedModel
from django.db.models import JSONField
from django.contrib.postgres.fields import ArrayField

from student_registration.students.models import AttachmentType, IDType, Nationality, Training
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
    )
    TEACHER_ASSIGNMENT = Choices(
        ('Makani only', _('Makani only')),
        ('Private and Makani', _('Private and Makani')),
    )
    YES_NO = Choices(
        ('', _('----------')),
        ('yes', _("Yes")),
        ('no', _("No")),
    )

    first_name = models.CharField(
        max_length=64, db_index=True, blank=True, null=True, verbose_name=_('First name')
    )
    father_name = models.CharField(
        max_length=64, db_index=True, blank=True, null=True, verbose_name=_('Father name')
    )
    last_name = models.CharField(
        max_length=64, db_index=True, blank=True, null=True, verbose_name=_('Last name')
    )
    mother_fullname = models.CharField(
        max_length=64, db_index=True, blank=True, null=True, verbose_name=_('Mother full name')
    )
    sex = models.CharField(
        max_length=6, choices=GENDER, blank=True, null=True, verbose_name=_('Sex')
    )
    birthdate = models.DateField(
        blank=True, null=True, verbose_name=_('Birth date')
    )
    id_number = models.CharField(
        max_length=45, db_index=True, blank=True, null=True, verbose_name=_('ID number')
    )
    id_type = models.ForeignKey(
        IDType,
        blank=True, null=True, verbose_name=_('ID type'),
        related_name='+', on_delete=models.SET_NULL,
    )
    nationality = models.ForeignKey(
        Nationality,
        blank=True, null=True, related_name='+',
        on_delete=models.SET_NULL, verbose_name=_('Nationality')
    )
    unicef_id = models.CharField(
        max_length=45, blank=True, null=True, verbose_name=_('UNIQUE ID')
    )
    round = models.ForeignKey(
        ALPRound,
        blank=True, null=True, related_name='+',
        on_delete=models.SET_NULL, verbose_name=_('Round')
    )
    school = models.ForeignKey(
        School,
        blank=False, null=True, related_name='+',
        on_delete=models.SET_NULL, verbose_name=_('School')
    )
    email = models.CharField(
        max_length=100, blank=True, null=True, verbose_name=_('Email')
    )
    phone_number = models.CharField(
        max_length=50, blank=True, null=True, verbose_name=_('Phone number')
    )
    subjects_provided = ArrayField(
        models.CharField(
            choices=SUBJECT_PROVIDED, max_length=200, blank=True, null=True,
        ),
        blank=True, null=True, verbose_name=_('Subjects provided')
    )
    registration_level = ArrayField(
        models.CharField(
            choices=REGISTRATION_LEVEL, max_length=200, blank=True, null=True,
        ),
        blank=True, null=True, verbose_name=_('Dirasa Grade level')
    )
    teacher_assignment = models.CharField(
        max_length=100, blank=True, null=True,
        choices=TEACHER_ASSIGNMENT, verbose_name=_('Teacher Assignment')
    )
    teaching_hours_private_school = models.IntegerField(
        blank=True, null=True, verbose_name=_('Number of teaching hours in private school')
    )
    teaching_hours_mscc = models.IntegerField(
        blank=True, null=True, verbose_name=_('Number of teaching hours')
    )
    years_of_experience = models.IntegerField(
        blank=True, null=True, verbose_name=_('Years of experience in NFE/FE')
    )
    trainings = models.ManyToManyField(
        Training, blank=True, related_name='alp_teachers',
        verbose_name=_('Topics of teacher training')
    )
    training_sessions_attended = models.IntegerField(
        blank=True, null=True, choices=((x, x) for x in range(0, 30)),
        verbose_name=_('Number of teacher training sessions (attended)')
    )
    training_date_of_completion = models.DateField(
        blank=True, null=True, verbose_name=_('Date of completion of the listed training')
    )
    extra_coaching = models.CharField(
        max_length=10, blank=True, null=True,
        choices=YES_NO, verbose_name=_('Extra coaching')
    )
    extra_coaching_specify = models.TextField(
        blank=True, null=True, verbose_name=_('Please specify')
    )
    attach_short_description_1 = models.CharField(
        max_length=255, blank=True, null=True, verbose_name=_('Description')
    )
    attach_file_1 = models.FileField(
        upload_to='uploads/alp_teacher', blank=True, null=True, verbose_name=_('Attachment'),
    )
    attach_type_1 = models.ForeignKey(
        AttachmentType, blank=True, null=True, on_delete=models.SET_NULL,
        related_name='+', verbose_name=_('Type')
    )
    attach_short_description_2 = models.CharField(
        max_length=255, blank=True, null=True, verbose_name=_('Description')
    )
    attach_file_2 = models.FileField(
        upload_to='uploads/alp_teacher', blank=True, null=True, verbose_name=_('Attachment'),
    )
    attach_type_2 = models.ForeignKey(
        AttachmentType, blank=True, null=True, on_delete=models.SET_NULL,
        related_name='+', verbose_name=_('Type')
    )
    attach_short_description_3 = models.CharField(
        max_length=255, blank=True, null=True, verbose_name=_('Description')
    )
    attach_file_3 = models.FileField(
        upload_to='uploads/alp_teacher', blank=True, null=True, verbose_name=_('Attachment'),
    )
    attach_type_3 = models.ForeignKey(
        AttachmentType, blank=True, null=True, on_delete=models.SET_NULL,
        related_name='+', verbose_name=_('Type')
    )
    attach_short_description_4 = models.CharField(
        max_length=255, blank=True, null=True, verbose_name=_('Description')
    )
    attach_file_4 = models.FileField(
        upload_to='uploads/alp_teacher', blank=True, null=True, verbose_name=_('Attachment'),
    )
    attach_type_4 = models.ForeignKey(
        AttachmentType, blank=True, null=True, on_delete=models.SET_NULL,
        related_name='+', verbose_name=_('Type')
    )
    attach_short_description_5 = models.CharField(
        max_length=255, blank=True, null=True, verbose_name=_('Description')
    )
    attach_file_5 = models.FileField(
        upload_to='uploads/alp_teacher', blank=True, null=True, verbose_name=_('Attachment'),
    )
    attach_type_5 = models.ForeignKey(
        AttachmentType, blank=True, null=True, on_delete=models.SET_NULL,
        related_name='+', verbose_name=_('Type')
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, blank=False, null=True, related_name='+',
        on_delete=models.SET_NULL, verbose_name=_('Owner')
    )
    modified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, blank=True, null=True, related_name='+',
        on_delete=models.SET_NULL, verbose_name=_('Modified by'),
    )

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
    YES_NO = Choices(
        ('', '----------'),
        ('Yes', _("Yes")),
        ('No', _("No")),
    )
    CLOSE_REASON = Choices(
        ('', '----------'),
        ('Public Holiday', _('Public Holiday')),
        ('School Holiday', _('School Holiday')),
        ('Strike', _('Strike')),
        ('Weekly Holiday', _('Weekly Holiday')),
        ('Roads Closed', _('Roads Closed')),
    )

    round = models.ForeignKey(ALPRound, blank=True, null=True, related_name='+', on_delete=models.SET_NULL, verbose_name=_('Round'))
    school = models.ForeignKey(School, blank=True, null=True, related_name='+', on_delete=models.SET_NULL, verbose_name=_('School'))
    programme = models.ForeignKey(ALPProgram, blank=True, null=True, related_name='+', on_delete=models.SET_NULL, verbose_name=_('Programme'))

    attendance_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('Attendance date')
    )
    day_off = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Day off ?')
    )
    close_reason = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=CLOSE_REASON,
        verbose_name=_('Day off reason')
    )

    class Meta:
        ordering = ['attendance_date']
        verbose_name = _("ALP Attendance")
        verbose_name_plural = _("ALP Attendances")

    def __str__(self):
        return f"{self.school} - {self.attendance_date}"


class ALPAttendanceChild(TimeStampedModel):
    ABSENCE_REASON = Choices(
        ('', '----------'),
        ('Sick', _('Sick')),
        ('No transport', _('No transport')),
        ('Other', _('Other')),
        ('Unspecified', _('Unspecified')),
    )
    attendance_day = models.ForeignKey(
        ALPAttendance,
        blank=True, null=True,
        related_name='attendance_child',
        on_delete=models.SET_NULL,
    )
    registration = models.ForeignKey(
        ALPRegistration,
        blank=False, null=True,
        related_name='+',
        on_delete=models.SET_NULL,
        verbose_name=_('Registration')
    )
    child = models.ForeignKey(
        Child,
        blank=False, null=True,
        related_name='+',
        on_delete=models.SET_NULL,
        verbose_name=_('Child')
    )
    attended = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=ALPRegistration.YES_NO,
        verbose_name=_('Child Attended?')
    )
    absence_reason = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=ABSENCE_REASON
    )
    absence_reason_other = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name=_('specify')
    )

    class Meta:
        ordering = ['id']
        verbose_name = _("ALP Child Attendance")

    @property
    def attendance_date(self):
        return self.attendance_day.attendance_date.strftime("%d/%m/%Y")

    @property
    def child_name(self):
        result = ''
        if self.child:
            result = self.child.full_name
        return result

    @property
    def child_gender(self):
        result = ''
        if self.child:
            result = self.child.gender
        return result

    @property
    def child_fullname(self):
        if self.child:
            return self.child.full_name
        return ''

    def __str__(self):
        return f"{self.child} - {self.attendance_day}"
