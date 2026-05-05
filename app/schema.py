from graphene_django import DjangoObjectType
from .models import (Shark,
                    Locations, Event, ObservationRecord,
                    EnvironmentalData, SharkBehaviour)
import graphene

from graphene_django.filter import DjangoFilterConnectionField

class SharkType(DjangoObjectType):
    class Meta:
        model = Shark
        fields = "__all__"

        filter_fields = {
            "name": ["exact", "icontains"],
            "species": ["exact", "icontains"]
        }

        interfaces = (graphene.relay.Node,)

class LocationType(DjangoObjectType):
    class Meta:
        model = Locations
        fields = "__all__"

        filter_fields = {
            "country": ["exact", "icontains"],
            "region": ["exact", "icontains"],
            "name": ["exact", "icontains"],
            "latitude": ["exact", "lt", "gt"],
            "longitude": ["exact", "lt", "gt"]
        }

        interfaces = (graphene.relay.Node,)



class EventType(DjangoObjectType):
    class Meta:
        model = Event
        fields = "__all__"

        filter_fields = {

            # Foreign Keys
            "location__id": ["exact"],
            "location__country": ["exact", "icontains"],
            "location__region": ["exact", "icontains"],
            "location__name": ["exact", "icontains"],
            "location__latitude": ["exact", "lt", "gt"],
            "location__longitude": ["exact", "lt", "gt"],

            "shark_type__id": ["exact"],
            "shark_type__name": ["exact", "icontains"],
            "shark_type__species": ["exact", "icontains"],

            # Related Environmental Data (one-to-one)
            "environmental_data__recorded_at_utc": ["exact", "lt", "gt"],
            "environmental_data__pressure": ["exact", "lt", "gt"],
            "environmental_data__wind_speed": ["exact", "lt", "gt"],
            "environmental_data__wind_direction": ["exact", "lt", "gt"],
            "environmental_data__temperature": ["exact", "lt", "gt"],
            "environmental_data__dewpoint": ["exact", "lt", "gt"],
            "environmental_data__relative_humidity": ["exact", "lt", "gt"],
            "environmental_data__visibility": ["exact", "lt", "gt"],
            "environmental_data__wind_gust": ["exact", "lt", "gt"],
            "environmental_data__precipitation_last_hour": ["exact", "lt", "gt"],
            "environmental_data__cloud_cover": ["exact", "lt", "gt"],
            "environmental_data__cloud_layers": ["exact", "lt", "gt"],
            "environmental_data__tide_height": ["exact", "lt", "gt"],
            "environmental_data__tide_standard_deviation": ["exact", "lt", "gt"],
            "environmental_data__tide_flags": ["exact", "icontains"],
            "environmental_data__tide_quality_indicator": ["exact", "icontains"],
            "environmental_data__water_temperature": ["exact", "lt", "gt"],
            "environmental_data__water_temperature_flags": ["exact", "icontains"],
            "environmental_data__conductivity": ["exact", "lt", "gt"],
            "environmental_data__conductivity_flags": ["exact", "icontains"],
            "environmental_data__current_speed": ["exact", "lt", "gt"],
            "environmental_data__current_direction": ["exact", "lt", "gt"],
            "environmental_data__current_bin_Number": ["exact", "lt", "gt"],
            "environmental_data__salinity": ["exact", "lt", "gt"],
            "environmental_data__sunrise": ["exact", "lt", "gt"],
            "environmental_data__sunset": ["exact", "lt", "gt"],
            "environmental_data__moonrise": ["exact", "lt", "gt"],
            "environmental_data__moonset": ["exact", "lt", "gt"],

            # Related Observations (many)
            "observations__source_type": ["exact"],
            "observations__source_name": ["exact", "icontains"],
            "observations__recorded_at_utc": ["exact", "lt", "gt"],
            "observations__payload": ["contains"],

            # Related Behaviour (one-to-one)
            "behaviour__feeding": ["exact"],
            "behaviour__aggression": ["exact", "lt", "gt"],

            # Scientific Fields
            "shark_number": ["exact", "lt", "gt"],
            "observed_at_utc": ["exact", "lt", "gt"],
            "outcome": ["exact"],
        }

        interfaces = (graphene.relay.Node,)


