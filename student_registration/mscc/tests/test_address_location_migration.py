from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import TransactionTestCase

from student_registration.locations.models import Location, LocationType


class ChildAddressLocationMigrationTests(TransactionTestCase):
    migrate_from = ('child', '0009_structured_child_address_and_nfe_programme')
    migrate_to = ('child', '0010_link_child_address_locations')

    def migrate(self, targets):
        executor = MigrationExecutor(connection)
        executor.migrate(targets)
        return executor.loader.project_state(targets).apps

    def setUp(self):
        super().setUp()
        self.latest_migrations = MigrationExecutor(connection).loader.graph.leaf_nodes()
        # Restore the full schema even if an assertion fails before rollback
        # validation, so following tests always use the current model fields.
        self.addCleanup(self.migrate, self.latest_migrations)
        self.old_apps = self.migrate([self.migrate_from])
        self.old_child = self.old_apps.get_model('child', 'Child')

        for pk, name in ((1, 'Governorate'), (2, 'District'), (3, 'Cadaster')):
            LocationType.objects.create(pk=pk, name=name)
        self.governorate = Location.objects.create(
            name='بيروت', name_en='Beirut', type_id=1,
        )
        self.district = Location.objects.create(
            name='بيروت المدينة', name_en='Beirut city', type_id=2,
            parent=self.governorate,
        )
        self.cadaster = Location.objects.create(
            name='رأس بيروت', name_en='Ras Beirut', type_id=3, parent=self.district,
        )
        self.other_governorate = Location.objects.create(
            name='جبل لبنان', name_en='Mount Lebanon', type_id=1,
        )
        self.other_district = Location.objects.create(
            # A repeated district name in a different governorate is safe when
            # the saved parent narrows the match to one location.
            name='بيروت المدينة', name_en='Beirut city', type_id=2,
            parent=self.other_governorate,
        )
        self.other_cadaster = Location.objects.create(
            name='الجديدة', name_en='Jdeideh', type_id=3, parent=self.other_district,
        )
        for p_code in ('A-1', 'A-2'):
            Location.objects.create(name='Ambiguous governorate', type_id=1, p_code=p_code)
            Location.objects.create(
                name='Ambiguous district', type_id=2, parent=self.governorate, p_code=p_code,
            )

    def test_mapping_is_unambiguous_parent_scoped_and_rollback_preserves_latest_address(self):
        saved_texts = {
            'Arabic': ('بيروت', 'بيروت المدينة', 'رأس بيروت'),
            'English': ('Beirut', 'Beirut city', 'Ras Beirut'),
            'Unknown': ('Unknown governorate', 'Unknown district', 'Unknown cadaster'),
            'Wrong parent': ('بيروت', 'بيروت المدينة', 'الجديدة'),
            'Ambiguous governorate': ('Ambiguous governorate', 'بيروت المدينة', 'رأس بيروت'),
            'Ambiguous district': ('Beirut', 'Ambiguous district', 'Ras Beirut'),
            'Other branch': ('Mount Lebanon', 'Beirut city', 'Jdeideh'),
        }
        children = {
            name: self.old_child.objects.create(
                first_name=name, governorate=texts[0], district=texts[1], cadaster=texts[2],
                municipality='Saved municipality', street='Saved street',
            ).pk
            for name, texts in saved_texts.items()
        }

        apps = self.migrate([self.migrate_to])
        Child = apps.get_model('child', 'Child')
        expected_ids = {
            'Arabic': (self.governorate.pk, self.district.pk, self.cadaster.pk),
            'English': (self.governorate.pk, self.district.pk, self.cadaster.pk),
            'Unknown': (None, None, None),
            'Wrong parent': (self.governorate.pk, self.district.pk, None),
            'Ambiguous governorate': (None, None, None),
            'Ambiguous district': (self.governorate.pk, None, None),
            'Other branch': (
                self.other_governorate.pk, self.other_district.pk, self.other_cadaster.pk,
            ),
        }
        for name, child_id in children.items():
            with self.subTest(saved_child=name):
                child = Child.objects.get(pk=child_id)
                self.assertEqual(
                    (child.governorate_id, child.district_id, child.cadaster_id),
                    expected_ids[name],
                )
                self.assertEqual(
                    (child.governorate_legacy, child.district_legacy, child.cadaster_legacy),
                    saved_texts[name],
                )
                self.assertEqual(child.municipality, 'Saved municipality')
                self.assertEqual(child.street, 'Saved street')

        new_child = Child.objects.create(
            first_name='New child', governorate_id=self.governorate.pk,
            district_id=self.district.pk, cadaster_id=self.cadaster.pk,
        )
        Child.objects.filter(pk=children['Arabic']).update(
            governorate_id=self.other_governorate.pk,
            district_id=self.other_district.pk, cadaster_id=self.other_cadaster.pk,
        )

        apps = self.migrate([self.migrate_from])
        Child = apps.get_model('child', 'Child')
        for name, child_id in children.items():
            with self.subTest(rollback_child=name):
                child = Child.objects.get(pk=child_id)
                expected_text = saved_texts[name]
                if name == 'Arabic':
                    expected_text = (
                        self.other_governorate.name, self.other_district.name,
                        self.other_cadaster.name,
                    )
                self.assertEqual(
                    (child.governorate, child.district, child.cadaster), expected_text,
                )
        child = Child.objects.get(pk=new_child.pk)
        self.assertEqual(
            (child.governorate, child.district, child.cadaster),
            (self.governorate.name, self.district.name, self.cadaster.name),
        )
