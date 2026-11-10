import time
import requests

# your location (rounding to 1 decimal is plenty for weather, and keeps your exact address private)
LATITUDE = 
LONGITUDE = 

CACHE_SECONDS = 600     # reuse the last answer for 10 minutes
cache = {"data": None, "time": 0}


def look_for(code, is_day):
    # returns (icon name, short label of 7 characters or fewer)
    if code == 0:
        return ("sun" if is_day else "moon"), "CLEAR"
    if code == 1:
        return ("sun" if is_day else "moon"), "FAIR"
    if code == 2:
        return ("partly" if is_day else "partly_night"), "PT CLDY"
    if code == 3:
        return "cloud", "OVRCAST"
    if code in (45, 48):
        return "fog", "FOG"
    if code in (51, 53, 55):
        return "drizzle", "DRIZZLE"
    if code in (56, 57):
        return "ice", "FRZ DRZ"
    if code in (61, 63, 65):
        return "rain", "RAIN"
    if code in (66, 67):
        return "ice", "FRZ RN"
    if code in (71, 73, 75, 77):
        return "snow", "SNOW"
    if code in (80, 81, 82):
        return "rain", "SHOWERS"
    if code in (85, 86):
        return "snow", "SNW SHR"
    if code == 95:
        return "storm", "STORM"
    if code in (96, 99):
        return "hail", "HAIL"
    return "cloud", "CLOUDY"


def parse(reply):
    # daily values come as lists, one entry per day, and index 0 is today
    is_day = reply["current"].get("is_day", 1)      # 1 = daylight, 0 = night
    icon, label = look_for(reply["current"]["weather_code"], is_day) 
    
    return {
        "now": round(reply["current"]["temperature_2m"]),
        "high": round(reply["daily"]["temperature_2m_max"][0]),
        "low": round(reply["daily"]["temperature_2m_min"][0]),
        "icon": icon,
        "label": label,
    }


def get_weather():
    if cache["data"] and time.time() - cache["time"] < CACHE_SECONDS:
        return cache["data"]

    try:
        reply = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": LATITUDE,
                "longitude": LONGITUDE,
                "current": "temperature_2m,weather_code,is_day",
                "daily": "temperature_2m_max,temperature_2m_min",
                "temperature_unit": "fahrenheit",
                "timezone": "auto",
                "forecast_days": 1,
            },
            timeout=10,
        ).json()
        cache["data"] = parse(reply)
        cache["time"] = time.time()
        return cache["data"]
    except Exception:
        return cache["data"]     # last good answer, or None if there never was one
