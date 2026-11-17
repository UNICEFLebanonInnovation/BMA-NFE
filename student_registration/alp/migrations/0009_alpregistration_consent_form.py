from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('alp', '0008_alter_alpregistration_source_of_identification'),
    ]

    operations = [
        migrations.AddField(
            model_name='alpregistration',
            name='consent_form',
            field=models.FileField(
                blank=True,
                null=True,
                upload_to='uploads/alp_registration/consent_forms',
                verbose_name='Consent form copy/photo',
            ),
        ),
    ]
