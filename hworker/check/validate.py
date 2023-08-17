"""Tasks meta-information checks and check results"""
import sys
from pathlib import Path

from ..depot import store
from ..depot.objects import Check, Solution, CheckResult, CheckCategoryEnum, VerdictEnum
from ..log import get_logger
from ..config import get_check_directory

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
    if get_check_directory() not in sys.path:
        sys.path.append(get_check_directory())
    validators = {}
    for name, b in validator.content.items():
        module_path = Path(get_check_directory()) / name
        with open(module_path, "wb") as m:
            m.write(b)
        module = import_module(name.rpartition(".")[0])
        module_path.unlink(missing_ok=True)
        for f in dir(module):
            if not f.startswith("_"):
                validators[f"{name}.{f}"] = getattr(module, f)

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
