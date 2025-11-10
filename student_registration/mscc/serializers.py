from rest_framework import serializers
from .models import (
    Registration
)


def create_instance(validated_data, model):
    from student_registration.child.serializers import ChildSerializer
    from student_registration.child.models import Child

    child_data = validated_data.pop('child', None)
    child = None

    if 'id' in child_data and child_data['id']:
        child_serializer = ChildSerializer(Child.objects.get(id=child_data['id']), data=child_data)
        child_serializer.is_valid(raise_exception=True)
        child_serializer.instance = child_serializer.save()
        child = child_serializer.instance

    if not child:
        child_serializer = ChildSerializer(data=child_data)
        child_serializer.is_valid(raise_exception=True)
        child_serializer.instance = child_serializer.save()
        child = child_serializer.instance

    try:
        instance = model.objects.create(**validated_data)
        instance.child = child
        instance.save()

    except Exception as ex:
        raise serializers.ValidationError({'Registration instance': ex})

    return instance


def update_instance(instance, validated_data):
    from student_registration.child.serializers import ChildSerializer
    child_data = validated_data.pop('child', None)

    if child_data:
        child_serializer = ChildSerializer(instance.child, data=child_data)
        child_serializer.is_valid(raise_exception=True)
        child_serializer.instance = child_serializer.save()

    try:

        for key in validated_data:
            if hasattr(instance, key):
                setattr(instance, key, validated_data[key])

        instance.save()

    except Exception as ex:
        raise serializers.ValidationError({'Registration instance': ex})

    return instance


