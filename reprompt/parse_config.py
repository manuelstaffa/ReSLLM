import tomlkit
import os

DEFAULT_CONFIG_PATH = os.path.join("context", "config")
_active_config = None


def _set_active_config(config):
    global _active_config
    _active_config = config


def get_active_config():
    if _active_config is None:
        raise RuntimeError("Config not initialized. Call set_active_config() first.")
    return _active_config


class ConfigParser:
    def __init__(self, path, overrides=None):
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

    def _load(self):
        """
        Load the configuration TOML file.

        Returns:
            dict: Parsed TOML content as a tomlkit TOMLDocument.
        """
        path = self.path

        if not path.endswith(".toml"):
            path += ".toml"

        if os.path.sep not in path:
            path = os.path.join(DEFAULT_CONFIG_PATH, path)

        with open(path, "r", encoding="utf-8") as f:
            return tomlkit.parse(f.read())

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
            d (TOMLDocument or dict): Dictionary to modify.
            key (str): Dot-separated key string.
            value: Value to set.
        """
        keys = key.split(".")
        for k in keys[:-1]:
            if k not in d or not isinstance(d[k], dict):
                d[k] = tomlkit.table()
            d = d[k]
        d[keys[-1]] = value

    def _get_nested(self, d, key):
        """
        Retrieve nested dictionary value by dot-separated key.

        Args:
            d (TOMLDocument or dict): Dictionary to search.
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
            return default

    def format(self, key, context=None):
        """
        Retrieve and format a string from the configuration with external variables.

        Args:
            key (str): Dot-separated key pointing to the string template in the config.
            context (dict, optional): External variables for formatting. Overrides config values with same keys.

        Returns:
            str: The formatted string with placeholders replaced by corresponding values.
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
        return self._get_nested(self.config, key)

    def __contains__(self, key):
        try:
            self._get_nested(self.config, key)
            return True
        except KeyError:
            return False

    def __str__(self):
        return tomlkit.dumps(self.config)
