from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('mscc', '0019_teacher_program_staff')]
    operations = [migrations.AlterField('teacher', 'email', models.CharField(blank=True, null=True, max_length=254, verbose_name='Email'))]
