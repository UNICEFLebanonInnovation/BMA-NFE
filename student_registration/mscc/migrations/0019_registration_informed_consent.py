from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mscc', '0018_rollback_teacher_assignment'),
    ]

    operations = [
        migrations.AddField(
            model_name='registration',
            name='informed_consent',
            field=models.FileField(
                blank=True,
                null=True,
                upload_to='uploads/mscc_registration/informed_consent',
                verbose_name='Informed Consent for Data Sharing\nNon-Formal Education Programming in Lebanon',
            ),
        ),
    ]
