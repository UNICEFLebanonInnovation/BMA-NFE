from collections import defaultdict

from django.db import migrations, models
import django.db.models.deletion


def link_existing_addresses(apps, schema_editor):
    Child = apps.get_model('child', 'Child')
    Location = apps.get_model('locations', 'Location')
    database = schema_editor.connection.alias

    # Names can repeat between branches and even within one branch. Only an
    # unambiguous exact Arabic or English name is safe to migrate.
    names = defaultdict(set)
    for location in Location.objects.using(database).filter(type_id__in=(1, 2, 3)).values(
        'id', 'name', 'name_en', 'type_id', 'parent_id',
    ):
        parent_id = None if location['type_id'] == 1 else location['parent_id']
        for name in {location['name'], location['name_en']}:
            if name:
                names[(location['type_id'], parent_id, name)].add(location['id'])

    def match(location_type, parent_id, name):
        candidates = names.get((location_type, parent_id, name), ())
        return next(iter(candidates)) if len(candidates) == 1 else None

    pending = []
    children = Child.objects.using(database).only(
        'id', 'governorate_legacy', 'district_legacy', 'cadaster_legacy',
    )
    for child in children.iterator(chunk_size=500):
        child.governorate_id = match(1, None, child.governorate_legacy)
        child.district_id = (
            match(2, child.governorate_id, child.district_legacy)
            if child.governorate_id else None
        )
        child.cadaster_id = (
            match(3, child.district_id, child.cadaster_legacy)
            if child.district_id else None
        )
        if child.governorate_id or child.district_id or child.cadaster_id:
            pending.append(child)
        if len(pending) >= 500:
            Child.objects.using(database).bulk_update(pending, ['governorate', 'district', 'cadaster'])
            pending = []
    if pending:
        Child.objects.using(database).bulk_update(pending, ['governorate', 'district', 'cadaster'])


def preserve_new_addresses(apps, schema_editor):
    Child = apps.get_model('child', 'Child')
    database = schema_editor.connection.alias
    pending = []
    # Retain the original language when it still names the selected location;
    # otherwise preserve the latest selection when reversing to text fields.
    children = Child.objects.using(database).select_related('governorate', 'district', 'cadaster')
    for child in children.iterator(chunk_size=500):
        changed = False
        for field in ('governorate', 'district', 'cadaster'):
            legacy_field = field + '_legacy'
            location = getattr(child, field)
            legacy_value = getattr(child, legacy_field)
            if location and (not legacy_value or legacy_value not in (location.name, location.name_en)):
                setattr(child, legacy_field, location.name)
                changed = True
        if changed:
            pending.append(child)
        if len(pending) >= 500:
            Child.objects.using(database).bulk_update(
                pending, ['governorate_legacy', 'district_legacy', 'cadaster_legacy'],
            )
            pending = []
    if pending:
        Child.objects.using(database).bulk_update(
            pending, ['governorate_legacy', 'district_legacy', 'cadaster_legacy'],
        )


class Migration(migrations.Migration):

    dependencies = [
        ('child', '0009_structured_child_address_and_nfe_programme'),
        ('locations', '0003_alter_location_options'),
    ]

    operations = [
        migrations.RenameField(model_name='child', old_name='governorate', new_name='governorate_legacy'),
        migrations.RenameField(model_name='child', old_name='district', new_name='district_legacy'),
        migrations.RenameField(model_name='child', old_name='cadaster', new_name='cadaster_legacy'),
        migrations.AddField(
            model_name='child', name='governorate',
            field=models.ForeignKey(
                blank=True, null=True, related_name='+', to='locations.location',
                on_delete=django.db.models.deletion.SET_NULL, limit_choices_to={'type_id': 1},
                verbose_name='Governorate (محافظة)',
            ),
        ),
        migrations.AddField(
            model_name='child', name='district',
            field=models.ForeignKey(
                blank=True, null=True, related_name='+', to='locations.location',
                on_delete=django.db.models.deletion.SET_NULL, limit_choices_to={'type_id': 2},
                verbose_name='District/Caza (قضاء)',
            ),
        ),
        migrations.AddField(
            model_name='child', name='cadaster',
            field=models.ForeignKey(
                blank=True, null=True, related_name='+', to='locations.location',
                on_delete=django.db.models.deletion.SET_NULL, limit_choices_to={'type_id': 3},
                verbose_name='Cadaster (منطقة عقارية)',
            ),
        ),
        migrations.RunPython(link_existing_addresses, preserve_new_addresses),
    ]
