
import json

from rest_framework import serializers
from .models import (
    CLM,
    BLN,
    ABLN,
    RS,
    CBECE,
    SelfPerceptionGrades,
    ABLN_FC,
    BLN_FC,
    RS_FC,
    CBECE_FC,
    GeneralQuestionnaire,
    Outreach,
    Bridging
)


def create_instance(validated_data, model):
    from student_registration.students.serializers import StudentSerializer
    from student_registration.students.models import Student

    student_data = validated_data.pop('student', None)
    student = None

    if 'partner' in validated_data and validated_data['partner'] and validated_data['partner'].id == 10:
        if 'internal_number' in validated_data and validated_data['internal_number']:
            queryset = model.objects.filter(internal_number=validated_data['internal_number'])

            if queryset.count():
                student = queryset.first().student

    if 'id' in student_data and student_data['id']:
        student_serializer = StudentSerializer(Student.objects.get(id=student_data['id']), data=student_data)
        student_serializer.is_valid(raise_exception=True)
        student_serializer.instance = student_serializer.save()
        student = student_serializer.instance

    if not student:
        student_serializer = StudentSerializer(data=student_data)
        student_serializer.is_valid(raise_exception=True)
        student_serializer.instance = student_serializer.save()
        student = student_serializer.instance

    try:
        instance = model.objects.create(**validated_data)
        instance.student = student
        instance.save()

    except Exception as ex:
        raise serializers.ValidationError({'Enrollment instance': ex})

    return instance


def update_instance(instance, validated_data):
    from student_registration.students.serializers import StudentSerializer
    student_data = validated_data.pop('student', None)

    if student_data:
        student_serializer = StudentSerializer(instance.student, data=student_data)
        student_serializer.is_valid(raise_exception=True)
        student_serializer.instance = student_serializer.save()

    try:

        for key in validated_data:
            if hasattr(instance, key):
                setattr(instance, key, validated_data[key])

        instance.save()

    except Exception as ex:
        raise serializers.ValidationError({'Enrollment instance': ex})

    return instance


