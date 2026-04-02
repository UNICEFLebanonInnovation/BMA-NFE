# Generated manually to add indexes from docs/analytics_dashboard.md
from django.db import migrations


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ('mscc', '0005_teacher'),
        ('child', '0004_initial'),
    ]

    operations = [
        migrations.RunSQL(
            sql=[
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_mscc_registration_created ON mscc_registration (created);",
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_mscc_registration_partner_created ON mscc_registration (partner_id, created);",
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_mscc_registration_center_created ON mscc_registration (center_id, created);",
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_mscc_registration_deleted_created ON mscc_registration (deleted, created);",
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_educationservice_registration_latest ON mscc_educationservice (registration_id, id DESC);"
            ],
            reverse_sql=[
                "DROP INDEX CONCURRENTLY IF EXISTS idx_mscc_registration_created;",
                "DROP INDEX CONCURRENTLY IF EXISTS idx_mscc_registration_partner_created;",
                "DROP INDEX CONCURRENTLY IF EXISTS idx_mscc_registration_center_created;",
                "DROP INDEX CONCURRENTLY IF EXISTS idx_mscc_registration_deleted_created;",
                "DROP INDEX CONCURRENTLY IF EXISTS idx_educationservice_registration_latest;"
            ],
            state_operations=[]
        ),
        migrations.RunSQL(
            sql=[
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_child_gender ON child_child (gender);",
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_child_nationality ON child_child (nationality_id);",
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_child_birthday_year ON child_child (birthday_year);"
            ],
            reverse_sql=[
                "DROP INDEX CONCURRENTLY IF EXISTS idx_child_gender;",
                "DROP INDEX CONCURRENTLY IF EXISTS idx_child_nationality;",
                "DROP INDEX CONCURRENTLY IF EXISTS idx_child_birthday_year;"
            ],
            state_operations=[]
        )
    ]
