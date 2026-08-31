from django.db import migrations, models


def update_assignment_values(apps, schema_editor):
    teacher = apps.get_model('mscc', 'Teacher')
    teacher.objects.filter(teacher_assignment='Makani only').update(
        teacher_assignment='ALP only'
    )
    teacher.objects.filter(teacher_assignment='Private and Makani').update(
        teacher_assignment='ALP and private'
    )


def restore_assignment_values(apps, schema_editor):
    teacher = apps.get_model('mscc', 'Teacher')
    teacher.objects.filter(teacher_assignment='ALP only').update(
        teacher_assignment='Makani only'
    )
    teacher.objects.filter(teacher_assignment='ALP and private').update(
        teacher_assignment='Private and Makani'
    )


class Migration(migrations.Migration):

    dependencies = [
        ('mscc', '0016_merge_20260830_1305'),
    ]

    operations = [
        migrations.AddField(
            model_name='teacher',
            name='teacher_assignment_other',
            field=models.CharField(
                blank=True,
                max_length=255,
                null=True,
                verbose_name='Other teacher assignment',
            ),
        ),
        migrations.RunPython(update_assignment_values, restore_assignment_values),
        migrations.AlterField(
            model_name='teacher',
            name='teacher_assignment',
            field=models.CharField(
                blank=True,
                choices=[
                    ('ALP only', 'ALP only'),
                    ('ALP and FE', 'ALP and FE'),
                    ('ALP and private', 'ALP and private'),
                    ('other', 'other'),
                ],
                max_length=100,
                null=True,
                verbose_name='Teacher Assignment',
            ),
        ),
    ]
