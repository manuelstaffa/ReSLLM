import ast
import re


def _extract_code_blocks(text: str) -> list[str]:
    """
    Extract code blocks from a given text.

    Args:
        text (str): The input text containing code blocks.

    Returns:
        list: A list of code blocks as strings.
    """
    pattern = r"```python\n(.*?)\n```"
    return re.findall(pattern, text, re.DOTALL)


def _extract_functions_from_block(text: str) -> list[str]:
    """
    Extract function definitions from a given text, including those with return annotations.

    Args:
        text (str): The input text containing function definitions.

    Returns:
        list: A list of function definitions as strings.
    """
    pattern = r"""
        (^def\s+\w+                   # 'def' and function name
        \s*\(.*?\)                    # parameters in parentheses
        \s*(?:->\s*[^\s:]+)?          # optional return annotation (e.g., '-> float')
        \s*:\s*                       # colon ending the function header
        (?:\n[ \t]+.*?)*              # indented lines of function body
        )(?=^def\s|\Z)                # lookahead for next function or end of text
    """

    matches = re.findall(pattern, text, re.MULTILINE | re.DOTALL | re.VERBOSE)

    return [m.strip("\n") for m in matches]


def get_function_name(func_code: str) -> str | None:
    """
    Extract the function name from a function code string.

    Args:
        func_code (str): The Python code string of a function.

    Returns:
        str: The name of the function.
    """
    match = re.match(r"def\s+(\w+)\s*\(", func_code)

    return match.group(1) if match else None


def extract_functions(text: str) -> list[str]:
    """
    Extract all functions from the text and check their syntax.

    Args:
        text (str): The input text containing function definitions.

    Returns:
        list: A list of strings with function code.
    """
    code_blocks = _extract_code_blocks(text)
    all_functions = []
    for block in code_blocks:
        functions = _extract_functions_from_block(block)
        for func in functions:
            all_functions.append(func)

    return all_functions


def remove_duplicate_functions(functions: list[str]) -> list[str]:
    """
    Remove duplicate function definitions from a list of functions.

    Args:
        functions (list): List of function code strings.

    Returns:
        list: List with duplicate functions removed.
    """
    seen = set()
    unique_functions = []
    for func in functions:
        func_name = get_function_name(func)
        if func_name not in seen:
            seen.add(func_name)
            unique_functions.append(func)

    return unique_functions


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
        return False, str(e)


def replace_function(functions: list[str], new_function: str) -> list[str]:
    """
    Replace a function with the same name in a list of functions.
    If the function name does not exist in the list, add the new function.

    Args:
        functions (list[str]): List of function code strings.
        new_function (str): The new function code to replace or add.

    Returns:
        list[str]: Updated list of function code strings.
    """
    new_func_name = get_function_name(new_function)
    if new_func_name is None:
        raise ValueError("Provided code does not contain a valid function definition.")

    updated_functions = []
    replaced = False

    for func in functions:
        func_name = get_function_name(func)
        if func_name == new_func_name:
            updated_functions.append(new_function)
            replaced = True
        else:
            updated_functions.append(func)

    if not replaced:
        updated_functions.append(new_function)

    return updated_functions
