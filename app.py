from flask import Flask, render_template, request, jsonify
from urllib.request import urlopen
from urllib.parse import urlencode
import json

app = Flask(__name__)


def get_weather_description(code):
    descriptions = {
        0: "Clear sky",
        1: "Mainly clear",
        2: "Partly cloudy",
        3: "Overcast",
        45: "Fog",
        48: "Freezing fog",
        51: "Light drizzle",
        53: "Moderate drizzle",
        55: "Heavy drizzle",
        61: "Light rain",
        63: "Moderate rain",
        65: "Heavy rain",
        71: "Light snow",
        73: "Moderate snow",
        75: "Heavy snow",
        80: "Rain showers",
        81: "Moderate rain showers",
        82: "Heavy rain showers",
        95: "Thunderstorm",
        96: "Thunderstorm with hail",
        99: "Heavy thunderstorm with hail"
    }
    return descriptions.get(code, "Weather information unavailable")


def fetch_json(url):
    with urlopen(url, timeout=10) as response:
        return json.loads(response.read().decode("utf-8"))


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/weather")
def weather():
    city = request.args.get("city", "").strip()

    if not city:
        return jsonify({"error": "Please enter a city name."}), 400

    try:
        geo_url = "https://geocoding-api.open-meteo.com/v1/search?" + urlencode({
            "name": city,
            "count": 1,
            "language": "en",
            "format": "json"
        })

        geo_data = fetch_json(geo_url)
        places = geo_data.get("results", [])

        if not places:
            return jsonify({"error": "City not found. Try another name."}), 404

        place = places[0]
        latitude = place["latitude"]
        longitude = place["longitude"]

        forecast_url = "https://api.open-meteo.com/v1/forecast?" + urlencode({
            "latitude": latitude,
            "longitude": longitude,
            "current": (
                "temperature_2m,relative_humidity_2m,"
                "apparent_temperature,is_day,precipitation,"
                "weather_code,wind_speed_10m"
            ),
            "timezone": "auto"
        })

        forecast_data = fetch_json(forecast_url)
        current = forecast_data["current"]

        result = {
            "city": place["name"],
            "country": place.get("country", ""),
            "temperature": current["temperature_2m"],
            "feels_like": current["apparent_temperature"],
            "humidity": current["relative_humidity_2m"],
            "wind": current["wind_speed_10m"],
            "description": get_weather_description(current["weather_code"]),
            "is_day": current["is_day"],
            "updated": current["time"].replace("T", " ")
        }

        return jsonify(result)

    except Exception:
        return jsonify({
            "error": "Could not get weather data. Check your internet and try again."
        }), 502


if __name__ == "__main__":
    app.run(debug=True)
