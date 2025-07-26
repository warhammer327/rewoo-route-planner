import requests
from agno.tools import Toolkit


class RoutingTools(Toolkit):
    def __init__(self):
        super().__init__(name="routing")
        self.base_url = "http://router.project-osrm.org/route/v1/"
        self.register(self.get_route)

    def get_route(
        self,
        origin_latitude: float,
        origin_longitude: float,
        destination_latitude: float,
        destination_longitude: float,
    ) -> str:
        """
        Calculates a route between two coordinate points using OSRM for a specified travel profile.

        Args:
            origin_latitude: Latitude of the starting point.
            origin_longitude: Longitude of the starting point.
            destination_latitude: Latitude of the ending point.
            destination_longitude: Longitude of the ending point.
            profile: The travel mode ('driving', 'cycling', 'walking'). Defaults to 'cycling'.

        Returns:
            A string describing the route, including distance, duration, and step-by-step instructions.
        """
        try:
            # OSRM API expects longitude,latitude pairs separated by semicolons
            coordinates = f"{origin_longitude},{origin_latitude};{destination_longitude},{destination_latitude}"
            url = f"{self.base_url}cycling/{coordinates}?overview=full&steps=true"

            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            if data["code"] == "Ok":
                route = data["routes"][0]
                summary = f"### Route Overview 🗺️\n"
                summary += f"- **Distance:** {route['distance'] / 1000:.2f} km\n"

                # Extract and format step-by-step instructions
                if "legs" in route and route["legs"]:
                    summary += "\n### Step-by-Step Directions:\n```\n"
                    step_number = 1
                    for leg in route["legs"]:
                        for step in leg["steps"]:
                            maneuver = step.get("maneuver", {})
                            step_type = maneuver.get("type", "unknown")
                            modifier = maneuver.get("modifier", "")
                            road_name = step.get("name", "").strip()
                            distance = step.get("distance", 0)

                            # Construct readable instruction
                            if step_type == "depart":
                                instruction = (
                                    f"Depart onto {road_name or 'an unnamed road'}"
                                )
                            elif step_type == "arrive":
                                instruction = "Arrive at your destination"
                            elif step_type == "roundabout":
                                instruction = f"Enter roundabout and take the exit onto {road_name or 'an unnamed road'}"
                            elif step_type == "end of road":
                                instruction = f"End of road {modifier.capitalize()} onto {road_name or 'an unnamed road'}"
                            elif step_type == "merge":
                                instruction = f"Merge {modifier.capitalize()} onto {road_name or 'an unnamed road'}"
                            elif step_type == "on ramp":
                                instruction = f"Take on ramp {modifier.capitalize()} onto {road_name or 'an unnamed road'}"
                            elif step_type == "off ramp":
                                instruction = f"Take off ramp {modifier.capitalize()} onto {road_name or 'an unnamed road'}"
                            else:
                                direction = (
                                    modifier.replace("_", " ").capitalize()
                                    if modifier
                                    else ""
                                )
                                instruction = f"{step_type.capitalize()} {direction} onto {road_name or 'an unnamed road'}".strip()

                            summary += f"{step_number}. {instruction} ({distance / 1000:.2f} km)\n"
                            step_number += 1
                    summary += "```\n"
                return summary

            elif data["code"] == "NoRoute":
                return "No route found between the given coordinates."

            else:
                return f"Error getting OSRM route: {data.get('code', 'Unknown error')}. Details: {data.get('message', '')}"

        except requests.exceptions.RequestException as e:
            return f"Error fetching OSRM routing data: {str(e)}"
        except KeyError as e:
            return f"Error parsing OSRM routing data: Missing field {str(e)}"
        except Exception as e:
            return f"Unexpected error in OSRM routing: {str(e)}"
