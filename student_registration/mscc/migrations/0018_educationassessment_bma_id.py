"""Store the Compiler identity of detailed education assessments."""

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('mscc', '0017_educationprogrammeassessment_bma_id_and_more')]

    operations = [
        migrations.AddField(
            model_name='educationassessment',
            name='bma_id',
            field=models.CharField(
                blank=True, max_length=64, null=True, unique=True,
                verbose_name='BMA ID',
            ),
        ),
    ]
