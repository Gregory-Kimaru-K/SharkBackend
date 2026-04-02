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
            "latitude": ["exact"],
            "longitude": ["exact"]
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

            "shark_type__id": ["exact"],
            "shark_type__name": ["exact", "icontains"],
            "shark_type__species": ["exact", "icontains"],

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

            # Atmospheric
            "pressure": ["exact", "lt", "gt"],
            "wind_speed": ["exact", "lt", "gt"],
            "wind_direction": ["exact", "lt", "gt"],
            "cloud_cover": ["exact", "lt", "gt"],
            "precipitation": ["exact", "lt", "gt"],

            # Marine
            "tide_height": ["exact", "lt", "gt"],
            "tide_stage": ["exact", "icontains"],
            "water_temperature": ["exact", "lt", "gt"],
            "salinity": ["exact", "lt", "gt"],

            # Astronomical
            "lunar_phase": ["exact", "icontains"],
            "moon_illumination": ["exact", "lt", "gt"],

            "recorded_at_utc": ["exact", "lt", "gt"],
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
