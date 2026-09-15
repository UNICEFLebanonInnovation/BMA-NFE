from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('alp', '0010_merge_20260912_1813'),
        ('schools', '0005_merge_20260831_1607'),
    ]

    operations = [
        migrations.AddField(
            model_name='alpregistration',
            name='section',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='+',
                to='schools.section',
                verbose_name='Section',
            ),
        ),
        migrations.AddField(
            model_name='alpattendance',
            name='section',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='+',
                to='schools.section',
                verbose_name='Section',
            ),
        ),
    ]
