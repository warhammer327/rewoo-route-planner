from textwrap import dedent
from agno.agent import Agent
from agno.models.openai import OpenAIChat


class ExecutiveAgent(Agent):
    def __init__(self, model: OpenAIChat, tools: list):
        """
        Initializes the ExecutiveAgent.

        Args:
            model: The language model to use for synthesis.
            tools: A list of tool instances that this agent can call during execution.
        """
        super().__init__(
            model=model,
            instructions=dedent(
                """\
            You are a smart and helpful cycling assistant 🚴‍♂️. Your goal is to help users plan optimal cycling routes.
            You have received a plan and executed its steps, gathering various pieces of information. Now, your task is to synthesize all the gathered information into a comprehensive, user-friendly response.

            The information you need to synthesize will be provided to you. Your final response should follow this structure:

            -   **Title with emojis and short summary of the route** (e.g., "🚴‍♂️ Your Cycling Route from A to B!")
            -   **Section: Route Overview 🗺️** (Detailed information about distance, duration, and major roads from the routing tool output.)
            -   **Section: Step-by-Step Directions:** (A full detailed list of step-by-step directions from the routing tool output.)
            -   **Section: Weather Conditions ☁️** (Current weather information for the start location from the weather tool output.)
            -   **Section: Recommendations and Tips 💡** (Practical advice based on the weather conditions and route details, e.g., "Wear a raincoat," "Strong headwinds," "Perfect weather for cycling!"). Also include any noteworthy stops or areas of interest along the way if applicable (though this might require an additional tool or more complex reasoning not currently in your toolset).

            Keep your tone friendly, concise, and helpful. Aim to empower the user to enjoy a safe and efficient ride!
            """
            ),
            markdown=True,
            tools=tools,  # Executive Agent needs access to tools to execute them
            show_tool_calls=True,
            add_references=True,
        )

    def synthesize_response(self, context: dict) -> str:
        """
        Synthesizes the final response based on the gathered context.

        Args:
            context: A dictionary containing all the outputs from the executed plan steps.

        Returns:
            A string representing the final, formatted response to the user.
        """
        # Construct a prompt for the Executive Agent using the context
        # We'll pass the relevant parts of the context to the executive agent for synthesis.
        # Ensure the keys here match the 'output_key' values used by the PlannerAgent.
        synthesis_prompt = dedent(
            f"""\
        Here is the information gathered from executing the plan:

        --- Weather Report ---
        {context.get("weather_report", "Weather information not available.")}

        --- Route Details ---
        {context.get("cycling_route_details", "Route information not available.")}

        --- Geocoding Information ---
        Origin Geocode: {context.get("origin_geocode", "Not available.")}
        Destination Geocode: {context.get("destination_geocode", "Not available.")}

        Please synthesize this information into a comprehensive cycling route plan, following the specified output format and including weather-based recommendations.
        """
        )
        return self.run(synthesis_prompt)  # type: ignore
