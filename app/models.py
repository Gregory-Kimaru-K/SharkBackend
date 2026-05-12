from django.db import models
import uuid
from django.core.validators import MinValueValidator, MaxValueValidator

###########
################
#####################
########### BASE MODEL
#####################
################
###########

class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    class Meta:
        abstract=True

###########
################
#####################
########### SHARK TYPE
#####################
################
###########

class Shark(BaseModel):
    name=models.CharField(max_length=200)
    species=models.CharField(max_length=400, unique=True)

###########
################
#####################
########### LOCATION
#####################
################
###########

class Locations(BaseModel):
    latitude=models.DecimalField(max_digits=20, decimal_places=15)
    longitude=models.DecimalField(max_digits=20, decimal_places=15)
    region=models.CharField(max_length=100)
    country=models.CharField(max_length=100)
    name=models.CharField(max_length=100)

    class Meta:
        indexes = [
            models.Index(fields=["latitude", "longitude"])
        ]



###########
################
#####################
########### TIME AND DATE EVENT
#####################
################
###########

class Event(BaseModel):
    OUTCOME_CHOICES=[
        ('FEEDING', 'Feeding observed'),
        ('NO_FEEDING', 'No feeding observed')
    ]
    
    title=models.CharField(max_length=100)
    notes=models.TextField(blank=True)
    location=models.ForeignKey(Locations, on_delete=models.PROTECT, related_name='events')
    shark_type=models.ForeignKey(Shark, on_delete=models.PROTECT, related_name='events')
    shark_number = models.PositiveIntegerField()
    observed_at_utc=models.DateTimeField()
    outcome = models.CharField(max_length=20, choices=OUTCOME_CHOICES)
    is_processed=models.BooleanField(default=False)


###########
################
#####################
########### Observation Data
#####################
################
###########

class ObservationRecord(BaseModel):
    SOURCE_TYPES = [
        ('USER', 'User Submission'),
        ('API', 'External API'),
        ('SENSOR', 'Sensor Device')
    ]

    source_type = models.CharField(max_length=20, choices=SOURCE_TYPES, default="USER")
    event=models.ForeignKey(Event, on_delete=models.CASCADE, related_name='observations')
    source_name=models.CharField(max_length=200)
    recorded_at_utc=models.DateTimeField()
    observation=models.TextField()
    payload=models.JSONField()

class ObservationMedia(BaseModel):
    observation=models.ForeignKey(ObservationRecord, related_name='media_observe', on_delete=models.CASCADE)
    media=models.FileField(upload_to='observations/')

###########
################
#####################
########### ENVIRONMENTAL DATA
#####################
################
###########

