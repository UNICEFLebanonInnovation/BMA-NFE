from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('child', '0007_child_photo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='child',
            name='unicef_id',
            field=models.CharField(blank=True, max_length=45, null=True, verbose_name='UNIQUE ID'),
        ),
    ]
