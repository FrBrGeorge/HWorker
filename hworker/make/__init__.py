from ..depot.objects import Homework, Check, Solution, CheckCategoryEnum
from ..config import (
    get_runtime_suffix,
    get_validate_suffix,
    get_check_name,
    get_remote_name,
    get_prog_name,
    get_task_info,
)


def get_checks(hw: Homework) -> list[Check]:
    """Get homework checks list

    :param hw: homework object
    :return: checks list
    """
    checks, seen = [], set()
    for check_path, check_content in hw.content.items():
        if check_path.startswith(get_check_name()):
            path_beg, _, suffix = check_path.rpartition(".")
            name = path_beg.rsplit("/", maxsplit=1)[-1]

            if name not in seen:
                content, category = {}, None
                if suffix in get_runtime_suffix():
                    category = CheckCategoryEnum.runtime
                    for suf in get_runtime_suffix():
                        content[f"{name}.{suf}"] = hw.content.get(f"{path_beg}.{suf}", None)
                elif suffix == get_validate_suffix():
                    category = CheckCategoryEnum.validate
                    content = {f"{name}.{suffix}": check_content}
                else:
                    continue

                check = Check(
                    content=content,
                    category=category,
                    ID=f"{hw.USER_ID}:{hw.TASK_ID}/{name}",
                    TASK_ID=hw.TASK_ID,
                    USER_ID=hw.USER_ID,
                    timestamp=hw.timestamp,
                )
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
