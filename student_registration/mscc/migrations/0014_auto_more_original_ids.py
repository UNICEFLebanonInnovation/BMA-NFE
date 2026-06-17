# Generated manually
from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('mscc', '0013_auto_original_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='educationprogrammeassessment',
            name='original_id',
            field=models.IntegerField(blank=True, help_text='ID from the original BMA system', null=True, unique=True),
        ),
        migrations.AddField(
            model_name='followupservice',
            name='original_id',
            field=models.IntegerField(blank=True, help_text='ID from the original BMA system', null=True, unique=True),
        ),
    ]
