from rest_framework import viewsets, permissions, serializers
from rest_framework.authentication import TokenAuthentication, BasicAuthentication

from student_registration.schools.models import School
from student_registration.students.models import Teacher
from student_registration.mscc.models import Registration
from student_registration.attendances.models import MSCCAttendanceChild

from student_registration.schools.serializers import SchoolSerializer
from student_registration.students.serializers import TeacherSerializer
from student_registration.mscc.serializers import MainSerializer
from student_registration.attendances.serializers import MSCCAttendanceChildSerializer

class SyncSchoolSerializer(SchoolSerializer):
    id = serializers.IntegerField(required=False, write_only=True)

    class Meta(SchoolSerializer.Meta):
        fields = SchoolSerializer.Meta.fields + ('id',) if isinstance(SchoolSerializer.Meta.fields, tuple) else SchoolSerializer.Meta.fields

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

class SyncAttendanceSerializer(MSCCAttendanceChildSerializer):
    id = serializers.IntegerField(required=False, write_only=True)

    class Meta(MSCCAttendanceChildSerializer.Meta):
        fields = MSCCAttendanceChildSerializer.Meta.fields + ('id',) if isinstance(MSCCAttendanceChildSerializer.Meta.fields, tuple) else MSCCAttendanceChildSerializer.Meta.fields

    def create(self, validated_data):
        if 'id' in validated_data:
            validated_data['original_id'] = validated_data.pop('id')
        return super().create(validated_data)

class SyncSchoolViewSet(viewsets.ModelViewSet):
    queryset = School.objects.all()
    serializer_class = SyncSchoolSerializer
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

class SyncAttendanceViewSet(viewsets.ModelViewSet):
    queryset = MSCCAttendanceChild.objects.all()
    serializer_class = SyncAttendanceSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'original_id'