class CLMSerializer(serializers.ModelSerializer):

    original_id = serializers.IntegerField(source='id', read_only=True)
    round_name = serializers.CharField(source='round.name', read_only=True)
    student_id = serializers.IntegerField(source='student.id', required=False)
    student_first_name = serializers.CharField(source='student.first_name')
    student_father_name = serializers.CharField(source='student.father_name')
    student_last_name = serializers.CharField(source='student.last_name')
    student_full_name = serializers.CharField(source='student.full_name', read_only=True)
    student_mother_fullname = serializers.CharField(source='student.mother_fullname')
    student_sex = serializers.CharField(source='student.sex')
    student_birthday_year = serializers.CharField(source='student.birthday_year')
    student_birthday_month = serializers.CharField(source='student.birthday_month')
    student_birthday_day = serializers.CharField(source='student.birthday_day')
    student_birthday = serializers.CharField(source='student.birthday', read_only=True)
    student_nationality = serializers.CharField(source='student.nationality')
    student_nationality_id = serializers.CharField(source='student.nationality.id', read_only=True)
    student_address = serializers.CharField(source='student.address', required=False)
    student_p_code = serializers.CharField(source='student.p_code', required=False)
    student_id_number = serializers.CharField(source='student.id_number', required=False)
    student_family_status = serializers.CharField(source='student.family_status', required=False)
    student_have_children = serializers.CharField(source='student.have_children', required=False)
    comments = serializers.CharField(required=False)
    unsuccessful_posttest_reason = serializers.CharField(required=False)
    unsuccessful_pretest_reason = serializers.CharField(required=False)
    pre_test = serializers.JSONField(required=False)
    post_test = serializers.JSONField(required=False)
    student_outreach_child = serializers.IntegerField(source='student.outreach_child', required=False)
    student_outreach_child_id = serializers.IntegerField(source='student.outreach_child.id', read_only=True)
    governorate_name = serializers.CharField(source='governorate.name', read_only=True)
    district_name = serializers.CharField(source='district.name', read_only=True)
    cadaster_name = serializers.CharField(source='cadaster.name', read_only=True)
    partner_name = serializers.CharField(source='partner.name', read_only=True)
    partner = serializers.CharField(source='partner.id', read_only=True)
    created = serializers.CharField(read_only=True)

    csrfmiddlewaretoken = serializers.IntegerField(source='owner.id', read_only=True)
    save = serializers.IntegerField(source='owner.id', read_only=True)
    # internal = serializers.CharField(read_only=True)
    enrollment_id = serializers.IntegerField(source='id', read_only=True)
    search_clm_student = serializers.CharField(source='student.full_name', read_only=True)
    search_barcode = serializers.CharField(source='outreach_barcode', read_only=True)

    owner_name = serializers.CharField(source='owner.username', read_only=True)
    modified_by_name = serializers.CharField(source='modified_by.username', read_only=True)

    class Meta:
        model = CLM
        fields = (
            'id',
            'original_id',
            'round_name',
            'enrollment_id',
            'student_id',
            'first_attendance_date',
            'round',
            'partner',
            'partner_name',
            'language',
            'student_outreach_child',
            'student_outreach_child_id',
            'student_first_name',
            'student_father_name',
            'student_last_name',
            'student_full_name',
            'student_mother_fullname',
            'student_sex',
            'student_birthday_year',
            'student_birthday_month',
            'student_birthday_day',
            'student_birthday',
            'student_nationality',
            'student_nationality_id',
            'student_address',
            'student_p_code',
            'student_id_number',
            'internal_number',
            'owner',
            'owner_name',
            'modified_by',
            'modified_by_name',
            'governorate',
            'governorate_name',
            'district',
            'district_name',
            'cadaster',
            'cadaster_name',
            'location',
            'center',
            'outreach_barcode',
            'disability',
            'student_family_status',
            'student_have_children',
            # 'have_labour',
            # 'labours',
            # 'labour_hours',
            'hh_educational_level',
            'father_educational_level',
            'participation',
            'learning_result',
            'learning_result_other',
            'barriers_single',
            'barriers_other',
            'test_done',
            'round_complete',
            'follow_up_type',
            'phone_call_number',
            'house_visit_number',
            'family_visit_number',
            'phone_call_follow_up_result',
            'house_visit_follow_up_result',
            'family_visit_follow_up_result',
            'cp_referral',
            'parent_attended_visits',
            'pss_session_attended',
            'pss_session_number',
            'pss_session_modality',
            'pss_parent_attended',
            'pss_parent_attended_other',
            'covid_session_attended',
            'covid_session_number',
            'covid_session_modality',
            'covid_parent_attended',
            'covid_parent_attended_other',
            'followup_session_attended',
            'followup_session_number',
            'followup_session_modality',
            'followup_parent_attended_other',
            'followup_parent_attended',
            'child_health_examed',
            'child_health_concern',
            'barriers',
            'student_outreached',
            'new_registry',
            'have_barcode',
            'search_clm_student',
            'search_barcode',
            'csrfmiddlewaretoken',
            'save',
            'comments',
            'unsuccessful_posttest_reason',
            'unsuccessful_pretest_reason',
            'pre_test',
            'post_test',
            'created',
            'modified',
            'cycle_completed',
            'enrolled_at_school',
            'caretaker_birthday_year',
            'caretaker_birthday_month',
            'caretaker_birthday_day'
        )


