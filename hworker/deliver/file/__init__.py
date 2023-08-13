"""file backend"""
import os
import datetime
from pathlib import Path

from ...log import get_logger
from ...config import get_file_root_path
from ... import depot
from ...depot.objects import Homework

_default_datetime = datetime.datetime.fromisoformat("2009-05-17 20:09:00")


def download_all():
    root = get_file_root_path()
    if not os.path.isdir(root):
        get_logger(__name__).warn(f"No {root=} directory — not using FILE bachkend")
        return

    for username in os.listdir(root):
        for task_name in os.listdir(user_path := root + os.sep + username):
            # TODO should take from config
            TASK_ID = task_name
            USER_ID = username
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
                        ID="f" + task_path,
                        USER_ID=USER_ID,
                        TASK_ID=TASK_ID,
                        timestamp=max(timestamps),
                        content=contents,
                        is_broken=False,
                    )
                )
                get_logger(__name__).warn(f"Added task {TASK_ID} for user {USER_ID}")
