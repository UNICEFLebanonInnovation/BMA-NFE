from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields

class Migration(migrations.Migration):

    dependencies = [
        ('alp', '0002_alpregistration_cash_support_programmes_and_more'),
        ('schools', '0001_initial'),
        ('child', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='alpattendance',
            options={'ordering': ['attendance_date'], 'verbose_name': 'ALP Attendance', 'verbose_name_plural': 'ALP Attendances'},
        ),
        migrations.RemoveField(
            model_name='alpattendance',
            name='date',
        ),
        migrations.RemoveField(
            model_name='alpattendance',
            name='owner',
        ),
        migrations.RemoveField(
            model_name='alpattendance',
            name='registration',
        ),
        migrations.RemoveField(
            model_name='alpattendance',
            name='shift',
        ),
        migrations.RemoveField(
            model_name='alpattendance',
            name='status',
        ),
        migrations.AddField(
            model_name='alpattendance',
            name='attendance_date',
            field=models.DateField(blank=True, null=True, verbose_name='Attendance date'),
        ),
        migrations.AddField(
            model_name='alpattendance',
            name='close_reason',
            field=models.CharField(blank=True, choices=[('', '----------'), ('Public Holiday', 'Public Holiday'), ('School Holiday', 'School Holiday'), ('Strike', 'Strike'), ('Weekly Holiday', 'Weekly Holiday'), ('Roads Closed', 'Roads Closed')], max_length=50, null=True, verbose_name='Day off reason'),
        ),
        migrations.AddField(
            model_name='alpattendance',
            name='day_off',
            field=models.CharField(blank=True, choices=[('', '----------'), ('Yes', 'Yes'), ('No', 'No')], max_length=10, null=True, verbose_name='Day off ?'),
        ),
        migrations.AddField(
            model_name='alpattendance',
            name='programme',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='alp.alpprogram', verbose_name='Programme'),
        ),
        migrations.AddField(
            model_name='alpattendance',
            name='round',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='alp.alpround', verbose_name='Round'),
        ),
        migrations.AddField(
            model_name='alpattendance',
            name='school',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='schools.school', verbose_name='School'),
        ),
        migrations.CreateModel(
            name='ALPAttendanceChild',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('attended', models.CharField(blank=True, choices=[('', '----------'), ('Yes', 'Yes'), ('No', 'No')], max_length=10, null=True, verbose_name='Child Attended?')),
                ('absence_reason', models.CharField(blank=True, choices=[('', '----------'), ('Sick', 'Sick'), ('No transport', 'No transport'), ('Other', 'Other'), ('Unspecified', 'Unspecified')], max_length=50, null=True)),
                ('absence_reason_other', models.CharField(blank=True, max_length=500, null=True, verbose_name='specify')),
                ('attendance_day', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='attendance_child', to='alp.alpattendance')),
                ('child', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='child.child', verbose_name='Child')),
                ('registration', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='alp.alpregistration', verbose_name='Registration')),
            ],
            options={
                'verbose_name': 'ALP Child Attendance',
                'ordering': ['id'],
            },
        ),
    ]
