# Teacher email migration and existing reporting views

Azure startup logs on 2026-10-28 show `mscc.0020_teacher_email_length` failing:

```
cannot alter type of a column used by a view or rule
rule _RETURN on view vw_center_teacher depends on column "email"
```

The original migration widens `mscc_teacher.email` from 100 to 254 characters.
PostgreSQL blocks this while a reporting view depends on that column. The
container entrypoint runs migrations before starting the app and exits on an
error, so this failure prevents that receiver instance from starting normally.

Migration 0020 now preserves ordinary dependent views in one transaction:

1. Lock the teacher table and collect the affected views and their dependencies.
2. Save their definitions, schema and column names, options, owner, comments,
   column defaults, effective permissions and grant options.
3. Remove affected views in dependency order using `RESTRICT`, widen the column,
   and restore the saved views and access settings.

An error rolls the transaction back. Unrelated views and teacher records are
retained. Materialized views, custom rules, triggers and security labels cause
an explicit failure before any views are removed, so a DBA can preserve their
deployment-specific behavior. The migration role needs ownership/DDL rights
over the table and affected views, including permission to restore their owners.

Deploy the updated BMA-NFE files and allow the normal deployment migration step
to retry pending migration 0020. Its Django model state remains email length
254. Environments where 0020 already succeeded do not rerun it. A later
migration cannot repair an environment that stops at the earlier failed 0020,
which is why the pending migration itself is corrected.

Rollback restores 100 characters only when no longer addresses exist. It refuses
to truncate saved addresses. The earlier 503 describes receiver availability;
after the receiver starts, verify the Compiler worker and existing bulk requests
separately if they still show zero queued events.

Regression checks reproduce the original PostgreSQL failure, upgrade and reverse
with views, long email storage, dependent-view chains, quoted identifiers,
owners, grant options, defaults, comments, column permissions, default-privilege
isolation, atomic rollback and unsupported-object preservation.

Validation: 208 NFE regression tests passed. All 13 focused migration checks
also passed after the final identifier-quoting and router-hint adjustments.
`makemigrations mscc --check --dry-run` found no model-state drift. Azure
staging must still apply the repaired pending migration during deployment.
