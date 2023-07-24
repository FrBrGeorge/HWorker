"""Default config consts"""

from typing import Final

MAX_SIZE: Final = 100
DEFAULT_TIME_LIMIT: Final = 2
DEFAULT_RESOURCE_LIMIT: Final = 1024 * 1024 * 3

_default_config_name: Final = "hworker.toml"

_default_config_content = {
    "logging": {"console level": "INFO", "file level": "DEBUG"},
    "modules": {
        "deliver": ["imap", "git"],
    },
    "git": {
        "directory": "~/.cache/hworker_git",
        "repos": {"username": "repo (example, fill it)"},
    },
    "IMAP": {
        "host": "host (example, fill it)",
        "port": "993",
        "folder": "folder (example, fill it)",
        "username": "username (example, fill it)",
        "password": "password (example, fill it)",
    },
    "tasks": {
        "task name": {
            "task ID": "20240101 (example, fill it)",
            "open date": "20240101 (example, fill it)",
            "soft deadline": "20240108 (example, fill it)",
            "hard deadline": "20240401 (example, fill it)",
            "time limit": f"{DEFAULT_TIME_LIMIT} (optional field)",
            "resource limit": f"{DEFAULT_RESOURCE_LIMIT} (optional field)",
        }
    },
    "tests": {
        "max size": MAX_SIZE,
        "default time limit": DEFAULT_TIME_LIMIT,
        "default resource limit": DEFAULT_RESOURCE_LIMIT,
    },
}
