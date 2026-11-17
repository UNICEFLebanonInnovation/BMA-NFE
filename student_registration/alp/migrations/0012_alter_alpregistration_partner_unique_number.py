from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('alp', '0011_alp_sections'),
    ]

    operations = [
        migrations.AlterField(
            model_name='alpregistration',
            name='partner_unique_number',
            field=models.CharField(
                blank=True,
                max_length=50,
                null=True,
                verbose_name='Unique child number',
            ),
        ),
    ]
