from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('child', '0004_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='child',
            name='disability_other',
            field=models.TextField(blank=True, null=True, verbose_name='Other Disability'),
        ),
    ]
