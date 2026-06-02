from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('mscc', '0010_teacher_training_date_of_completion'),
    ]

    operations = [
        migrations.AlterField(
            model_name='teacher',
            name='unicef_id',
            field=models.CharField(blank=True, max_length=45, null=True, verbose_name='UNIQUE ID'),
        ),
    ]
