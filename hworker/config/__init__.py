"""Read and parse config"""

from typing import Final
from functools import cache
from tomllib import load
from pathlib import Path
import os

from mergedeep import merge
from tomli_w import dump

_final_config_name: Final = "final_hworker.toml"
_user_config_name: Final = "hworker.toml"
_default_config_name: Final = "default_hworker.toml"


def read_default_config(config_name: str = _default_config_name) -> dict:
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


def read_config(config_name: str) -> dict:
    """

    :param config_name:
    :return:
    """
    content = {}
    if os.path.isfile(config_name):
        with open(config_name, "rb") as cfg:
            content |= load(cfg)

    return content


def create_config(config_name: str, content: dict = None) -> None:
    """Creates config file

    :param content: config content dict
    :param config_name: config file name
    """
    if content is None:
        content = get_final_config(Path(__path__[0]) / _default_config_name)
    with open(config_name, "wb") as cfg:
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
    if not os.path.isfile(user_config):
        create_config(user_config, read_default_config(default_config))
    dflt, usr = read_default_config(default_config), read_config(user_config)
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
def get_git_uids() -> list[str]:
    """Get all git user ids list

    :return: all user ids list
    """
    return list(get_final_config()["git"]["users"].keys())


def get_uids() -> list[str]:
    """Get all uids

    :return: all uids list
    """
    uids = []
    for module in get_deliver_modules():
        uids += get_final_config().get(module, {}).get("users", [])

    return uids


def get_tasks_list() -> list[str]:
    """ Get all tasks list

    :return: all tasks list
    """
    return get_final_config()["tasks"].keys()


def uid_to_repo(uid: str) -> str | None:
    """Converts user id to repo

    :param uid: user id
    :return: repo URL
    """
    return get_final_config()["git"]["users"].get(uid, None)


def repo_to_uid(repo: str) -> str | None:
    """Converts repo to user id

    :param repo: repo URL
    :return: user id
    """
    reverse = {repo: student_id for student_id, repo in get_final_config()["git"]["users"].items()}
    return reverse.get(repo, None)


def uid_to_email(uid: str) -> str | None:
    """Converts user id to email

    :param uid: user id
    :return: email address
    """
    return get_final_config()["IMAP"]["users"].get(uid, None)


def email_to_uid(email: str) -> str | None:
    """Converts email address to user id

    :param email: email address
    :return: user id
    """
    reverse = {email: uid for uid, email in get_final_config()["IMAP"]["users"].items()}
    return reverse.get(email, None)


def taskid_to_deliverid(task_id: str) -> str | None:
    """Converts task id to deliver id

    :param task_id: task name in config
    :return: task name for specific deliver backend
    """
    return get_final_config()["tasks"].get(task_id, {}).get("deliver_ID", None)


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
    return get_final_config()["tasks"].get(task_name, {})


def get_check_directory() -> str:
    """Get a dir for check

    :return: check dir
    """
    return get_final_config()["check"]["directory"]


def get_prog_name() -> str:
    """Get course program name

    :return: program name
    """
    return get_final_config()["formalization"]["prog_name"]


def get_urls_name() -> str:
    """Get remote tests file name

    :return: urls name
    """
    return get_final_config()["formalization"]["remotes_name"]


def get_checks_dir() -> str:
    """Get tests dir name

    :return: tests dir name
    """
    return get_final_config()["formalization"]["checks_dir"]


def get_checks_suffix() -> str:
    """Get tests suffix

    :return: tets suffix
    """
    return get_final_config()["formalization"]["checks_suffix"]
