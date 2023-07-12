"""Git config reading (temporary)"""

from functools import cache
from tomllib import load
import os


_default_config_name = "git.toml"


@cache
def read_config(config_name: str = _default_config_name) -> dict:
    """Reads config

    :param config_name: config file name
    :return: config info dict
    """
    if os.path.isfile(config_name):
        with open(config_name, "rb") as cfg:
            return load(cfg)
    raise FileNotFoundError("GIt config file doesn't exist")


def get_git_directory() -> str:
    return read_config()["directory"]


def get_repos() -> list[str]:
    return read_config()["repos"].values()


def get_ids() -> list[str]:
    return read_config()["repos"].keys()


def id_to_repo(student_id: str) -> str:
    return read_config()["repos"].get(student_id, None)


def repo_to_id(repo: str) -> str:
    reverse = {repo: student_id for student_id, repo in read_config()["repos"].items()}
    return reverse.get(repo, None)
