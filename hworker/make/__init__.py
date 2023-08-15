import os

from ..depot.objects import Homework, Check, Solution, CheckCategoryEnum
from ..config import get_runtime_suffix, get_validate_suffix, get_remotes_name, get_prog_name


def get_checks(hw: Homework) -> list[Check]:
    """

    :param hw:
    :return:
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
    """

    :param hw:
    :return:
    """
    pass


def store_homework():
    pass
