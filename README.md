# 🗺️ Route Planner

A route planning system that combines geocoding, weather data, and routing services to provide comprehensive route recommendations with real-time weather conditions.

## ✨ Features

- **Route Planning**: Calculates optimal routes between any two locations
- **Weather Integration**: Provides current weather conditions and recommendations
- **Geocoding Support**: Converts location names to precise coordinates
- **Step-by-Step Directions**: Detailed turn-by-turn navigation instructions
- **Multi-Agent Architecture**: Separate planning and execution agents

## 🏗️ Architecture: ReWoo

### 1. **Planner Agent** (`agents/planner_agent.py`)

- Analyzes user queries and breaks them into executable steps
- Creates structured JSON plans with sequential tool calls

### 2. **Executive Agent** (`agents/executive_agent.py`)

- Executes the generated plan steps
- Synthesizes information from multiple tools
- Formats the final user-friendly response

### 3. **Custom Tools** (`custom_tools/`)

- **Geocoding Tool**: Converts addresses to coordinates
- **Weather Tool**: Fetches current weather data
- **Routing Tool**: Calculates routes between points

## 📋 Prerequisites

- Python 3.8+
- OpenAI API key
- Tavily API key
- OpenWeatherMap API key

## 🛠️ Dependencies

- `agno` - Agent framework
- `openai` - OpenAI API client
- `python-dotenv` - Environment variable management
- `requests` - HTTP requests for APIs

## 🚀 Installation

1. **Clone the repository**

```bash
git clone <repository-url>
cd route-planner
```

2. **Install dependencies**

```bash
pip install -r requirements.txt
```

3. **Set up environment variables**
Create a `.env` file:

```env
OPENAI_API_KEY=your_openai_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
OPEN_WEATHER_KEY=your_openweather_api_key_here
```

## 📁 Project Structure

```
route-planner/
├── app
│   ├── agents
│   │   ├── executive_agent.py
│   │   ├── **init**.py
│   │   └── planner_agent.py
│   └── custom_tools
│       ├── geocoding.py
│       ├── **init**.py
│       ├── routing.py
│       └── weather.py
├── main.py
├── README.md
└── requirements.txt
```



```

## 🎯 Usage

Run the main script:
```bash
python main.py
```

Modify the `user_query` variable in `main.py` for custom routes:

```python
user_query = "Give me a route plan from [START] to [END] and weather condition"
```

## 🖥️ Sample Output

```
🚴‍♂️ CYCLING ROUTE PLANNER
================================================================================
📍 Query: Give me a route plan from savar,dhaka to dhanmondi,dhaka and weather condition on along the route
⏳ Generating plan...
✅ Plan generated with 6 steps

🔄 EXECUTING PLAN...
--------------------------------------------------------------------------------
📋 Step 1/6: Geocode the origin address in Savar, Dhaka.
   🔧 Calling: geocoding.geocode_location
   ✅ Completed and stored in context
📋 Step 2/6: Geocode the destination address in Dhanmondi, Dhaka.
   🔧 Calling: geocoding.geocode_location
   ✅ Completed and stored in context
📋 Step 3/6: Calculate the route between Savar and Dhanmondi using the geocoded coordinates.
   🔧 Calling: routing.get_route
   ✅ Completed and stored in context
📋 Step 4/6: Get the current weather conditions for Savar, Dhaka.
   🔧 Calling: weather_tools.get_current_weather
   ✅ Completed and stored in context
📋 Step 5/6: Get the current weather conditions for Dhanmondi, Dhaka.
   🔧 Calling: weather_tools.get_current_weather
   ✅ Completed and stored in context
📋 Step 6/6: Synthesize all gathered data into a comprehensive route and weather plan.
   📝 Synthesis step - preparing for final response

🎯 GENERATING FINAL RESPONSE...
--------------------------------------------------------------------------------

================================================================================
  🚴‍♂️ Cycling Route from Savar to Dhanmondi
================================================================================

------------------------------------------------------------
  Route Overview 🗺️
------------------------------------------------------------
  • Distance: 20.60 km
  Step-by-Step Directions:
  1. Depart onto Rajason-Birulia Road (0.11 km)
  2. Turn Left onto Dhaka - Aricha Mahasarak (0.54 km)
  3. Continue Straight onto Dhaka - Aricha Mahasarak (2.75 km)
  4. Continue Straight onto Dhaka - Aricha Mahasarak (2.97 km)
  5. Continue Straight onto Dhaka-Aricha Mahasarak (5.70 km)
  6. Continue Straight onto Dhaka - Aricha Mahasarak (1.43 km)
  7. Continue Straight onto Aminbazar Bridge (0.36 km)
  8. Fork Slight left onto an unnamed road (0.14 km)
  9. Turn Straight onto an unnamed road (0.44 km)
  10. End of road Right onto an unnamed road (0.04 km)
  11. Fork Slight left onto Bedebad Sadak (3.62 km)
  12. Turn Left onto Mohammadpur Bedibandh Sangog Sadak (0.52 km)
  13. Turn Right onto Satmasjid Road (1.62 km)
  14. Turn Left onto Road-10A (0.22 km)
  15. Continue Straight onto Road 10A (0.15 km)
  16. Arrive at your destination (0.00 km)

------------------------------------------------------------
  Weather Conditions ☁️
------------------------------------------------------------
  Current weather in Savar, BD:
  • 🌡️ Temperature: 31.48°C (Feels like 38.48°C)
  • ☁️ Conditions: Overcast Clouds
  • 💧 Humidity: 71%
  • 🌬️ Wind Speed: 2.14 m/s
  • 📊 Pressure: 991 hPa
  • 👁️ Visibility: 10000 meters

------------------------------------------------------------
  Recommendations and Tips 💡
------------------------------------------------------------
  • Hydration: It's quite warm today, so make sure to stay hydrated
  • Clothing: The high humidity could make it feel hotter, so wear breathable clothing
  • Protection: Although it's overcast, applying sunscreen is wise
  • Travel Time: Check for traffic updates, especially near major junctions
  • Plan for Stops: The route takes you along Dhaka-Aricha Mahasarak with various shops

================================================================================
🎉 Route planning completed! Have a safe ride! 🚴‍♀️
================================================================================
```

### API Keys Setup

1. **OpenAI API Key**: Get from [OpenAI Platform](https://platform.openai.com/)
2. **Tavily API Key**: Get from [Tavily](https://tavily.com/)
3. **OpenWeatherMap API Key**: Get from [OpenWeatherMap](https://openweathermap.org/api)

## 📄 License

This project is licensed under the MIT License.
