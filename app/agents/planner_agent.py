import json
from textwrap import dedent
from agno.agent import Agent
from agno.models.openai import OpenAIChat


class PlannerAgent(Agent):
    def __init__(self, model: OpenAIChat, tools: list):
        """
        Initializes the PlannerAgent.

        Args:
            model: The language model to use for planning.
            tools: A list of tool instances available to the planner.
                   The planner will use these to understand available actions
                   and generate appropriate tool calls in its plan.
        """
        super().__init__(
            model=model,
            instructions=dedent(
                """\
            You are a highly analytical and strategic planner agent. Your core responsibility is to break down complex user requests into a series of explicit, sequential, and executable steps.
            **REMEMBER PLACES LOCATED IN BANGLADESH**

            For each step in the plan, you must specify:
                - `step_id`: A unique integer identifier for the step.
                - `goal`: A clear, concise description of the objective for this step.
                - `tool`: The full name of the tool method to be called (e.g., "geocoding.geocode_location", "weather_tools.get_current_weather", "routing.get_route"). If no tool is needed for a step (e.g., for final synthesis), set this to `null`.
                - `args`: A dictionary of arguments for the specified tool. If a value for an argument depends on the output of a previous step, use a placeholder in the format "{previous_step_output_key.attribute}". For example, to use the latitude from a geocoding step that had `output_key: "origin_geocode"`, you would use "{origin_geocode.latitude}". If no arguments are needed, set this to `null`.
                - `output_key`: A unique string key to store the result of this step in the execution context. This allows subsequent steps to reference its output. If the step does not produce a significant output for later steps, set this to `null`.
                - `input_keys`: (Only for steps with `tool: null`) A list of `output_key`s from previous steps that this step will need as input for its synthesis.

            Important Notes:
                1. Always use the exact tool names:
                    - "geocoding.geocode_location" for geocoding
                    - "weather_tools.get_current_weather" for weather
                    - "routing.get_route" for routing
                2. Do NOT use parallel tool execution or "multi_tool_use.parallel" - all steps must be sequential.
                3. The final step should always be a synthesis step with `tool: null` that combines all gathered information.

            The final output must be a JSON array of these step objects. Do NOT include any conversational text, explanations, or markdown formatting outside the JSON block.
            Example User Request: "Give me a route plan from New York to Los Angeles and weather in New York."

            Example JSON Plan:
```json
[
    {
        "step_id": 1,
        "goal": "Get current weather for the origin city.",
        "tool": "weather_tools.get_current_weather",
        "args": {"city": "New York", "country_code": "US"},
        "output_key": "weather_report"
    },
    {
        "step_id": 2,
        "goal": "Geocode the origin address.",
        "tool": "geocoding.geocode_location",
        "args": {"location_name": "New York, NY, USA"},
        "output_key": "origin_geocode"
    },
    {
        "step_id": 3,
        "goal": "Geocode the destination address.",
        "tool": "geocoding.geocode_location",
        "args": {"location_name": "Los Angeles, CA, USA"},
        "output_key": "destination_geocode"
    },
    {
        "step_id": 4,
        "goal": "Calculate the cycling route between the geocoded coordinates.",
        "tool": "routing.get_route",
        "args": {
            "origin_latitude": "{origin_geocode.latitude}",
            "origin_longitude": "{origin_geocode.longitude}",
            "destination_latitude": "{destination_geocode.latitude}",
            "destination_longitude": "{destination_geocode.longitude}"
        },
        "output_key": "cycling_route_details"
    },
    {
        "step_id": 5,
        "goal": "Synthesize all gathered information into a comprehensive cycling plan.",
        "tool": null,
        "args": null,
        "input_keys": ["weather_report", "cycling_route_details"],
        "output_key": "final_response"
    }
]

            """
            ),
            tools=tools,  # Planner needs tool descriptions to formulate calls
            show_tool_calls=False,  # Planner's internal tool calls are not directly relevant to the user
            add_references=False,
        )

    def run_planning(self, user_query: str) -> list[dict]:
        """
        Generates a structured plan in JSON format based on the user's query.

        Args:
            user_query: The natural language request from the user.

        Returns:
            A list of dictionaries, where each dictionary represents a step in the plan.
        """
        # The base Agent's run method will execute the planning instructions
        # and return the raw string output.
        raw_plan_output = self.run(f"Plan the following task: {user_query}")
        response_content = (
            raw_plan_output.content
            if hasattr(raw_plan_output, "content")
            else str(raw_plan_output)
        )

        # Attempt to parse the raw output as JSON
        try:
            # Look for the JSON block within the response
            json_start = response_content.find("[")  # type: ignore
            json_end = response_content.rfind("]") + 1  # type: ignore
            if json_start != -1 and json_end != -1:
                json_string = response_content[json_start:json_end]  # type: ignore
                return json.loads(json_string)
            else:
                print(
                    "Warning: Could not find a valid JSON array in the planner's output."
                )
                return []
        except json.JSONDecodeError as e:
            print(f"Error parsing planner's JSON output: {e}")
            print(f"Raw output: {raw_plan_output}")
            return []
        except Exception as e:
            print(f"An unexpected error occurred during plan parsing: {e}")
            print(f"Raw output: {raw_plan_output}")
            return []
