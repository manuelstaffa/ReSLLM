import json
import os

DEFAULT_CONFIG_PATH = os.path.join("RePrompt", "context", "config", "default.json")


class ConfigParser:
    """
    Loads and manages configuration settings from a JSON file, with support for overrides
    and formatted string substitution using external context variables.
    """

    def __init__(self, path=None, overrides=None):
        """
        Initialize the ConfigParser.

        Args:
            path (str, optional): Path to the JSON config file. If None, uses DEFAULT_CONFIG_PATH.
            overrides (dict, optional): Dictionary of key-value pairs to override values in the loaded config.
        """
        self.path = path or DEFAULT_CONFIG_PATH
        self.config = self._load()
        if overrides:
            self._apply_overrides(overrides)

    def _load(self):
        """
        Load the configuration JSON file.

        Returns:
            dict: Parsed JSON content as a dictionary.
        """
        with open(self.path, "r") as f:
            return json.load(f)

    def _apply_overrides(self, overrides):
        """
        Apply override values to the loaded configuration.

        Args:
            overrides (dict): Key-value pairs to override in the configuration.
        """
        for key, value in overrides.items():
            if value is not None:
                self.config[key] = value

    def get(self, key, default=None):
        """
        Retrieve a configuration value by key, supporting dot-separated nested keys.

        Args:
            key (str): Dot-separated key to retrieve (e.g., "api.model").
            default (any, optional): Value to return if the key does not exist.

        Returns:
            any: The corresponding value or the provided default.
        """
        keys = key.split(".")
        value = self.config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value

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

        combined_context = dict(self.config)  # Start with config values
        if context:
            combined_context.update(context)  # External context takes precedence

        return value.format(**combined_context)

    def __getitem__(self, key):
        """
        Dictionary-like access to top-level configuration keys.

        Args:
            key (str): Key name.

        Returns:
            any: Value associated with the key.

        Raises:
            KeyError: If the key does not exist in the configuration.
        """
        return self.config[key]

    def __str__(self):
        """
        Get a pretty-printed JSON string representation of the configuration.

        Returns:
            str: JSON-formatted string.
        """
        return json.dumps(self.config, indent=2)