class EnvironmentalData(BaseModel):

    event = models.OneToOneField(Event, on_delete=models.CASCADE, related_name='environmental_data')

    #Atmospheric, Marine and Astronomical sources
    sources=models.JSONField()
    recorded_at_utc = models.DateTimeField()

    # Atmospheric
    atmospheric_text = models.TextField(null=True, blank=True)
    raw_message = models.TextField(null=True, blank=True)
    pressure = models.FloatField(null=True, blank=True)
    wind_speed = models.FloatField(null=True, blank=True)
    wind_direction = models.FloatField(null=True, blank=True)
    temperature = models.FloatField(null=True, blank=True)
    dewpoint = models.FloatField(null=True, blank=True)
    relative_humidity = models.FloatField(null=True, blank=True)
    visibility = models.FloatField(null=True, blank=True)
    wind_gust = models.FloatField(null=True, blank=True)
    precipitation_last_hour = models.FloatField(null=True, blank=True)
    cloud_cover = models.FloatField(null=True, blank=True)
    cloud_layers = models.FloatField(null=True, blank=True)


    # Atmospheric 1 hour prior
    atmospheric_text_1hr_prior = models.TextField(null=True, blank=True)
    raw_message_1hr_prior = models.TextField(null=True, blank=True)
    pressure_1hr_prior = models.FloatField(null=True, blank=True)
    wind_speed_1hr_prior = models.FloatField(null=True, blank=True)
    wind_direction_1hr_prior = models.FloatField(null=True, blank=True)
    temperature_1hr_prior = models.FloatField(null=True, blank=True)
    dewpoint_1hr_prior = models.FloatField(null=True, blank=True)
    relative_humidity_1hr_prior = models.FloatField(null=True, blank=True)
    visibility_1hr_prior = models.FloatField(null=True, blank=True)
    wind_gust_1hr_prior = models.FloatField(null=True, blank=True)
    precipitation_last_hour_1hr_prior = models.FloatField(null=True, blank=True)
    cloud_cover_1hr_prior = models.FloatField(null=True, blank=True)
    cloud_layers_1hr_prior = models.FloatField(null=True, blank=True)


    # Atmospheric 3 hours prior
    atmospheric_text_3hr_prior = models.TextField(null=True, blank=True)
    raw_message_3hr_prior = models.TextField(null=True, blank=True)
    pressure_3hr_prior = models.FloatField(null=True, blank=True)
    wind_speed_3hr_prior = models.FloatField(null=True, blank=True)
    wind_direction_3hr_prior = models.FloatField(null=True, blank=True)
    temperature_3hr_prior = models.FloatField(null=True, blank=True)
    dewpoint_3hr_prior = models.FloatField(null=True, blank=True)
    relative_humidity_3hr_prior = models.FloatField(null=True, blank=True)
    visibility_3hr_prior = models.FloatField(null=True, blank=True)
    wind_gust_3hr_prior = models.FloatField(null=True, blank=True)
    precipitation_last_hour_3hr_prior = models.FloatField(null=True, blank=True)
    cloud_cover_3hr_prior = models.FloatField(null=True, blank=True)
    cloud_layers_3hr_prior = models.FloatField(null=True, blank=True)

    # Tide current
    tide_height = models.FloatField(null=True, blank=True)
    tide_standard_deviation = models.FloatField(null=True, blank=True)
    tide_flags = models.CharField(max_length=10, null=True, blank=True)
    tide_quality_indicator = models.CharField(max_length=1, null=True, blank=True)


    # Tide 1 hour prior
    tide_height_1hr_prior = models.FloatField(null=True, blank=True)
    tide_standard_deviation_1hr_prior = models.FloatField(null=True, blank=True)
    tide_flags_1hr_prior = models.CharField(max_length=10, null=True, blank=True)
    tide_quality_indicator_1hr_prior = models.CharField(max_length=1, null=True, blank=True)


    # Tide 3 hours prior
    tide_height_3hr_prior = models.FloatField(null=True, blank=True)
    tide_standard_deviation_3hr_prior = models.FloatField(null=True, blank=True)
    tide_flags_3hr_prior = models.CharField(max_length=10, null=True, blank=True)
    tide_quality_indicator_3hr_prior = models.CharField(max_length=1, null=True, blank=True)


    # Tide 6 hours prior
    tide_height_6hr_prior = models.FloatField(null=True, blank=True)
    tide_standard_deviation_6hr_prior = models.FloatField(null=True, blank=True)
    tide_flags_6hr_prior = models.CharField(max_length=10, null=True, blank=True)
    tide_quality_indicator_6hr_prior = models.CharField(max_length=1, null=True, blank=True)

    ######## Water Temperature
    water_temperature = models.FloatField(null=True, blank=True)
    water_temperature_flags = models.CharField(max_length=10, null=True, blank=True)
    
    ######## Conductivity
    conductivity = models.FloatField(null=True, blank=True)
    conductivity_flags = models.CharField(max_length=10, null=True, blank=True)
    
    ######## currents
    current_speed = models.FloatField(null=True, blank=True)
    current_direction = models.IntegerField(null=True, blank=True)
    current_bin_Number = models.IntegerField(null=True, blank=True)
    salinity=models.FloatField(null=True, blank=True)

    #Solar Data
    sunrise = models.DateTimeField(null=True, blank=True)
    sunset = models.DateTimeField(null=True, blank=True)
    solar_noon = models.DateTimeField(null=True, blank=True)
    civil_twilight_begin = models.DateTimeField(null=True, blank=True)
    civil_twilight_end = models.DateTimeField(null=True, blank=True)
    nautical_twilight_begin = models.DateTimeField(null=True, blank=True)
    nautical_twilight_end = models.DateTimeField(null=True, blank=True)
    astronomical_twilight_begin = models.DateTimeField(null=True, blank=True)
    astronomical_twilight_end = models.DateTimeField(null=True, blank=True)
    day_length = models.CharField(max_length=30, null=True, blank=True)

    #Lunar Data
    moon_phase = models.CharField(max_length=30, null=True, blank=True)
    phase_angle = models.FloatField(null=True, blank=True)
    illumination = models.FloatField(null=True, blank=True)
    age_days = models.FloatField(null=True, blank=True)
    distance_km = models.FloatField(null=True, blank=True)
    is_waxing = models.BooleanField(null=True, blank=True)
    moonrise = models.DateTimeField(null=True, blank=True)
    moonset = models.DateTimeField(null=True, blank=True)
    is_eclipse = models.BooleanField(null=True, blank=True)
    is_blood_moon = models.BooleanField(null=True, blank=True)
    next_new_moon=models.DateTimeField(null=True, blank=True)
    next_first_quarter=models.DateTimeField(null=True, blank=True)
    next_full_moon=models.DateTimeField(null=True, blank=True)
    next_last_quarter=models.DateTimeField(null=True, blank=True)


    # 1 hour prior
    moon_phase_1hr_prior = models.CharField(max_length=30, null=True, blank=True)
    phase_angle_1hr_prior = models.FloatField(null=True, blank=True)
    illumination_1hr_prior = models.FloatField(null=True, blank=True)
    age_days_1hr_prior = models.FloatField(null=True, blank=True)
    distance_km_1hr_prior = models.FloatField(null=True, blank=True)
    is_waxing_1hr_prior = models.BooleanField(null=True, blank=True)
    moonrise_1hr_prior = models.DateTimeField(null=True, blank=True)
    moonset_1hr_prior = models.DateTimeField(null=True, blank=True)
    is_eclipse_1hr_prior = models.BooleanField(null=True, blank=True)
    is_blood_moon_1hr_prior = models.BooleanField(null=True, blank=True)


    # 3 hours prior
    moon_phase_3hr_prior = models.CharField(max_length=30, null=True, blank=True)
    phase_angle_3hr_prior = models.FloatField(null=True, blank=True)
    illumination_3hr_prior = models.FloatField(null=True, blank=True)
    age_days_3hr_prior = models.FloatField(null=True, blank=True)
    distance_km_3hr_prior = models.FloatField(null=True, blank=True)
    is_waxing_3hr_prior = models.BooleanField(null=True, blank=True)
    moonrise_3hr_prior = models.DateTimeField(null=True, blank=True)
    moonset_3hr_prior = models.DateTimeField(null=True, blank=True)
    is_eclipse_3hr_prior = models.BooleanField(null=True, blank=True)
    is_blood_moon_3hr_prior = models.BooleanField(null=True, blank=True)


    # 6 hours prior
    moon_phase_6hr_prior = models.CharField(max_length=30, null=True, blank=True)
    phase_angle_6hr_prior = models.FloatField(null=True, blank=True)
    illumination_6hr_prior = models.FloatField(null=True, blank=True)
    age_days_6hr_prior = models.FloatField(null=True, blank=True)
    distance_km_6hr_prior = models.FloatField(null=True, blank=True)
    is_waxing_6hr_prior = models.BooleanField(null=True, blank=True)
    moonrise_6hr_prior = models.DateTimeField(null=True, blank=True)
    moonset_6hr_prior = models.DateTimeField(null=True, blank=True)
    is_eclipse_6hr_prior = models.BooleanField(null=True, blank=True)
    is_blood_moon_6hr_prior = models.BooleanField(null=True, blank=True)


###########
################
#####################
########### SHARK BEHAVIOUR
#####################
################
###########

class SharkBehaviour(BaseModel):

    event = models.OneToOneField(Event, on_delete=models.CASCADE, related_name='behaviour')
    feeding = models.BooleanField(default=False)
    aggression = models.PositiveIntegerField(
                    null=True,
                    blank=True,
                    validators=[MinValueValidator(1), MaxValueValidator(10)])
    activity_notes = models.TextField(blank=True)

###########
################
#####################
########### NORMALIZED DATA
#####################
################
###########



###########
################
#####################
########### DERIVED FEATURES
#####################
################
###########