"""Read and parse config"""

from functools import cache
from tomllib import load
from collections import namedtuple
import os

from tomli_w import dump

LoggerInfo = namedtuple("LoggerInfo", ["file", "console"])

_default_config_name = "hworker.toml"
_default_config_content = {
    "logging": {
        "console level": "INFO",
        "file level": "DEBUG"},
    "git": {
        "directory": "~/.cache/hworker_git",
        "repos": {"username": "repo (example, remove it)"},
    },
    "IMAP": {
        "host": "host (example, remove it)",
        "port": "port (example, remove it)",
        "folder": "folder (example, remove it)",
        "username": "username (example, remove it)",
        "password": "password (example, remove it)"
    },
}


def create_config(content=None):
    """Creates config file"""
    if content is None:
        content = _default_config_content
    with open(_default_config_name, "wb") as cfg:
        dump(content, cfg)


@cache
def read_config(config_name: str = _default_config_name) -> dict:
    """Reads config

    :param config_name: config file name
    :return: config info dict
    """
    if os.path.isfile(config_name):
        with open(config_name, "rb") as cfg:
            return load(cfg)
    create_config()
    raise FileNotFoundError("Config file doesnt exist, so it has been created. Please fill it with your data.")


def get_git_directory() -> str:
    return read_config()["git"]["directory"]


def get_repos() -> list[str]:
    return read_config()["git"]["repos"].values()


def get_uids() -> list[str]:
    return read_config()["git"]["repos"].keys()


def uid_to_repo(uid: str) -> str:
    return read_config()["git"]["repos"].get(uid, None)


def repo_to_uid(repo: str) -> str:
    reverse = {repo: student_id for student_id, repo in read_config()["git"]["repos"].items()}
    return reverse.get(repo, None)


def get_logger_info() -> dict:
    return read_config()["logging"]


def get_imap_info() -> dict:
    return read_config()["IMAP"]
