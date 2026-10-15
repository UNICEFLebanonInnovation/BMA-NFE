"""Backfill assessment identities after adding their BMA ID column.

Keep this separate from 0003: that migration was already applied before the
EducationAssessment field existed on databases receiving the first sync release.
"""

from django.db import migrations, models


# Freeze the vocabulary introduced with detailed assessment replication.
RESOURCE_CHOICES = (
    ('mscc.round', 'Round'),
    ('locations.center', 'Center'),
    ('mscc.teacher', 'Teacher'),
    ('mscc.registration', 'Registration'),
    ('mscc.education_service', 'Child education situation'),
    ('mscc.education_assessment', 'Education assessment'),
    ('mscc.education_grading', 'Grading'),
    ('mscc.referral', 'Referral'),
    ('attendances.mscc_attendance', 'Attendance'),
    ('child.child', 'Child'),
)


def backfill_assessment_bma_ids(apps, schema_editor):
    alias = schema_editor.connection.alias
    Assessment = apps.get_model('mscc', 'EducationAssessment')
    Mapping = apps.get_model('datasync', 'SyncedRecord')
    ContentType = apps.get_model('contenttypes', 'ContentType')
    content_type = ContentType.objects.using(alias).filter(
        app_label='mscc', model='educationassessment',
    ).first()
    if content_type is None:
        return

    mappings = Mapping.objects.using(alias).filter(
        source_system='compiler', resource='mscc.education_assessment',
        deleted=False, content_type_id=content_type.pk, object_id__isnull=False,
    )
    for mapping in mappings.iterator():
        assessment = Assessment.objects.using(alias).filter(pk=mapping.object_id).first()
        if assessment is None:
            continue
        bma_id = str(mapping.source_id).strip()
        if not bma_id or len(bma_id) > 64:
            raise ValueError('Invalid BMA ID on sync mapping #{}'.format(mapping.pk))
        if assessment.bma_id is not None and assessment.bma_id != bma_id:
            raise ValueError(
                'EducationAssessment #{} maps to multiple BMA IDs; '
                'reconcile mappings before migrating'.format(assessment.pk)
            )
        if Assessment.objects.using(alias).filter(bma_id=bma_id).exclude(pk=assessment.pk).exists():
            raise ValueError(
                'EducationAssessment BMA ID {} is mapped to multiple local rows; '
                'reconcile before migrating'.format(bma_id)
            )
        Assessment.objects.using(alias).filter(pk=assessment.pk).update(bma_id=bma_id)


class Migration(migrations.Migration):
    dependencies = [
        ('datasync', '0003_backfill_model_bma_ids'),
        ('mscc', '0018_educationassessment_bma_id'),
    ]
    operations = [
        migrations.AlterField(
            model_name=model_name,
            name='resource',
            field=models.CharField(
                choices=RESOURCE_CHOICES, db_index=True, max_length=100,
                verbose_name='Resource',
            ),
        )
        for model_name in ('syncconflict', 'syncedrecord', 'synceventlog')
    ] + [
        migrations.RunPython(backfill_assessment_bma_ids, migrations.RunPython.noop),
    ]
