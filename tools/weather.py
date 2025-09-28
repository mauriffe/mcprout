from google.genai.types import FunctionDeclaration

def get_current_weather(location: str) -> str:
    """Gets the current weather for a given location.

    Args:
        location: The city

    Returns:
        A string with the current weather information.
    """
    print(f"Executing tool: get_current_weather for {location}")
    return "The weather is 75°F and sunny."

get_current_weather_tool = FunctionDeclaration(
    name="get_current_weather",
    description="Get the current weather for a specified location.",
    parameters={
        "type": "OBJECT",
        "properties": {
            "location": {"type": "string", "description": "The city."},
        },
        "required": ["location"],
    },
)

TOOL_MAP = {
    "get_current_weather": get_current_weather,
}

