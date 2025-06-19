import tomlkit
import os
from typing import Any


_active_config = None


class ConfigParser:
    def __init__(self, path: str, overrides: dict | None = None) -> None:
        """
        Initialize ConfigParser, load TOML config, and apply optional overrides.

        Args:
            path (str): Path to the config TOML file.
            overrides (dict, optional): Keys and values to override config.
        """
        self.path = path
        self.config = self._load()

        if overrides:
            self._apply_overrides(overrides)

        _set_active_config(self)

    def _load(self) -> tomlkit.TOMLDocument:
        """
        Load the configuration TOML file.

        Returns:
            dict: Parsed TOML content as a tomlkit TOMLDocument.
        """
        path = self.path
        default_path = os.path.join("context", "config")

        if not path.endswith(".toml"):
            path += ".toml"

        if os.path.sep not in path:
            path = os.path.join(default_path, path)

        with open(path, "r", encoding="utf-8") as f:
            return tomlkit.parse(f.read())

    def _apply_overrides(self, overrides: dict | None) -> None:
        """
        Override config values with given dictionary.

        Args:
            overrides (dict): Keys and values to override.
        """
        if not overrides:
            return

        if not isinstance(overrides, dict):
            raise TypeError("Overrides must be a dictionary.")

        for key, value in overrides.items():
            if value is not None:
                self._set_nested(self.config, key, value)

    def _set_nested(self, dictionary: dict, key: str, value: Any) -> None:
        """
        Set a nested dictionary value using dot-separated key.

        Args:
            d (TOMLDocument or dict): Dictionary to modify.
            key (str): Dot-separated key string.
            value: Value to set.
        """
        keys = key.split(".")
        for key in keys[:-1]:
            if key not in dictionary or not isinstance(dictionary[key], dict):
                dictionary[key] = tomlkit.table()
            dictionary = dictionary[key]
        dictionary[keys[-1]] = value

    def _get_nested(self, dictionary: dict, key: str) -> Any:
        """
        Retrieve nested dictionary value by dot-separated key.

        Args:
            d (TOMLDocument or dict): Dictionary to search.
            key (str): Dot-separated key string.

        Returns:
            Value found, or raises KeyError if any key is missing.
        """
        keys = key.split(".")
        for key in keys:
            dictionary = dictionary[key]
        return dictionary

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a config value by key.

        Args:
            key (str): Key to look up, dot-separated for nested.
            default: Default value if key not found.

        Returns:
            The config value or default if key missing.
        """
        try:
            return self._get_nested(self.config, key)
        except KeyError:
            if default is not None:
                return default
            else:
                raise KeyError(f"Config key '{key}' not found and no default provided.")

    def __getitem__(self, key: str) -> Any:
        return self._get_nested(self.config, key)

    def __contains__(self, key: str) -> bool:
        try:
            self._get_nested(self.config, key)
            return True
        except KeyError:
            return False

    def __str__(self) -> str:
        return tomlkit.dumps(self.config)


def _set_active_config(config: ConfigParser) -> None:
    global _active_config
    _active_config = config


def get_active_config() -> ConfigParser:
    if _active_config is None:
        raise RuntimeError("Config not initialized. Call set_active_config() first.")
    return _active_config
