import requests
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from datetime import datetime, timezone, timedelta
from geopy.distance import geodesic
from .models import EnvironmentalData
from .marine_helpers import (
    _extract_environmental_data,
    _fetch_weathergov_observations,
    _get_closest_observation,
    _closest_station,
    _get_closest_observation_tide
)


@api_view(['POST'])
def fetch_all_environmental_data(request):
    pass

@api_view(['GET'])
def fetch_and_store_environmental_data(request):
    """
    Fetch observations from NOAA (weather.gov) and extract environmental data.
    Query params: latitude (default 32.78), longitude (default -79.93)
    """
    date_time = datetime.now(timezone.utc)
    latitude = request.query_params.get("latitude", 32.78)
    longitude = request.query_params.get("longitude", -79.93)
    
    payload = _fetch_weathergov_observations(float(latitude), float(longitude), date_time)
    observations = payload["observations"]
    observation = _get_closest_observation(observations, date_time)
    
    if not observation:
        return Response(
            {"error": "No observations found near target time"},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Extract structured environmental data
    env_data = _extract_environmental_data(observation)
        
    return Response(env_data, status=status.HTTP_200_OK)


@api_view(['GET'])
def fetch_water_level_data(request):
    date_time=datetime.now(timezone.utc)
    begin_time = date_time - timedelta(hours=6, minutes=10)
    place_coords=(32.78, -79.93)
    station_api="https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/stations.json"
    station_res=requests.get(station_api).json()
    stations = station_res.get("stations") or []
    count, station = _closest_station(place_coords, stations)
    if station is None:
        return Response(
            {"error": "No stations returned from NOAA", "upstream": station_res},
            status=status.HTTP_502_BAD_GATEWAY,
        )
    station_id = station["id"]
            
    api="https://api.tidesandcurrents.noaa.gov/api/prod/datagetter"
    params = {
        "product": 'water_level',
        "station": station_id,
        "begin_date": begin_time.strftime("%Y%m%d %H:%M"),
        "end_date": date_time.strftime("%Y%m%d %H:%M"),
        "datum": "MLLW",
        "units": "metric",
        "time_zone": "gmt",
        "application": "NOAA National Weather Service API",
        "format": "json"
    }

    water_level_res = requests.get(api, params=params).json()

    api_error = water_level_res.get("error")
    if api_error:
        return Response(
            {"error": api_error, "upstream": water_level_res},
            status=status.HTTP_502_BAD_GATEWAY,
        )

    data = water_level_res.get("data") or []
    last_water_level = data[-1] if data else None

    return Response(
        {
            "date_time": date_time,
            "count": count,
            "station_id": station_id,
            "station_name": station.get("name"),
            "last_water_level": last_water_level,
            "water_level": water_level_res,
        },
        status=status.HTTP_200_OK)

@api_view(["GET"])
def fetch_water_temperature(request):
    date_time=datetime.now(timezone.utc)
    begin_time = date_time - timedelta(hours=6, minutes=10)
    place_coords=(32.78, -79.93)
    station_api="https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/stations.json"
    station_res=requests.get(station_api).json()
    stations = station_res.get("stations") or []
    count, station = _closest_station(place_coords, stations)
    if station is None:
        return Response(
            {"error": "No stations returned from NOAA", "upstream": station_res},
            status=status.HTTP_502_BAD_GATEWAY,
        )
    station_id = station["id"]
            
    api="https://api.tidesandcurrents.noaa.gov/api/prod/datagetter"
    params = {
        "product": 'water_temperature',
        "station": station_id,
        "begin_date": begin_time.strftime("%Y%m%d %H:%M"),
        "end_date": date_time.strftime("%Y%m%d %H:%M"),
        "datum": "MLLW",
        "units": "metric",
        "time_zone": "gmt",
        "application": "NOAA National Weather Service API",
        "format": "json"
    }

    water_temp_res = requests.get(api, params=params).json()

    api_error = water_temp_res.get("error")
    if api_error:
        return Response(
            {"error": api_error, "upstream": water_temp_res},
            status=status.HTTP_502_BAD_GATEWAY,
        )

    data = water_temp_res.get("data") or []
    last_temp = data[-1] if data else None

    return Response(
        {
            "date_time": date_time,
            "count": count,
            "station_id": station_id,
            "station_name": station.get("name"),
            "water_temp": last_temp,
        },
        status=status.HTTP_200_OK)

@api_view(['GET'])
def fetch_conductivity(request):
    date_time=datetime.now(timezone.utc)
    place_coords=(32.78, -79.93)
    station_api="https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/stations.json"
    station_res=requests.get(station_api).json()
    stations = station_res.get("stations") or []
    count, station = _closest_station(place_coords, stations)
    if station is None:
        return Response(
            {"error": "No stations returned from NOAA", "upstream": station_res},
            status=status.HTTP_502_BAD_GATEWAY,
        )
    station_id = station["id"]
            
    api="https://api.tidesandcurrents.noaa.gov/api/prod/datagetter"
    params = {
        "product": 'conductivity',
        "station": station_id,
        "date": "recent",
        "units": "metric",
        "time_zone": "gmt",
        "application": "NOAA National Weather Service API",
        "format": "json"
    }

    conductivity_res = requests.get(api, params=params).json()

    api_error = conductivity_res.get("error")
    if api_error:
        return Response(
            {"error": api_error, "upstream": conductivity_res},
            status=status.HTTP_502_BAD_GATEWAY,
        )

    data = conductivity_res.get("data") or []
    last_cond = data[-1] if data else None

    return Response(
        {
            "date_time": date_time,
            "count": count,
            "station_id": station_id,
            "station_name": station.get("name"),
            "conductivity": last_cond,
        },
        status=status.HTTP_200_OK)

@api_view(['GET'])
def fetch_salinity(request):
    date_time=datetime.now(timezone.utc)
    place_coords=(32.78, -79.93)
    station_api="https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/stations.json"
    station_res=requests.get(station_api).json()
    stations = station_res.get("stations") or []
    count, station = _closest_station(place_coords, stations)
    if station is None:
        return Response(
            {"error": "No stations returned from NOAA", "upstream": station_res},
            status=status.HTTP_502_BAD_GATEWAY,
        )
    station_id = station["id"]
            
    api="https://api.tidesandcurrents.noaa.gov/api/prod/datagetter"
    params = {
        "product": 'salinity',
        "station": station_id,
        "date": "recent",
        "units": "metric",
        "time_zone": "gmt",
        "application": "NOAA National Weather Service API",
        "format": "json"
    }

    salinity_res = requests.get(api, params=params).json()

    api_error = salinity_res.get("error")
    if api_error:
        return Response(
            {"error": api_error, "upstream": salinity_res},
            status=status.HTTP_502_BAD_GATEWAY,
        )

    data = salinity_res.get("data") or []
    last_sal = data[-1] if data else None

    return Response(
        {
            "date_time": date_time,
            "count": count,
            "station_id": station_id,
            "station_name": station.get("name"),
            "salinity": last_sal,
        },
        status=status.HTTP_200_OK)

@api_view(['GET'])
def fetch_currents(request):
    date_time=datetime.now(timezone.utc)
    place_coords=(32.78, -79.93)
    station_api="https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/stations.json?type=currentpredictions"
    station_res=requests.get(station_api).json()
    stations = station_res.get("stations") or []
    count, station = _closest_station(place_coords, stations)
    if station is None:
        return Response(
            {"error": "No stations returned from NOAA", "upstream": station_res},
            status=status.HTTP_502_BAD_GATEWAY,
        )
    station_id = station["id"]
            
    api="https://api.tidesandcurrents.noaa.gov/api/prod/datagetter"
    params = {
        "product": 'currents',
        "station": station_id,
        'bin': 1,
        "date": "recent",
        "units": "metric",
        "time_zone": "gmt",
        "application": "NOAA National Weather Service API",
        "format": "json"
    }

    currents_res = requests.get(api, params=params).json()

    api_error = currents_res.get("error")
    if api_error:
        return Response(
            {"error": api_error, "upstream": currents_res, "station": station},
            status=status.HTTP_502_BAD_GATEWAY,
        )

    data = currents_res.get("data") or []
    last_curr = data[-1] if data else None

    return Response(
        {
            "date_time": date_time,
            "count": count,
            "station_id": station_id,
            "station_name": station.get("name"),
            "currents": last_curr,
        },
        status=status.HTTP_200_OK)


@api_view(['GET'])
def fetch_solar(request):
    date_time = datetime.now(timezone.utc)
    date_3_days_ago = (date_time - timedelta(days=3)).strftime('%Y-%m-%d')
    header = {"User-Agent": "gregorykariara1@gmail.com"}
    latitude = 32.78
    longitude = -79.93

    noaa = f"https://api.sunrise-sunset.org/json?lat={latitude}&lng={longitude}&date={date_3_days_ago}"
    res = requests.get(noaa, headers=header, timeout=20).json()

    results = res['results']
    data = {}
    
    for key, value in results.items():
        try:
            dt = datetime.strptime(f'{date_3_days_ago} {value}', "%Y-%m-%d %I:%M:%S %p")
            formatted = dt.replace(tzinfo=timezone.utc).isoformat()

            data[key] = formatted

        except Exception:
            data[key] = value

    return Response(data, status=status.HTTP_200_OK)