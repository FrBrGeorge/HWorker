"""Tasks meta-information checks and check results"""
import os

from ..depot import store
from ..depot.objects import Check, Solution, CheckResult, CheckCategoryEnum, VerdictEnum
from ..log import get_logger

from importlib import import_module
import time
from datetime import date
from importlib import import_module


def validate_wo_store(validator: Check, solution: Solution, check_num: int = 0) -> CheckResult:
    """Runs validator on a given solution and returns result object

    :param validator:
    :param solution:
    :param check_num:
    :return:
    """
    # TODO: add check nums for parallel work
    # TODO: change check parsing
    validators = {}
    for name, b in validator.content.items():
        with open(f"{name}.py", "wb") as n:
            n.write(b)
        module = import_module(name)
        os.remove(f"{name}.py")
        for f in dir(module):
            if not f.startswith("_"):
                validators[f"{name}.{f}"] = getattr(module, name)

    for name, v in validators.items():
        stderr, result = b"", 0.0
        try:
            result = v(solution)
        except Exception as error:
            stderr = str(error).encode()

        return CheckResult(
            ID=validator.ID + solution.ID,
            USER_ID=solution.USER_ID,
            TASK_ID=solution.TASK_ID,
            timestamp=date.fromtimestamp(time.time()),
            rating=result,
            category=validator.category,
            stderr=stderr,
            check_ID=validator.ID,
            solution_ID=solution.ID,
            verdict=VerdictEnum.passed if not stderr else VerdictEnum.failed,
        )


def validate(validator: Check, solution: Solution, check_num: int = 0) -> None:
    """Runs validator on a given solution and save the result

    :param validator:
    :param solution:
    :param check_num:
    :return:
    """
    get_logger(__name__).info(f"Checking solution {solution.ID} with {validator.ID} validator")
    if validator.category == CheckCategoryEnum.validate:
        result = validate_wo_store(validator, solution, check_num)
        store(result)
    else:
        get_logger(__name__).warning(f"The {validator.ID} object given to validate is not a validator")
