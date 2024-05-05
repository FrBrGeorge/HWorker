from operator import attrgetter

from hworker.depot.objects import UserScore
from hworker.depot import search

__all__ = ["final"]


def _filter_by_name(name: str, scores: list[UserScore]):
    return filter(lambda x: x.name == name, scores)


def _get_average():
    vals = list(map(attrgetter("rating"), search(UserScore)))
    return sum(vals) / len(vals) if len(vals) != 0 else 0


def final(scores: list[UserScore]) -> str:
    ratings = list(map(attrgetter("rating"), scores))
    cur_average = sum(ratings) / len(ratings) if len(ratings) != 0 else 0
    return "Отлично" if cur_average > _get_average() else "Хорошо"
