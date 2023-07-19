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


def create_config(content: dict = None) -> None:
    """Creates config file

    :param content: config content dict
    """
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
    """Get a user-repo dict

    :return: user-repo dict
    """
    return read_config()["git"]["directory"]


def get_repos() -> list[str]:
    """Get all repos list

    :return: all repos list
    """
    return read_config()["git"]["repos"].values()


def get_uids() -> list[str]:
    """Get all user ids list

    :return: all user ids list
    """
    return read_config()["git"]["repos"].keys()


def uid_to_repo(uid: str) -> str:
    """Converts user id to repo

    :param uid: user id
    :return: repo URL
    """
    return read_config()["git"]["repos"].get(uid, None)


def repo_to_uid(repo: str) -> str:
    """Converts repo to user id

    :param repo: repo URL
    :return: user id
    """
    reverse = {repo: student_id for student_id, repo in read_config()["git"]["repos"].items()}
    return reverse.get(repo, None)


def get_logger_info() -> dict:
    """Get file-console logger info dict

    :return: file-console logger info dict
    """
    return read_config()["logging"]


def get_imap_info() -> dict:
    """Get IMAP info dict

    :return: IMAP info dict
    """
    return read_config()["IMAP"]
