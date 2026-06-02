from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('child', '0005_child_disability_other'),
    ]
    operations = [
        migrations.AddField(
            model_name='child',
            name='photo',
            field=models.ImageField(blank=True, null=True, upload_to='child_photos/', verbose_name='Child Photo'),
        ),
    ]
