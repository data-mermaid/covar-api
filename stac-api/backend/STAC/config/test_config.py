import pytest
from .config import load_config

def test_config():
    conf = load_config()
    conf_values = [
        "HOST",
        "PORT",
        "NAME",
    ]
    for value in conf_values:
        assert bool(
            conf.get("databases", {}).get("default", {}).get(value, "")
        ) is True, f"{value}, not found on config.yml"