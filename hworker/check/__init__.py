"""Universal check function"""

from .runtime import runtime_wo_store
from .validate import validate_wo_store
from ..depot.objects import Check, Solution, CheckCategoryEnum, CheckResult


def check(checker: Check, solution: Solution, check_num: int = 0) -> CheckResult:
    """Universal check run on given solution

    :param checker: check object
    :param solution: solution object
    :param check_num: optional parameter, will be used for parallelization
    :return: -
    """
    match checker.category:
        case CheckCategoryEnum.runtime:
            return runtime_wo_store(checker, solution, check_num)
        case CheckCategoryEnum.validate:
            return validate_wo_store(checker, solution, check_num)


def get_result_ID(checker: Check, solution: Solution) -> str:
    """CheckResult ID generator

    :param checker: check object
    :param solution: solution object
    :return: CheckResult ID
    """
    return checker.ID + solution.ID
