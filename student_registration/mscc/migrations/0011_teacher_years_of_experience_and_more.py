# Generated manually
from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('mscc', '0010_teacher_training_date_of_completion'),
    ]

    operations = [
        migrations.AddField(
            model_name='teacher',
            name='years_of_experience',
            field=models.IntegerField(blank=True, null=True, verbose_name='Years of experience in NFE/FE'),
        ),
        migrations.AlterField(
            model_name='teacher',
            name='training_date_of_completion',
            field=models.DateField(blank=True, null=True, verbose_name='Date of completion of the listed training'),
        ),
    ]
