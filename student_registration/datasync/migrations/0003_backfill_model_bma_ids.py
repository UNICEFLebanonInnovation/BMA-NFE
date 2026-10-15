"""Recover verified BMA IDs from previous synchronization mappings."""

from django.db import migrations


RESOURCE_MODELS = (
    ('mscc.round', 'mscc', 'Round'),
    ('locations.center', 'locations', 'Center'),
    ('child.child', 'child', 'Child'),
    ('mscc.registration', 'mscc', 'Registration'),
    ('mscc.education_service', 'mscc', 'EducationService'),
    ('mscc.education_grading', 'mscc', 'EducationProgrammeAssessment'),
    ('mscc.referral', 'mscc', 'Referral'),
    ('attendances.mscc_attendance', 'attendances', 'MSCCAttendance'),
    ('mscc.teacher', 'mscc', 'Teacher'),
)


def backfill_bma_ids(apps, schema_editor):
    alias = schema_editor.connection.alias
    Mapping = apps.get_model('datasync', 'SyncedRecord')
    ContentType = apps.get_model('contenttypes', 'ContentType')
    Center = apps.get_model('locations', 'Center')
    for resource, app_label, model_name in RESOURCE_MODELS:
        Model = apps.get_model(app_label, model_name)
        content_type = ContentType.objects.using(alias).filter(
            app_label=app_label, model=model_name.lower(),
        ).first()
        if content_type is None:
            continue
        mappings = Mapping.objects.using(alias).filter(
            source_system='compiler', resource=resource, deleted=False,
            content_type_id=content_type.pk, object_id__isnull=False,
        )
        for mapping in mappings.iterator():
            instance = Model.objects.using(alias).filter(pk=mapping.object_id).first()
            if instance is None:
                continue
            bma_id = str(mapping.source_id).strip()
            if not bma_id or len(bma_id) > 64:
                raise ValueError('Invalid BMA ID on sync mapping #{}'.format(mapping.pk))
            if instance.bma_id is not None and instance.bma_id != bma_id:
                raise ValueError(
                    '{} #{} maps to multiple BMA IDs; reconcile mappings before migrating'.format(
                        model_name, instance.pk
                    )
                )
            identity = {'bma_id': bma_id}
            if resource == 'mscc.teacher':
                center = Center.objects.using(alias).filter(pk=instance.center_id).first()
                if center is None or not center.bma_id:
                    raise ValueError(
                        'Teacher #{} needs a center with a verified BMA ID before migrating'.format(
                            instance.pk
                        )
                    )
                identity['center_id'] = center.pk
                Mapping.objects.using(alias).filter(pk=mapping.pk).update(source_scope=center.bma_id)
            if Model.objects.using(alias).filter(**identity).exclude(pk=instance.pk).exists():
                raise ValueError(
                    '{} BMA ID {} is mapped to multiple local rows; reconcile before migrating'.format(
                        model_name, bma_id
                    )
                )
            Model.objects.using(alias).filter(pk=instance.pk).update(bma_id=bma_id)


class Migration(migrations.Migration):
    dependencies = [
        ('datasync', '0002_alter_syncedrecord_unique_together_and_more'),
        ('mscc', '0017_educationprogrammeassessment_bma_id_and_more'),
        ('locations', '0004_center_bma_id'),
        ('child', '0009_child_bma_id'),
        ('attendances', '0004_msccattendance_bma_id_and_round_fk'),
    ]
    operations = [migrations.RunPython(backfill_bma_ids, migrations.RunPython.noop)]
