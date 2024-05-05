import re
from typing import Iterable
from hworker.depot.objects import TaskScore


def _filter_by_name(name: str, scores: list[TaskScore]):
    return filter(lambda x: x.name == name, scores)


def _get_field(name: str, scores: Iterable[TaskScore]):
    return map(lambda x: getattr(x, name), scores)


def _filter(scores: list, name: str = "", ident: str = ""):
    ire = re.compile(ident)
    return filter(lambda x: x.name == name and ire.search(x.ID), scores)


def average(scores: list[TaskScore]) -> float:
    return sum([score.rating for score in scores]) / len(scores)


def attendance(scores: list[TaskScore]) -> float:
    ascores = list(_filter_by_name("attendance", scores))
    return sum(_get_field("rating", ascores)) / len(ascores)


def deadline(scores: list) -> float:
    dscores = list(_filter(scores, name="deadline", ident=".*"))
    return sum(score.rating for score in dscores) / len(dscores)
