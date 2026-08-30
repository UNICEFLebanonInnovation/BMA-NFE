from django.db import migrations, models
import django.db.models.deletion
import django.contrib.postgres.fields

class Migration(migrations.Migration):

    dependencies = [
        ('alp', '0001_initial'),
        ('students', '0001_initial'),
        ('schools', '0001_initial'),
        migrations.swappable_dependency(django.conf.settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='alpteacher',
            name='attach_file_1',
            field=models.FileField(blank=True, null=True, upload_to='uploads/alp_teacher', verbose_name='Attachment'),
        ),
        migrations.AddField(
            model_name='alpteacher',
            name='attach_file_2',
            field=models.FileField(blank=True, null=True, upload_to='uploads/alp_teacher', verbose_name='Attachment'),
        ),
        migrations.AddField(
            model_name='alpteacher',
            name='attach_file_3',
            field=models.FileField(blank=True, null=True, upload_to='uploads/alp_teacher', verbose_name='Attachment'),
        ),
        migrations.AddField(
            model_name='alpteacher',
            name='attach_file_4',
            field=models.FileField(blank=True, null=True, upload_to='uploads/alp_teacher', verbose_name='Attachment'),
        ),
        migrations.AddField(
            model_name='alpteacher',
            name='attach_file_5',
            field=models.FileField(blank=True, null=True, upload_to='uploads/alp_teacher', verbose_name='Attachment'),
        ),
        migrations.AddField(
            model_name='alpteacher',
            name='attach_short_description_1',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Description'),
        ),
        migrations.AddField(
            model_name='alpteacher',
            name='attach_short_description_2',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Description'),
        ),
        migrations.AddField(
            model_name='alpteacher',
            name='attach_short_description_3',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Description'),
        ),
        migrations.AddField(
            model_name='alpteacher',
            name='attach_short_description_4',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Description'),
        ),
        migrations.AddField(
            model_name='alpteacher',
            name='attach_short_description_5',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Description'),
        ),
        migrations.AddField(
            model_name='alpteacher',
            name='attach_type_1',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='students.AttachmentType', verbose_name='Type'),
        ),
        migrations.AddField(
            model_name='alpteacher',
            name='attach_type_2',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='students.AttachmentType', verbose_name='Type'),
        ),
        migrations.AddField(
            model_name='alpteacher',
            name='attach_type_3',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='students.AttachmentType', verbose_name='Type'),
        ),
        migrations.AddField(
            model_name='alpteacher',
            name='attach_type_4',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='students.AttachmentType', verbose_name='Type'),
        ),
        migrations.AddField(
            model_name='alpteacher',
            name='attach_type_5',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='students.AttachmentType', verbose_name='Type'),
        ),
        migrations.AddField(
            model_name='alpteacher',
            name='birthdate',
            field=models.DateField(blank=True, null=True, verbose_name='Birth date'),
        ),
        migrations.AddField(
            model_name='alpteacher',
            name='email',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Email'),
        ),
        migrations.AddField(
            model_name='alpteacher',
            name='extra_coaching',
            field=models.CharField(blank=True, choices=[('', '----------'), ('yes', 'Yes'), ('no', 'No')], max_length=10, null=True, verbose_name='Extra coaching'),
        ),
        migrations.AddField(
            model_name='alpteacher',
            name='extra_coaching_specify',
            field=models.TextField(blank=True, null=True, verbose_name='Please specify'),
        ),
        migrations.AddField(
            model_name='alpteacher',
            name='id_number',
            field=models.CharField(blank=True, db_index=True, max_length=45, null=True, verbose_name='ID number'),
        ),
        migrations.AddField(
            model_name='alpteacher',
            name='id_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='students.IDType', verbose_name='ID type'),
        ),
        migrations.AddField(
            model_name='alpteacher',
            name='modified_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=django.conf.settings.AUTH_USER_MODEL, verbose_name='Modified by'),
        ),
        migrations.AddField(
            model_name='alpteacher',
            name='mother_fullname',
            field=models.CharField(blank=True, db_index=True, max_length=64, null=True, verbose_name='Mother full name'),
        ),
        migrations.AddField(
            model_name='alpteacher',
            name='nationality',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='students.Nationality', verbose_name='Nationality'),
        ),
        migrations.AddField(
            model_name='alpteacher',
            name='registration_level',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, choices=[('Level one', 'Level one'), ('Level two', 'Level two'), ('Level three', 'Level three'), ('Level four', 'Level four'), ('Level five', 'Level five'), ('Level six', 'Level six')], max_length=200, null=True), blank=True, null=True, size=None, verbose_name='Dirasa Grade level'),
        ),
        migrations.AddField(
            model_name='alpteacher',
            name='round',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='alp.ALPRound', verbose_name='Round'),
        ),
        migrations.AddField(
            model_name='alpteacher',
            name='subjects_provided',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, choices=[('arabic', 'Arabic'), ('math', 'Math'), ('english', 'English'), ('french', 'French'), ('PSS / Counsellor', 'PSS / Counsellor'), ('Physical Education', 'Physical Education'), ('Art', 'Art'), ('Sciences', 'Sciences'), ('PSS', 'PSS'), ('History', 'History'), ('Geography', 'Geography'), ('Civics', 'Civics'), ('Computer', 'Computer')], max_length=200, null=True), blank=True, null=True, size=None, verbose_name='Subjects provided'),
        ),
        migrations.AddField(
            model_name='alpteacher',
            name='teacher_assignment',
            field=models.CharField(blank=True, choices=[('Makani only', 'Makani only'), ('Private and Makani', 'Private and Makani')], max_length=100, null=True, verbose_name='Teacher Assignment'),
        ),
        migrations.AddField(
            model_name='alpteacher',
            name='teaching_hours_mscc',
            field=models.IntegerField(blank=True, null=True, verbose_name='Number of teaching hours'),
        ),
        migrations.AddField(
            model_name='alpteacher',
            name='teaching_hours_private_school',
            field=models.IntegerField(blank=True, null=True, verbose_name='Number of teaching hours in private school'),
        ),
        migrations.AddField(
            model_name='alpteacher',
            name='training_date_of_completion',
            field=models.DateField(blank=True, null=True, verbose_name='Date of completion of the listed training'),
        ),
        migrations.AddField(
            model_name='alpteacher',
            name='training_sessions_attended',
            field=models.IntegerField(blank=True, choices=[(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10, 10), (11, 11), (12, 12), (13, 13), (14, 14), (15, 15), (16, 16), (17, 17), (18, 18), (19, 19), (20, 20), (21, 21), (22, 22), (23, 23), (24, 24), (25, 25), (26, 26), (27, 27), (28, 28), (29, 29)], null=True, verbose_name='Number of teacher training sessions (attended)'),
        ),
        migrations.AddField(
            model_name='alpteacher',
            name='trainings',
            field=models.ManyToManyField(blank=True, related_name='alp_teachers', to='students.Training', verbose_name='Topics of teacher training'),
        ),
        migrations.AddField(
            model_name='alpteacher',
            name='unicef_id',
            field=models.CharField(blank=True, max_length=45, null=True, verbose_name='UNIQUE ID'),
        ),
        migrations.AddField(
            model_name='alpteacher',
            name='years_of_experience',
            field=models.IntegerField(blank=True, null=True, verbose_name='Years of experience in NFE/FE'),
        ),
        migrations.AlterField(
            model_name='alpteacher',
            name='owner',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=django.conf.settings.AUTH_USER_MODEL, verbose_name='Owner'),
        ),
        migrations.AlterField(
            model_name='alpteacher',
            name='phone_number',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Phone number'),
        ),
    ]
