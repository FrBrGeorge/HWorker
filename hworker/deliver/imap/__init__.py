"""IMAP backend"""
import inspect
import re
import tarfile
import tempfile
import datetime

from ...deliver import Backend
from .mailer_utilities import get_mailbox
from ...log import get_logger

_default_datetime = datetime.datetime.fromisoformat("2009-05-17 20:09:00")


def get_report_date(file):
    """Report creation date."""
    line = file.extractfile("./TIME.txt").read().decode().split("\n")[0]
    time_lines = re.findall(r"START_TIME \d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", line)
    if time_lines:
        creation_date = re.findall(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", time_lines[0])[0]
        return datetime.datetime.strptime(creation_date, "%Y-%m-%d %H:%M:%S")


def parse_tar_file(content: bytes):
    with tempfile.NamedTemporaryFile("wb") as file:
        file.write(content)
        file.flush()

        creation_date = _default_datetime
        text = ""
        is_broken = False

        try:
            file = tarfile.open(file.name)
            creation_date = get_report_date(file)

            raw_text = file.extractfile("./OUT.txt").read()

            try:
                text = raw_text.decode()
            except Exception:
                try:
                    text = raw_text.decode("cp1251")
                except Exception:
                    text = raw_text.decode(errors="ignore")

        except Exception:
            text = ""
            is_broken = True

    return creation_date, text, is_broken


class IMAPBackend(Backend):
    def download_all(self):
        box = get_mailbox()

        for mail in box.fetch("ALL", limit=43):
            for attachment in mail.attachments:
                homework_name = attachment.filename

                task_name = re.findall(r"(?<=\.).+(?=\.)", homework_name)
                task_name = task_name[0] if len(task_name) == 1 else None

                if task_name is not None:
                    student_email = mail.from_

                    metadata = parse_tar_file(attachment.payload)

                    get_logger(__name__).warn(f"Find {homework_name} for email {student_email}")

                    # add homework in depot
