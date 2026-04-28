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

    source_type = models.CharField(max_length=20, choices=SOURCE_TYPES)
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
    dewpoint=models.FloatField(null=True, blank=True)
    relative_humidity=models.FloatField(null=True, blank=True)
    visibility=models.FloatField(null=True, blank=True)
    wind_gust=models.FloatField(null=True, blank=True)
    precipitation_last_hour = models.FloatField(null=True, blank=True)
    cloud_cover = models.FloatField(null=True, blank=True)
    cloud_layers=models.FloatField(null=True, blank=True)

    # Marine
    tide_height = models.FloatField(null=True, blank=True)
    tide_stage = models.CharField(max_length=50, null=True, blank=True)
    water_temperature = models.FloatField(null=True, blank=True)
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

    moonrise = models.DateTimeField(null=True, blank=True)
    moonset = models.DateTimeField(null=True, blank=True)

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