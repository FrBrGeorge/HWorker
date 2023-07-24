"""Interface objects for depot management"""
from typing import Any


def get_field_from_object(obj: Any):
    return {name: value for name, value in obj.__dict__.items() if not name.startswith("_") and value is not None}


class StoreObject:
    ID: str  # Unique ID
    USER_ID: str  # User name
    TASK_ID: str  # Task name
    timestamp: int  # Timestamp
    _is_versioned: bool

    def __init__(self, ID: str = None, USER_ID: str = None, TASK_ID: str = None, timestamp: int = None, **kwargs):
        super().__init__(**kwargs)
        self.ID = ID
        self.USER_ID = USER_ID
        self.TASK_ID = TASK_ID
        self.timestamp = timestamp

    def __str__(self):
        return ", ".join([f"{key}={value}" for key, value in get_field_from_object(self).items()])

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        self_fields = get_field_from_object(self)
        other_fields = get_field_from_object(other)
        return self_fields == other_fields


class Homework(StoreObject):
    content: dict[str, bytes]  # filename : file_content
    _is_versioned = True

    def __init__(self, content: dict[str, bytes] = None, **kwargs):
        super().__init__(**kwargs)
        self.content = content


class Check(StoreObject):
    content: dict[str, str]  # just dict object, for storage just pickled
    category: str  # needs to be enum
    _is_versioned = True


class Solution(StoreObject):
    content: dict[str, str]  # filename with path: file text
    tests: list[str]  # ?? or list[Check]?
    _is_versioned = True


class CheckResult(StoreObject):
    content: float
    category: str
    _is_versioned = False


class Plagiary(StoreObject):
    content: list[str]  # ID's ?? or list[Homework] or list[Solution]


class ScoreFunction(StoreObject):
    content: str
    _is_versioned = False


class PartialScore(StoreObject):
    content: float
    _is_versioned = False


class Formula(StoreObject):
    content: str
    _is_versioned = False


class Score(StoreObject):
    content: str
    _is_versioned = False


class Criteria:
    _pos_conditions: dict[str, str] = {
        "==": "__eq__",
        "!=": "__ne__",
        "<": "__lt__",
        "<=": "__le__",
        ">": "__gt__",
        ">=": "__ge__",
    }

    field_name: str
    condition: str
    field_value: Any

    def __init__(self, field_name, condition, field_value):
        if condition not in self._pos_conditions:
            raise ValueError(f"Condition is not possible. Possible is {self._pos_conditions}")
        self.field_name = field_name
        self.condition = condition
        self.field_value = field_value

    def get_condition_function(self):
        return self._pos_conditions[self.condition]
