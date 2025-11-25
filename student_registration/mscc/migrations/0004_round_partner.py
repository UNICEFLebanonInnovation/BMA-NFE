import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('schools', '0001_initial'),
        ('mscc', '0003_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='round',
            name='end_date',
        ),
        migrations.RemoveField(
            model_name='round',
            name='start_date',
        ),
        migrations.CreateModel(
            name='RoundPartner',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('start_date', models.DateField(blank=True, null=True)),
                ('end_date', models.DateField(blank=True, null=True)),
                ('partner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rounds', to='schools.partnerorganization')),
                ('round', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='partner_rounds', to='mscc.round')),
            ],
            options={
                'verbose_name': 'Round Partner',
                'verbose_name_plural': 'Round Partners',
                'ordering': ['round__name', 'partner__name'],
                'unique_together': {('round', 'partner')},
            },
        ),
    ]
