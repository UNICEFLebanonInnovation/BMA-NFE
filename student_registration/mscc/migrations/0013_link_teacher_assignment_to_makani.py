from django.db import migrations, models


def use_makani_assignment_names(apps, schema_editor):
    teacher = apps.get_model('mscc', 'Teacher')
    teacher.objects.filter(teacher_assignment='Dirasa only').update(
        teacher_assignment='Makani only'
    )
    teacher.objects.filter(teacher_assignment='Private and Dirasa').update(
        teacher_assignment='Private and Makani'
    )


def use_dirasa_assignment_names(apps, schema_editor):
    teacher = apps.get_model('mscc', 'Teacher')
    teacher.objects.filter(teacher_assignment='Makani only').update(
        teacher_assignment='Dirasa only'
    )
    teacher.objects.filter(teacher_assignment='Private and Makani').update(
        teacher_assignment='Private and Dirasa'
    )


class Migration(migrations.Migration):

    dependencies = [
        ('mscc', '0012_merge_20260602_1359'),
    ]

    operations = [
        migrations.RunPython(
            use_makani_assignment_names,
            use_dirasa_assignment_names,
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
    ]
