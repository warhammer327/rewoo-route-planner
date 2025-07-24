import requests
from agno.tools import Toolkit


class GeocodingTools(Toolkit):
    def __init__(self):
        super().__init__(name="geocoding")
        self.nominatim_url = "https://nominatim.openstreetmap.org/search"
        self.register(self.geocode_location)

    def geocode_location(self, location_name: str, country_code: str = "bd") -> dict:
        """
        Geocodes a location name to its latitude and longitude using OpenStreetMap Nominatim.

        Args:
            location_name: The name of the location (e.g., "Gulshan 1, Dhaka").
            country_code: Optional 2-letter country code (e.g., 'bd' for Bangladesh) to bias results.
                          This helps ensure results are for Dhaka, not a similarly named place elsewhere.

        Returns:
            A dictionary with 'latitude', 'longitude', and 'display_name', or an empty dict if not found.
            'display_name' is useful for the agent to confirm the location found.
        """
        try:
            params = {
                "q": location_name,
                "format": "json",  # Request JSON output
                "limit": 1,  # We typically only need the top result
                "countrycodes": country_code,  # Filter results by country
            }
            headers = {
                # Nominatim requires a User-Agent header that identifies your application.
                # Replace 'your_email@example.com' with your actual email or a descriptive contact.
                "User-Agent": "AgnoRoutePlanner/1.0 (jbc.syedrizwan@gmail.com)",
                "Accept-Language": "en",
            }

            response = requests.get(self.nominatim_url, params=params, headers=headers)
            response.raise_for_status()  # Raises an HTTPError for bad responses (4xx or 5xx)
            data = response.json()

            if data:
                # If a result is found, extract latitude, longitude, and display name.
                return {
                    "latitude": float(data[0]["lat"]),
                    "longitude": float(data[0]["lon"]),
                    "display_name": data[0]["display_name"],
                }
            return {}  # Return an empty dictionary if no location is found
        except requests.exceptions.RequestException as e:
            # Handle network-related errors (e.g., connection refused, timeout)
            print(f"Error geocoding: {e}")
            return {}
        except Exception as e:
            # Catch any other unexpected errors
            print(f"Unexpected error in geocoding: {e}")
            return {}
