"""Read and parse config"""

from copy import copy
from typing import Final
from tomllib import load
from pathlib import Path
import datetime

from pytimeparse import parse
from mergedeep import merge
from tomli_w import dump

final_name_suffix: Final = "_final"
user_name = "hworker"
default_name: Final = "default_hworker"
extension: Final = ".toml"
profile: list = []


def read_from_path(path: Path) -> dict:
    """Read given config

    :param path: config file to read
    :return: config info dict
    """
    if not path.is_file():
        return {}
    with path.open(mode="rb") as cfg:
        return load(cfg)


def create_config(name: Path, content: dict) -> None:
    with name.open(mode="wb") as cfg:
        dump(content, cfg)


def process_configs(user_config: str, *extras: str) -> Path:
    """Search, read, merge and process all config files, creating finalized config

    :param user_config: user config file prefix
    :param extras: additional config file prefix
    :return: finalized config file
    """
    userpath = Path(user_config)
    userdir = userpath.parent
    username = userpath.name.removesuffix(extension)
    content = {}
    for folder in [*__path__, str(userdir)]:
        for name in [default_name, *extras, username]:
            merge(content, read_from_path(Path(folder) / f"{name}{extension}"))
    fill_final_config(content)
    clear_underscores(content)
    finalpath = userdir / f"{username}{final_name_suffix}{extension}"
    create_config(finalpath, content)
    profile[:] = [content, *extras, username]
    return finalpath


def config() -> dict:
    """Get final config info

    :return: config info dict
    """
    if not profile:
        process_configs(user_name)
    return profile[0]


def fill_final_config(final_content: dict) -> None:
    """

    :param final_content:
    :return:
    """
    for task_ID, task in final_content.get("tasks", {}).items():
        if not task_ID.startswith("_"):
            for dflt_name, dflt in final_content["tasks"]["_default"].items():
                if dflt_name not in task.keys():
                    task[dflt_name] = dflt

            for key, val in copy(task).items():
                if key.endswith("delta"):
                    open_date, delta = val.split("+")
                    field = key.rsplit("_", 1)[0]
                    if field not in task.keys():
                        time_delta = datetime.timedelta(seconds=parse(delta))
                        open_date = task[open_date]
                        task[field] = open_date + time_delta


def clear_underscores(final_content: dict) -> None:
    """

    :param final_content:
    :return:
    """
    for k, v in copy(final_content).items():
        if k.startswith("_"):
            final_content.pop(k)
        elif isinstance(v, dict):
            clear_underscores(v)


def get_git_directory() -> str:
    """Get a user-repo dict

    :return: user-repo dict
    """
    return config()["git"]["directory"]


def get_file_root_path() -> str:
    """Get a user-repo dict

    :return: user-repo dict
    """
    return config()["file"]["root_path"]


def get_repos() -> list[str]:
    """Get all repos list

    :return: all repos list
    """
    return list(config()["git"]["users"].values())


# TODO: add multiback get uids  and get uids for every back
def get_git_uids() -> list[str]:
    """Get all git user ids list

    :return: all user ids list
    """
    return list(config()["git"]["users"].keys())


def get_users() -> dict[str:str]:
    """Get all UID: Deliver_ID pairs"""
    users = {}
    for module in get_deliver_modules():
        users |= config().get(module, {}).get("users", {})
    return users


def get_uids() -> list[str]:
    """Get all uids

    :return: all uids list
    """
    return list(get_users().keys())


def get_tasks_list() -> list[str]:
    """Get all tasks list

    :return: all tasks list
    """
    return config()["tasks"].keys()


def uid_to_repo(uid: str) -> str | None:
    """Converts user id to repo

    :param uid: user id
    :return: repo URL
    """
    return config()["git"]["users"].get(uid, None)


def repo_to_uid(repo: str) -> str | None:
    """Converts repo to user id

    :param repo: repo URL
    :return: user id
    """
    reverse = {repo: student_id for student_id, repo in config()["git"]["users"].items()}
    return reverse.get(repo, None)


def uid_to_email(uid: str) -> str | None:
    """Converts user id to email

    :param uid: user id
    :return: email address
    """
    return config()["imap"]["users"].get(uid, None)


def email_to_uid(email: str) -> str | None:
    """Converts email address to user id

    :param email: email address
    :return: user id
    """
    reverse = {email: uid for uid, email in config()["imap"]["users"].items()}
    return reverse.get(email, None)


def taskid_to_deliverid(task_id: str) -> str | None:
    """Converts task id to deliver id

    :param task_id: task name in config
    :return: task name for specific deliver backend
    """
    return config()["tasks"].get(task_id, {}).get("deliver_ID", None)


def deliverid_to_taskid(deliver_id: str) -> str | None:
    """Converts deliver id to task id

    :param deliver_id: task name in config
    :return: task name for specific deliver backend
    """
    reverse = {t_dict["deliver_ID"]: t_id for t_id, t_dict in config()["tasks"].items()}
    return reverse.get(deliver_id, None)


def get_logger_info() -> dict[str, str]:
    """Get file-console logger info dict

    :return: file-console logger info dict
    """
    return config()["logging"]


def get_publish_info() -> dict[str, str]:
    """Get publish info dict

    :return: publish info dict
    """
    return config()["publish"]


def get_deliver_modules() -> list:
    """Get modules for deliver

    :return: list of modules
    """
    return config()["modules"]["deliver"]


def get_imap_info() -> dict[str, str]:
    """Get imap info dict

    :return: imap info dict
    """
    return config()["imap"]


def get_task_info(task_name: str) -> dict:
    """Get dict with task info: deadlines, special limits, special checks etc.

    :param task_name: task name from config
    :return: task info dict
    """
    return config()["tasks"].get(task_name, {})


def get_check_directory() -> str:
    """Get a dir for check

    :return: check dir
    """
    return config()["check"]["directory"]


def get_prog_name() -> str:
    """Get course program name

    :return: program name
    """
    return config()["formalization"]["prog_name"]


def get_remotes_name() -> str:
    """Get remote tests file name

    :return: remotes name
    """
    return config()["formalization"]["remotes_name"]


def get_checks_dir() -> str:
    """Get tests dir name

    :return: tests dir name
    """
    return config()["formalization"]["checks_dir"]


def get_runtime_suffix() -> list:
    """Get runtime suffix

    :return: runtime suffix
    """
    return config()["formalization"]["runtime_suffix"]


def get_validate_suffix() -> str:
    """Get validate suffix

    :return: validate suffix
    """
    return config()["formalization"]["validate_suffix"]
