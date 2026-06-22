import json
from rest_framework import viewsets, permissions, serializers, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response

from student_registration.locations.models import Location
from student_registration.students.models import Teacher
from student_registration.mscc.models import Registration, EducationProgrammeAssessment, FollowUpService, EducationAssessment, SyncLog

from student_registration.locations.serializers import LocationSerializer
from student_registration.students.serializers import TeacherSerializer
from student_registration.mscc.serializers import MainSerializer

class BaseSyncSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False, write_only=True)

    def create(self, validated_data):
        if 'id' in validated_data:
            validated_data['original_id'] = validated_data.pop('id')
        return super().create(validated_data)

class SyncLocationSerializer(BaseSyncSerializer, LocationSerializer):
    class Meta(LocationSerializer.Meta):
        fields = LocationSerializer.Meta.fields + ('id',) if isinstance(LocationSerializer.Meta.fields, tuple) else LocationSerializer.Meta.fields

class SyncTeacherSerializer(BaseSyncSerializer, TeacherSerializer):
    class Meta(TeacherSerializer.Meta):
        fields = TeacherSerializer.Meta.fields + ('id',) if isinstance(TeacherSerializer.Meta.fields, tuple) else TeacherSerializer.Meta.fields

class SyncRegistrationSerializer(BaseSyncSerializer, MainSerializer):
    class Meta(MainSerializer.Meta):
        fields = MainSerializer.Meta.fields + ('id',) if isinstance(MainSerializer.Meta.fields, tuple) else MainSerializer.Meta.fields

class SyncEducationProgrammeAssessmentSerializer(BaseSyncSerializer):
    class Meta:
        model = EducationProgrammeAssessment
        fields = '__all__'

class SyncFollowUpServiceSerializer(BaseSyncSerializer):
    class Meta:
        model = FollowUpService
        fields = '__all__'

class SyncEducationAssessmentSerializer(BaseSyncSerializer):
    class Meta:
        model = EducationAssessment
        fields = '__all__'

class LoggingViewSetMixin:
    def _log_sync(self, request, action, status_str, error_message=None):
        payload = request.data
        original_id = payload.get('id') if action == 'create' else self.kwargs.get(self.lookup_field)

        SyncLog.objects.create(
            model_name=self.queryset.model.__name__,
            original_id=original_id,
            action=action,
            status=status_str,
            error_message=error_message,
            payload=payload
        )

    def create(self, request, *args, **kwargs):
        try:
            response = super().create(request, *args, **kwargs)
            self._log_sync(request, 'create', 'success')
            return response
        except Exception as e:
            self._log_sync(request, 'create', 'failed', str(e))
            raise e

    def update(self, request, *args, **kwargs):
        try:
            response = super().update(request, *args, **kwargs)
            self._log_sync(request, 'update', 'success')
            return response
        except Exception as e:
            self._log_sync(request, 'update', 'failed', str(e))
            raise e

    def destroy(self, request, *args, **kwargs):
        try:
            response = super().destroy(request, *args, **kwargs)
            self._log_sync(request, 'delete', 'success')
            return response
        except Exception as e:
            self._log_sync(request, 'delete', 'failed', str(e))
            raise e


class SyncLocationViewSet(LoggingViewSetMixin, viewsets.ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = SyncLocationSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'original_id'

class SyncTeacherViewSet(LoggingViewSetMixin, viewsets.ModelViewSet):
    queryset = Teacher.objects.all()
    serializer_class = SyncTeacherSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'original_id'

class SyncRegistrationViewSet(LoggingViewSetMixin, viewsets.ModelViewSet):
    queryset = Registration.objects.all()
    serializer_class = SyncRegistrationSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'original_id'

class SyncEducationProgrammeAssessmentViewSet(LoggingViewSetMixin, viewsets.ModelViewSet):
    queryset = EducationProgrammeAssessment.objects.all()
    serializer_class = SyncEducationProgrammeAssessmentSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'original_id'

class SyncFollowUpServiceViewSet(LoggingViewSetMixin, viewsets.ModelViewSet):
    queryset = FollowUpService.objects.all()
    serializer_class = SyncFollowUpServiceSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'original_id'

class SyncEducationAssessmentViewSet(LoggingViewSetMixin, viewsets.ModelViewSet):
    queryset = EducationAssessment.objects.all()
    serializer_class = SyncEducationAssessmentSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'original_id'
