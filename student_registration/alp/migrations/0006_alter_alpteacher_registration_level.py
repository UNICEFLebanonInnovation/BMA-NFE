from django.contrib.postgres.fields import ArrayField
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('alp', '0005_merge_20260830_1305'),
    ]

    operations = [
        migrations.AlterField(
            model_name='alpteacher',
            name='registration_level',
            field=ArrayField(
                base_field=models.CharField(
                    blank=True,
                    choices=[
                        ('Level one', 'Level one'),
                        ('Level two', 'Level two'),
                        ('Level three', 'Level three'),
                        ('Level four', 'Level four'),
                    ],
                    max_length=200,
                    null=True,
                ),
                blank=True,
                null=True,
                size=None,
                verbose_name='Dirasa Grade level',
            ),
        ),
    ]
