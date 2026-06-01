from django.db import migrations

def create_attachment_types(apps, schema_editor):
    AttachmentType = apps.get_model('students', 'AttachmentType')
    types_to_create = [
        "Photo",
        "إخراج قيد",
        "ID",
        "University certificate"
    ]
    for type_name in types_to_create:
        AttachmentType.objects.get_or_create(name=type_name)

class Migration(migrations.Migration):

    dependencies = [
        ('students', '0003_teacher_training_date_of_completion_and_more'),
    ]

    operations = [
        migrations.RunPython(create_attachment_types, reverse_code=migrations.RunPython.noop),
    ]
