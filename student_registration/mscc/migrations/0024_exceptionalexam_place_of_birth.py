from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mscc', '0023_translate_exceptional_exam_labels'),
    ]

    operations = [
        migrations.AddField(
            model_name='exceptionalexam',
            name='place_of_birth',
            field=models.CharField(blank=True, default='', max_length=100, verbose_name='Place of Birth'),
        ),
    ]
