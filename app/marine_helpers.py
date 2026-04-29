import requests
from datetime import datetime, timedelta, timezone
from geopy.distance import geodesic

def _closest_station(place_coords, stations):
    closest_idx = None
    closest_km = float("inf")

    for idx, station in enumerate(stations):
        coords = (station["lat"], station["lng"])
        km = geodesic(place_coords, coords).km
        if km < closest_km:
            closest_km = km
            closest_idx = idx

    if closest_idx is None:
        return None, None

    return closest_idx, stations[closest_idx]

def _get_closest_observation(observations, target_time):
    features = observations.get("features")

    closest = None
    smallest_delta = timedelta.max  # max allowed

    for feature in features:
        props = feature.get("properties", {})
        timestamp = props.get("timestamp")
        if not timestamp:
            continue

        # Convert string → datetime
        obs_time = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))

        delta = abs(obs_time - target_time)

        # Only consider if within 10 minutes AND closer than previous
        if delta < smallest_delta:
            smallest_delta = delta
            closest = feature

    return closest

def _get_closest_observation_tide(observations, target_time):
    datas = observations.get("data")
    closest = None
    
    smallest_delta = timedelta(minutes=60)

    for data in datas:
        timestamp = data["t"]
        if not timestamp:
            continue

        obs_time = datetime.strptime(timestamp, "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc)

        delta = abs(target_time - obs_time)

        if delta < smallest_delta:
            smallest_delta = delta
            closest = data


    return ({"closest": closest, "datas": datas})

def _extract_environmental_data(observation_feature: dict) -> dict:
    """
    Extract environmental data from a weather.gov observation feature.
    
    Returns a dict with extracted atmospheric data ready for EnvironmentalData model.
    """
    if not observation_feature:
        return {}
    
    props = observation_feature.get("properties", {})
    geometry = observation_feature.get("geometry", {})
    
    def get_value(key, default=None):
        """Helper to extract numeric value from nested dict with unitCode"""
        obj = props.get(key, {})
        if isinstance(obj, dict):
            return obj.get("value", default)
        return default
    
    coords = geometry.get("coordinates", [None, None])
    cloud_cover = None
    cloud_layers = props.get("cloudLayers", [])
    if cloud_layers:
        # Approximate cloud cover from cloud layers
        amount_map = {"SKC": 100, "CLR": 0, "FEW": 25, "SCT": 50, "BKN": 75, "OVC": 100}
        cloud_cover = amount_map.get(cloud_layers[0].get("amount", ""), None)
    
    return {
        "text_description": props.get("textDescription"),
        "raw_message": props.get("rawMessage"),
        "pressure": get_value("barometricPressure"),  # in Pa
        "wind_speed": get_value("windSpeed"),  # in km/h
        "wind_direction": get_value("windDirection"),  # in degrees
        "temperature": get_value("temperature"),  # in °C
        "dewpoint": get_value("dewpoint"),  # in °C
        "relative_humidity": get_value("relativeHumidity"),  # in %
        "visibility": get_value("visibility"),  # in m
        "wind_gust": get_value("windGust"),  # in km/h
        "precipitation_last_hour": get_value("precipitationLastHour"),  # in mm
        "cloud_cover": cloud_cover,  # estimated %
        "cloud_layers": cloud_layers[0]["base"]["value"]
    }

def _fetch_weathergov_observations(latitude: float, longitude: float, date_time: datetime) -> dict:
    """
    Fetch latest observation payload from weather.gov for the given coordinates.
    Returns a dict that is safe to store in `EnvironmentalData.sources`.
    """

    header = {"User-Agent": "gregorykariara1@gmail.com"}

    noaa = f'https://api.weather.gov/points/{latitude},{longitude}'
    res = requests.get(noaa, headers=header, timeout=20).json()

    observation_stations = res["properties"]["observationStations"]
    station_res = requests.get(observation_stations, headers=header, timeout=20).json()

    features = station_res.get("features") or []
    if not features:
        raise ValueError("No weather.gov observation stations returned")

    station_id = features[0]["properties"]["stationIdentifier"]
    obs_url = f"https://api.weather.gov/stations/{station_id}/observations"
    observations = requests.get(obs_url, headers=header, timeout=20).json()

    return {
        "recorded_at_utc": date_time,
        "weather_station_id": station_id,
        "observations": observations,
    }