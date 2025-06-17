import ast
import string
from typing import Any, Dict


def format_string(template: str, context: Dict[str, Any]) -> str:
    """
    Format a template string by replacing placeholders with context values.

    Args:
        template (str): Template string containing `{placeholders}`.
        context (dict): Dictionary with values for placeholders.

    Returns:
        str: Formatted string with placeholders replaced.

    Raises:
        KeyError: If any placeholders in the template are missing in the context.
        ValueError: If there are unused keys in the context.
    """
    formatter = string.Formatter()
    expected_keys = {
        field_name for _, field_name, _, _ in formatter.parse(template) if field_name
    }

    missing_keys = expected_keys - context.keys()

    if missing_keys:
        raise KeyError(f"Missing keys in context for template: {missing_keys}")

    return template.format(**context)


def read_file(path: str, default: Any = None) -> str:
    """
    Read the content of a file.

    Args:
        path (str): Path to the file to read.
        default (Any, optional): Default value to return if the file is not found.

    Returns:
        str: The content of the file.

    Raises:
        FileNotFoundError: If the file does not exist and no default is provided.
    """
    try:
        with open(path, "r") as file:
            file_content = file.read().strip()
            return file_content
    except FileNotFoundError:
        if default is not None:
            return default
        else:
            raise FileNotFoundError(f"File not found: {path}")


def check_function_syntax(code: str) -> tuple[bool, str | None]:
    """
    Check syntax of a single Python function string.

    Args:
        code (str): The Python code string of a function to check.

    Returns:
        tuple: (bool, str or None)
            - True, None if syntax is valid.
            - False, error message string if syntax error found.
    """
    try:
        ast.parse(code)
        return True, None
    except SyntaxError as e:
        error_message = f"{type(e).__name__}: {e.msg} (line {e.lineno})"
        return False, error_message
