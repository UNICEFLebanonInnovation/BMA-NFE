from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('child', '0005_child_disability_other'),
    ]
    operations = [
        migrations.RemoveField(
            model_name='child',
            name='unicef_id',
        ),
    ]
