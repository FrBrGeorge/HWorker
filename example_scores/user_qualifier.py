from hworker.depot.objects import TaskScore


def _filter_by_name(name: str, scores: list[TaskScore]):
    return filter(lambda x: x.name == name, scores)


def average(scores: list[TaskScore]) -> float:
    return sum([score.rating for score in scores]) / len(list(scores))


def attendance(scores: list[TaskScore]) -> float:
    return len(list(_filter_by_name("attendance", scores)))