class BLNSerializer(CLMSerializer):

    def create(self, validated_data):
        return create_instance(validated_data=validated_data, model=self.Meta.model)

    def update(self, instance, validated_data):
        return update_instance(instance=instance, validated_data=validated_data)

    class Meta:
        model = BLN
        fields = CLMSerializer.Meta.fields + (
            # 'cycle',
            # 'referral',
            'have_labour',
            'labours',
            'labour_hours',
            'have_labour_single_selection',
            'labours_single_selection',
            'labour_weekly_income',
            'student_family_status',
            'student_have_children',
            'phone_number',
            'phone_number_confirm',
            'second_phone_number',
            'second_phone_number_confirm',
            'phone_owner',
            'second_phone_owner',
            'id_type',
            'case_number',
            'case_number_confirm',
            'individual_case_number',
            'individual_case_number_confirm',
            'parent_individual_case_number',
            'parent_individual_case_number_confirm',
            'recorded_number',
            'recorded_number_confirm',
            'national_number',
            'national_number_confirm',
            'syrian_national_number',
            'syrian_national_number_confirm',
            'sop_national_number',
            'sop_national_number_confirm',
            'parent_national_number',
            'parent_national_number_confirm',
            'parent_syrian_national_number',
            'parent_syrian_national_number_confirm',
            'parent_sop_national_number',
            'parent_sop_national_number_confirm',
            'parent_other_number',
            'parent_other_number_confirm',
            'other_number',
            'other_number_confirm',
            'no_child_id_confirmation',
            'source_of_identification',
            'rims_case_number',
            'source_of_identification_specify',
            'other_nationality',
            'education_status',
            'caretaker_first_name',
            'caretaker_middle_name',
            'caretaker_last_name',
            'caretaker_mother_name',
            'round_start_date',
            'registration_level',
            'cadaster',
            'miss_school_date',
            'source_of_transportation',
            'main_caregiver',
            'main_caregiver_nationality',
            'main_caregiver_nationality_other',
            'other_caregiver_relationship',
            'student_number_children',
            'basic_stationery',
            'pss_kit',
            'remote_learning',
            'remote_learning_reasons_not_engaged',
            'reasons_not_engaged_other',
            'reliable_internet',
            'gender_participate',
            'gender_participate_explain',
            'remote_learning_engagement',
            'meet_learning_outcomes',
            'parent_learning_support_rate',
            'covid_message',
            'covid_message_how_often',
            'covid_parents_message',
            'covid_parents_message_how_often',
            'follow_up_done',
            'follow_up_done_with_who',
            'labours_other_specify',
            'child_received_books',
            'child_received_printout',
            'child_received_internet',
            'referal_wash',
            'referal_health',
            'referal_other',
            'referal_other_specify',
            'akelius_program'
        )


class BridgingSerializer(CLMSerializer):

    def create(self, validated_data):
        return create_instance(validated_data=validated_data, model=self.Meta.model)

    def update(self, instance, validated_data):
        return update_instance(instance=instance, validated_data=validated_data)

    mid_test1 = serializers.JSONField(required=False)
    mid_test2 = serializers.JSONField(required=False)

    class Meta:
        model = Bridging
        fields = CLMSerializer.Meta.fields + (
            # 'cycle',
            # 'referral',
            'child_outreach',
            'residence_type',
            'have_labour',
            'labours',
            'labour_hours',
            'have_labour_single_selection',
            'labours_single_selection',
            'labour_weekly_income',
            'student_family_status',
            'student_have_children',
            'phone_number',
            'phone_number_confirm',
            'second_phone_number',
            'second_phone_number_confirm',
            'phone_owner',
            'second_phone_owner',
            'id_type',
            # 'case_number',
            # 'case_number_confirm',
            'individual_case_number',
            'individual_case_number_confirm',
            # 'parent_individual_case_number',
            # 'parent_individual_case_number_confirm',
            'recorded_number',
            'recorded_number_confirm',
            'national_number',
            'national_number_confirm',
            'syrian_national_number',
            'syrian_national_number_confirm',
            'sop_national_number',
            'sop_national_number_confirm',
            # 'parent_national_number',
            # 'parent_national_number_confirm',
            # 'parent_syrian_national_number',
            # 'parent_syrian_national_number_confirm',
            # 'parent_sop_national_number',
            # 'parent_sop_national_number_confirm',
            # 'parent_other_number',
            # 'parent_other_number_confirm',
            'other_number',
            'other_number_confirm',
            # 'parent_extract_record',
            # 'parent_extract_record_confirm',
            'individual_extract_record',
            'individual_extract_record_confirm',
            'no_child_id_confirmation',
            'source_of_identification',
            'rims_case_number',
            'source_of_identification_specify',
            'other_nationality',
            'education_status',
            'caretaker_first_name',
            'caretaker_middle_name',
            'caretaker_last_name',
            'caretaker_mother_name',
            'round_start_date',
            'registration_level',
            'cadaster',
            'school',
            'miss_school_date',
            'source_of_transportation',
            'main_caregiver',
            'main_caregiver_nationality',
            'main_caregiver_nationality_other',
            'other_caregiver_relationship',
            'student_number_children',
            'basic_stationery',
            'pss_kit',
            'remote_learning',
            'remote_learning_reasons_not_engaged',
            'reasons_not_engaged_other',
            'reliable_internet',
            'gender_participate',
            'gender_participate_explain',
            'remote_learning_engagement',
            'meet_learning_outcomes',
            'parent_learning_support_rate',
            'covid_message',
            'covid_message_how_often',
            'covid_parents_message',
            'covid_parents_message_how_often',
            'follow_up_done',
            'follow_up_done_with_who',
            'labours_other_specify',
            'child_received_internet',
            'referal_wash',
            'referal_health',
            'referal_other',
            'referal_other_specify',
            'akelius_program',
            'community_Liaison_follow_up',
            'community_liaison_specify',
            'receiving_social_assistance',
            'receiving_transportation_support',
            'using_digital_platform',
            'school_contacted_caretaker',
            'discussion_topic',
            'registration_date',
            'mid_test1',
            'mid_test2',
            'dropout_date',
            'dropout_reason',
            'referral_school',
            'referral_school_type',
            'enrolled_formal_education',
        )


