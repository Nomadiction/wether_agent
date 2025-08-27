# Берём город -> координаты -> текущая погода.

import requests

def get_weather(city: str) -> str:
    city = (city or "").strip()
    if not city:
        return "Please specify a city, for example: Berlin"

    # Геокодинг города
    geo_url = "https://geocoding-api.open-meteo.com/v1/search"
    r = requests.get(geo_url, params={"name": city, "count": 1, "language": "en", "format": "json"}, timeout=8.0)
    r.raise_for_status()
    data = r.json()
    results = data.get("results") or []
    if not results:
        return f"City not found: {city}"

    top = results[0]
    lat, lon = top["latitude"], top["longitude"]
    name, country = top.get("name", city), top.get("country", "")

    # Текущая погода
    wx_url = "https://api.open-meteo.com/v1/forecast"
    w = requests.get(
        wx_url,
        params={
            "latitude": lat,
            "longitude": lon,
            "current_weather": True,
            "hourly": "temperature_2m,relative_humidity_2m,precipitation,weathercode",
            "forecast_days": 1,
        },
        timeout=8.0,
    )
    w.raise_for_status()
    wj = w.json()
    cur = wj.get("current_weather") or {}
    t = cur.get("temperature")
    wind = cur.get("windspeed")
    code = cur.get("weathercode")
    return f"{name}, {country}: currently {t}°C, wind {wind} km/h, weather code {code}."
