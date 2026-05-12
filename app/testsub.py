from datetime import datetime, timezone, timedelta
import requests
longitude=-79.93
latitude=32.78
date_time = datetime.now(timezone.utc)
def lunar(mydatetime=date_time):
        try:
            url = "https://api.freeastroapi.com/api/v1/moon/phase"
            headers={
                "Content-Type": "application/json",
                "x-api-key": "999c66918a039208e046654609f4a56d78009d637174b348a12cfb8b3c865c8a"
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
        
success, lunar = lunar(mydatetime= date_time - timedelta(days=25))

print(lunar)