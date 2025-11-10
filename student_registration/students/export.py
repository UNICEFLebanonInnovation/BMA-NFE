from import_export import resources, fields
from .models import Teacher



class TeacherResource(resources.ModelResource):
    class Meta:
        model = Teacher
        fields = (
            'id',
            'first_name',
            'father_name',
            'last_name',
            'sex',
            'primary_phone_number',
            'school__name',
            'email',
            'subjects_provided',
            'registration_level',
            'teacher_assignment',
            'teaching_hours_private_school',
            'teaching_hours_dirasa',
            'trainings',
            'training_sessions_attended',
            'extra_coaching',
            'extra_coaching_specify',
            'owner__username',
            'modified_by__username',
            'created',
            'modified',
        )
        export_order = fields

