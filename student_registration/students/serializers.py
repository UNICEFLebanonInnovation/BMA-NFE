from rest_framework import serializers
from .models import (
    Student,
    Teacher
)
from datetime import date



class StudentSerializer(serializers.ModelSerializer):

    id = serializers.IntegerField(read_only=True)
    number = serializers.CharField(read_only=True)
    birthday = serializers.CharField(read_only=True)
    place_of_birth = serializers.CharField(required=False)
    have_children = serializers.CharField(required=False)
    p_code = serializers.CharField(required=False)
    
    def validate(self, attrs):
        birthday_year = attrs.get('birthday_year')
        birthday_month = attrs.get('birthday_month')
        birthday_day = attrs.get('birthday_day')

        if birthday_year and birthday_month and birthday_day:
            try:
                birth_date = date(
                    int(birthday_year),
                    int(birthday_month),
                    int(birthday_day)
                )
            except ValueError:
                raise serializers.ValidationError({
                    'birthday_day': 'Invalid birth date.'
                })

            if birth_date > date.today():
                raise serializers.ValidationError({
                    'birthday_day': 'Birth date cannot be in the future.'
                })

        return attrs

    def create(self, validated_data):

        try:
            instance = Student.objects.create(**validated_data)
            instance.save()

        except Exception as ex:
            raise serializers.ValidationError({'Student instance': ex})

        return instance

    class Meta:
        model = Student
        fields = (
            'id',
            'first_name',
            'father_name',
            'last_name',
            'full_name',
            'mother_fullname',
            'sex',
            'age',
            'birthday_year',
            'birthday_month',
            'birthday_day',
            'place_of_birth',
            'birthday',
            'phone',
            'phone_prefix',
            'id_number',
            'id_type',
            'registered_in_unhcr',
            'nationality',
            'mother_nationality',
            'family_status',
            'address',
            'number',
            'hh_barcode',
            'have_children',
            'p_code',
        )


class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = (
            'id',
            'round',
            'first_name',
            'father_name',
            'last_name',
            'full_name',
            'sex',
            'primary_phone_number',
            'school',
            'email',
            'subjects_provided',
            'registration_level',
            'teacher_assignment',
            'teaching_hours_private_school',
            'teaching_hours_dirasa',
            'trainings',
            'years_of_experience',
            'training_sessions_attended',
            'extra_coaching',
            'extra_coaching_specify',
            'attach_short_description_1',
            'attach_file_1',
            'attach_type_1',
            'attach_short_description_2',
            'attach_file_2',
            'attach_type_2',
            'attach_short_description_3',
            'attach_file_3',
            'attach_type_3',
            'attach_short_description_4',
            'attach_file_4',
            'attach_type_4',
            'attach_short_description_5',
            'attach_file_5',
            'attach_type_5',
        )
