"""Universal check function"""

from datetime import datetime

from .runtime import runtime_wo_store
from .validate import validate_wo_store
from ..depot.objects import Check, Solution, CheckCategoryEnum, CheckResult, VerdictEnum


def check(checker: Check, solution: Solution, check_num: int = 0) -> CheckResult:
    """Universal check run on given solution

    :param checker: check object
    :param solution: solution object
    :param check_num: optional parameter, will be used for parallelization
    :return: -
    """

    match checker.category if isinstance(checker, Check) else checker:
        case CheckCategoryEnum.runtime:
            return runtime_wo_store(checker, solution, check_num)
        case CheckCategoryEnum.validate:
            return validate_wo_store(checker, solution, check_num)
        case _:
            return CheckResult(
                ID=checker.ID + solution.ID,
                USER_ID=solution.USER_ID,
                TASK_ID=solution.TASK_ID,
                timestamp=datetime.now().timestamp(),
                rating=0.0,
                category=checker.category,
                stderr=b"",
                stdout=b"",
                check_ID=checker.ID,
                solution_ID=solution.ID,
                verdict=VerdictEnum.missing,
            )


def get_result_ID(checker: Check, solution: Solution) -> str:
    """CheckResult ID generator

    :param checker: check object
    :param solution: solution object
    :return: CheckResult ID
    """
    return checker.ID + solution.ID
