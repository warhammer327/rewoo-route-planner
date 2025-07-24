import os
import re
from textwrap import dedent
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.tavily import TavilyTools
from custom_tools.weather import WeatherTools
from custom_tools.geocoding import GeocodingTools
from custom_tools.routing import RoutingTools

from agents.planner_agent import PlannerAgent
from agents.executive_agent import ExecutiveAgent

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
tavily_api_key = os.getenv("TAVILY_API_KEY")
open_weather_api_key = os.getenv("OPEN_WEATHER_KEY")

if not openai_api_key:
    raise ValueError(
        "OPENAI_API_KEY not found in environment variables. Please check your .env file."
    )

if not tavily_api_key:
    raise ValueError(
        "TAVILY_API_KEY not found in environment variables. Please check your .env file."
    )

if not open_weather_api_key:
    raise ValueError(
        "OPEN_WEATHER_KEY not found in environment variables. Please check your .env file."
    )

tavily_tools = TavilyTools(api_key=tavily_api_key)
weather_tools = WeatherTools(api_key=open_weather_api_key)
routing_tools = RoutingTools()
geocoding_tools = GeocodingTools()


def format_terminal_output(response):
    """
    Format the response content for better terminal readability
    """
    # Extract content from the response object
    content = response.content if hasattr(response, "content") else str(response)

    # Remove markdown formatting for terminal
    content = content.replace("# ", "")
    content = content.replace("## ", "\n")
    content = content.replace("### ", "\n  ")
    content = content.replace("**", "")
    content = content.replace("```", "")
    content = content.replace("- ", "  • ")

    # Add nice dividers
    lines = content.split("\n")
    formatted_lines = []

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Main headers (originally #)
        if "🚴‍♂️" in line or "Your Cycling Route" in line:
            formatted_lines.append("=" * 80)
            formatted_lines.append(f"  {line}")
            formatted_lines.append("=" * 80)

        # Section headers (originally ##)
        elif any(emoji in line for emoji in ["🗺️", "☁️", "💡"]) and ":" not in line:
            formatted_lines.append("\n" + "-" * 60)
            formatted_lines.append(f"  {line}")
            formatted_lines.append("-" * 60)

        # Regular content
        else:
            formatted_lines.append(f"  {line}")

    return "\n".join(formatted_lines)


executive_agent = Agent(
    model=OpenAIChat(id="gpt-3.5-turbo", api_key=openai_api_key),
    instructions=dedent(
        """\
    You are a smart and helpful cycling route planner.

    Your goal is to help users plan optimal cycling routes based on:
    - User-provided start and destination addresses
    - Geocoding and routing tools available to you
    - Today's weather conditions
    - Practical travel and safety considerations

    How you should operate:
    1. Always use the weather tool to fetch the current day's weather at the start location.
    2. Use the geocoding tool to convert location names or addresses into latitude and longitude.
    3. Use the routing tool to find a cycling-friendly route between the coordinates. **Ensure you explicitly set the 'profile' parameter to 'cycling' when using the routing tool.**
    4. Factor in weather conditions (e.g., rain, wind, heat) to advise if cycling is safe or suggest alternatives.
    5. Provide the user with:
        - Full details of the route (distance, major roads/landmarks)
        - A full detailed list of step-by-step directions from the routing tool, **use english names for bangla font**
        - Practical tips based on the weather (e.g., "Wear a raincoat", "Strong headwinds", "Perfect weather for cycling!")


    Your response format:
    - Title with emojis and short summary of the route
    - Section: Route Overview 🗺️
    - Section: Weather Conditions ☁️
    - Section: Recommendations and Tips 💡

    Keep your tone friendly, concise, and helpful. Aim to empower the user to enjoy a safe and efficient ride!
    """
    ),
    tools=[tavily_tools, weather_tools, geocoding_tools, routing_tools],
    show_tool_calls=True,
    add_references=True,
)

if __name__ == "__main__":
    try:
        tool_instances = {
            "geocoding": geocoding_tools,  # This matches "geocoding.geocode_location"
            "weather_tools": weather_tools,  # This matches "weather_tools.get_current_weather"
            "routing": routing_tools,  # This matches "routing.get_route"
        }

        user_query = "Give me a route plan from savar,dhaka to dhanmondi,dhaka and weather condition on along the route"
        planner_model = OpenAIChat(id="gpt-4o", api_key=openai_api_key)
        planner_agent = PlannerAgent(
            model=planner_model, tools=[geocoding_tools, weather_tools, routing_tools]
        )

        print("🚴‍♂️ CYCLING ROUTE PLANNER")
        print("=" * 80)
        print(f"📍 Query: {user_query}")
        print("⏳ Generating plan...")

        plan_steps = planner_agent.run_planning(user_query)

        if not plan_steps:
            print("❌ Failed to generate a valid plan. Exiting.")
            exit()

        print(f"✅ Plan generated with {len(plan_steps)} steps")

        executive_model = OpenAIChat(id="gpt-4o", api_key=openai_api_key)
        executive_agent = ExecutiveAgent(
            model=executive_model, tools=list(tool_instances.values())
        )

        execution_context = {}
        print("\n🔄 EXECUTING PLAN...")
        print("-" * 80)

        for i, step in enumerate(plan_steps, 1):
            step_id = step.get("step_id", "N/A")
            goal = step.get("goal", "No Goal Defined")
            tool_call = step.get("tool")
            args = step.get("args")
            output_key = step.get("output_key")

            print(f"📋 Step {i}/{len(plan_steps)}: {goal}")

            if tool_call:
                try:
                    # Parse tool_call (e.g., "geocoding.geocode_location")
                    tool_instance_name, method_name = tool_call.split(".")
                    tool_instance = tool_instances.get(tool_instance_name)

                    if not tool_instance:
                        print(f"   ❌ Tool instance '{tool_instance_name}' not found")
                        continue

                    method = getattr(tool_instance, method_name)

                    # Resolve arguments with placeholders from execution_context
                    resolved_args = {}
                    if args:
                        for arg_key, arg_value in args.items():
                            if isinstance(arg_value, str) and re.match(
                                r"\{.+\..+\}", arg_value
                            ):
                                # This is a placeholder, e.g., "{origin_geocode.latitude}"
                                parts = arg_value.strip("{}").split(".")
                                if len(parts) == 2:
                                    context_key, attribute = parts
                                    if context_key in execution_context and isinstance(
                                        execution_context[context_key], dict
                                    ):
                                        resolved_args[arg_key] = execution_context[
                                            context_key
                                        ].get(attribute)
                                    else:
                                        print(
                                            f"   ⚠️  Could not resolve placeholder '{arg_value}'"
                                        )
                                        resolved_args[arg_key] = None
                                else:
                                    print(
                                        f"   ⚠️  Invalid placeholder format '{arg_value}'"
                                    )
                                    resolved_args[arg_key] = arg_value
                            else:
                                resolved_args[arg_key] = arg_value

                    # Filter out args that are None after resolution
                    final_tool_args = {
                        k: v for k, v in resolved_args.items() if v is not None
                    }

                    print(f"   🔧 Calling: {tool_call}")
                    step_result = method(**final_tool_args)

                    if output_key:
                        execution_context[output_key] = step_result
                        print("   ✅ Completed and stored in context")
                    else:
                        print("   ✅ Completed")

                except AttributeError:
                    print(
                        f"   ❌ Method '{method_name}' not found in tool '{tool_instance_name}'"  # type: ignore
                    )
                except Exception as e:
                    print(f"   ❌ Error: {e}")
            else:
                print("   📝 Synthesis step - preparing for final response")
                if "input_keys" in step and step["input_keys"] and output_key:
                    execution_context[output_key] = "Ready for synthesis."

        print("\n🎯 GENERATING FINAL RESPONSE...")
        print("-" * 80)

        # Generate the final response using the Executive Agent
        final_response = executive_agent.synthesize_response(execution_context)

        print("\n")
        print(format_terminal_output(final_response))
        print("\n" + "=" * 80)
        print("🎉 Route planning completed! Have a safe ride! 🚴‍♀️")
        print("=" * 80)

    except Exception as e:
        print(f"❌ Error running agent: {e}")
        print(
            "💡 Make sure your OpenAI API key is valid and you have sufficient credits."
        )
