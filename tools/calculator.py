from google.genai.types import FunctionDeclaration

def calculate(expression: str) -> str:
    """Calculates the result of a mathematical expression.

    Args:
        expression: A string containing the mathematical expression.

    Returns:
        The result of the calculation as a string.
    """
    try:
        # A simple and unsafe way to evaluate an expression.
        # In a production app, use a safer library like `asteval` or `numexpr`.
        result = eval(expression)
        return str(result)
    except Exception as e:
        return f"Error: Unable to calculate the expression. {e}"

calculate_tool = FunctionDeclaration(
    name="calculate",
    description="[USER-APPROVAL-REQUIRED] Performs a mathematical calculation.",
    parameters={
        "type": "OBJECT",
        "properties": {
            "expression": {"type": "string", "description": "The mathematical expression to evaluate."},
        },
        "required": ["expression"]
    }
)

TOOL_MAP = {
    "calculate": calculate,
}