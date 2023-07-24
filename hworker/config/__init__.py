"""Read and parse config"""

from .default_config import _default_config_content, _default_config_name

from functools import cache
from tomllib import load
import os

from tomli_w import dump


def create_config(content: dict = None, config_name: str = _default_config_name) -> None:
    """Creates config file

    :param content: config content dict
    :param config_name: config file name
    """
    if content is None:
        content = _default_config_content
    with open(config_name, "wb") as cfg:
        dump(content, cfg)


def check_config(content: dict = None, config_name: str = _default_config_name) -> None:
    """Check field of current config file and add default values for missing ones

    :param content: config content dict
    :param config_name: config file name
    """
    if content is None:
        content = _default_config_content
    with open(config_name, "rb") as cfg:
        cur_content = load(cfg)
    for key, value in content.items():
        cur_content.setdefault(key, value)
        if isinstance(value, dict):
            for subkey, subvalue in value.items():
                cur_content[key].setdefault(subkey, subvalue)
    with open(_default_config_name, "wb") as cfg:
        dump(cur_content, cfg)


@cache
def read_config(config_name: str = _default_config_name) -> dict:
    """Reads config

    :param config_name: config file name
    :return: config info dict
    """
    if os.path.isfile(config_name):
        check_config(config_name=config_name)
        with open(config_name, "rb") as cfg:
            return load(cfg)
    create_config(config_name=config_name)
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


def get_deliver_modules() -> list:
    """Get modules for deliver

    :return: list of modules
    """
    return read_config()["modules"]["deliver"]


def get_imap_info() -> dict:
    """Get IMAP info dict

    :return: IMAP info dict
    """
    return read_config()["IMAP"]


def get_max_test_size() -> int:
    """Get maximum test rows size

    :return: maximum test rows size
    """
    return int(read_config()["tests"]["max size"])


def get_default_time_limit() -> int:
    """Get task default time limit

    :return: task default time limit
    """
    return int(read_config()["tests"]["default time limit"])


def get_default_resource_limit() -> int:
    """Get task default resource limit

    :return: task default resource limit
    """
    return int(read_config()["tests"]["default resource limit"])


def get_task_info(task_name: str) -> dict:
    """Get dict with task info: deadlines, special limits, special checks etc.

    :param task_name: task name from config
    :return: task info dict
    """
    return read_config()["tasks"].get(task_name, None)


def get_check_directory() -> str:
    """Get a dir for check

    :return: check dir
    """
    return read_config()["check"]["directory"]
