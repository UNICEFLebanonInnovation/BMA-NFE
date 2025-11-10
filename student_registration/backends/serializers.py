
from rest_framework import serializers
from .models import Notification, Exporter


class NotificationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Notification
        fields = (
            'status',
        )


class ExporterSerializer(serializers.ModelSerializer):

    class Meta:
        model = Exporter
        fields = (
            'name',
        )
