"""Registration detail changes preserve historical addresses and exam answers."""

from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import TransactionTestCase

from student_registration.locations.models import Location, LocationType


class RegistrationDetailsMigrationTests(TransactionTestCase):
    migrate_from = [
        ('child', '0010_link_child_address_locations'),
        ('mscc', '0026_exceptional_exam_programme_levels'),
    ]
    migrate_to = [
        ('child', '0011_birth_details'),
        ('mscc', '0027_registration_programme_levels'),
    ]

    def migrate(self, targets):
        executor = MigrationExecutor(connection)
        executor.migrate(targets)
        return executor.loader.project_state(targets).apps

    def columns(self, table):
        with connection.cursor() as cursor:
            return {
                column.name for column in connection.introspection.get_table_description(cursor, table)
            }

    def setUp(self):
        super().setUp()
        self.latest_migrations = MigrationExecutor(connection).loader.graph.leaf_nodes()
        self.addCleanup(self.migrate, self.latest_migrations)

    def test_upgrade_preserves_legacy_data_without_inferring_registration_answers(self):
        old_apps = self.migrate(self.migrate_from)
        Child = old_apps.get_model('child', 'Child')
        Registration = old_apps.get_model('mscc', 'Registration')
        EducationService = old_apps.get_model('mscc', 'EducationService')
        Exam = old_apps.get_model('mscc', 'ExceptionalExam')
        old_columns = {
            model._meta.db_table: self.columns(model._meta.db_table)
            for model in (Child, Registration, Exam)
        }

        for pk, name in ((1, 'Governorate'), (2, 'District'), (3, 'Cadaster')):
            LocationType.objects.create(pk=pk, name=name)
        governorate = Location.objects.create(name='بيروت', name_en='Beirut', type_id=1)
        district = Location.objects.create(
            name='بيروت', name_en='Beirut', type_id=2, parent=governorate,
        )
        cadaster = Location.objects.create(
            name='الأشرفية', name_en='Achrafieh', type_id=3, parent=district,
        )
        saved_address = {
            'governorate_id': governorate.pk,
            'district_id': district.pk,
            'cadaster_id': cadaster.pk,
            'governorate_legacy': 'بيروت',
            'district_legacy': 'بيروت',
            'cadaster_legacy': 'الأشرفية',
            'municipality': 'Saved municipality',
            'street': 'Saved street',
            'building_camp': 'Saved camp',
            'village': 'Legacy village absent from the catalogue',
            'photo': 'child_photos/registered-child.jpg',
        }
        records = []
        for programme, grade in (('BLN', '2'), ('DIRASA', '4')):
            child = Child.objects.create(first_name=programme, **saved_address)
            registration = Registration.objects.create(child=child, nfe_programme=programme)
            service = EducationService.objects.create(
                registration=registration, education_program='BLN Level 3',
            )
            exam = Exam.objects.create(
                registration=registration, programme=programme, grade=grade,
                governorate_id=governorate.pk, district_id=district.pk,
                governorate_legacy='beirut', district_legacy='beirut', nearest_town='achrafieh',
                country_of_birth='SY', place_of_birth='دمشق',
                math_language='ar', language_exam='en',
            )
            records.append((child.pk, registration.pk, service.pk, exam.pk, programme, grade))

        apps = self.migrate(self.migrate_to)
        Child = apps.get_model('child', 'Child')
        Registration = apps.get_model('mscc', 'Registration')
        EducationService = apps.get_model('mscc', 'EducationService')
        Exam = apps.get_model('mscc', 'ExceptionalExam')
        for model in (Child, Registration, Exam):
            with self.subTest(table=model._meta.db_table):
                expected_columns = old_columns[model._meta.db_table]
                if model is Child:
                    expected_columns = expected_columns | {'country_of_birth', 'place_of_birth'}
                self.assertEqual(self.columns(model._meta.db_table), expected_columns)
                self.assertNotIn('bln_level', self.columns(model._meta.db_table))

        for child_id, registration_id, service_id, exam_id, programme, grade in records:
            with self.subTest(existing_programme=programme):
                child = Child.objects.get(pk=child_id)
                self.assertIsNone(child.country_of_birth)
                self.assertIsNone(child.place_of_birth)
                for field, value in saved_address.items():
                    self.assertEqual(str(getattr(child, field)), str(value))
                registration = Registration.objects.get(pk=registration_id)
                self.assertEqual((registration.child_id, registration.nfe_programme),
                                 (child_id, programme))
                self.assertEqual(
                    EducationService.objects.get(pk=service_id).education_program, 'BLN Level 3',
                )
                exam = Exam.objects.get(pk=exam_id)
                self.assertEqual((exam.registration_id, exam.programme, exam.grade),
                                 (registration_id, programme, grade))
                self.assertEqual((exam.country_of_birth, exam.place_of_birth), ('SY', 'دمشق'))
                self.assertEqual((exam.governorate_id, exam.district_id),
                                 (governorate.pk, district.pk))
                self.assertEqual(
                    (exam.governorate_legacy, exam.district_legacy, exam.nearest_town),
                    ('beirut', 'beirut', 'achrafieh'),
                )
                self.assertEqual((exam.math_language, exam.language_exam), ('ar', 'en'))

        country_field = Child._meta.get_field('country_of_birth')
        place_field = Child._meta.get_field('place_of_birth')
        self.assertEqual(tuple(value for value, _ in country_field.choices), ('LB', 'SY', 'OTHER'))
        self.assertEqual((country_field.max_length, place_field.max_length), (5, 100))
        for field in (country_field, place_field):
            self.assertTrue(field.null)
            self.assertTrue(field.blank)
        programme_field = Registration._meta.get_field('nfe_programme')
        programmes = ('BLN Level 1', 'BLN Level 2', 'BLN Level 3')
        self.assertEqual(tuple(value for value, _ in programme_field.choices), programmes)
        self.assertEqual(programme_field.max_length, 20)
        for programme in programmes:
            with self.subTest(new_programme=programme):
                child = Child.objects.create(
                    country_of_birth='LB', place_of_birth='بيروت', village='achrafieh',
                    governorate_id=governorate.pk, district_id=district.pk,
                )
                registration = Registration.objects.create(child=child, nfe_programme=programme)
                child.refresh_from_db()
                registration.refresh_from_db()
                self.assertEqual((child.country_of_birth, child.place_of_birth, child.village),
                                 ('LB', 'بيروت', 'achrafieh'))
                self.assertEqual(registration.nfe_programme, programme)
