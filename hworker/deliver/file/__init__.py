"""file backend"""
import os
import datetime
from pathlib import Path

from ...log import get_logger
from ...config import get_file_root_path, dirname_to_uid, get_tasks_list
from ... import depot
from ...depot.objects import Homework

_default_datetime = datetime.datetime.fromisoformat("2009-05-17 20:09:00")
_depot_prefix = "f"


def download_all():
    root = get_file_root_path()

    for username in os.listdir(root):
        if dirname_to_uid(username) is None:
            get_logger(__name__).error(f"Found unspecified username {username:<15}")
            continue
        USER_ID = dirname_to_uid(username)
        for task_name in os.listdir(user_path := root + os.sep + username):
            if task_name not in get_tasks_list():
                get_logger(__name__).error(
                    f"For user {dirname_to_uid(username):<15} found unspecified task name {task_name:<15}"
                )
                continue
            TASK_ID = task_name

            timestamps = []
            contents = {}
            for file in Path(task_path := user_path + os.sep + task_name).rglob("**/*"):
                if file.is_file():
                    with open(file, "rb") as file_in:
                        contents[str(file.relative_to(get_file_root_path()))] = file_in.read()
                    timestamps.append(os.path.getmtime(file))

            if len(contents) != 0:
                depot.store(
                    Homework(
                        ID=f"{_depot_prefix}{task_path}",
                        USER_ID=dirname_to_uid(username),
                        TASK_ID=TASK_ID,
                        timestamp=max(timestamps, default=_default_datetime.timestamp()),
                        content=contents,
                        is_broken=False,
                    )
                )
                get_logger(__name__).info(f"Added task {TASK_ID:<15} for user {USER_ID:<15}")
