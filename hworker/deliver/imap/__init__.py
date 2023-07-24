"""IMAP backend"""
import os
import re
import tarfile
import tempfile
import datetime

from .mailer_utilities import get_mailbox
from ...log import get_logger
from ... import depot
from ...depot.objects import Homework

_default_datetime = datetime.datetime.fromisoformat("2009-05-17 20:09:00")


def parse_tar_file(filename: str, content: bytes):
    with tempfile.NamedTemporaryFile("wb", delete=False) as tmp_file:
        tmp_file.write(content)
        tmp_file.flush()

    timestamps = [_default_datetime.timestamp()]
    contents = {}

    with tarfile.open(tmp_file.name) as tar:
        for member in tar.getmembers():
            member: tarfile.TarInfo
            if member.isfile():
                timestamps.append(member.mtime)
                contents[f"{filename}/{member.name}"] = tar.extractfile(member).read()

    os.remove(tmp_file.name)
    return max(timestamps), contents


def download_all():
    box = get_mailbox()

    for mail in box.fetch("ALL", limit=47):
        # TODO should take from config
        TASK_ID = None
        USER_ID = mail.from_
        timestamps = []
        contents = {}

        for attachment in mail.attachments:
            task_name = re.findall(r"(?<=report\.).+(?=\.)", attachment.filename)
            task_name = task_name[0] if len(task_name) == 1 else None

            if task_name is not None:
                # TODO should take from config
                TASK_ID = task_name

                timestamp, content = parse_tar_file(filename=attachment.filename, content=attachment.payload)
                timestamps.append(timestamp)
                contents.update(content)

                get_logger(__name__).warn(f"Find {attachment.filename} for email {USER_ID}")
        if TASK_ID is not None:
            depot.store(
                Homework(
                    ID=mail.uid,
                    USER_ID=mail.from_,
                    TASK_ID=TASK_ID,
                    timestamp=max(timestamps),
                    content=contents,
                )
            )
