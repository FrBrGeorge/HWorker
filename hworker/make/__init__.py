from ..depot.objects import Homework, Check, Solution, CheckResult, CheckCategoryEnum, VerdictEnum
from ..config import get_checks_dir, get_checks_suffix, get_remotes_name, get_prog_name


def get_checks(hw: Homework) -> list[Check]:
    """

    :param hw:
    :return:
    """
    checks = []
    checks_dir = hw.content.get(get_checks_dir(), {})
    for check_name, check_content in checks_dir.items():
        suffix = get_checks_suffix().split("/")
        for i in range(len(suffix)):
            if check_name.endswith(suffix[i]):
                second_check = check_name[: -len(suffix[i])] + suffix[1 - i]
                content = {check_name: check_content, second_check: checks_dir.get(second_check, None)}
                checks.append(Check(content, category=CheckCategoryEnum.runtime, ID=hw.ID, timestamp=hw.timestamp))
            else:
                checks.append(
                    Check(
                        {check_name: check_content},
                        category=CheckCategoryEnum.validate,
                        ID=hw.ID,
                        timestamp=hw.timestamp,
                    )
                )

    return checks


def get_solution(hw: Homework) -> Solution:
    """

    :param hw:
    :return:
    """
    pass