class ABLNSerializer(CLMSerializer):

    def create(self, validated_data):
        return create_instance(validated_data=validated_data, model=self.Meta.model)

    def update(self, instance, validated_data):
        return update_instance(instance=instance, validated_data=validated_data)

    class Meta:
        model = ABLN
        fields = CLMSerializer.Meta.fields + (
            # 'cycle',
            # 'referral',
            'have_labour',
            'labours',
            'labour_hours',
            'have_labour_single_selection',
            'labours_single_selection',
            'labour_weekly_income',
            'student_family_status',
            'student_have_children',
            'phone_number',
            'phone_number_confirm',
            'second_phone_number',
            'second_phone_number_confirm',
            'phone_owner',
            'id_type',
            'case_number',
            'case_number_confirm',
            'individual_case_number',
            'individual_case_number_confirm',
            'parent_individual_case_number',
            'parent_individual_case_number_confirm',
            'recorded_number',
            'recorded_number_confirm',
            'national_number',
            'national_number_confirm',
            'syrian_national_number',
            'syrian_national_number_confirm',
            'sop_national_number',
            'sop_national_number_confirm',
            'parent_national_number',
            'parent_national_number_confirm',
            'parent_syrian_national_number',
            'parent_syrian_national_number_confirm',
            'parent_sop_national_number',
            'parent_sop_national_number_confirm',
            'parent_other_number',
            'parent_other_number_confirm',
            'other_number',
            'other_number_confirm',
            'no_child_id_confirmation',
            'source_of_identification',
            'rims_case_number',
            'source_of_identification_specify',
            'other_nationality',
            'education_status',
            'caretaker_first_name',
            'caretaker_middle_name',
            'caretaker_last_name',
            'caretaker_mother_name',
            'round_start_date',
            'registration_level',
            'cadaster',
            'miss_school_date',
            'source_of_transportation',
            'main_caregiver',
            'main_caregiver_nationality',
            'main_caregiver_nationality_other',
            'other_caregiver_relationship',
            'student_number_children',
            'basic_stationery',
            'pss_kit',
            'remote_learning',
            'remote_learning_reasons_not_engaged',
            'reasons_not_engaged_other',
            'reliable_internet',
            'gender_participate',
            'gender_participate_explain',
            'remote_learning_engagement',
            'meet_learning_outcomes',
            'parent_learning_support_rate',
            'covid_message',
            'covid_message_how_often',
            'covid_parents_message',
            'covid_parents_message_how_often',
            'follow_up_done',
            'follow_up_done_with_who',
            'labours_other_specify',
            'child_received_books',
            'child_received_printout',
            'child_received_internet',
            'referal_wash',
            'referal_health',
            'referal_other',
            'referal_other_specify',
            'akelius_program'
        )


