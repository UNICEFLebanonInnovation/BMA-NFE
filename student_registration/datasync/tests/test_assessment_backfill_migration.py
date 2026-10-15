"""Upgrade databases that applied the original assessment-free backfill."""

from datetime import timedelta

from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.db.migrations.recorder import MigrationRecorder
from django.test import TransactionTestCase
from django.utils import timezone


class EducationAssessmentBackfillMigrationTests(TransactionTestCase):
    legacy_targets = [
        ('datasync', '0003_backfill_model_bma_ids'),
        ('mscc', '0017_educationprogrammeassessment_bma_id_and_more'),
    ]
    field_targets = [
        ('datasync', '0003_backfill_model_bma_ids'),
        ('mscc', '0018_educationassessment_bma_id'),
    ]
    backfill = ('datasync', '0004_backfill_educationassessment_bma_ids')

    def setUp(self):
        super().setUp()
        executor = MigrationExecutor(connection)
        self.latest = executor.loader.graph.leaf_nodes()
        self.mapping_ids = []
        self.addCleanup(self.restore_latest)
        # Failed backfills must not prevent restoring the schema for other tests.
        self.addCleanup(self.remove_test_mappings)
        self.apps = self.migrate_to(self.legacy_targets)

    def migrate_to(self, targets):
        executor = MigrationExecutor(connection)
        executor.migrate(targets)
        return executor.loader.project_state(targets).apps

    def restore_latest(self):
        self.migrate_to(self.latest)

    def remove_test_mappings(self):
        self.apps.get_model('datasync', 'SyncedRecord').objects.filter(
            pk__in=self.mapping_ids,
        ).delete()

    def make_assessment(self, **fields):
        return self.apps.get_model('mscc', 'EducationAssessment').objects.create(**fields)

    def make_mapping(self, assessment, source_id, **overrides):
        ContentType = self.apps.get_model('contenttypes', 'ContentType')
        content_type, _ = ContentType.objects.get_or_create(
            app_label='mscc', model='educationassessment',
        )
        values = {
            'source_system': 'compiler',
            'resource': 'mscc.education_assessment',
            'source_id': source_id,
            'content_type_id': content_type.pk,
            'object_id': assessment.pk,
        }
        values.update(overrides)
        mapping = self.apps.get_model('datasync', 'SyncedRecord').objects.create(**values)
        self.mapping_ids.append(mapping.pk)
        return mapping

    def prepare_valid_mapping(self):
        """Exercise rollback after a valid row has already been processed."""
        assessment = self.make_assessment()
        mapping = self.make_mapping(assessment, 'verified-before-conflict')
        # Original SyncedRecord ordering is newest first. Also create this row
        # first so a migration that orders by primary key processes it first.
        self.apps.get_model('datasync', 'SyncedRecord').objects.filter(
            pk=mapping.pk,
        ).update(modified=timezone.now() + timedelta(days=1))
        return assessment

    def assert_backfill_rolled_back(self, assessment):
        assessment.refresh_from_db()
        self.assertIsNone(assessment.bma_id)
        self.assertNotIn(self.backfill, MigrationRecorder(connection).applied_migrations())

    def test_applied_legacy_backfill_has_consistent_history_and_upgrades_without_rekeying(self):
        applied = MigrationRecorder(connection).applied_migrations()
        self.assertIn(('datasync', '0003_backfill_model_bma_ids'), applied)
        self.assertNotIn(('mscc', '0018_educationassessment_bma_id'), applied)
        MigrationExecutor(connection).loader.check_consistent_history(connection)
        Assessment = self.apps.get_model('mscc', 'EducationAssessment')
        self.assertNotIn('bma_id', [field.name for field in Assessment._meta.fields])

        child = self.apps.get_model('child', 'Child').objects.create(unicef_id='LOCAL-CHILD')
        registration = self.apps.get_model('mscc', 'Registration').objects.create(
            child_id=child.pk,
        )
        assessment = self.make_assessment(
            registration_id=registration.pk, pre_math_grade=4,
        )
        mapping = self.make_mapping(
            assessment, '  assessment-42  ',
            last_applied_snapshot={'pre_math_grade': 4},
        )
        Mapping = self.apps.get_model('datasync', 'SyncedRecord')
        original_mapping = Mapping.objects.values().get(pk=mapping.pk)

        upgraded = self.migrate_to(self.latest)

        saved = upgraded.get_model('mscc', 'EducationAssessment').objects.get(pk=assessment.pk)
        self.assertEqual(saved.bma_id, 'assessment-42')
        self.assertEqual(saved.registration_id, registration.pk)
        self.assertEqual(saved.pre_math_grade, 4)
        self.assertEqual(
            upgraded.get_model('mscc', 'Registration').objects.get(pk=registration.pk).child_id,
            child.pk,
        )
        self.assertEqual(Mapping.objects.values().get(pk=mapping.pk), original_mapping)
        self.assertIn(self.backfill, MigrationRecorder(connection).applied_migrations())
        connection.check_constraints()

    def test_already_added_field_backfills_missing_ids_and_preserves_matching_ids_on_replay(self):
        self.apps = self.migrate_to(self.field_targets)
        missing = self.make_assessment()
        existing = self.make_assessment(bma_id='already-verified')
        self.make_mapping(missing, 'assessment-new')
        self.make_mapping(existing, 'already-verified')

        self.migrate_to(self.latest)
        missing.refresh_from_db()
        existing.refresh_from_db()
        self.assertEqual(missing.bma_id, 'assessment-new')
        self.assertEqual(existing.bma_id, 'already-verified')

        # RunPython's reverse preserves recovered identities; rerunning is safe.
        self.migrate_to(self.field_targets)
        self.migrate_to(self.latest)
        missing.refresh_from_db()
        existing.refresh_from_db()
        self.assertEqual(missing.bma_id, 'assessment-new')
        self.assertEqual(existing.bma_id, 'already-verified')

    def test_only_active_compiler_assessment_mappings_to_existing_assessments_are_used(self):
        self.apps = self.migrate_to(self.field_targets)
        ContentType = self.apps.get_model('contenttypes', 'ContentType')
        other_type, _ = ContentType.objects.get_or_create(
            app_label='mscc', model='registration',
        )
        ignored = []
        for index, overrides in enumerate((
            {'source_system': 'another-system'},
            {'resource': 'mscc.education_grading'},
            {'deleted': True},
            {'content_type_id': other_type.pk},
            {'content_type_id': None},
            {'object_id': None},
            {'object_id': 1000000},
        )):
            assessment = self.make_assessment()
            ignored.append(assessment)
            self.make_mapping(assessment, 'ignored-{}'.format(index), **overrides)
        ignored.append(self.make_assessment())  # No mapping is not a verified identity.
        valid = self.make_assessment()
        self.make_mapping(valid, 'verified-assessment')

        self.migrate_to(self.latest)

        valid.refresh_from_db()
        self.assertEqual(valid.bma_id, 'verified-assessment')
        for assessment in ignored:
            with self.subTest(assessment=assessment.pk):
                assessment.refresh_from_db()
                self.assertIsNone(assessment.bma_id)

    def test_existing_different_identity_stops_backfill_and_rolls_back_other_updates(self):
        self.apps = self.migrate_to(self.field_targets)
        valid = self.prepare_valid_mapping()
        conflicting = self.make_assessment(bma_id='existing-identity')
        self.make_mapping(conflicting, 'different-identity')

        with self.assertRaisesMessage(ValueError, 'maps to multiple BMA IDs'):
            self.migrate_to(self.latest)

        self.assert_backfill_rolled_back(valid)
        conflicting.refresh_from_db()
        self.assertEqual(conflicting.bma_id, 'existing-identity')

    def test_two_mappings_for_one_assessment_stop_backfill_without_choosing_an_identity(self):
        self.apps = self.migrate_to(self.field_targets)
        valid = self.prepare_valid_mapping()
        conflicting = self.make_assessment()
        self.make_mapping(conflicting, 'assessment-one')
        self.make_mapping(conflicting, 'assessment-two')

        with self.assertRaisesMessage(ValueError, 'maps to multiple BMA IDs'):
            self.migrate_to(self.latest)

        self.assert_backfill_rolled_back(valid)
        conflicting.refresh_from_db()
        self.assertIsNone(conflicting.bma_id)

    def test_one_identity_cannot_merge_two_local_assessments(self):
        self.apps = self.migrate_to(self.field_targets)
        valid = self.prepare_valid_mapping()
        first = self.make_assessment()
        second = self.make_assessment()
        self.make_mapping(first, 'shared-upstream-id', source_scope='old-scope-one')
        self.make_mapping(second, 'shared-upstream-id', source_scope='old-scope-two')

        with self.assertRaisesMessage(ValueError, 'mapped to multiple local rows'):
            self.migrate_to(self.latest)

        self.assert_backfill_rolled_back(valid)
        first.refresh_from_db()
        second.refresh_from_db()
        self.assertIsNone(first.bma_id)
        self.assertIsNone(second.bma_id)

    def test_blank_source_identity_stops_backfill_and_rolls_back_other_updates(self):
        self.apps = self.migrate_to(self.field_targets)
        valid = self.prepare_valid_mapping()
        invalid = self.make_assessment()
        self.make_mapping(invalid, '   ')

        with self.assertRaisesMessage(ValueError, 'Invalid BMA ID'):
            self.migrate_to(self.latest)

        self.assert_backfill_rolled_back(valid)
        invalid.refresh_from_db()
        self.assertIsNone(invalid.bma_id)
