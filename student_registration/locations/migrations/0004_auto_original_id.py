# Generated manually
from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('locations', '0003_alter_location_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='location',
            name='original_id',
            field=models.IntegerField(blank=True, help_text='ID from the original BMA system', null=True, unique=True),
        ),
    ]
