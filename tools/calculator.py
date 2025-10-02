from google.genai.types import FunctionDeclaration

def calculate(expression: str) -> str:
    """[USER-APPROVAL-REQUIRED]
    Evaluates a user-provided mathematical expression and returns the result as a string.

    The expression must be a valid Python-style arithmetic expression (e.g., "3 * (4 + 2)").
    If the expression cannot be evaluated, an error message is returned instead.

    Args:
        expression: A string containing the mathematical expression to evaluate.

    Returns:
        A string containing either the result of the calculation or an error message.
    """
    try:
        # A simple and unsafe way to evaluate an expression.
        # In a production app, use a safer library like `asteval` or `numexpr`.
        result = eval(expression)
        return str(result)
    except Exception as e:
        return f"Error: Unable to calculate the expression. {e}"