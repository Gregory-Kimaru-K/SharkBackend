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
import os

def fetch_all_environmental_data(event,
                                 date_time=datetime.now(timezone.utc),
                                 latitude=32.78, longitude=-79.93):
    print(date_time)
    begin_time = date_time - timedelta(hours=6, minutes=10)
    station_api = "https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/stations.json"
    api = "https://api.tidesandcurrents.noaa.gov/api/prod/datagetter"
    
    def atmospheric(mydatetime=date_time):
        """
            Fetch observations from NOAA (weather.gov) and extract environmental data.
            Query params: latitude (default 32.78), longitude (default -79.93)
        """
        try:
            payload = _fetch_weathergov_observations(float(latitude), float(longitude), mydatetime)
            observations = payload["observations"]
            observation = _get_closest_observation(observations, mydatetime)

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
    
    def other(name, mydatetime=date_time):
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
            
            data = _get_closest_observation_tide(res, mydatetime)

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
    
    def lunar(mydatetime=date_time):
        try:
            url = "https://api.freeastroapi.com/api/v1/moon/phase"
            headers={
                "Content-Type": "application/json",
                "x-api-key": os.getenv("FREEASTROAPI")
            }

            params = {
                "date": mydatetime,
                "lat": latitude,
                "lon": longitude,
                "tz_str": "AUTO",
                "include_visuals": "false",
                "include_zodiac": "true",
                "include_rise_set": "true",
                "include_interpretation": "true",
                "include_traditional_moon": "false"
            }

            res = requests.get(url, headers=headers, params=params).json()
            return (
                True,
                res
                )
        
        except Exception as e:
            return(
                False,
                {"error": str(e)}
            )

    atm_cond_success, atm_cond = atmospheric()
    atm_1hr_success, atm_1hr_prior = atmospheric(mydatetime=date_time - timedelta(hours=1))
    atm_3hr_success, atm_3hr_prior = atmospheric(mydatetime=date_time - timedelta(hours=3))
    atm_6hr_success, atm_6hr_prior = atmospheric(mydatetime=date_time - timedelta(hours=6))



    level_success, water_level = other("water_level")
    level_1hr_success, water_level_1hr_prior = other("water_level", mydatetime=date_time - timedelta(hours=1))
    level_3hr_success, water_level_3hr_prior = other("water_level", mydatetime=date_time - timedelta(hours=3))
    level_6hr_success, water_level_6hr_prior = other("water_level", mydatetime=date_time - timedelta(hours=6))

    water_temp_success, water_temp = other("water_temperature")
    cond_success, cond = other('conductivity')
    curr_success, currents = other("currents")
    solar_success, solardata = solar()
    lunar_success, lunardata = lunar()    
    
    responses = {
        "atmospheric": {
            "success": atm_cond_success,
            "data": atm_cond
        },
        "atmospheric_1hr_prior": {
            "success": atm_1hr_success, 
            "data": atm_1hr_prior
        },
        "atmospheric_3hr_prior": {
            "success": atm_3hr_success,
            "data": atm_3hr_prior
        },

        "water_level": {
            "success": level_success,
            "data": water_level,
        },
         "water_level_1hr_prior": {
            "success": level_1hr_success,
            "data": water_level_1hr_prior
        },
        "water_level_3hr_prior": {
            "success": level_3hr_success,
            "data": water_level_3hr_prior
        },
        "water_level_6hr_prior": {
            "success": level_6hr_success, 
            "data": water_level_6hr_prior
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
        },
        "lunar": {
            "success": lunar_success,
            "data": lunardata
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
        return(
            False,
            {
                "error": "Failed to save environmental data",
                "detail": str(e)
            }
        )
    return(
        True,
        {
            "successful": all_success,
            "successful": successful,
            "failed_requests": failed
        }
    )