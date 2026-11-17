from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schools', '0003_school_fields'),
    ]

    operations = [
        migrations.AlterField(
            model_name='school',
            name='type',
            field=models.CharField(
                blank=True,
                choices=[
                    ('', '----------'),
                    ('Public School', 'Public School'),
                    ('Private School', 'Private School'),
                    ('Private Free School', 'Private Free School'),
                ],
                max_length=100,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name='school',
            name='operating_shift',
            field=models.CharField(
                blank=True,
                choices=[
                    ('', '----------'),
                    ('morning shift', 'Morning shift'),
                    ('afternoon shift', 'Afternoon shift'),
                ],
                max_length=20,
                null=True,
                verbose_name='Operating shift',
            ),
        ),
    ]
