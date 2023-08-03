"""Read and parse config"""

from typing import Final
from functools import cache
from tomllib import load
from pathlib import Path

from mergedeep import merge
from tomli_w import dump

_final_config_name: Final = "final_hworker.toml"
_user_config_name: Final = "hworker.toml"
_default_config_name: Final = "default_hworker.toml"


def read_config(config_name: str) -> dict:
    """Read given config

    :param config_name: config name to read
    :return: config info dict
    """
    content = {}
    for path in __path__:
        if (cfg_path := Path(path) / config_name).is_file():
            with cfg_path.open(mode="rb") as cfg:
                content |= load(cfg)
    return content


def create_config(config_name: str, content: dict = None) -> None:
    """Creates config file

    :param content: config content dict
    :param default_config:
    :param config_name: config file name
    """
    if content is None:
        content = get_final_config(Path(__path__[0]) / _default_config_name)
    with open(Path(__path__[0]) / config_name, "wb") as cfg:
        dump(content, cfg)


@cache
def get_final_config(default_config: str = _default_config_name,
                     user_config: str = _user_config_name,
                     final_config: str = _final_config_name) -> dict:
    """Get final config info and create user config if it doesn't exist

    :param default_config: default config name
    :param user_config: user config name
    :param final_config: final config name
    :return: config info dict
    """
    if not (Path(__path__[0]) / user_config).is_file():
        create_config(user_config, read_config(default_config))
    dflt, usr = read_config(default_config), read_config(user_config)
    create_config(final_config, dict(merge(dflt, usr)))
    return read_config(final_config)


def get_git_directory() -> str:
    """Get a user-repo dict

    :return: user-repo dict
    """
    return get_final_config()["git"]["directory"]


def get_file_root_path() -> str:
    """Get a user-repo dict

    :return: user-repo dict
    """
    return get_final_config()["file"]["root_path"]


def get_repos() -> list[str]:
    """Get all repos list

    :return: all repos list
    """
    return list(get_final_config()["git"]["users"].values())


# TODO: add multiback get uids  and get uids for every back
def get_uids() -> list[str]:
    """Get all user ids list

    :return: all user ids list
    """
    return list(get_final_config()["git"]["users"].keys())


def uid_to_repo(uid: str) -> str:
    """Converts user id to repo

    :param uid: user id
    :return: repo URL
    """
    return get_final_config()["git"]["users"].get(uid, None)


def repo_to_uid(repo: str) -> str:
    """Converts repo to user id

    :param repo: repo URL
    :return: user id
    """
    reverse = {repo: student_id for student_id, repo in get_final_config()["git"]["users"].items()}
    return reverse.get(repo, None)


def get_logger_info() -> dict[str, str]:
    """Get file-console logger info dict

    :return: file-console logger info dict
    """
    return get_final_config()["logging"]


def get_deliver_modules() -> list:
    """Get modules for deliver

    :return: list of modules
    """
    return get_final_config()["modules"]["deliver"]


def get_imap_info() -> dict[str, str]:
    """Get IMAP info dict

    :return: IMAP info dict
    """
    return get_final_config()["IMAP"]


def get_max_test_size() -> int:
    """Get maximum test rows size

    :return: maximum test rows size
    """
    return int(get_final_config()["tests"]["max_size"])


def get_default_time_limit() -> int:
    """Get task default time limit

    :return: task default time limit
    """
    return int(get_final_config()["tests"]["default_time_limit"])


def get_default_resource_limit() -> int:
    """Get task default resource limit

    :return: task default resource limit
    """
    return int(get_final_config()["tests"]["default_resource_limit"])


def get_task_info(task_name: str) -> dict:
    """Get dict with task info: deadlines, special limits, special checks etc.

    :param task_name: task name from config
    :return: task info dict
    """
    return get_final_config()["tasks"].get(task_name, None)


def get_check_directory() -> str:
    """Get a dir for check

    :return: check dir
    """
    return get_final_config()["check"]["directory"]


def get_prog_name() -> str:
    """

    :return:
    """
    return get_final_config()["formalization"]["prog_name"]


def get_urls_name() -> str:
    """

    :return:
    """
    return get_final_config()["formalization"]["remotes_name"]


def get_checks_dir() -> str:
    """

    :return:
    """
    return get_final_config()["formalization"]["checks_dir"]


def get_checks_suffix() -> str:
    """

    :return:
    """
    return get_final_config()["formalization"]["checks_suffix"]
