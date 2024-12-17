"""file backend"""
import datetime
import re
from pathlib import Path

from tqdm import tqdm

from ... import depot
from ...config import get_file_root_path, dirname_to_uid, get_tasks_list, taskid_to_deliverid
from ...depot.objects import Homework, FileObject
from ...log import get_logger

_default_timestamp = datetime.datetime.fromisoformat("2009-05-17 20:09:00").timestamp()
_depot_prefix = "f"
_ignore_pattern = re.compile(r"(.*/|^)__pycache__/.*")


def download_all():
    log = get_logger(__name__)
    depot.store(depot.objects.UpdateTime(name="File deliver", timestamp=datetime.datetime.now().timestamp()))

    root = Path(get_file_root_path()).absolute()

    if not root.exists():
        log.error(f"Directory {root} doesnt exists")
        return

    log.info(f"Files at {root}...")
    tasks = get_tasks_list()
    for userdir in tqdm(root.iterdir(), colour="green", desc="Imap download", delay=2):
        log.debug(f"User {userdir}")
        if not userdir.is_dir():  # Irrelivate
            continue
        if (USER_ID := dirname_to_uid(userdir.name)) is None:
            log.error(f"Found unspecified username {userdir.name:<15}")
            continue
        for TASK_ID in tasks:
            deliver_id = taskid_to_deliverid(TASK_ID)
            if not (taskdir := userdir / deliver_id).exists():
                log.warning(f"User {userdir.name} did not provide {deliver_id} task")
                continue
            contents = {
                file.relative_to(taskdir).as_posix(): FileObject(
                    content=file.read_bytes(), timestamp=file.stat().st_mtime
                )
                for file in taskdir.rglob("**/*")
                if file.is_file() and not _ignore_pattern.match(str(file))
            }
            if len(contents) > 0:
                depot.store(
                    Homework(
                        ID=f"{_depot_prefix}.{taskdir}",
                        USER_ID=USER_ID,
                        TASK_ID=TASK_ID,
                        timestamp=max(c.timestamp for c in contents.values()),
                        content=contents,
                        is_broken=False,
                    )
                )
                log.debug(f"Added task {TASK_ID:<15} for user {USER_ID:<15}")
            else:
                log.warning(f"No files in {str(taskdir.relative_to(root)):<15}")
