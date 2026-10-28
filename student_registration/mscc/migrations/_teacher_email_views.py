"""Preserve PostgreSQL reporting views while migration 0020 widens email."""


def _quote_identifier(name):
    return '"{}"'.format(name.replace('"', '""'))


def _role(grantee, name, quote):
    return 'PUBLIC' if grantee == 0 else quote(name)


def _relation_grants(cursor, oid):
    cursor.execute('''
        SELECT acl.grantee, pg_get_userbyid(acl.grantee),
               acl.privilege_type, acl.is_grantable
        FROM pg_class c,
             LATERAL aclexplode(COALESCE(c.relacl, acldefault('r', c.relowner))) acl
        WHERE c.oid = %s
    ''', [oid])
    return cursor.fetchall()


def _dependent_views(cursor, table, column, quote):
    cursor.execute('''
        WITH RECURSIVE dependent(oid) AS (
            SELECT rw.ev_class
            FROM pg_depend d JOIN pg_rewrite rw ON rw.oid = d.objid
            WHERE d.classid = 'pg_rewrite'::regclass
              AND d.refclassid = 'pg_class'::regclass
              AND d.refobjid = %s::regclass
              AND d.refobjsubid IN (0, (
                  SELECT attnum FROM pg_attribute
                  WHERE attrelid = %s::regclass AND attname = %s))
              AND rw.ev_class <> d.refobjid
            UNION
            SELECT rw.ev_class
            FROM dependent parent
            JOIN pg_depend d ON d.refobjid = parent.oid
            JOIN pg_rewrite rw ON rw.oid = d.objid
            WHERE d.classid = 'pg_rewrite'::regclass
              AND d.refclassid = 'pg_class'::regclass
              AND rw.ev_class <> parent.oid
        )
        SELECT c.oid, n.nspname, c.relname, c.relkind,
               pg_get_userbyid(c.relowner), c.reloptions,
               obj_description(c.oid, 'pg_class'), pg_get_viewdef(c.oid, false)
        FROM dependent JOIN pg_class c ON c.oid = dependent.oid
        JOIN pg_namespace n ON n.oid = c.relnamespace
        ORDER BY c.oid
    ''', [table, table, column])
    views = {}
    for oid, schema, name, kind, owner, options, comment, definition in cursor.fetchall():
        qualified = '{}.{}'.format(quote(schema), quote(name))
        if kind != 'v':
            raise RuntimeError('Teacher email migration requires DBA handling for dependent materialized view {}. '
                               'No reporting objects have been removed.'.format(qualified))
        views[oid] = dict(oid=oid, name=qualified, owner=owner, options=options or [],
                          comment=comment, definition=definition)
    if not views:
        return []

    # Capture all metadata before dropping anything. Custom writable views and
    # security labels require deployment-specific handling rather than data loss.
    for view in views.values():
        oid = view['oid']
        cursor.execute('''
            SELECT EXISTS(SELECT 1 FROM pg_rewrite WHERE ev_class = %s AND rulename <> '_RETURN'),
                   EXISTS(SELECT 1 FROM pg_trigger WHERE tgrelid = %s AND NOT tgisinternal),
                   EXISTS(SELECT 1 FROM pg_seclabel WHERE classoid = 'pg_class'::regclass AND objoid = %s)
        ''', [oid, oid, oid])
        if any(cursor.fetchone()):
            raise RuntimeError('Dependent view {} has custom rules, triggers or security labels. '
                               'A DBA must preserve these before changing Teacher.email. '
                               'No reporting objects have been removed.'.format(view['name']))
        cursor.execute('''
            SELECT a.attname, col_description(a.attrelid, a.attnum),
                   pg_get_expr(d.adbin, d.adrelid)
            FROM pg_attribute a LEFT JOIN pg_attrdef d
              ON d.adrelid = a.attrelid AND d.adnum = a.attnum
            WHERE a.attrelid = %s AND a.attnum > 0 AND NOT a.attisdropped
            ORDER BY a.attnum
        ''', [oid])
        view['columns'] = cursor.fetchall()
        view['grants'] = _relation_grants(cursor, oid)
        cursor.execute('''
            SELECT a.attname, acl.grantee, pg_get_userbyid(acl.grantee),
                   acl.privilege_type, acl.is_grantable
            FROM pg_attribute a, LATERAL aclexplode(a.attacl) acl
            WHERE a.attrelid = %s AND a.attnum > 0 AND NOT a.attisdropped
        ''', [oid])
        view['column_grants'] = cursor.fetchall()

    cursor.execute('''
        SELECT DISTINCT rw.ev_class, d.refobjid
        FROM pg_depend d JOIN pg_rewrite rw ON rw.oid = d.objid
        WHERE d.classid = 'pg_rewrite'::regclass AND d.refclassid = 'pg_class'::regclass
          AND rw.ev_class = ANY(%s::oid[]) AND d.refobjid = ANY(%s::oid[])
          AND rw.ev_class <> d.refobjid
    ''', [list(views), list(views)])
    parents = {oid: set() for oid in views}
    for child, parent in cursor.fetchall():
        parents[child].add(parent)
    ordered = []
    remaining = set(views)
    while remaining:
        ready = sorted(oid for oid in remaining if not parents[oid].intersection(remaining))
        if not ready:
            raise RuntimeError('Dependent reporting views contain a cycle; Teacher.email was not changed.')
        ordered.extend(views[oid] for oid in ready)
        remaining.difference_update(ready)
    return ordered


