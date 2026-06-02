from django.db import migrations

def create_other_disability(apps, schema_editor):
    Disability = apps.get_model('clm', 'Disability')
    Disability.objects.get_or_create(name='غير ذلك', name_en='Other', active=True)

class Migration(migrations.Migration):

    dependencies = [
        ('clm', '0005_initial'),
    ]

    operations = [
        migrations.RunPython(create_other_disability),
    ]
