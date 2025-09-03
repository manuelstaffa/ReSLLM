import string
from typing import Any, Dict
import os
import subprocess


def import_roms(rom_dir: str) -> None:
    """
    Imports ROMs from the specified directory using ale-import-roms.

    Parameters:
        rom_dir (str): Path to the directory containing ROM files.

    Raises:
        FileNotFoundError: If the ROM directory does not exist.
        ValueError: If the ROM directory is not a directory.
        RuntimeError: If importing ROMs fails.
    """
    if not os.path.exists(rom_dir):
        raise FileNotFoundError(f"ROM directory '{rom_dir}' does not exist.")

    if not os.path.isdir(rom_dir):
        raise ValueError(f"ROM directory '{rom_dir}' is not a directory.")

    try:
        subprocess.run(
            ["ale-import-roms", rom_dir],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except subprocess.CalledProcessError as e:
        raise RuntimeError(
            "Failed to import ROMs. Ensure 'ale-import-roms' is installed and the ROMs directory is correct."
        ) from e


def autorom_accept() -> None:
    """
    Accept the AutoROM license agreement by running the AutoROM command.

    Raises:
        RuntimeError: If the AutoROM command fails to execute or accept the license.
    """
    try:
        subprocess.run(
            ["AutoROM --accept-license"],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except subprocess.CalledProcessError as e:
        raise RuntimeError(
            "Failed to accept AutoROM license. Ensure 'AutoROM' is installed and the command is correct."
        ) from e


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
