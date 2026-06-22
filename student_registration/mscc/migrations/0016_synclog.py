# Generated manually
from django.db import migrations, models
import django.contrib.postgres.fields.jsonb
import django.utils.timezone
import model_utils.fields

class Migration(migrations.Migration):

    dependencies = [
        ('mscc', '0015_auto_more_original_ids'),
    ]

    operations = [
        migrations.CreateModel(
            name='SyncLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('model_name', models.CharField(max_length=100)),
                ('original_id', models.IntegerField(blank=True, null=True)),
                ('action', models.CharField(max_length=20)),
                ('status', models.CharField(choices=[('success', 'Success'), ('failed', 'Failed')], max_length=20)),
                ('error_message', models.TextField(blank=True, null=True)),
                ('payload', django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict, null=True)),
            ],
            options={
                'ordering': ['-created'],
            },
        ),
    ]
