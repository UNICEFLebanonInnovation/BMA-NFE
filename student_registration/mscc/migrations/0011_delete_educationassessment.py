# Generated manually

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mscc', '0010_teacher_training_date_of_completion'),
    ]

    operations = [
        migrations.DeleteModel(
            name='EducationAssessment',
        ),
    ]
