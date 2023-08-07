"""Tasks meta-information checks and check results"""

from ..depot import store
from ..depot.objects import Check, Solution, CheckResult, CheckCategoryEnum
from ..log import get_logger


from importlib import import_module


def validate(validator: Check, solution: Solution, check_num: int = 0) -> None:
    """Runs validator on a given solution

    :param validator:
    :param solution:
    :param check_num:
    :return:
    """
    # TODO: add check nums for parallel work
    get_logger(__name__).info(f"Checking solution {solution.ID} with {validator.ID} validator")
    if validator.category == CheckCategoryEnum.validate:
        # TODO: change check parsing
        validators = {}
        for name, b in validator.content:
            import_module(name)
            for f in dir(validator):
                if not f.startswith("_") and callable(f):
                    validators[f"{name}.{f}"] = name

        for name, v in validators:
            result = v(solution)
            check_result = CheckResult(rating=result,
                                       category=validator.category,
                                       check_ID=validator.ID,
                                       solution_ID=solution.ID)
            store(check_result)
    else:
        get_logger(__name__).warning(f"The {validator.ID} object given to validate is not a validator")
