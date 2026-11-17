"""Programme level choices fit the existing exam field and preserve saved data."""

from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import TransactionTestCase


class ExceptionalExamProgrammeMigrationTests(TransactionTestCase):
    migrate_from = ('mscc', '0025_exceptional_exam_birth_details')
    migrate_to = ('mscc', '0026_exceptional_exam_programme_levels')

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

    def test_upgrade_preserves_existing_choices_and_stores_explicit_levels_in_programme(self):
        old_apps = self.migrate([self.migrate_from])
        Registration = old_apps.get_model('mscc', 'Registration')
        EducationService = old_apps.get_model('mscc', 'EducationService')
        Exam = old_apps.get_model('mscc', 'ExceptionalExam')
        original_columns = self.columns(Exam._meta.db_table)
        records = []
        for programme, grade in (('BLN', '2'), ('DIRASA', '4')):
            registration = Registration.objects.create(nfe_programme=programme)
            service = EducationService.objects.create(
                registration=registration, education_program='BLN Level 3',
            )
            exam = Exam.objects.create(
                registration=registration, programme=programme, grade=grade,
                governorate_legacy='beirut', district_legacy='beirut', nearest_town='achrafieh',
                country_of_birth='SY', place_of_birth='دمشق',
                math_language='ar', language_exam='en',
            )
            records.append((exam.pk, registration.pk, service.pk, programme, grade))

        apps = self.migrate([self.migrate_to])
        Exam = apps.get_model('mscc', 'ExceptionalExam')
        Registration = apps.get_model('mscc', 'Registration')
        EducationService = apps.get_model('mscc', 'EducationService')
        self.assertEqual(self.columns(Exam._meta.db_table), original_columns)
        self.assertNotIn('bln_level', self.columns(Exam._meta.db_table))
        self.assertEqual(
            tuple(value for value, _ in Exam._meta.get_field('programme').choices),
            ('BLN Level 1', 'BLN Level 2', 'BLN Level 3'),
        )
        self.assertEqual(Exam._meta.get_field('programme').max_length, 20)
        self.assertEqual(Exam.objects.count(), len(records))
        for pk, registration_id, service_id, programme, grade in records:
            with self.subTest(existing_programme=programme):
                exam = Exam.objects.get(pk=pk)
                self.assertEqual((exam.registration_id, exam.programme, exam.grade),
                                 (registration_id, programme, grade))
                self.assertEqual((exam.country_of_birth, exam.place_of_birth), ('SY', 'دمشق'))
                self.assertEqual((exam.math_language, exam.language_exam), ('ar', 'en'))
                self.assertEqual(
                    (exam.governorate_legacy, exam.district_legacy, exam.nearest_town),
                    ('beirut', 'beirut', 'achrafieh'),
                )
                self.assertEqual(Registration.objects.get(pk=registration_id).nfe_programme, programme)
                self.assertEqual(
                    EducationService.objects.get(pk=service_id).education_program, 'BLN Level 3',
                )

        for programme, grade in (('BLN Level 1', '2'), ('BLN Level 2', '3'), ('BLN Level 3', '4')):
            with self.subTest(new_programme=programme):
                exam = Exam.objects.create(
                    registration=Registration.objects.create(nfe_programme='BLN'),
                    programme=programme, grade=grade, country_of_birth='LB', place_of_birth='بيروت',
                    nearest_town='achrafieh', math_language='ar', language_exam='en',
                )
                exam.refresh_from_db()
                self.assertEqual((exam.programme, exam.grade), (programme, grade))
                self.assertEqual(exam.get_programme_display(), programme)
