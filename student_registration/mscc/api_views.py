from rest_framework import viewsets, permissions, serializers
from rest_framework.authentication import TokenAuthentication, BasicAuthentication

from student_registration.locations.models import Location
from student_registration.students.models import Teacher
from student_registration.mscc.models import Registration

from student_registration.mscc.models import EducationProgrammeAssessment, FollowUpService
from student_registration.mscc.models import EducationAssessment

from student_registration.locations.serializers import LocationSerializer
from student_registration.students.serializers import TeacherSerializer
from student_registration.mscc.serializers import MainSerializer

class SyncLocationSerializer(LocationSerializer):
    id = serializers.IntegerField(required=False, write_only=True)

    class Meta(LocationSerializer.Meta):
        fields = LocationSerializer.Meta.fields + ('id',) if isinstance(LocationSerializer.Meta.fields, tuple) else LocationSerializer.Meta.fields

    def create(self, validated_data):
        if 'id' in validated_data:
            validated_data['original_id'] = validated_data.pop('id')
        return super().create(validated_data)

class SyncTeacherSerializer(TeacherSerializer):
    id = serializers.IntegerField(required=False, write_only=True)

    class Meta(TeacherSerializer.Meta):
        fields = TeacherSerializer.Meta.fields + ('id',) if isinstance(TeacherSerializer.Meta.fields, tuple) else TeacherSerializer.Meta.fields

    def create(self, validated_data):
        if 'id' in validated_data:
            validated_data['original_id'] = validated_data.pop('id')
        return super().create(validated_data)

class SyncRegistrationSerializer(MainSerializer):
    id = serializers.IntegerField(required=False, write_only=True)

    class Meta(MainSerializer.Meta):
        fields = MainSerializer.Meta.fields + ('id',) if isinstance(MainSerializer.Meta.fields, tuple) else MainSerializer.Meta.fields

    def create(self, validated_data):
        if 'id' in validated_data:
            validated_data['original_id'] = validated_data.pop('id')
        return super().create(validated_data)

class SyncEducationProgrammeAssessmentSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False, write_only=True)

    class Meta:
        model = EducationProgrammeAssessment
        fields = '__all__'

    def create(self, validated_data):
        if 'id' in validated_data:
            validated_data['original_id'] = validated_data.pop('id')
        return super().create(validated_data)

class SyncFollowUpServiceSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False, write_only=True)

    class Meta:
        model = FollowUpService
        fields = '__all__'

    def create(self, validated_data):
        if 'id' in validated_data:
            validated_data['original_id'] = validated_data.pop('id')
        return super().create(validated_data)

class SyncEducationAssessmentSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False, write_only=True)

    class Meta:
        model = EducationAssessment
        fields = '__all__'

    def create(self, validated_data):
        if 'id' in validated_data:
            validated_data['original_id'] = validated_data.pop('id')
        return super().create(validated_data)

class SyncLocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = SyncLocationSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'original_id'

class SyncTeacherViewSet(viewsets.ModelViewSet):
    queryset = Teacher.objects.all()
    serializer_class = SyncTeacherSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'original_id'

class SyncRegistrationViewSet(viewsets.ModelViewSet):
    queryset = Registration.objects.all()
    serializer_class = SyncRegistrationSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'original_id'

class SyncEducationProgrammeAssessmentViewSet(viewsets.ModelViewSet):
    queryset = EducationProgrammeAssessment.objects.all()
    serializer_class = SyncEducationProgrammeAssessmentSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'original_id'

class SyncFollowUpServiceViewSet(viewsets.ModelViewSet):
    queryset = FollowUpService.objects.all()
    serializer_class = SyncFollowUpServiceSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'original_id'

class SyncEducationAssessmentViewSet(viewsets.ModelViewSet):
    queryset = EducationAssessment.objects.all()
    serializer_class = SyncEducationAssessmentSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'original_id'
