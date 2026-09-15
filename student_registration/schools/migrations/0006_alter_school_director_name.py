from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schools', '0005_merge_20260831_1607'),
    ]

    operations = [
        migrations.AlterField(
            model_name='school',
            name='director_name',
            field=models.CharField(
                blank=True,
                max_length=100,
                null=True,
                verbose_name='Program Manager Name',
            ),
        ),
    ]