class RSSerializer(CLMSerializer):

    def create(self, validated_data):
        return create_instance(validated_data=validated_data, model=self.Meta.model)

    def update(self, instance, validated_data):
        return update_instance(instance=instance, validated_data=validated_data)

    class Meta:
        model = RS
        fields = CLMSerializer.Meta.fields + (
            # 'grade',
            # 'section',

            'student_have_children',
            'student_family_status',
            'student_number_children',
            'have_labour',
            'labours',
            'labour_hours',
            'have_labour_single_selection',
            'labours_single_selection',
            'labour_weekly_income',
            'phone_number',
            'phone_number_confirm',
            'second_phone_number',
            'second_phone_number_confirm',
            'phone_owner',
            'second_phone_owner',
            'id_type',
            'case_number',
            'case_number_confirm',
            'individual_case_number',
            'individual_case_number_confirm',
            'parent_individual_case_number',
            'parent_individual_case_number_confirm',
            'recorded_number',
            'recorded_number_confirm',
            'national_number',
            'national_number_confirm',
            'syrian_national_number',
            'syrian_national_number_confirm',
            'sop_national_number',
            'sop_national_number_confirm',
            'parent_national_number',
            'parent_national_number_confirm',
            'parent_syrian_national_number',
            'parent_syrian_national_number_confirm',
            'parent_sop_national_number',
            'parent_sop_national_number_confirm',
            'parent_other_number',
            'parent_other_number_confirm',
            'other_number',
            'other_number_confirm',
            'no_child_id_confirmation',
            'source_of_identification',
            'rims_case_number',
            'source_of_identification_specify',
            'other_nationality',
            'education_status',
            'caretaker_first_name',
            'caretaker_middle_name',
            'caretaker_last_name',
            'caretaker_mother_name',
            'round_start_date',
            'registration_level',
            'cadaster',
            'miss_school',
            'miss_school_date',
            # 'source_of_transportation',
            'main_caregiver',
            'main_caregiver_nationality',
            'other_caregiver_relationship',
            'basic_stationery',
            'remote_learning',
            'remote_learning_reasons_not_engaged',
            'reasons_not_engaged_other',
            'reliable_internet',
            'gender_participate',
            'gender_participate_explain',
            'remote_learning_engagement',
            'meet_learning_outcomes',
            'parent_learning_support_rate',
            'covid_message',
            'covid_message_how_often',
            'covid_parents_message',
            'covid_parents_message_how_often',
            'follow_up_done',
            'follow_up_done_with_who',
            'labours_other_specify',
            'grade_level',
            'source_join_fe',
            'grade_registration',
            'registered_in_school',
            'shift',
            'phone_call_number',
            'house_visit_number',
            'family_visit_number',
            'child_received_books',
            'child_received_printout',
            'child_received_internet',
            'referal_wash',
            'referal_health',
            'referal_other',
            'referal_other_specify',
            'akelius_program'
        )


