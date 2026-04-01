from django.db import migrations, models
import django.utils.timezone
import model_utils.fields

class Migration(migrations.Migration):

    dependencies = [
        ('mscc', '0008_alter_educationservice_education_program'),
    ]

    operations = [
        migrations.CreateModel(
            name='EducationProgrammeGrading',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('programme_type', models.CharField(max_length=100, verbose_name='Education Programme Type')),
                ('key', models.CharField(help_text='JSON key (e.g., arabic_grade)', max_length=50, verbose_name='Field Key')),
                ('label', models.CharField(max_length=200, verbose_name='Label')),
                ('max_score', models.IntegerField(default=100, verbose_name='Max Score')),
                ('condition', models.CharField(blank=True, choices=[('', 'None'), ('french_only', 'French Only (If center provides French)'), ('english_only', 'English Only (If center does not provide French)')], max_length=50, null=True, verbose_name='Condition')),
                ('order', models.IntegerField(default=0, verbose_name='Order')),
                ('form_type', models.CharField(choices=[('education', 'Education Grading'), ('youth', 'Youth Scoring')], default='education', max_length=50, verbose_name='Form Type')),
            ],
            options={
                'verbose_name': 'Education Programme Grading',
                'verbose_name_plural': 'Education Programme Gradings',
                'ordering': ['programme_type', 'order'],
                'unique_together': {('programme_type', 'key', 'form_type')},
            },
        ),
    ]
