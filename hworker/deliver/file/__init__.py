"""file backend"""
import datetime
import os
import re
from operator import attrgetter
from pathlib import Path

from ... import depot
from ...config import get_file_root_path, dirname_to_uid, get_tasks_list
from ...depot.objects import Homework, FileObject
from ...log import get_logger

_default_timestamp = datetime.datetime.fromisoformat("2009-05-17 20:09:00").timestamp()
_depot_prefix = "f"
_ignore_pattern = re.compile(r"(.*/|^)__pycache__/.*")


def download_all():
    depot.store(depot.objects.UpdateTime(name="File deliver", timestamp=datetime.datetime.now().timestamp()))

    root = Path(get_file_root_path())

    get_logger(__name__).info("Downloading files...")

    for username in os.listdir(root):
        if dirname_to_uid(username) is None:
            get_logger(__name__).error(f"Found unspecified username {username:<15}")
            continue
        USER_ID = dirname_to_uid(username)
        for task_name in os.listdir(user_path := root / username):
            if task_name not in get_tasks_list():
                get_logger(__name__).error(
                    f"For user {dirname_to_uid(username):<15} found unspecified task name {task_name:<15}"
                )
                continue
            TASK_ID = task_name

            contents: dict[str, FileObject] = dict()
            for file in (task_path := user_path / task_name).rglob("**/*"):
                if file.is_file() and not _ignore_pattern.match(str(file)):
                    with open(file, "rb") as file_in:
                        contents[file.relative_to(task_path).as_posix()] = FileObject(
                            content=file_in.read(), timestamp=os.path.getmtime(file)
                        )

            if len(contents) != 0:
                depot.store(
                    Homework(
                        ID=f"{_depot_prefix}{task_path}",
                        USER_ID=dirname_to_uid(username),
                        TASK_ID=TASK_ID,
                        timestamp=max(map(attrgetter("timestamp"), contents.values()), default=_default_timestamp),
                        content=contents,
                        is_broken=False,
                    )
                )
                get_logger(__name__).debug(f"Added task {TASK_ID:<15} for user {USER_ID:<15}")
