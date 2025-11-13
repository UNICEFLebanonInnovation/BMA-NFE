
import json

from rest_framework import serializers
from .models import Location, Center, ProgramStaff


class LocationSerializer(serializers.ModelSerializer):

    id = serializers.IntegerField(required=True)
    name = serializers.CharField(required=False)
    name_en = serializers.CharField(required=True)
    type_id = serializers.IntegerField(required=True)
    parent_id = serializers.IntegerField(required=True)

    def create(self, validated_data):

        try:
            instance = Location.objects.create(**validated_data)
            instance.save()

        except Exception as ex:
            raise serializers.ValidationError({'Location instance': ex})

        return instance

    class Meta:
        model = Location
        fields = (
            'id',
            'name',
            'name_en',
            'type_id',
            'parent_id',

        )
