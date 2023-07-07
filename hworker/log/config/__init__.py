"""Configs infrastructure"""

import configparser
import os.path

from functools import cache

__all__ = ["load_configs"]

_default_config_filename = "mailer.cfg"


def create_default_configs_file():
    """Create default configs."""
    config = configparser.ConfigParser()
    config["Logging"] = {
        "console level": "INFO",
        "file level": "DEBUG",
    }

    with open(_default_config_filename, "w") as file:
        config.write(file)


@cache
def load_configs(
    config_file_name: str = _default_config_filename,
) -> configparser.ConfigParser:
    """Load configs."""
    if os.path.isfile(config_file_name):
        config = configparser.ConfigParser()
        with open(config_file_name, "r") as configfile:
            config.read_file(configfile)
            return config
    else:
        create_default_configs_file()
        raise FileNotFoundError("Config file doesnt exist. We created default file. Please fill it with your data.")
