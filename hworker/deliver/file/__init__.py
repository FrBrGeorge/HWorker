"""IMAP backend"""
import glob
import os
import datetime

from ...log import get_logger
from ...config import get_file_root_path
from ... import depot
from ...depot.objects import Homework

_default_datetime = datetime.datetime.fromisoformat("2009-05-17 20:09:00")


def download_all():
    root = get_file_root_path()

    for username in os.listdir(root):
        for task_name in os.listdir(user_path := root + os.sep + username):
            # TODO should take from config
            TASK_ID = task_name
            USER_ID = username
            timestamps = []
            contents = {}
            for filename in glob.glob(task_path := user_path + os.sep + task_name, recursive=True):
                file_path = filename + os.sep + filename
                with open(file_path, "rb") as file:
                    contents[filename] = file.read()
                timestamps.append(os.path.getmtime(file_path))

            depot.store(
                Homework(
                    ID=task_path,
                    USER_ID=USER_ID,
                    TASK_ID=TASK_ID,
                    timestamp=max(timestamps),
                    content=contents,
                )
            )
            get_logger(__name__).warn(f"Added task {TASK_ID} for user {USER_ID}")
