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


class Query(graphene.ObjectType):

    all_sharks = DjangoFilterConnectionField(SharkType)
    all_locations = DjangoFilterConnectionField(LocationType)
    all_events = DjangoFilterConnectionField(EventType)