class CBECESerializer(CLMSerializer):

    def create(self, validated_data):
        return create_instance(validated_data=validated_data, model=self.Meta.model)

    def update(self, instance, validated_data):
        return update_instance(instance=instance, validated_data=validated_data)

    class Meta:
        model = CBECE
        fields = CLMSerializer.Meta.fields + (
            # 'cycle',
            # 'site',
            # 'school',
            # 'referral',
            # 'child_muac',
            # 'final_grade',

            'have_labour',
            'labours',
            'labour_hours',
            'have_labour_single_selection',
            'labours_single_selection',
            'labour_weekly_income',
            'phone_number',
            'phone_number_confirm',
            'second_phone_number',
            'second_phone_number_confirm',
            'phone_owner',
            'second_phone_owner',
            'id_type',
            'case_number',
            'case_number_confirm',
            'individual_case_number',
            'individual_case_number_confirm',
            'parent_individual_case_number',
            'parent_individual_case_number_confirm',
            'recorded_number',
            'recorded_number_confirm',
            'national_number',
            'national_number_confirm',
            'syrian_national_number',
            'syrian_national_number_confirm',
            'sop_national_number',
            'sop_national_number_confirm',
            'parent_national_number',
            'parent_national_number_confirm',
            'parent_syrian_national_number',
            'parent_syrian_national_number_confirm',
            'parent_sop_national_number',
            'parent_sop_national_number_confirm',
            'parent_other_number',
            'parent_other_number_confirm',
            'other_number',
            'other_number_confirm',
            'no_child_id_confirmation',
            'source_of_identification',
            'rims_case_number',
            'source_of_identification_specify',
            'other_nationality',
            'education_status',
            'caretaker_first_name',
            'caretaker_middle_name',
            'caretaker_last_name',
            'caretaker_mother_name',
            'round_start_date',
            'registration_level',
            'cadaster',
            'miss_school_date',
            'source_of_transportation',
            'main_caregiver',
            'main_caregiver_nationality',
            'main_caregiver_nationality_other',
            'other_caregiver_relationship',
            'basic_stationery',
            'remote_learning',
            'remote_learning_reasons_not_engaged',
            'reasons_not_engaged_other',
            'reliable_internet',
            'gender_participate',
            'gender_participate_explain',
            'remote_learning_engagement',
            'meet_learning_outcomes',
            'parent_learning_support_rate',
            'covid_message',
            'covid_message_how_often',
            'covid_parents_message',
            'covid_parents_message_how_often',
            'follow_up_done',
            'follow_up_done_with_who',
            'labours_other_specify',
            'mid_test_done',
            'mid_test',
            'child_received_books',
            'child_received_printout',
            'child_received_internet',
            'referal_wash',
            'referal_health',
            'referal_other',
            'referal_other_specify',
            'akelius_program'
        )


class OutreachSerializer(CLMSerializer):

    def create(self, validated_data):
        return create_instance(validated_data=validated_data, model=self.Meta.model)

    def update(self, instance, validated_data):
        return update_instance(instance=instance, validated_data=validated_data)

    class Meta:
        model = Outreach
        ref_name = 'CLMOutreach'
        fields = CLMSerializer.Meta.fields + (
            'have_labour',
            'labours',
            'labour_hours',
            'have_labour_single_selection',
            'labours_single_selection',
            'labour_weekly_income',
            'student_family_status',
            'student_have_children',
            'student_number_children',
            'phone_number',
            'phone_number_confirm',
            'second_phone_number',
            'second_phone_number_confirm',
            'phone_owner',
            'second_phone_owner',
            'id_type',
            'case_number',
            'case_number_confirm',
            'individual_case_number',
            'individual_case_number_confirm',
            'parent_individual_case_number',
            'parent_individual_case_number_confirm',
            'recorded_number',
            'recorded_number_confirm',
            'national_number',
            'national_number_confirm',
            'syrian_national_number',
            'syrian_national_number_confirm',
            'sop_national_number',
            'sop_national_number_confirm',
            'parent_national_number',
            'parent_national_number_confirm',
            'parent_syrian_national_number',
            'parent_syrian_national_number_confirm',
            'parent_sop_national_number',
            'parent_sop_national_number_confirm',
            'parent_other_number',
            'parent_other_number_confirm',
            'other_number',
            'other_number_confirm',
            'no_child_id_confirmation',
            'source_of_identification',
            'source_of_identification_specify',
            'other_nationality',
            'education_status',
            'caretaker_first_name',
            'caretaker_middle_name',
            'caretaker_last_name',
            'caretaker_mother_name',
            'registration_level',
            'governorate',
            'district',
            'cadaster',
            'miss_school_date',
            'source_of_transportation',
            'main_caregiver',
            'main_caregiver_nationality',
            'main_caregiver_nationality_other',
            'other_caregiver_relationship',
            'basic_stationery',
            'pss_kit',
            'remote_learning',
            'remote_learning_reasons_not_engaged',
            'reasons_not_engaged_other',
            'reliable_internet',
            'gender_participate',
            'gender_participate_explain',
            'remote_learning_engagement',
            'meet_learning_outcomes',
            'parent_learning_support_rate',
            'covid_message',
            'covid_message_how_often',
            'covid_parents_message',
            'covid_parents_message_how_often',
            'follow_up_done',
            'follow_up_done_with_who',
            'child_received_books',
            'child_received_printout',
            'child_received_internet',
            'referal_wash',
            'referal_health',
            'referal_other',
            'referal_other_specify'
        )


