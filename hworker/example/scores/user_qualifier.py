from typing import Iterable

from hworker.depot.objects import TaskScore


def _filter_by_name(name: str, scores: list[TaskScore]):
    return filter(lambda x: x.name == name, scores)


def _get_field(name: str, scores: Iterable[TaskScore]):
    return map(lambda x: getattr(x, name), scores)


def average(scores: list[TaskScore]) -> float:
    return sum([score.rating for score in scores]) / len(scores) if len(scores) != 0 else 0


def attendance(scores: list[TaskScore]) -> float:
    return sum(_get_field("rating", _filter_by_name("attendance", scores)))
