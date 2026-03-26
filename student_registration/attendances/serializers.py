
from rest_framework import serializers
from .models import CLMAttendanceStudent, MSCCAttendanceChild


class CLMAttendanceStudentSerializer(serializers.ModelSerializer):

    governorate = serializers.CharField(source='attendance_day.school.location.parent.name', read_only=True)
    district = serializers.CharField(source='attendance_day.school.location.name', read_only=True)
    school_number = serializers.CharField(source='attendance_day.school.number', read_only=True)
    school_name = serializers.CharField(source='attendance_day.school.name', read_only=True)
    school_type = serializers.CharField(source='attendance_day.school.type', read_only=True)
    attendance_date = serializers.CharField(source='attendance_day.attendance_date', read_only=True)
    close_reason = serializers.CharField(source='attendance_day.close_reason', read_only=True)
    registration_level = serializers.CharField(source='attendance_day.registration_level', read_only=True)
    day_off = serializers.CharField(source='attendance_day.day_off', read_only=True)

    student_number = serializers.CharField(source='student.number', read_only=True)
    student_first_name = serializers.CharField(source='student.first_name', read_only=True)
    student_last_name = serializers.CharField(source='student.last_name', read_only=True)
    student_father_name = serializers.CharField(source='student.father_name', read_only=True)

    class Meta:
        model = CLMAttendanceStudent
        fields = (
            'school_name',
            'school_number',
            'school_type',
            'education_year',
            'governorate',
            'district',
            'attendance_date',
            'close_reason',
            'registration_level',
            'day_off',
            'student_number',
            'student_first_name',
            'student_last_name',
            'student_father_name',
            'attended',
            'absence_reason',
            'absence_reason_other',
        )


class MSCCAttendanceChildSerializer(serializers.ModelSerializer):

    class Meta:
        model = MSCCAttendanceChild
        fields = (
            '__all__'
        )


