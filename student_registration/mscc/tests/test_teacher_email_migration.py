"""Upgrade existing PostgreSQL reporting views, not just an empty schema."""
from importlib import import_module
from unittest import skipUnless
from unittest.mock import patch
import uuid

from django.db import connection, migrations, models, NotSupportedError
from django.db.migrations.executor import MigrationExecutor
from django.test import TransactionTestCase

from student_registration.mscc.models import Teacher


@skipUnless(connection.vendor == 'postgresql', 'Reporting-view regression is PostgreSQL-specific')
class TeacherEmailViewMigrationTests(TransactionTestCase):
    def setUp(self):
        self.helper = import_module('student_registration.mscc.migrations._teacher_email_views')
        module = import_module('student_registration.mscc.migrations.0020_teacher_email_length')
        self.migration = module.Migration('0020_teacher_email_length', 'mscc')
        self.before = MigrationExecutor(connection).loader.project_state([('mscc', '0019_teacher_program_staff')])
        self.after = self.before.clone()
        for operation in self.migration.operations:
            operation.state_forwards('mscc', self.after)
        self.schema = 'qa_teacher_email_' + uuid.uuid4().hex[:10]
        self.roles = []
        self.quote = lambda name: '"{}"'.format(name.replace('"', '""'))
        with connection.cursor() as cursor:
            cursor.execute('CREATE SCHEMA {}'.format(self.quote(self.schema)))
        with connection.schema_editor() as editor:
            self.helper.restore_teacher_email(self.after.apps, editor)
        self.teacher = Teacher.objects.create(email='teacher@example.test')

    def tearDown(self):
        # Only this test's unique schema is removed; real teacher data is kept.
        assert self.schema.startswith('qa_teacher_email_')
        with connection.cursor() as cursor:
            cursor.execute('DROP SCHEMA {} CASCADE'.format(self.quote(self.schema)))
        with connection.schema_editor() as editor:
            self.helper.widen_teacher_email(self.before.apps, editor)
        for role in self.roles:
            self.execute('DROP ROLE {}'.format(self.quote(role)))
        super().tearDown()

    def name(self, name='vw_center_teacher'):
        return '{}.{}'.format(self.quote(self.schema), self.quote(name))

    def execute(self, sql, params=None):
        with connection.cursor() as cursor:
            cursor.execute(sql, params)
            return cursor.fetchall() if cursor.description else None

    def view(self, name='vw_center_teacher', source=None, options=''):
        self.execute('CREATE VIEW {} {} AS {}'.format(self.name(name), options,
                     source or 'SELECT id, email FROM mscc_teacher'))

    def upgrade(self):
        with connection.schema_editor() as editor:
            state = self.migration.apply(self.before.clone(), editor)
        self.assertEqual(state.apps.get_model('mscc', 'Teacher')._meta.get_field('email').max_length, 254)

    def reverse(self):
        with connection.schema_editor() as editor:
            for operation in reversed(self.migration.operations):
                operation.database_backwards('mscc', editor, self.after, self.before)

    def length(self):
        return self.execute("SELECT character_maximum_length FROM information_schema.columns "
                            "WHERE table_schema=current_schema() AND table_name='mscc_teacher' "
                            "AND column_name='email'")[0][0]

    def metadata(self, name='vw_center_teacher'):
        qualified = self.name(name)
        row = self.execute('SELECT c.relowner, c.reloptions, obj_description(c.oid), pg_get_viewdef(c.oid, false) '
                           'FROM pg_class c WHERE c.oid=%s::regclass', [qualified])[0]
        columns = self.execute('SELECT a.attname, col_description(a.attrelid,a.attnum), '
                               'pg_get_expr(d.adbin,d.adrelid) FROM pg_attribute a LEFT JOIN pg_attrdef d '
                               'ON d.adrelid=a.attrelid AND d.adnum=a.attnum WHERE a.attrelid=%s::regclass '
                               'AND a.attnum>0 ORDER BY a.attnum', [qualified])
        grants = self.execute("SELECT x.grantee,x.privilege_type,x.is_grantable FROM pg_class c, "
                              "LATERAL aclexplode(COALESCE(c.relacl,acldefault('r',c.relowner))) x "
                              "WHERE c.oid=%s::regclass ORDER BY 1,2,3", [qualified])
        column_grants = self.execute('SELECT a.attname,x.grantee,x.privilege_type,x.is_grantable '
                                     'FROM pg_attribute a, LATERAL aclexplode(a.attacl) x '
                                     'WHERE a.attrelid=%s::regclass ORDER BY 1,2,3,4', [qualified])
        return row, columns, grants, column_grants

    def test_original_failure_is_reproduced_and_patched_migration_preserves_data(self):
        self.view()
        old = migrations.AlterField('teacher', 'email', models.CharField(
            blank=True, null=True, max_length=254, verbose_name='Email'))
        with self.assertRaises(NotSupportedError):
            with connection.schema_editor() as editor:
                old.database_forwards('mscc', editor, self.before, self.after)
        self.assertEqual(self.length(), 100)
        self.upgrade()
        self.assertEqual(self.length(), 254)
        self.assertEqual(self.execute('SELECT email FROM {} WHERE id=%s'.format(self.name()),
                                     [self.teacher.pk]), [('teacher@example.test',)])
        long_email = 'teacher-' + 'a' * 110 + '@example.test'
        Teacher.objects.filter(pk=self.teacher.pk).update(email=long_email)
        self.assertEqual(self.execute('SELECT email FROM {} WHERE id=%s'.format(self.name()),
                                     [self.teacher.pk])[0][0], long_email)

    def test_clean_schema_without_reporting_views_still_upgrades(self):
        self.upgrade()
        self.assertEqual(self.length(), 254)

    def test_view_dependency_diamond_is_restored_in_order(self):
        self.view('Teacher "Quoted" Report')
        self.view('Second Report', 'SELECT id,email FROM mscc_teacher WHERE email IS NOT NULL')
        self.view('Combined Report', 'SELECT a.id,a.email FROM {} a JOIN {} b USING(id)'.format(
            self.name('Teacher "Quoted" Report'), self.name('Second Report')))
        self.view('Final Report', 'SELECT * FROM {}'.format(self.name('Combined Report')))
        self.upgrade()
        self.assertEqual(self.execute('SELECT email FROM {}'.format(self.name('Final Report'))),
                         [('teacher@example.test',)])

    def test_options_comments_defaults_column_names_and_grants_survive(self):
        self.view(options='WITH (security_barrier=true)')
        self.execute('COMMENT ON VIEW {} IS %s'.format(self.name()), ['Teacher report comment'])
        self.execute('COMMENT ON COLUMN {}.email IS %s'.format(self.name()), ['Full contact email'])
        self.execute("ALTER VIEW {} ALTER COLUMN email SET DEFAULT 'default@example.test'".format(self.name()))
        self.execute('GRANT SELECT ON TABLE {} TO PUBLIC'.format(self.name()))
        self.execute('GRANT SELECT(email) ON TABLE {} TO PUBLIC'.format(self.name()))
        self.execute('ALTER VIEW {} RENAME COLUMN email TO {}'.format(self.name(), self.quote('Email Contact')))
        before = self.metadata()
        self.upgrade()
        self.assertEqual(self.metadata(), before)

    def test_new_default_privileges_do_not_expand_original_view_access(self):
        self.view()
        before = self.metadata()
        self.execute('ALTER DEFAULT PRIVILEGES IN SCHEMA {} GRANT SELECT ON TABLES TO PUBLIC'.format(
            self.quote(self.schema)))
        self.upgrade()
        self.assertEqual(self.metadata(), before)

    def test_existing_owner_and_grant_options_survive(self):
        allowed = self.execute('SELECT rolsuper OR rolcreaterole FROM pg_roles WHERE rolname=current_user')[0][0]
        if not allowed:
            self.skipTest('Test role cannot create disposable ownership fixtures')
        owner, reader = ['qa_email_{}_{}'.format(kind, uuid.uuid4().hex[:8]) for kind in ('owner', 'reader')]
        for role in (owner, reader):
            self.execute('CREATE ROLE {} NOLOGIN'.format(self.quote(role)))
            self.roles.append(role)
        self.view()
        self.execute('GRANT USAGE, CREATE ON SCHEMA {} TO {}'.format(self.quote(self.schema), self.quote(owner)))
        self.execute('ALTER VIEW {} OWNER TO {}'.format(self.name(), self.quote(owner)))
        self.execute('GRANT SELECT ON TABLE {} TO {} WITH GRANT OPTION'.format(self.name(), self.quote(reader)))
        before = self.metadata()
        self.upgrade()
        self.assertEqual(self.metadata(), before)

    def test_view_column_type_tracks_the_wider_table_column(self):
        self.view()
        self.upgrade()
        value = self.execute('SELECT character_maximum_length FROM information_schema.columns '
                             'WHERE table_schema=%s AND table_name=%s AND column_name=%s',
                             [self.schema, 'vw_center_teacher', 'email'])[0][0]
        self.assertEqual(value, 254)

    def test_unrelated_view_is_not_recreated(self):
        self.view()
        self.view('Unrelated Report', 'SELECT 42 AS answer')
        oid = self.execute('SELECT %s::regclass::oid', [self.name('Unrelated Report')])[0][0]
        self.upgrade()
        self.assertEqual(self.execute('SELECT %s::regclass::oid', [self.name('Unrelated Report')])[0][0], oid)

    def test_recreation_failure_rolls_back_column_and_reporting_view(self):
        self.view()
        before = self.metadata()
        with patch.object(self.helper, '_restore_views', side_effect=RuntimeError('simulated restore failure')):
            with self.assertRaisesMessage(RuntimeError, 'simulated restore failure'):
                self.upgrade()
        self.assertEqual(self.length(), 100)
        self.assertEqual(self.metadata(), before)
        self.assertEqual(self.execute('SELECT count(*) FROM {}'.format(self.name()))[0][0], 1)

    def test_reverse_restores_short_column_and_views(self):
        self.view()
        self.upgrade()
        self.reverse()
        self.assertEqual(self.length(), 100)
        self.assertEqual(self.execute('SELECT email FROM {}'.format(self.name())), [('teacher@example.test',)])

    def test_reverse_refuses_to_truncate_long_email_addresses(self):
        self.view()
        self.upgrade()
        long_email = 'a' * 110 + '@example.test'
        Teacher.objects.filter(pk=self.teacher.pk).update(email=long_email)
        before = self.metadata()
        with self.assertRaisesMessage(RuntimeError, 'longer addresses exist'):
            self.reverse()
        self.assertEqual(self.length(), 254)
        self.assertEqual(self.metadata(), before)
        self.assertEqual(self.execute('SELECT email FROM {}'.format(self.name()))[0][0], long_email)

    def test_materialized_dependency_is_preserved_with_actionable_failure(self):
        self.view()
        self.execute('CREATE MATERIALIZED VIEW {} AS SELECT * FROM {}'.format(
            self.name('Cached Report'), self.name()))
        before = self.metadata()
        with self.assertRaisesMessage(RuntimeError, 'dependent materialized view'):
            self.upgrade()
        self.assertEqual(self.length(), 100)
        self.assertEqual(self.metadata(), before)
        self.assertEqual(self.execute('SELECT email FROM {}'.format(self.name('Cached Report'))),
                         [('teacher@example.test',)])

    def test_custom_trigger_is_preserved_with_actionable_failure(self):
        self.view()
        self.execute('CREATE FUNCTION {}() RETURNS trigger LANGUAGE plpgsql AS '
                     '$$ BEGIN RETURN NEW; END $$'.format(self.name('keep_trigger')))
        self.execute('CREATE TRIGGER keep_insert INSTEAD OF INSERT ON {} FOR EACH ROW '
                     'EXECUTE FUNCTION {}()'.format(self.name(), self.name('keep_trigger')))
        before = self.metadata()
        with self.assertRaisesMessage(RuntimeError, 'custom rules, triggers or security labels'):
            self.upgrade()
        self.assertEqual(self.length(), 100)
        self.assertEqual(self.metadata(), before)
        self.assertEqual(self.execute("SELECT count(*) FROM pg_trigger WHERE tgrelid=%s::regclass "
                                      "AND tgname='keep_insert'", [self.name()])[0][0], 1)
