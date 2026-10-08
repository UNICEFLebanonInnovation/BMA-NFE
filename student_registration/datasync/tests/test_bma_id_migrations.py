"""Upgrade real legacy tables without guessing identities or losing relations."""

from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import TransactionTestCase


class BmaIdMigrationTests(TransactionTestCase):
    migrate_from = [
        ('mscc', '0016_merge_20260830_1305'),
        ('locations', '0003_alter_location_options'),
        ('child', '0008_alter_child_unicef_id'),
        ('attendances', '0003_initial'),
        ('datasync', '0001_initial'),
    ]

    def setUp(self):
        super().setUp()
        executor = MigrationExecutor(connection)
        self.latest = executor.loader.graph.leaf_nodes()
        self.addCleanup(self.restore_latest)
        executor.migrate(self.migrate_from)
        self.old_apps = executor.loader.project_state(self.migrate_from).apps

    def restore_latest(self):
        MigrationExecutor(connection).migrate(self.latest)

    def upgrade(self):
        executor = MigrationExecutor(connection)
        executor.migrate(self.latest)
        return executor.loader.project_state(self.latest).apps

    def make_mapping(self, resource, instance, source_id, **extra):
        ContentType = self.old_apps.get_model('contenttypes', 'ContentType')
        content_type, _ = ContentType.objects.get_or_create(
            app_label=instance._meta.app_label, model=instance._meta.model_name,
        )
        return self.old_apps.get_model('datasync', 'SyncedRecord').objects.create(
            source_system='compiler', resource=resource, source_id=source_id,
            content_type_id=content_type.pk, object_id=instance.pk, **extra,
        )

    def test_verified_ids_backfill_and_existing_foreign_keys_survive_upgrade(self):
        def model(app, name):
            return self.old_apps.get_model(app, name)

        round_row = model('mscc', 'Round').objects.create(name='Legacy round')
        center = model('locations', 'Center').objects.create(name='Legacy centre')
        child = model('child', 'Child').objects.create(unicef_id='NOT-THE-BMA-ID')
        untagged = model('child', 'Child').objects.create(unicef_id='LOCAL-ONLY')
        registration = model('mscc', 'Registration').objects.create(
            child_id=child.pk, center_id=center.pk, round_id=round_row.pk,
        )
        teacher = model('mscc', 'Teacher').objects.create(center_id=center.pk)
        day = model('attendances', 'MSCCAttendance').objects.create(
            center_id=center.pk, round_id=round_row.pk,
        )
        child_day = model('attendances', 'MSCCAttendanceChild').objects.create(
            attendance_day_id=day.pk, registration_id=registration.pk, child_id=child.pk,
        )
        entities = [
            ('mscc.round', round_row, 'round-3'),
            ('locations.center', center, 'center-41'),
            ('child.child', child, 'child-900'),
            ('mscc.registration', registration, 'registration-1234'),
            ('mscc.teacher', teacher, 'teacher-7'),
            ('attendances.mscc_attendance', day, 'day-500'),
        ]
        for name, resource, source_id in (
            ('EducationService', 'mscc.education_service', 'service-10'),
            ('EducationProgrammeAssessment', 'mscc.education_grading', 'grading-11'),
            ('Referral', 'mscc.referral', 'referral-12'),
        ):
            row = model('mscc', name).objects.create(registration_id=registration.pk)
            entities.append((resource, row, source_id))
        for resource, instance, source_id in entities:
            self.make_mapping(resource, instance, source_id)
        # A deleted mapping does not verify an active BMA identity.
        stale = model('child', 'Child').objects.create(unicef_id='STALE')
        self.make_mapping('child.child', stale, 'old-child', deleted=True)

        new_apps = self.upgrade()
        for resource, instance, source_id in entities:
            with self.subTest(resource=resource):
                upgraded = new_apps.get_model(instance._meta.app_label, instance._meta.model_name)
                self.assertEqual(upgraded.objects.get(pk=instance.pk).bma_id, source_id)
        Child = new_apps.get_model('child', 'Child')
        self.assertIsNone(Child.objects.get(pk=untagged.pk).bma_id)
        self.assertIsNone(Child.objects.get(pk=stale.pk).bma_id)
        Registration = new_apps.get_model('mscc', 'Registration')
        upgraded_registration = Registration.objects.get(pk=registration.pk)
        self.assertEqual(upgraded_registration.child_id, child.pk)
        self.assertEqual(upgraded_registration.round_id, round_row.pk)
        self.assertEqual(upgraded_registration.center_id, center.pk)
        Attendance = new_apps.get_model('attendances', 'MSCCAttendance')
        self.assertEqual(Attendance.objects.get(pk=day.pk).round_id, round_row.pk)
        self.assertTrue(Attendance._meta.get_field('round').is_relation)
        AttendanceChild = new_apps.get_model('attendances', 'MSCCAttendanceChild')
        self.assertEqual(AttendanceChild.objects.get(pk=child_day.pk).registration_id, registration.pk)
        Mapping = new_apps.get_model('datasync', 'SyncedRecord')
        self.assertEqual(Mapping.objects.get(resource='mscc.teacher').source_scope, 'center-41')
        connection.check_constraints()

    def test_conflicting_legacy_mappings_stop_upgrade_without_merging_children(self):
        Child = self.old_apps.get_model('child', 'Child')
        child = Child.objects.create(unicef_id='LOCAL-CHILD')
        self.make_mapping('child.child', child, 'child-900')
        conflicting = self.make_mapping('child.child', child, 'child-901')
        try:
            with self.assertRaisesMessage(ValueError, 'maps to multiple BMA IDs'):
                self.upgrade()
            executor = MigrationExecutor(connection)
            state = executor.loader.project_state([
                ('datasync', '0002_alter_syncedrecord_unique_together_and_more'),
                ('mscc', '0017_educationprogrammeassessment_bma_id_and_more'),
                ('attendances', '0004_msccattendance_bma_id_and_round_fk'),
                ('child', '0009_child_bma_id'),
            ]).apps
            NewChild = state.get_model('child', 'Child')
            self.assertEqual(NewChild.objects.count(), 1)
            self.assertIsNone(NewChild.objects.get(pk=child.pk).bma_id)
        finally:
            # Reconcile the fixture so normal teardown can restore the new schema.
            self.old_apps.get_model('datasync', 'SyncedRecord').objects.filter(pk=conflicting.pk).delete()
        self.upgrade()
