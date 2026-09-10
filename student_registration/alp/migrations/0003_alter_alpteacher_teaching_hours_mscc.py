from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('alp', '0002_alpteacher_updates'),
    ]

    operations = [
        migrations.AlterField(
            model_name='alpteacher',
            name='teaching_hours_mscc',
            field=models.IntegerField(
                blank=True,
                null=True,
                verbose_name='Number of teaching hours per week under ALP',
            ),
        ),
    ]