class ObservationRecordType(DjangoObjectType):
    class Meta:
        model = ObservationRecord
        fields = "__all__"

        filter_fields = {
            "source_type": ["exact"],

            "event__id": ["exact"],

            "recorded_at_utc": ["exact", "lt", "gt"],

            # JSON payload filtering
            "payload": ["contains"],
        }

        interfaces = (graphene.relay.Node,)


class EnvironmentalDataType(DjangoObjectType):
    class Meta:
        model = EnvironmentalData
        fields = "__all__"

        filter_fields = {
            "event__id": ["exact"],

            # JSON / metadata
            "sources": ["contains"],

            # Timestamps
            "recorded_at_utc": ["exact", "lt", "gt"],

            # Atmospheric
            "atmospheric_text": ["exact", "icontains"],
            "raw_message": ["exact", "icontains"],
            "pressure": ["exact", "lt", "gt"],
            "wind_speed": ["exact", "lt", "gt"],
            "wind_direction": ["exact", "lt", "gt"],
            "temperature": ["exact", "lt", "gt"],
            "dewpoint": ["exact", "lt", "gt"],
            "relative_humidity": ["exact", "lt", "gt"],
            "visibility": ["exact", "lt", "gt"],
            "wind_gust": ["exact", "lt", "gt"],
            "precipitation_last_hour": ["exact", "lt", "gt"],
            "cloud_cover": ["exact", "lt", "gt"],
            "cloud_layers": ["exact", "lt", "gt"],

            # Marine - Tide
            "tide_height": ["exact", "lt", "gt"],
            "tide_standard_deviation": ["exact", "lt", "gt"],
            "tide_flags": ["exact", "icontains"],
            "tide_quality_indicator": ["exact", "icontains"],

            # Marine - Water / Conductivity / Currents
            "water_temperature": ["exact", "lt", "gt"],
            "water_temperature_flags": ["exact", "icontains"],
            "conductivity": ["exact", "lt", "gt"],
            "conductivity_flags": ["exact", "icontains"],
            "current_speed": ["exact", "lt", "gt"],
            "current_direction": ["exact", "lt", "gt"],
            "current_bin_Number": ["exact", "lt", "gt"],
            "salinity": ["exact", "lt", "gt"],

            # Solar / Astronomical datetimes
            "sunrise": ["exact", "lt", "gt"],
            "sunset": ["exact", "lt", "gt"],
            "solar_noon": ["exact", "lt", "gt"],
            "civil_twilight_begin": ["exact", "lt", "gt"],
            "civil_twilight_end": ["exact", "lt", "gt"],
            "nautical_twilight_begin": ["exact", "lt", "gt"],
            "nautical_twilight_end": ["exact", "lt", "gt"],
            "astronomical_twilight_begin": ["exact", "lt", "gt"],
            "astronomical_twilight_end": ["exact", "lt", "gt"],
            "day_length": ["exact", "icontains"],
            "moonrise": ["exact", "lt", "gt"],
            "moonset": ["exact", "lt", "gt"],
        }

        interfaces = (graphene.relay.Node,)


class SharkBehaviourType(DjangoObjectType):
    class Meta:
        model = SharkBehaviour
        fields = "__all__"

        filter_fields = {
            "event__id": ["exact"],
            "feeding": ["exact"],
            'aggression': ['exact']
        }

        interfaces = (graphene.relay.Node,)


class Query(graphene.ObjectType):

    all_sharks = DjangoFilterConnectionField(SharkType)
    all_locations = DjangoFilterConnectionField(LocationType)
    all_events = DjangoFilterConnectionField(EventType)
    all_observations = DjangoFilterConnectionField(ObservationRecordType)
    all_environmental_data = DjangoFilterConnectionField(EnvironmentalDataType)
    all_shark_behaviours = DjangoFilterConnectionField(SharkBehaviourType)