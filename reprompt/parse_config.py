import json
import os

DEFAULT_CONFIG_PATH = os.path.join("context", "config")
DEFAULT_CONFIG_NAME = "default.json"


class ConfigParser:
    def __init__(self, path=DEFAULT_CONFIG_PATH, overrides=None):
        """
        Initialize ConfigParser, load JSON config, and apply optional overrides.

        Args:
            path (str): Path to the config JSON file.
            overrides (dict, optional): Keys and values to override config.
        """
        self.path = path
        self.config = self._load()
        if overrides:
            self._apply_overrides(overrides)

    def _load(self):
        """
        Load the configuration JSON file.

        Returns:
            dict: Parsed JSON content as a dictionary.
        """
        path = self.path

        if not path.endswith(".json"):
            path += ".json"

        path = os.path.join(DEFAULT_CONFIG_PATH, path)

        with open(path, "r") as f:
            return json.load(f)

    def _apply_overrides(self, overrides):
        """
        Override config values with given dictionary.

        Args:
            overrides (dict): Keys and values to override.
        """
        for key, value in overrides.items():
            if value is not None:
                self._set_nested(self.config, key, value)

    def _set_nested(self, d, key, value):
        """
        Set a nested dictionary value using dot-separated key.

        Args:
            d (dict): Dictionary to modify.
            key (str): Dot-separated key string.
            value: Value to set.
        """
        keys = key.split(".")
        for k in keys[:-1]:
            d = d.setdefault(k, {})
        d[keys[-1]] = value

    def _get_nested(self, d, key):
        """
        Retrieve nested dictionary value by dot-separated key.

        Args:
            d (dict): Dictionary to search.
            key (str): Dot-separated key string.

        Returns:
            Value found, or raises KeyError if any key is missing.
        """
        keys = key.split(".")
        for k in keys:
            d = d[k]
        return d

    def get(self, key, default=None):
        """
        Get a config value by key (supports nested keys).

        Args:
            key (str): Key to look up, dot-separated for nested.
            default: Default value if key not found.

        Returns:
            The config value or default if key missing.
        """
        try:
            return self._get_nested(self.config, key)
        except KeyError:
            return default

    def format(self, key, context=None):
        """
        Retrieve and format a string from the configuration with external variables.

        Args:
            key (str): Dot-separated key pointing to the string template in the config.
            context (dict, optional): External variables for formatting. Overrides config values with same keys.

        Returns:
            str: The formatted string with placeholders replaced by corresponding values.

        Raises:
            ValueError: If the retrieved value is not a string.
            KeyError: If required placeholders are missing in context or config.
        """
        value = self.get(key)
        if not isinstance(value, str):
            raise ValueError(
                f"Config value at '{key}' is not a string and cannot be formatted."
            )

        combined_context = dict(self.config)
        if context:
            combined_context.update(context)

        return value.format(**combined_context)

    def __getitem__(self, key):
        """
        Dict-style access to config values, supports nested keys.

        Args:
            key (str): Dot-separated key string.

        Returns:
            The config value.

        Raises:
            KeyError if key is not found.
        """
        return self._get_nested(self.config, key)

    def __contains__(self, key):
        """
        Check if a key exists in config (supports nested keys).

        Args:
            key (str): Dot-separated key string.

        Returns:
            bool: True if key exists, False otherwise.
        """
        try:
            self._get_nested(self.config, key)
            return True
        except KeyError:
            return False

    def __str__(self):
        """
        Pretty-print the config dictionary.

        Returns:
            str: JSON formatted string.
        """
        return json.dumps(self.config, indent=2)
