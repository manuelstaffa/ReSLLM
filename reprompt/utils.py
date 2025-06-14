import ast


def format_prompt(self, template, context):
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
    import string

    formatter = string.Formatter()
    expected_keys = {
        field_name for _, field_name, _, _ in formatter.parse(template) if field_name
    }

    missing_keys = expected_keys - context.keys()
    extra_keys = context.keys() - expected_keys

    if missing_keys:
        raise KeyError(f"Missing keys in context for template: {missing_keys}")

    if extra_keys:
        raise ValueError(f"Extra keys in context not used in template: {extra_keys}")

    return template.format(**context)


def read_file(path):
    """
    Read the content of a file.

    Returns:
        str: The content of the file.
    """
    with open(path, "r") as file:
        file_content = file.read().strip()
        return file_content


def check_function_syntax(code):
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