class MainSerializer(serializers.ModelSerializer):
    original_id = serializers.IntegerField(source='id', read_only=True)
    registration_id = serializers.IntegerField(source='id', read_only=True)
    child_id = serializers.IntegerField(source='child.id', required=False)
    child_first_name = serializers.CharField(source='child.first_name')
    child_father_name = serializers.CharField(source='child.father_name')
    child_last_name = serializers.CharField(source='child.last_name')
    child_full_name = serializers.CharField(source='child.full_name', read_only=True)
    child_mother_fullname = serializers.CharField(source='child.mother_fullname')
    child_gender = serializers.CharField(source='child.gender')
    child_birthday_year = serializers.CharField(source='child.birthday_year')
    child_birthday_month = serializers.CharField(source='child.birthday_month')
    child_birthday_day = serializers.CharField(source='child.birthday_day')
    child_birthday = serializers.CharField(source='child.birthday', read_only=True)
    child_age = serializers.CharField(source='child.age', read_only=True)
    child_nationality = serializers.CharField(source='child.nationality')
    child_nationality_id = serializers.CharField(source='child.nationality.id', read_only=True)
    child_nationality_other = serializers.CharField(source='child.nationality_other', required=False)
    child_address = serializers.CharField(source='child.address', required=False)
    child_living_arrangement = serializers.CharField(source='child.living_arrangement', required=False)
    child_disability = serializers.CharField(source='child.disability', required=False)
    child_disability_id = serializers.CharField(source='child.disability.id', read_only=True)
    child_p_code = serializers.CharField(source='child.p_code', required=False)
    child_id_number = serializers.CharField(source='child.id_number', required=False)
    child_fe_unique_id = serializers.CharField(source='child.fe_unique_id', required=False)
    child_marital_status = serializers.CharField(source='child.marital_status', required=False)
    child_have_children = serializers.CharField(source='child.have_children', required=False)
    child_children_number = serializers.CharField(source='child.children_number', required=False)
    child_have_sibling = serializers.CharField(source='child.have_sibling', required=False)
    child_siblings_have_disability = serializers.CharField(source='child.siblings_have_disability', required=False)
    child_mother_pregnant_expecting = serializers.CharField(source='child.mother_pregnant_expecting', required=False)
    main_caregiver_nationality = serializers.CharField(source='child.main_caregiver_nationality', required=False)
    main_caregiver_nationality_id = serializers.CharField(source='child.main_caregiver_nationality.id', required=False)
    main_caregiver_nationality_other = serializers.CharField(source='child.main_caregiver_nationality_other',
                                                             required=False)
    id_type = serializers.CharField(source='child.id_type', required=False)
    id_type_id = serializers.CharField(source='child.id_type.id', required=False)
    case_number = serializers.CharField(source='child.case_number', required=False)
    case_number_confirm = serializers.CharField(source='child.case_number_confirm', required=False)
    parent_individual_case_number = serializers.CharField(source='child.parent_individual_case_number',
                                                          required=False)
    parent_individual_case_number_confirm = serializers.CharField(source='child.parent_individual_case_number_confirm',
                                                                  required=False)
    individual_case_number = serializers.CharField(source='child.individual_case_number', required=False)
    individual_case_number_confirm = serializers.CharField(source='child.individual_case_number_confirm',
                                                           required=False)
    recorded_number = serializers.CharField(source='child.recorded_number', required=False)
    recorded_number_confirm = serializers.CharField(source='child.recorded_number_confirm', required=False)
    parent_national_number = serializers.CharField(source='child.parent_national_number', required=False)
    parent_national_number_confirm = serializers.CharField(source='child.parent_national_number_confirm',
                                                           required=False)
    national_number = serializers.CharField(source='child.national_number', required=False)
    national_number_confirm = serializers.CharField(source='child.national_number_confirm', required=False)


    parent_extract_record = serializers.CharField(source='child.parent_extract_record', required=False)
    parent_extract_record_confirm = serializers.CharField(source='child.parent_extract_record_confirm', required=False)


    parent_syrian_national_number = serializers.CharField(source='child.parent_syrian_national_number',
                                                          required=False)
    parent_syrian_national_number_confirm = serializers.CharField(source='child.parent_syrian_national_number_confirm',
                                                                  required=False)
    syrian_national_number = serializers.CharField(source='child.syrian_national_number', required=False)
    syrian_national_number_confirm = serializers.CharField(source='child.syrian_national_number_confirm',
                                                           required=False)
    parent_sop_national_number = serializers.CharField(source='child.parent_sop_national_number', required=False)
    parent_sop_national_number_confirm = serializers.CharField(source='child.parent_sop_national_number_confirm',
                                                               required=False)
    sop_national_number = serializers.CharField(source='child.sop_national_number', required=False)
    sop_national_number_confirm = serializers.CharField(source='child.sop_national_number_confirm', required=False)
    parent_other_number = serializers.CharField(source='child.parent_other_number', required=False)
    parent_other_number_confirm = serializers.CharField(source='child.parent_other_number_confirm', required=False)
    other_number = serializers.CharField(source='child.other_number', required=False)
    other_number_confirm = serializers.CharField(source='child.other_number_confirm', required=False)
    father_educational_level = serializers.CharField(source='child.father_educational_level', required=False)
    father_educational_level_id = serializers.CharField(source='child.father_educational_level.id', required=False)
    mother_educational_level = serializers.CharField(source='child.mother_educational_level', required=False)
    mother_educational_level_id = serializers.CharField(source='child.mother_educational_level.id', required=False)
    first_phone_owner = serializers.CharField(source='child.first_phone_owner', required=False)
    first_phone_number = serializers.CharField(source='child.first_phone_number', required=False)
    first_phone_number_confirm = serializers.CharField(source='child.first_phone_number_confirm', required=False)
    second_phone_owner = serializers.CharField(source='child.second_phone_owner', required=False)
    second_phone_number = serializers.CharField(source='child.second_phone_number', required=False)
    second_phone_number_confirm = serializers.CharField(source='child.second_phone_number_confirm', required=False)
    main_caregiver = serializers.CharField(source='child.main_caregiver', required=False)
    main_caregiver_other = serializers.CharField(source='child.main_caregiver_other', required=False)
    children_number_under18 = serializers.CharField(source='child.children_number_under18', required=False)
    caregiver_first_name = serializers.CharField(source='child.caregiver_first_name', required=False)
    caregiver_middle_name = serializers.CharField(source='child.caregiver_middle_name', required=False)
    caregiver_last_name = serializers.CharField(source='child.caregiver_last_name', required=False)
    caregiver_mother_name = serializers.CharField(source='child.caregiver_mother_name', required=False)
    created = serializers.CharField(read_only=True)
    csrfmiddlewaretoken = serializers.IntegerField(source='owner.id', read_only=True)
    save = serializers.IntegerField(source='owner.id', read_only=True)
    owner_name = serializers.CharField(source='owner.username', read_only=True)
    modified_by_name = serializers.CharField(source='modified_by.username', read_only=True)

    def create(self, validated_data):
        return create_instance(validated_data=validated_data, model=self.Meta.model)

    def update(self, instance, validated_data):
        return update_instance(instance=instance, validated_data=validated_data)

    class Meta:
        model = Registration
        fields = (
            'id',
            'original_id',
            'registration_id',
            'child_id',
            'csrfmiddlewaretoken',
            'save',
            'owner',
            'owner_name',
            'modified_by',
            'modified_by_name',
            'created',
            'modified',
            'child_first_name',
            'child_father_name',
            'child_last_name',
            'child_mother_fullname',
            'child_full_name',
            'child_gender',
            'child_nationality',
            'child_nationality_other',
            'child_nationality_id',
            'child_birthday_year',
            'child_birthday_month',
            'child_birthday_day',
            'child_birthday',
            'child_age',
            'main_caregiver_nationality',
            'main_caregiver_nationality_id',
            'main_caregiver_nationality_other',
            'child_p_code',
            'child_id_number',
            'child_address',
            'child_living_arrangement',
            'child_disability',
            'child_disability_id',
            'child_marital_status',
            'child_have_children',
            'child_children_number',
            'child_have_sibling',
            'child_siblings_have_disability',
            'child_mother_pregnant_expecting',
            'partner_unique_number',
            'source_of_identification',
            'source_of_identification_specify',
            'child_fe_unique_id',
            'cash_support_programmes',
            'mscc_packages',
            'father_educational_level',
            'father_educational_level_id',
            'mother_educational_level',
            'mother_educational_level_id',
            'first_phone_owner',
            'first_phone_number',
            'first_phone_number_confirm',
            'second_phone_owner',
            'second_phone_number',
            'second_phone_number_confirm',
            'main_caregiver',
            'main_caregiver_other',
            'children_number_under18',
            'caregiver_first_name',
            'caregiver_middle_name',
            'caregiver_last_name',
            'caregiver_mother_name',
            'have_labour',
            'labour_type',
            'labour_type_specify',
            'labour_hours',
            'labour_weekly_income',
            'labour_condition',
            'id_type',
            'id_type_id',
            'case_number',
            'case_number_confirm',
            'parent_individual_case_number',
            'parent_individual_case_number_confirm',
            'individual_case_number',
            'individual_case_number_confirm',
            'parent_extract_record',
            'parent_extract_record_confirm',
            'recorded_number',
            'recorded_number_confirm',
            'parent_national_number',
            'parent_national_number_confirm',
            'national_number',
            'national_number_confirm',
            'parent_syrian_national_number',
            'parent_syrian_national_number_confirm',
            'syrian_national_number',
            'syrian_national_number_confirm',
            'parent_sop_national_number',
            'parent_sop_national_number_confirm',
            'sop_national_number',
            'sop_national_number_confirm',
            'parent_other_number',
            'parent_other_number_confirm',
            'other_number',
            'other_number_confirm',
            'type'
        )
