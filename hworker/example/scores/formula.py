from hworker.depot.objects import UserScore


def _filter_by_name(name: str, scores: list[UserScore]):
    return filter(lambda x: x.name == name, scores)


def final(scores: list[UserScore]) -> str:
    return "Отлично"
