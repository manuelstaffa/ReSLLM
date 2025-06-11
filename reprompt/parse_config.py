import json
import os

DEFAULT_CONFIG_PATH = os.path.join("RePrompt", "context", "config", "default.json")


class ConfigParser:
    def __init__(self, path=DEFAULT_CONFIG_PATH, overrides=None):
        self.path = path or DEFAULT_CONFIG_PATH
        self.config = self._load()
        if overrides:
            self._apply_overrides(overrides)

    def _load(self):
        with open(self.path, "r") as f:
            return json.load(f)

    def _apply_overrides(self, overrides):
        for key, value in overrides.items():
            if value is not None:
                self.config[key] = value

    def get(self, key, default=None):
        keys = key.split(".")
        value = self.config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value

    def __getitem__(self, key):
        return self.config[key]  # For dict-like access

    def __str__(self):
        return json.dumps(self.config, indent=2)
