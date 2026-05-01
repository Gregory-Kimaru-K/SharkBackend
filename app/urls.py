from django.urls import path
from . import views
from .marine import fetch_all_environmental_data

urlpatterns = [

    path('sharks/', views.sharks_list_view, name='list_sharks'),
    path('shark/create/', views.shark_view, name='create_shark'),
    path('location/create/', views.location_view, name='create_location'),
    path('event/create/', views.event_view, name='create_event'),
    path('observation/create/', views.observation_view, name='create_observation'),
    path('observation-media/create/', views.observation_media_view, name='create_observation_media'),
    path('shark-behaviour/create/', views.shark_behaviour, name='create_shark_behaviour'),
    path("all/", fetch_all_environmental_data, name="everything")
    

]
