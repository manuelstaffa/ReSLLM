from reprompt.utils import read_file
import ast
import re

text = read_file("RePrompt/conversation.txt")
print(text)


def _extract_code_blocks(text):
    """
    Extract code blocks from a given text.

    Args:
        text (str): The input text containing code blocks.

    Returns:
        list: A list of code blocks as strings.
    """
    pattern = r"```python\n(.*?)\n```"
    return re.findall(pattern, text, re.DOTALL)


def _extract_functions(text):
    """
    Extract function definitions from a given text.

    Args:
        text (str): The input text containing function definitions.

    Returns:
        list: A list of function definitions as strings.
    """
    pattern = r"""
        (^def\s+\w+\(.*?\):           # function header line
        (?:\n[ \t]+.*?)*              # indented lines of function body (including blank lines)
        )
        (?=^def\s|\Z)                 # lookahead for next function start or end of text
    """
    matches = re.findall(pattern, text, re.MULTILINE | re.DOTALL | re.VERBOSE)
    return [m.strip("\n") for m in matches]


def extract_all_functions(text):
    """
    Extract all functions from the text and check their syntax.

    Args:
        text (str): The input text containing function definitions.

    Returns:
        list: A list of tuples with function code and syntax check result.
    """
    code_blocks = _extract_code_blocks(text)
    all_functions = []
    for block in code_blocks:
        functions = _extract_functions(block)
        for func in functions:
            all_functions.append(func)

    return all_functions


def _get_function_name(func_code):
    """
    Extract the function name from a function code string.

    Args:
        func_code (str): The Python code string of a function.

    Returns:
        str: The name of the function.
    """
    match = re.match(r"def\s+(\w+)\s*\(", func_code)
    return match.group(1) if match else None


def _check_function_syntax(code):
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


def remove_duplicate_methods(functions):
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
        func_name = _get_function_name(func)
        if func_name not in seen:
            seen.add(func_name)
            unique_functions.append(func)
    return unique_functions


functions = extract_all_functions(text)
print(f"Extracted {len(functions)} functions from code blocks.")
for func_code in functions:
    func_name = _get_function_name(func_code)
    print(f"Function: {func_name}")

deduplicated_functions = remove_duplicate_methods(functions)
print(f"After deduplication, {len(deduplicated_functions)} unique functions found.")
for func_code in deduplicated_functions:
    func_name = _get_function_name(func_code)
    print(f"Function: {func_name}")

print("\n\n")

for func_code in deduplicated_functions:
    print(f"Function '{_get_function_name(func_code)}':\n{func_code}\n")

print("\n\n")

for func_code in deduplicated_functions:
    is_valid, error = _check_function_syntax(func_code)
    if is_valid:
        print(f"Function '{_get_function_name(func_code)}' syntax is valid.")
    else:
        print(f"Function '{_get_function_name(func_code)}' has syntax error.")

for func_code in deduplicated_functions:
    try:
        ast.parse(func_code)
        print(f"Function '{_get_function_name(func_code)}' syntax is valid.")
    except SyntaxError as e:
        print(
            f"Function '{_get_function_name(func_code)}' has syntax error: {e.msg} at line {e.lineno}, column {e.offset}. for code:\n{func_code}"
        )
