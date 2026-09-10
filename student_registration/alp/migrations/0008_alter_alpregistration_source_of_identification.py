from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('alp', '0007_update_teacher_assignment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='alpregistration',
            name='source_of_identification',
            field=models.CharField(
                blank=True,
                choices=[
                    ('', '----------'),
                    ('Dirassa', 'Dirassa'),
                    ('Awareness Session', 'Awareness Session'),
                    ("Child's parents", "Child's parents"),
                    ('From Hosted Community', 'From Hosted Community'),
                    (
                        'Sector Partners referral (CP, Education, Health, Wash, Youth, Palestenian program...) ',
                        'Sector Partners referral (CP, Education, Health, Wash, Youth, Palestenian program...) ',
                    ),
                    ('From Profiling Database', 'From Profiling Database'),
                    ('From Other NGO', 'From Other NGO'),
                    ('From Displaced Community', 'From Displaced Community'),
                    (
                        'Referred by the municipality/Other formal sources',
                        'Referred by the municipality/Other formal sources',
                    ),
                    ('BLN programme', 'BLN programme'),
                    (
                        'Transitioned from National NFE assessment',
                        'Transitioned from National NFE assessment',
                    ),
                    ('Other Sources', 'Other Sources'),
                ],
                max_length=100,
                null=True,
                verbose_name='Source of referral of the child',
            ),
        ),
    ]