class ABLN_FCSerializer(serializers.ModelSerializer):
    # enrollment_id = serializers.IntegerField(source='enrollment.id')

    class Meta:
        model = ABLN_FC
        fields = (
            'enrollment_id',
            'fc_type',
            'facilitator_name',
            'subject_taught',
            'date_of_monitoring',
            'targeted_competencies',
            'activities_reported',
            'activities_reported_other',
            'share_expectations',
            'share_expectations_no_reason',
            'share_expectations_other_reason',
            'materials_needed_available',
            'attend_lesson',
            'child_interact_teacher',
            'child_interact_friends',
            'child_clear_responses',
            'child_ask_questions',
            'child_acquire_competency',
            'child_show_improvement',
            'child_expected_work_independently',
            'work_independently_evaluation',
            'complete_printed_package',
            'sessions_participated',
            'not_participating_reason',
            'e_recharge_card_provided',
            'action_to_taken',
            'action_to_taken_specify',
            'child_needs_pss',
            'child_cant_access_resources',
            'homework_after_lesson',
            'parents_supporting_student',
            'completed_tasks',
            'meet_objectives',
            'meet_objectives_verified',
            'objectives_verified_specify',
            'additional_notes',
            'lesson_modality',
            'steps_acquire_competency',
            'steps_acquire_competency_other',
        )


class BLN_FCSerializer(serializers.ModelSerializer):
    class Meta:
        model = BLN_FC
        fields = (
            'enrollment_id',
            'fc_type',
            'facilitator_name',
            'subject_taught',
            'date_of_monitoring',
            'targeted_competencies',
            'activities_reported',
            'activities_reported_other',
            'share_expectations',
            'share_expectations_no_reason',
            'share_expectations_other_reason',
            'materials_needed_available',
            'attend_lesson',
            'child_interact_teacher',
            'child_interact_friends',
            'child_clear_responses',
            'child_ask_questions',
            'child_acquire_competency',
            'child_show_improvement',
            'child_expected_work_independently',
            'work_independently_evaluation',
            'complete_printed_package',
            'sessions_participated',
            'not_participating_reason',
            'e_recharge_card_provided',
            'action_to_taken',
            'action_to_taken_specify',
            'child_needs_pss',
            'child_cant_access_resources',
            'homework_after_lesson',
            'parents_supporting_student',
            'completed_tasks',
            'meet_objectives',
            'meet_objectives_verified',
            'objectives_verified_specify',
            'additional_notes',
            'lesson_modality',
            'steps_acquire_competency',
            'steps_acquire_competency_other',
        )


class RS_FCSerializer(serializers.ModelSerializer):
    # enrollment_id = serializers.IntegerField(source='enrollment.id')

    class Meta:
        model = RS_FC
        fields = (
            'enrollment_id',
            'fc_type',
            'facilitator_name',
            'subject_taught',
            'date_of_monitoring',
            'targeted_competencies',
            'activities_reported',
            'activities_reported_other',
            'share_expectations',
            'share_expectations_no_reason',
            'share_expectations_other_reason',
            'materials_needed_available',
            'attend_lesson',
            'child_interact_teacher',
            'child_interact_friends',
            'child_clear_responses',
            'child_ask_questions',
            'child_acquire_competency',
            'child_show_improvement',
            'child_expected_work_independently',
            'work_independently_evaluation',
            'complete_printed_package',
            'sessions_participated',
            'not_participating_reason',
            'e_recharge_card_provided',
            'action_to_taken',
            'action_to_taken_specify',
            'child_needs_pss',
            'child_cant_access_resources',
            'homework_after_lesson',
            'parents_supporting_student',
            'completed_tasks',
            'meet_objectives',
            'meet_objectives_verified',
            'objectives_verified_specify',
            'additional_notes',
            'lesson_modality',
            'steps_acquire_competency',
            'steps_acquire_competency_other',
        )


