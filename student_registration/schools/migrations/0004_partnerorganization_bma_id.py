"""Track the Compiler ID independently of a partner's display name."""

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('schools', '0003_school_fields')]

    operations = [
        migrations.AddField(
            model_name='partnerorganization',
            name='bma_id',
            field=models.CharField(
                blank=True, max_length=64, null=True, unique=True,
                verbose_name='Compiler partner ID',
            ),
        ),
    ]
