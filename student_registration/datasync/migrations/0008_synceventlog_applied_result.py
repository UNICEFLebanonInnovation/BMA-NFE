"""Keep the original acknowledgement when a sender retries an applied event."""
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('datasync', '0007_merge_photo_and_assessment_backfill')]
    operations = [migrations.AddField(
        model_name='synceventlog', name='applied_result',
        field=models.JSONField(blank=True, default=dict, verbose_name='Original event result'),
    )]
