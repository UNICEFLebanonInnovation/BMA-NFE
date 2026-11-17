from django.db import migrations, models

from ._teacher_email_views import restore_teacher_email, widen_teacher_email


class Migration(migrations.Migration):
    dependencies = [('mscc', '0019_teacher_program_staff')]
    operations = [migrations.SeparateDatabaseAndState(
        database_operations=[migrations.RunPython(
            widen_teacher_email, restore_teacher_email, hints={'model_name': 'teacher'})],
        state_operations=[migrations.AlterField(
            'teacher', 'email', models.CharField(blank=True, null=True, max_length=254, verbose_name='Email'))],
    )]
