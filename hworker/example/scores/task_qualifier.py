import random
from typing import Iterable

from hworker.depot.objects import CheckResult, CheckCategoryEnum


def _filter_by_category(category: CheckCategoryEnum, results: list[CheckResult]):
    return filter(lambda x: x.category == category, results)


def _get_field(name: str, scores: Iterable[CheckResult]):
    return map(lambda x: getattr(x, name), scores)


def average(results: list[CheckResult]) -> float:
    return sum([check.rating for check in results]) / len(results) if len(results) != 0 else 0


def attendance(results: list[CheckResult]) -> float:
    return random.randint(0, 1)
