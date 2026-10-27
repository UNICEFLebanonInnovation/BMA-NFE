from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('mscc', '0018_educationassessment_bma_id')]
    operations = [
        migrations.AddField('teacher', 'bma_source', models.CharField(default='mscc.teacher', editable=False, max_length=64)),
        migrations.AddField('teacher', 'facilitator_name', models.CharField(blank=True, default='', max_length=200, verbose_name='Facilitator name')),
        migrations.AddField('teacher', 'program_staff_details', models.JSONField(blank=True, default=dict, verbose_name='Makani program staff details')),
        migrations.RemoveConstraint('teacher', 'mscc_teacher_bma_center_uniq'),
        migrations.AddConstraint('teacher', models.UniqueConstraint(fields=['bma_source', 'bma_id', 'center'], name='mscc_teacher_source_center_uniq')),
        migrations.AddConstraint('teacher', models.UniqueConstraint(fields=['bma_source', 'bma_id'], condition=models.Q(bma_source='locations.program_staff'), name='mscc_program_staff_bma_uniq')),
    ]
