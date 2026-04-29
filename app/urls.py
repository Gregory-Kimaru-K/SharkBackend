from django.urls import path
from . import views
from .marine import (
    fetch_and_store_environmental_data,
    fetch_water_level_data,
    fetch_water_temperature,
    fetch_conductivity,
    fetch_currents,
    fetch_solar
    )

urlpatterns = [

    path('sharks/', views.sharks_list_view, name='list_sharks'),
    path('shark/create/', views.shark_view, name='create_shark'),
    path('location/create/', views.location_view, name='create_location'),
    path('event/create/', views.event_view, name='create_event'),
    path('observation/create/', views.observation_view, name='create_observation'),
    path('observation-media/create/', views.observation_media_view, name='create_observation_media'),
    path('shark-behaviour/create/', views.shark_behaviour, name='create_shark_behaviour'),
    path('environment/', fetch_and_store_environmental_data, name='services'),
    path("tide/", fetch_water_level_data, name='Tide Data'),
    path("water_temp/", fetch_water_temperature, name='Water Temp'),
    path("conductivity/", fetch_conductivity, name='conductivity'),
    path("currents/", fetch_currents, name="Currents"),
    path("solar/", fetch_solar, name="Astrological")
    

]
