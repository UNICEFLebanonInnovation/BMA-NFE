# Generated manually
from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('schools', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='school',
            name='original_id',
            field=models.IntegerField(blank=True, help_text='ID from the original BMA system', null=True, unique=True),
        ),
    ]
