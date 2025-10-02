from google.genai.types import FunctionDeclaration

def get_current_weather(location: str) -> str:
    """Retrieves the current weather for a specified location.

    Args:
        location: The name of the city or location for which to fetch weather information.

    Returns:
        A string describing the current weather conditions (e.g., temperature and sky status).
    """
    print(f"Executing tool: get_current_weather for {location}")
    return "The weather is 75°F and sunny."
