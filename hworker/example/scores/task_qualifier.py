from typing import Iterable
from hworker.depot.objects import CheckResult, CheckCategoryEnum
import re


def _reID(regex, results):
    if isinstance(regex, str):
        regex = re.compile(regex)
    return filter(lambda res: regex.match(res.ID), results)


def _filter_by_category(category: CheckCategoryEnum, results: list[CheckResult]):
    return filter(lambda x: x.category == category, results)


def _get_field(name: str, scores: Iterable[CheckResult]):
    return map(lambda x: getattr(x, name), scores)


def average(results: list[CheckResult]) -> float:
    return sum([check.rating for check in results]) / len(results) if len(results) != 0 else 0


def attendance(results):
    for r in _reID("The teacher:first/attendance@.*", results):
        if r.rating > 0:
            return 1.0
    return 0.0


def deadline(results):
    res = list(_reID("The teacher:first/deadline@.*", results))
    return min((r.rating for r in res), default=0)
