"""Tasks meta-information checks and check results"""
import sys
from pathlib import Path

from ..depot import store, search
from ..depot.objects import Check, Solution, CheckResult, CheckCategoryEnum, VerdictEnum, Criteria
from ..log import get_logger
from ..config import get_check_directory, get_validator_name, get_version_validator_name

import time
from datetime import datetime
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

    name, b = list(validator.content.items())[0]
    module_path = Path(get_check_directory()) / name
    with open(module_path, "wb") as m:
        m.write(b)
    module = import_module(name.rpartition(".")[0])

    validator_type = None
    if get_validator_name() in dir(module):
        validator_type = get_validator_name()
    elif get_version_validator_name() in dir(module):
        validator_type = get_version_validator_name()

    if validator_type:
        stderr, result, v = b"", 0.0, getattr(module, validator_type)
        if validator_type == get_validator_name():
            try:
                if validator_type == get_validator_name():
                    result = v(solution)
                else:
                    result = v(search(Solution, Criteria("ID", "==", solution.ID)))
            except Exception as error:
                stderr = str(error).encode()
            finally:
                module_path.unlink(missing_ok=True)

        return CheckResult(
            ID=validator.ID + solution.ID,
            USER_ID=solution.USER_ID,
            TASK_ID=solution.TASK_ID,
            timestamp=datetime.now().timestamp(),
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
