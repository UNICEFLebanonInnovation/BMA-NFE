"""Keep historical applications intact when introducing required exam answers."""

from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import TransactionTestCase


class ExceptionalExamRequirementsMigrationTests(TransactionTestCase):
    migrate_from = ('mscc', '0024_exceptionalexam_place_of_birth')
    migrate_to = ('mscc', '0025_exceptional_exam_birth_country_bln_level')

    def migrate(self, targets):
        executor = MigrationExecutor(connection)
        executor.migrate(targets)
        return executor.loader.project_state(targets).apps

    def setUp(self):
        super().setUp()
        self.latest_migrations = MigrationExecutor(connection).loader.graph.leaf_nodes()
        self.addCleanup(self.migrate, self.latest_migrations)

    def test_upgrade_preserves_answers_without_guessing_country_or_bln_level(self):
        old_apps = self.migrate([self.migrate_from])
        Registration = old_apps.get_model('mscc', 'Registration')
        EducationService = old_apps.get_model('mscc', 'EducationService')
        Exam = old_apps.get_model('mscc', 'ExceptionalExam')
        records = []
        for programme, grade, birthplace in (
            ('BLN', '2', ''), ('BLN', '6', 'دمشق'), ('DIRASA', '7', 'بيروت'),
        ):
            registration = Registration.objects.create(nfe_programme=programme)
            EducationService.objects.create(
                registration=registration, education_program='BLN Level 2',
            )
            exam = Exam.objects.create(
                registration=registration,
                governorate_legacy='beirut', district_legacy='beirut',
                nearest_town='achrafieh', place_of_birth=birthplace,
                programme=programme, grade=grade,
                math_language='ar', language_exam='en',
            )
            records.append((exam.pk, registration.pk, programme, grade, birthplace))

        apps = self.migrate([self.migrate_to])
        Exam = apps.get_model('mscc', 'ExceptionalExam')
        self.assertEqual(Exam.objects.count(), len(records))
        for pk, registration_id, programme, grade, birthplace in records:
            with self.subTest(programme=programme, grade=grade):
                exam = Exam.objects.get(pk=pk)
                self.assertEqual(exam.registration_id, registration_id)
                self.assertEqual((exam.programme, exam.grade), (programme, grade))
                self.assertEqual(exam.place_of_birth, birthplace)
                self.assertEqual(exam.country_of_birth, '')
                self.assertEqual(exam.bln_level, '')
                self.assertEqual(
                    (exam.governorate_legacy, exam.district_legacy, exam.nearest_town),
                    ('beirut', 'beirut', 'achrafieh'),
                )
                self.assertIsNone(exam.governorate_id)
                self.assertIsNone(exam.district_id)