class CBECE_FCSerializer(serializers.ModelSerializer):
    # enrollment_id = serializers.IntegerField(source='enrollment.id')

    class Meta:
        model = CBECE_FC
        fields = (
            'enrollment_id',
            'fc_type',
            'facilitator_name',
            'subject_taught',
            'date_of_monitoring',
            'targeted_competencies',
            'activities_reported',
            'activities_reported_other',
            'share_expectations',
            'share_expectations_no_reason',
            'share_expectations_other_reason',
            'materials_needed_available',
            'attend_lesson',
            'child_interact_teacher',
            'child_interact_friends',
            'child_clear_responses',
            'child_ask_questions',
            'child_acquire_competency',
            'child_show_improvement',
            'child_expected_work_independently',
            'work_independently_evaluation',
            'complete_printed_package',
            'sessions_participated',
            'not_participating_reason',
            'e_recharge_card_provided',
            'action_to_taken',
            'action_to_taken_specify',
            'child_needs_pss',
            'child_cant_access_resources',
            'homework_after_lesson',
            'parents_supporting_student',
            'completed_tasks',
            'meet_objectives',
            'meet_objectives_verified',
            'objectives_verified_specify',
            'additional_notes',
            'lesson_modality',
            'steps_acquire_competency',
            'steps_acquire_competency_other',
        )


class GeneralQuestionnaireSerializer(serializers.ModelSerializer):
    # enrollment_id = serializers.IntegerField(source='enrollment.id')

    class Meta:
        model = GeneralQuestionnaire
        fields = (
            # 'enrollment_id',
            'facilitator_full_name',
        )


class CBECEExportSerializer(CLMSerializer):

    def create(self, validated_data):
        return create_instance(validated_data=validated_data, model=self.Meta.model)

    def update(self, instance, validated_data):
        return update_instance(instance=instance, validated_data=validated_data)

    class Meta:
        model = CBECE
        fields = (

            'id',
            'new_registry',
            'partner',
            # 'round__name',
            # 'governorate__name_en',
            # 'district__name_en',
            # 'cadaster__name_en',
            'location',
            # 'center__name',
            'language',
            # 'student__address',
            'registration_level',
            'first_attendance_date',
            # 'student__id_number',
            # 'student__number',
            # 'student_first_name',
            # 'student_father_name',
            # 'student_last_name',
            # 'student_mother_fullname',
            # 'student_sex',
            # 'student__nationality__name',
            'other_nationality',
            # 'student__birthday_day',
            # 'student__birthday_month',
            # 'student__birthday_year',
            # 'student__p_code',
            # 'disability__name_en',
            'education_status',
            'miss_school_date',
            'internal_number',
            'rims_case_number',
            'source_of_identification',
            'source_of_identification_specify',
            'source_of_transportation',
            # 'hh_educational_level__name',
            # 'father_educational_level__name',
            'phone_number',
            'phone_owner',
            'second_phone_number',
            'second_phone_owner',
            'main_caregiver',
            # 'main_caregiver_nationality__name',
            'other_caregiver_relationship',
            'caretaker_first_name',
            'caretaker_middle_name',
            'caretaker_last_name',
            'caretaker_mother_name',
            'id_type',
            'case_number',
            'parent_individual_case_number',
            'individual_case_number',
            'recorded_number',
            'parent_national_number',
            'national_number',
            'parent_syrian_national_number',
            'syrian_national_number',
            'parent_sop_national_number',
            'sop_national_number',
            'parent_other_number',
            'other_number',
            # 'student__family_status',
            # 'student__have_children',
            'student_number_children',
            'have_labour_single_selection',
            'labours_single_selection',
            'labours_other_specify',
            'labour_hours',
            'labour_weekly_income',
            'participation',
            'barriers_single',
            'barriers_other',
            'round_complete',
            'basic_stationery',
            'pss_kit',
            'learning_result',
            'learning_result_other',
            'parent_attended_visits',
            # 'owner__username',
            # 'modified_by__username',
        )


class SelfPerceptionGradesSerializer(serializers.ModelSerializer):

    class Meta:
        model = SelfPerceptionGrades
        fields = '__all__'
