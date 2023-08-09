"""Logging infrastructure"""
import logging
import sys
from pathlib import Path
from typing import Optional

from ..config import get_logger_info


def set_up_logger(logger: logging.Logger, true_name: str):
    """Set up logger for first time"""
    logger.setLevel(logging.DEBUG)

    Path("./logs").mkdir(exist_ok=True)
    file_handler = logging.FileHandler(f"./logs/{true_name}.log", encoding="UTF-8")
    file_handler.setLevel(get_logger_info()["file level"])

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(get_logger_info()["console level"])

    formatter = logging.Formatter(
        fmt="{asctime} [{name:>25}]: |{levelname:>7}|: {message}", datefmt="%H:%M:%S %d.%m.%Y", style="{"
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)


def get_logger(package_name: str, true_name: Optional[str] = None):
    """Get logger for current package"""
    if true_name is None:
        true_name = package_name[package_name.find(".") + 1 :]

    root_logger = logging.getLogger()

    if not root_logger.hasHandlers():
        set_up_logger(root_logger, true_name)

    return logging.getLogger(true_name)
