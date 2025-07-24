import os
import requests
from typing import Optional
from agno.tools import Toolkit


class WeatherTools(Toolkit):
    def __init__(self, api_key: str):
        super().__init__(name="weather_tools")
        self.api_key = api_key
        self.base_url = "https://api.openweathermap.org/data/2.5"

        self.register(self.get_current_weather)

    def get_current_weather(self, city: str, country_code: Optional[str] = None) -> str:
        """
        Get current weather information for a city.

        Args:
            city: Name of the city
            country_code: Optional 2-letter country code (e.g., 'BD' for Bangladesh)

        Returns:
            Current weather information as a string
        """
        try:
            # Build location string
            location = city
            if country_code:
                location = f"{city},{country_code}"

            # Make API request
            url = f"{self.base_url}/weather"
            params = {
                "q": location,
                "appid": self.api_key,
                "units": "metric",  # Use Celsius
            }

            response = requests.get(url, params=params)
            response.raise_for_status()

            data = response.json()

            # Format the weather information
            weather_info = {
                "city": data["name"],
                "country": data["sys"]["country"],
                "temperature": data["main"]["temp"],
                "feels_like": data["main"]["feels_like"],
                "humidity": data["main"]["humidity"],
                "pressure": data["main"]["pressure"],
                "description": data["weather"][0]["description"].title(),
                "wind_speed": data["wind"]["speed"],
                "visibility": data.get("visibility", "N/A"),
            }

            return (
                f"Current weather in {weather_info['city']}, {weather_info['country']}:\n"
                f"🌡️ Temperature: {weather_info['temperature']}°C (feels like {weather_info['feels_like']}°C)\n"
                f"☁️ Conditions: {weather_info['description']}\n"
                f"💧 Humidity: {weather_info['humidity']}%\n"
                f"🌬️ Wind Speed: {weather_info['wind_speed']} m/s\n"
                f"📊 Pressure: {weather_info['pressure']} hPa\n"
                f"👁️ Visibility: {weather_info['visibility']} meters"
            )

        except requests.exceptions.RequestException as e:
            return f"Error fetching weather data: {str(e)}"
        except KeyError as e:
            return f"Error parsing weather data: Missing field {str(e)}"
        except Exception as e:
            return f"Unexpected error: {str(e)}"