def _restore_views(cursor, views, quote):
    for view in views:
        options = ''
        if view['options']:
            items = [option.split('=', 1) for option in view['options']]
            options = ' WITH ({})'.format(', '.join('{} = %s'.format(quote(key)) for key, _ in items))
            values = [value for _, value in items]
        else:
            values = []
        columns = ', '.join(quote(name) for name, _, _ in view['columns'])
        cursor.execute('CREATE VIEW {} ({}){} AS {}'.format(
            view['name'], columns, options, view['definition']), values or None)

    for view in views:
        name = view['name']
        cursor.execute('COMMENT ON VIEW {} IS %s'.format(name), [view['comment']])
        for column, comment, default in view['columns']:
            cursor.execute('COMMENT ON COLUMN {}.{} IS %s'.format(name, quote(column)), [comment])
            if default is not None:
                cursor.execute('ALTER VIEW {} ALTER COLUMN {} SET DEFAULT {}'.format(name, quote(column), default))

        # Remove grants introduced by current DEFAULT PRIVILEGES, then restore
        # the saved effective grants (including column grants and grant options).
        cursor.execute('SELECT %s::regclass::oid', [name])
        new_oid = cursor.fetchone()[0]
        grantees = {(grantee, role_name) for grantee, role_name, _, _ in _relation_grants(cursor, new_oid)}
        for grantee, role_name in grantees:
            cursor.execute('REVOKE ALL PRIVILEGES ON TABLE {} FROM {}'.format(
                name, _role(grantee, role_name, quote)))
        for grantee, role_name, privilege, grantable in view['grants']:
            cursor.execute('GRANT {} ON TABLE {} TO {}{}'.format(
                privilege, name, _role(grantee, role_name, quote), ' WITH GRANT OPTION' if grantable else ''))
        for column, grantee, role_name, privilege, grantable in view['column_grants']:
            cursor.execute('GRANT {} ({}) ON TABLE {} TO {}{}'.format(
                privilege, quote(column), name, _role(grantee, role_name, quote),
                ' WITH GRANT OPTION' if grantable else ''))
        cursor.execute('ALTER VIEW {} OWNER TO {}'.format(name, quote(view['owner'])))


def _alter_email(apps, schema_editor, old_length, new_length):
    Teacher = apps.get_model('mscc', 'Teacher')
    original = Teacher._meta.get_field('email')
    fields = []
    for length in (old_length, new_length):
        field = original.clone()
        field.set_attributes_from_name(original.name)
        field.model = Teacher
        field.max_length = length
        fields.append(field)
    if schema_editor.connection.vendor != 'postgresql':
        schema_editor.alter_field(Teacher, *fields)
        return
    if not schema_editor.connection.in_atomic_block:
        raise RuntimeError('Teacher email migration requires an atomic database transaction.')
    quote = _quote_identifier
    table = Teacher._meta.db_table
    with schema_editor.connection.cursor() as cursor:
        # Lock before collecting dependencies, so another transaction cannot add
        # a view between the snapshot and the ALTER COLUMN operation.
        cursor.execute('LOCK TABLE {} IN ACCESS EXCLUSIVE MODE'.format(quote(table)))
        if new_length < old_length:
            cursor.execute('SELECT 1 FROM {} WHERE length({}) > %s LIMIT 1'.format(
                quote(table), quote(original.column)), [new_length])
            if cursor.fetchone():
                raise RuntimeError('Cannot shorten Teacher.email to {} while longer addresses exist.'.format(new_length))
        views = _dependent_views(cursor, table, original.column, quote)
        for view in reversed(views):
            # RESTRICT is intentional: unknown dependencies abort atomically.
            cursor.execute('DROP VIEW {} RESTRICT'.format(view['name']))
        schema_editor.alter_field(Teacher, *fields)
        _restore_views(cursor, views, quote)


def widen_teacher_email(apps, schema_editor):
    _alter_email(apps, schema_editor, 100, 254)


def restore_teacher_email(apps, schema_editor):
    _alter_email(apps, schema_editor, 254, 100)
