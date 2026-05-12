import django_filters
from .models import Event

class EventFilter(django_filters.FilterSet):
    class Meta:
        model = Event
        fields = {
            # --------------------
            # BASIC EVENT INFO
            # --------------------
            "title": ["exact", "icontains"],
            "outcome": ["exact"],
            "source_type": ["exact"],
            "observed_at_utc": ["exact", "gte", "lte"],
            "shark_number": ["exact", "gte", "lte"],
            "is_processed": ["exact"],

            # --------------------
            # SHARK
            # --------------------
            "shark_type__name": ["exact", "icontains"],
            "shark_type__species": ["exact"],

            # --------------------
            # LOCATION
            # --------------------
            "location__name": ["exact", "icontains"],
            "location__region": ["exact", "icontains"],
            "location__country": ["exact", "icontains"],
            "location__latitude": ["exact", "gte", "lte"],
            "location__longitude": ["exact", "gte", "lte"],

            # --------------------
            # ATMOSPHERIC DATA
            # --------------------
            "environmental_data__pressure": ["exact", "gte", "lte"],
            "environmental_data__wind_speed": ["exact", "gte", "lte"],
            "environmental_data__wind_direction": ["exact", "gte", "lte"],
            "environmental_data__temperature": ["exact", "gte", "lte"],
            "environmental_data__dewpoint": ["exact", "gte", "lte"],
            "environmental_data__relative_humidity": ["exact", "gte", "lte"],
            "environmental_data__visibility": ["exact", "gte", "lte"],
            "environmental_data__wind_gust": ["exact", "gte", "lte"],
            "environmental_data__precipitation_last_hour": ["exact", "gte", "lte"],
            "environmental_data__cloud_cover": ["exact", "gte", "lte"],
            "environmental_data__cloud_layers": ["exact", "gte", "lte"],

            # --------------------
            # TIDE
            # --------------------
            "environmental_data__tide_height": ["exact", "gte", "lte"],
            "environmental_data__tide_standard_deviation": ["exact", "gte", "lte"],
            "environmental_data__tide_flags": ["exact"],
            "environmental_data__tide_quality_indicator": ["exact"],

            # --------------------
            # WATER
            # --------------------
            "environmental_data__water_temperature": ["exact", "gte", "lte"],
            "environmental_data__conductivity": ["exact", "gte", "lte"],
            "environmental_data__salinity": ["exact", "gte", "lte"],

            # --------------------
            # CURRENTS
            # --------------------
            "environmental_data__current_speed": ["exact", "gte", "lte"],
            "environmental_data__current_direction": ["exact"],
            "environmental_data__current_bin_Number": ["exact"],

            # --------------------
            # SOLAR
            # --------------------
            "environmental_data__sunrise": ["exact", "gte", "lte"],
            "environmental_data__sunset": ["exact", "gte", "lte"],
            "environmental_data__solar_noon": ["exact", "gte", "lte"],
            "environmental_data__civil_twilight_begin": ["exact", "gte", "lte"],
            "environmental_data__civil_twilight_end": ["exact", "gte", "lte"],
            "environmental_data__nautical_twilight_begin": ["exact", "gte", "lte"],
            "environmental_data__nautical_twilight_end": ["exact", "gte", "lte"],
            "environmental_data__astronomical_twilight_begin": ["exact", "gte", "lte"],
            "environmental_data__astronomical_twilight_end": ["exact", "gte", "lte"],
            "environmental_data__day_length": ["exact", "icontains"],

            # --------------------
            # LUNAR
            # --------------------
            "environmental_data__moon_phase": ["exact", "icontains"],
            "environmental_data__phase_angle": ["exact", "gte", "lte"],
            "environmental_data__illumination": ["exact", "gte", "lte"],
            "environmental_data__age_days": ["exact", "gte", "lte"],
            "environmental_data__distance_km": ["exact", "gte", "lte"],
            "environmental_data__is_waxing": ["exact"],
            "environmental_data__moonrise": ["exact", "gte", "lte"],
            "environmental_data__moonset": ["exact", "gte", "lte"],
            "environmental_data__is_eclipse": ["exact"],
            "environmental_data__is_blood_moon": ["exact"],

            # --------------------
            # NEXT PHASES (JSON)
            # --------------------
            "environmental_data__next_phases": ["exact"],
            "environmental_data__next_new_moon": ["exact", "gte", "lte"],
            "environmental_data__next_first_quarter": ["exact", "gte", "lte"],
            "environmental_data__next_full_moon": ["exact", "gte", "lte"],
            "environmental_data__next_last_quarter": ["exact", "gte", "lte"],

            # --------------------
            # SHARK BEHAVIOUR
            # --------------------
            "behaviour__feeding": ["exact"],
            "behaviour__aggression": ["exact", "gte", "lte"],
        }