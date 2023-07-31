"""IMAP backend"""
import os
import re
import tarfile
import tempfile
import datetime
import traceback

from .mailer_utilities import get_mailbox
from ...config import get_imap_info
from ...log import get_logger
from ... import depot
from ...depot.objects import Homework

_default_datetime = datetime.datetime.fromisoformat("2009-05-17 20:09:00")


def parse_tar_file(filename: str, content: bytes):
    timestamps = [_default_datetime.timestamp()]
    contents = {}
    is_broken = False

    try:
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
    except Exception as e:
        get_logger(__name__).warn(f"Exception during archive parsing\n {''.join(traceback.format_exception(e))}")
    return max(timestamps), contents, is_broken


def download_all():
    box = get_mailbox()

    # TODO should only get new latter, not all
    # print(box.uids("ALL"))

    found_mails = 0

    get_logger(__name__).info(f"Started")

    for mail in box.fetch("ALL", limit=get_imap_info()["letter_limit"]):
        # TODO should take from config
        TASK_ID = None
        USER_ID = mail.from_
        timestamps = []
        contents = {}
        is_broken_all = False

        for attachment in mail.attachments:
            task_name = re.findall(r"(?<=report\.).+(?=\.)", attachment.filename)
            task_name = task_name[0] if len(task_name) == 1 else None

            if task_name is not None:
                # TODO should take from config
                TASK_ID = task_name

                timestamp, content, is_broken = parse_tar_file(filename=attachment.filename, content=attachment.payload)
                timestamps.append(timestamp)
                contents.update(content)
                is_broken_all = is_broken_all or is_broken

                get_logger(__name__).debug(f"Find {attachment.filename:<20} for email {USER_ID:<30}")
        if TASK_ID is not None:
            depot.store(
                Homework(
                    ID="i" + mail.uid,
                    USER_ID=mail.from_,
                    TASK_ID=TASK_ID,
                    timestamp=max(timestamps),
                    content=contents,
                    is_broken=is_broken_all,
                )
            )
            found_mails += 1
    get_logger(__name__).info(f"Find a total of {found_mails} homeworks")
