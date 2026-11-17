from django.db import migrations, models


def restore_mscc_assignment_values(apps, schema_editor):
    teacher = apps.get_model('mscc', 'Teacher')
    teacher.objects.filter(teacher_assignment='ALP only').update(
        teacher_assignment='Makani only'
    )
    teacher.objects.filter(teacher_assignment='ALP and private').update(
        teacher_assignment='Private and Makani'
    )


def reapply_alp_assignment_values(apps, schema_editor):
    teacher = apps.get_model('mscc', 'Teacher')
    teacher.objects.filter(teacher_assignment='Makani only').update(
        teacher_assignment='ALP only'
    )
    teacher.objects.filter(teacher_assignment='Private and Makani').update(
        teacher_assignment='ALP and private'
    )


class Migration(migrations.Migration):

    dependencies = [
        ('mscc', '0017_update_teacher_assignment'),
    ]

    operations = [
        migrations.RunPython(
            restore_mscc_assignment_values,
            reapply_alp_assignment_values,
        ),
        migrations.AlterField(
            model_name='teacher',
            name='teacher_assignment',
            field=models.CharField(
                blank=True,
                choices=[
                    ('Makani only', 'Makani only'),
                    ('Private and Makani', 'Private and Makani'),
                ],
                max_length=100,
                null=True,
                verbose_name='Teacher Assignment',
            ),
        ),
        migrations.RemoveField(
            model_name='teacher',
            name='teacher_assignment_other',
        ),
    ]
