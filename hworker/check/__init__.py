"""Universal check function"""

from .runtime import runtime
from .validate import validate
from ..depot.objects import Check, Solution, CheckCategoryEnum


def check(checker: Check, solution: Solution, check_num: int = 0) -> None:
    """Universal check run on given solution

    :param checker: check object
    :param solution: solution object
    :param check_num: optional parameter, will be used for parallelization
    :return: -
    """
    match checker.category:
        case CheckCategoryEnum.runtime:
            runtime(checker, solution, check_num)
        case CheckCategoryEnum.validate:
            validate(checker, solution, check_num)
