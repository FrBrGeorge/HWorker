import os

from ..depot.objects import Homework, Check, Solution, CheckCategoryEnum
from ..config import get_runtime_suffix, get_validate_suffix, get_remote_name, get_prog_name, get_task_info


def get_checks(hw: Homework) -> list[Check]:
    """Get homework checks list

    :param hw: homework object
    :return: checks list
    """
    checks, seen = [], set()
    for path, path_content in hw.content.items():
        filename = path.rsplit(os.sep, maxsplit=1)[-1]
        name, _, suffix = filename.rpartition(".")
        if name not in seen:
            if suffix in get_runtime_suffix():
                content = {}
                for suf in get_runtime_suffix():
                    file = f"{name}.{suf}"
                    content[file] = hw.content.get(path.removesuffix(suffix) + suf, None)
                check = Check(
                    content=content,
                    category=CheckCategoryEnum.runtime,
                    ID=f"{hw.USER_ID}:{hw.TASK_ID}/{filename}",
                    TASK_ID=hw.TASK_ID,
                    USER_ID=hw.USER_ID,
                    timestamp=hw.timestamp,
                )
            elif suffix == get_validate_suffix() and filename != get_prog_name():
                check = Check(
                    content={filename: path_content},
                    category=CheckCategoryEnum.validate,
                    ID=f"{hw.USER_ID}:{hw.TASK_ID}/{filename}",
                    TASK_ID=hw.TASK_ID,
                    USER_ID=hw.USER_ID,
                    timestamp=hw.timestamp,
                )
            else:
                continue
            seen.add(name)
            checks.append(check)

    return checks


def get_solution(hw: Homework) -> Solution:
    """Get solution object from homework

    :param hw: homework object
    :return: solution object
    """
    content, remote_checks, prog = {}, [], get_prog_name()
    # TODO: Solution content for imap?
    for path, path_content in hw.content.items():
        if path.endswith(prog):
            content = {prog: path_content}
        if path.endswith(get_remote_name()):
            remote_checks = path_content.decode("utf-8").split()
    own_checks = [check.ID for check in get_checks(hw)]
    config_checks = get_task_info(hw.TASK_ID).get("checks", [])

    return Solution(
        content=content,
        checks=own_checks + remote_checks + config_checks,
        ID=f"{hw.USER_ID}:{hw.TASK_ID}",
        TASK_ID=hw.TASK_ID,
        USER_ID=hw.USER_ID,
        timestamp=hw.timestamp,
    )
