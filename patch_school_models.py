import re

with open('student_registration/schools/models.py', 'r') as f:
    content = f.read()

new_fields = """
    admin_staff_number = models.IntegerField(
        blank=True,
        null=True,
        choices=((x, x) for x in range(0, 300)),
        verbose_name=_('Number of Admin staff in the school')
    )
    offer_digital_learning = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Does the school offer digital learning services?')
    )
    have_digital_hub = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Does the school have a digital hub?')
    )
    neaby_phcc = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name=_('Nearby PHCC name')
    )
"""

new_properties = """
    @property
    def total_admin_staff(self):
        return self.admin_staff_number if self.admin_staff_number is not None else 0

    @property
    def total_teachers(self):
        from student_registration.students.models import Teacher
        return Teacher.objects.filter(school=self.id).count()

    @property
    def total_teachers_male(self):
        from student_registration.students.models import Teacher
        return Teacher.objects.filter(school=self.id, sex='Male').count()

    @property
    def total_teachers_female(self):
        from student_registration.students.models import Teacher
        return Teacher.objects.filter(school=self.id, sex='Female').count()

    @property
    def total_staff(self):
        admin_staff = self.total_admin_staff
        teachers = self.total_teachers
        return admin_staff + teachers
"""

# Insert new fields before `class Meta:`
content = content.replace("    class Meta:\n        ordering = ['number']", new_fields + "\n    class Meta:\n        ordering = ['number']")

# Insert new properties after `have_academic_year_dates`
content = content.replace('            return False\n        return True', '            return False\n        return True\n' + new_properties)

with open('student_registration/schools/models.py', 'w') as f:
    f.write(content)
