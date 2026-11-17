from django.db import migrations, models
import django.contrib.postgres.fields


class Migration(migrations.Migration):

    dependencies = [
        ('schools', '0003_school_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='school',
            name='provided_packages',
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.CharField(
                    blank=True,
                    choices=[
                        ('Education', 'Education'),
                        ('Youth', 'Youth'),
                        ('Health & Nutrition', 'Health & Nutrition'),
                        ('Child Protection', 'Child Protection'),
                        ('Social Protection', 'Social Protection'),
                    ],
                    max_length=200,
                    null=True,
                ),
                blank=True,
                null=True,
                size=None,
                verbose_name='Provided Services',
            ),
        ),
        migrations.AddField(
            model_name='school',
            name='programs',
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.CharField(
                    blank=True,
                    choices=[
                        ('ALP', 'ALP'),
                        ('BLN', 'BLN'),
                        ('ABLN', 'ABLN'),
                        ('RS', 'RS'),
                        ('CBECE', 'CBECE'),
                        ('YBLN', 'YBLN'),
                        ('YFS', 'YFS'),
                    ],
                    max_length=200,
                    null=True,
                ),
                blank=True,
                null=True,
                size=None,
                verbose_name='Programs',
            ),
        ),
    ]
