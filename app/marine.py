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
    _get_closest_observation_tide,
    _find_products
)


@api_view(['POST'])
def fetch_all_environmental_data(request):
    date_time = request.data.get("date_time", datetime.now(timezone.utc))
    latitude = request.data.get("latitude", 32.78)
    longitude = request.data.get("longitude", -79.93)
    begin_time = date_time - timedelta(hours=6, minutes=10)
    station_api = "https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/stations.json"
    api = "https://api.tidesandcurrents.noaa.gov/api/prod/datagetter"
    
    def atmospheric():
        """
            Fetch observations from NOAA (weather.gov) and extract environmental data.
            Query params: latitude (default 32.78), longitude (default -79.93)
        """
        try:
            payload = _fetch_weathergov_observations(float(latitude), float(longitude), date_time)
            observations = payload["observations"]
            observation = _get_closest_observation(observations, date_time)

            if not observation:
                return (
                    False,
                    {
                        "sources": 'NOAA National Weather Service API',
                        "error": "No observations found near target time"
                    })

            # Extract structured environmental data
            env_data = _extract_environmental_data(observation)

            return(True, env_data)

        except Exception as e:
            return(
                False,
                {"error": str(e)}
            )
    
    def other(name):
        station_res = None
        try:
            if name == 'conductivity' or name == "currents":
                if name == "conductivity":
                    stat_params = {
                        "type": "cond"
                    }

                    station_res = requests.get(station_api, params=stat_params).json()
                else:
                    stat_params = {
                        'type': "currents"
                    }

                    station_res = requests.get(station_api, params=stat_params).json()
            else:
                station_res = requests.get(station_api).json()
            stations = station_res.get("stations") or []
            count, station = _closest_station((latitude, longitude), stations)
            if station is None:
                return(
                    False,
                    {
                        "error": "No stations returned from NOAA", "upstream": station_res
                    })
            station_id = station["id"]
            params = {
                "product": name,
                "station": station_id,
                "begin_date": begin_time.strftime("%Y%m%d %H:%M"),
                "end_date": date_time.strftime("%Y%m%d %H:%M"),
                "datum": "MLLW",
                "units": "metric",
                "time_zone": "gmt",
                "application": "NOAA National Weather Service API",
                "format": "json"
            }

            res = requests.get(api, params=params).json()
            api_error = res.get("error")
            if api_error:
                return (
                    False,
                    {
                        "error": api_error, "upstream": res
                    })
            
            data = _get_closest_observation_tide(res, date_time)

            return (
                    True,
                    data
                )
        except Exception as e:
            return (
                False,
                {
                    "error": str(e)
                }
            )
    
    def solar():
        datenow = date_time.strftime('%Y-%m-%d')
        header ={"User-Agent": "gregorykariara1@gmail.com"}

        solar_api = f"https://api.sunrise-sunset.org/json?lat={latitude}&lng={longitude}&date={datenow}"

        res = requests.get(solar_api, headers=header).json()

        results = res["results"]
        data = {}

        for key, value in results.items():
            try:
                dt = datetime.strptime(f"{datenow} {value}", "%Y-%m-%d %I:%M:%S %p")
                formatted = dt.replace(tzinfo=timezone.utc).isoformat()

                data[key] = formatted

            except Exception:
                data[key] = value

        return (
            True,
            data
        )

    atm_cond_success, atm_cond = atmospheric()
    level_success, water_level = other("water_level")
    water_temp_success, water_temp = other("water_temperature")
    cond_success, cond = other('conductivity')
    curr_success, currents = other("currents")
    solar_success, solardata = solar()
    
    responses = {
        "atmospheric": {
            "success": atm_cond_success,
            "data": atm_cond
        },
        "water_level": {
            "success": level_success,
            "data": water_level
        },
        "water_temp": {
            "success": water_temp_success,
            'data': water_temp
        },
        "conductivity": {
            "success": cond_success,
            "data": cond
        },
        "currents": {
            "success": curr_success,
            "data": currents
        },
        "solar": {
            "success": solar_success,
            'data': solardata
        }
    }

    successful = {
        key: value["data"]
        for key, value in responses.items()
        if value["success"]
    }

    failed = {
        key: value["data"]
        for key, value in responses.items()
        if not value["success"]
    }

    all_success = all(
        value["success"]
        for value in responses.values()
    )

    return Response(
        {
            "successful": all_success,
            "successful_requests": successful,
            "failed_requests": failed
        },
        status=(
            status.HTTP_200_OK
            if all_success
            else status.HTTP_207_MULTI_STATUS
        )
    )

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

    level = _get_closest_observation_tide(water_level_res, date_time)

    return Response(
        {
            "date_time": date_time,
            "count": count,
            "station_id": station_id,
            "station_name": station.get("name"),
            "level": level
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

    last_temp = _get_closest_observation_tide(water_temp_res, date_time)

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
    begin_time = date_time - timedelta(hours=6, minutes=10)
    place_coords=(32.78, -79.93)
    station_api="https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/stations.json"
    stat_params = {
        "type": 'cond'
    }
    station_res=requests.get(station_api, params=stat_params).json()
    stations = station_res.get("stations") or []
    count, station = _closest_station(place_coords, stations)
    station_id = station["id"]

    api="https://api.tidesandcurrents.noaa.gov/api/prod/datagetter"
    params = {
        "product": 'conductivity',
        "station": station_id,
        "begin_date": begin_time.strftime("%Y%m%d %H:%M"),
        "end_date": date_time.strftime("%Y%m%d %H:%M"),
        "datum": "MLLW",
        "units": "metric",
        "time_zone": "gmt",
        "application": "NOAA National Weather Service API",
        "format": "json"
    }

    cond_res = requests.get(api, params=params).json()
    data = _get_closest_observation_tide(cond_res, date_time)

    return Response({"station": station, "res": data}, status=status.HTTP_200_OK)

@api_view(['GET'])
def fetch_currents(request):
    date_time=datetime.now(timezone.utc)
    place_coords=(32.78, -79.93)
    station_api="https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/stations.json"
    stat_params = {
        'type': 'currents'
    }
    station_res=requests.get(station_api, params=stat_params).json()
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

    data = _get_closest_observation_tide(currents_res, date_time)
    

    return Response(
        {
            "date_time": date_time,
            "count": count,
            "station_id": station_id,
            "station_name": station.get("name"),
            "currents": data
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