# Generated manually
from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('mscc', '0012_merge_20260602_1359'),
    ]

    operations = [
        migrations.AddField(
            model_name='registration',
            name='original_id',
            field=models.IntegerField(blank=True, help_text='ID from the original BMA system', null=True, unique=True),
        ),
    ]
