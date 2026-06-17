# Generated manually
from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('students', '0004_teacher_years_of_experience_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='teacher',
            name='original_id',
            field=models.IntegerField(blank=True, help_text='ID from the original BMA system', null=True, unique=True),
        ),
    ]
