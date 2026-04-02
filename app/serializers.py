from rest_framework import serializers
from .models import (
    Shark,
    Locations,
    Event,
    ObservationRecord,
    ObservationMedia,
    EnvironmentalData,
    SharkBehaviour
)


class SharkSerializer(serializers.ModelSerializer):
    class Meta:
        model=Shark
        fields='__all__'

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model=Locations
        fields='__all__'

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model=Event
        fields='__all__'
        read_only_fields=['is_processed']
    
class ObservationRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model=ObservationRecord
        exclude = ["source_type"]

class ObeservationMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model=ObservationMedia
        fields='__all__'

class EnvironmentalDataSerializer(serializers.ModelSerializer):
    class Meta:
        model=EnvironmentalData
        fields='__all__'
        # No read_only_fields: we want this serializer to work for API responses.

class SharkBehaviourSerializer(serializers.ModelSerializer):
    class Meta:
        model=SharkBehaviour
        fields='__all__'