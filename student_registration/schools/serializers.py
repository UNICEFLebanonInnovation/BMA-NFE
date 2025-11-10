
from rest_framework import serializers
from .models import (
    School,
    ClassRoom,
    Section,
)


class SchoolSerializer(serializers.ModelSerializer):

    class Meta:
        model = School
        fields = (
            'id',
            'number',
            'name',
            'director_name',
            'land_phone_number',
            'email',
            'governorate',
            'district',
            'cadaster',
            'longitude',
            'latitude',
            'registration_level',
            'school_capacity',
            'empty_building',
            'number_children',
            'number_children_male',
            'number_children_female',
            'number_children_lebanese',
            'number_children_non_lebanese',
            'number_children_sbp',
            'number_children_male_sbp',
            'number_children_female_sbp',
            'number_children_lebanese_sbp',
            'number_children_non_lebanese_sbp',
            'CWD_accessible',
            'internet_available',
            'school_digital_capacity',
            'digital_learning_programme',
            'is_closed',
            'weekend',
            'working_days',
            'academic_year_start',
            'academic_year_end',
            'receive_supplies',
            'number_dirasa_children_disability',
            'number_total_children_disability',
            'type',
            'benefit_wfp_service',
            'wfp_service_type',
            'owner',
            'modified_by',
            'created',
            'modified',
        )


class ClassRoomSerializer(serializers.ModelSerializer):

    class Meta:
        model = ClassRoom
        fields = (
            'id',
            'name',
        )


class SectionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Section
        fields = (
            'id',
            'name',
        )
