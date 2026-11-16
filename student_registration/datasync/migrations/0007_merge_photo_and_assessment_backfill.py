"""Join the receiver hardening work with the upstream assessment backfill."""

from django.db import migrations, models


RESOURCE_CHOICES = [
    ('schools.partner', 'Partner'), ('mscc.round', 'Round'),
    ('locations.center', 'Center'), ('mscc.teacher', 'Teacher'),
    ('mscc.registration', 'Registration'),
    ('mscc.education_service', 'Child education situation'),
    ('mscc.education_assessment', 'Education assessment'),
    ('mscc.education_grading', 'Grading'), ('mscc.referral', 'Referral'),
    ('attendances.mscc_attendance', 'Attendance'), ('child.child', 'Child'),
]


class Migration(migrations.Migration):
    dependencies = [
        ('datasync', '0006_syncedchildphoto'),
        ('datasync', '0004_backfill_educationassessment_bma_ids'),
    ]
    operations = [migrations.AlterField(
        model_name=name, name='resource',
        field=models.CharField(choices=RESOURCE_CHOICES, db_index=True,
                               max_length=100, verbose_name='Resource'),
    ) for name in ('syncconflict', 'syncedrecord', 'synceventlog')]
