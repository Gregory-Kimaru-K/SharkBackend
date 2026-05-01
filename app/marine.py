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
    date_time = request.data.get("date_time", datetime.now(timezone.utc))
    print(date_time)
    latitude = request.data.get("latitude", 32.78)
    longitude = request.data.get("longitude", -79.93)
    event = request.data.get("event")
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
        try:
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
        
        except Exception as e:
            return(
                False,
                {
                    "error": str(e)
                }
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

    try:
        EnvironmentalData.objects.create(

            event=event,

            sources={
                "atmospheric": "NOAA National Weather Service API",
                "marine": "NOAA Tides and Currents API",
                "solar": "Sunrise Sunset API"
            },

            recorded_at_utc=date_time,

            # Atmospheric
            atmospheric_text=successful.get(
                "atmospheric", {}
            ).get("text_description"),

            raw_message=successful.get(
                "atmospheric", {}
            ).get("raw_message"),

            pressure=successful.get(
                "atmospheric", {}
            ).get("pressure"),

            wind_speed=successful.get(
                "atmospheric", {}
            ).get("wind_speed"),

            wind_direction=successful.get(
                "atmospheric", {}
            ).get("wind_direction"),

            temperature=successful.get(
                "atmospheric", {}
            ).get("temperature"),

            dewpoint=successful.get(
                "atmospheric", {}
            ).get("dewpoint"),

            relative_humidity=successful.get(
                "atmospheric", {}
            ).get("relative_humidity"),

            visibility=successful.get(
                "atmospheric", {}
            ).get("visibility"),

            wind_gust=successful.get(
                "atmospheric", {}
            ).get("wind_gust"),

            precipitation_last_hour=successful.get(
                "atmospheric", {}
            ).get("precipitation_last_hour"),

            cloud_cover=successful.get(
                "atmospheric", {}
            ).get("cloud_cover"),

            cloud_layers=successful.get(
                "atmospheric", {}
            ).get("cloud_layers"),


            # Tide
            tide_height=successful.get(
                "water_level", {}
            ).get("v"),

            tide_standard_deviation=successful.get(
                "water_level", {}
            ).get("s"),

            tide_flags=successful.get(
                "water_level", {}
            ).get("f"),

            tide_quality_indicator=successful.get(
                "water_level", {}
            ).get("q"),


            # Water temperature
            water_temperature=successful.get(
                "water_temp", {}
            ).get("v"),

            water_temperature_flags=successful.get(
                "water_temp", {}
            ).get("f"),


            # Conductivity
            conductivity=successful.get(
                "conductivity", {}
            ).get("v"),

            conductivity_flags=successful.get(
                "conductivity", {}
            ).get("f"),


            # Currents
            current_speed=successful.get(
                "currents", {}
            ).get("s"),

            current_direction=successful.get(
                "currents", {}
            ).get("d"),

            current_bin_Number=successful.get(
                "currents", {}
            ).get("b"),


            # Solar
            sunrise=successful.get(
                "solar", {}
            ).get("sunrise"),

            sunset=successful.get(
                "solar", {}
            ).get("sunset"),

            solar_noon=successful.get(
                "solar", {}
            ).get("solar_noon"),

            civil_twilight_begin=successful.get(
                "solar", {}
            ).get("civil_twilight_begin"),

            civil_twilight_end=successful.get(
                "solar", {}
            ).get("civil_twilight_end"),

            nautical_twilight_begin=successful.get(
                "solar", {}
            ).get("nautical_twilight_begin"),

            nautical_twilight_end=successful.get(
                "solar", {}
            ).get("nautical_twilight_end"),

            astronomical_twilight_begin=successful.get(
                "solar", {}
            ).get("astronomical_twilight_begin"),

            astronomical_twilight_end=successful.get(
                "solar", {}
            ).get("astronomical_twilight_end"),

            day_length=successful.get(
                "solar", {}
            ).get("day_length"),
        )

    except Exception as e:
        return Response(
            {
                "error": "Failed to save environmental data",
                "detail": str(e)
            },
            status=status.HTTP_501_NOT_IMPLEMENTED
        )
    return Response(
        {
            "successful": all_success,
            "successful": successful,
            "failed_requests": failed
        },
        status=(
            status.HTTP_201_CREATED
            if all_success
            else status.HTTP_207_MULTI_STATUS
        )
    )