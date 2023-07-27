"""Interface objects for depot management"""
import enum
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
    content: dict[str, bytes]  # filepath : file_content
    is_broken: bool
    _is_versioned: bool = True

    def __init__(self, content: dict[str, bytes] = None, is_broken: bool = None, **kwargs):
        super().__init__(**kwargs)
        self.content = content
        self.is_broken = is_broken


class CheckCategoryEnum(enum.Enum):
    runtime = 1
    validate = 2
    plagiary = 3


class Check(StoreObject):
    name: str  # name of this check for searching
    content: dict[str, bytes]  # filename : file_content
    category: CheckCategoryEnum
    _is_versioned: bool = True

    def __init__(self, content: dict[str, bytes] = None, category: CheckCategoryEnum = None, **kwargs):
        super().__init__(**kwargs)
        self.content = content
        self.category = category


class Solution(StoreObject):
    content: dict[str, bytes]  # filepath : file_content
    checks: list[str]  # list[ID]
    _is_versioned: bool = True

    def __init__(self, content: dict[str, bytes] = None, checks: list[str] = None, **kwargs):
        super().__init__(**kwargs)
        self.content = content
        self.checks = checks


class VerdictEnum(enum.Enum):
    failed = 1


class CheckResult(StoreObject):
    rating: float
    category: CheckCategoryEnum
    check_ID: str
    solution_ID: str
    verdict: VerdictEnum
    stdout: bytes
    stderr: bytes
    _is_versioned: bool = False

    def __init__(
        self,
        rating: float = None,
        category: CheckCategoryEnum = None,
        check_ID: str = None,
        solution_ID: str = None,
        verdict: VerdictEnum = None,
        stdout: bytes = None,
        stderr: bytes = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.rating = rating
        self.category = category
        self.check_ID = check_ID
        self.solution_ID = solution_ID
        self.verdict = verdict
        self.stdout = stdout
        self.stderr = stderr


class Plagiary(StoreObject):
    content: list[str]  # ID's ?? or list[Homework] or list[Solution]


class ScoreFunction(StoreObject):
    content: str
    _is_versioned: bool = False


class PartialScore(StoreObject):
    content: float
    _is_versioned: bool = False


class Formula(StoreObject):
    content: str
    _is_versioned: bool = False


class Score(StoreObject):
    content: str
    _is_versioned: bool = False


class Criteria:
    _pos_conditions: dict[str, str] = {
        "==": "__eq__",
        "!=": "__ne__",
        "<": "__lt__",
        "<=": "__le__",
        ">": "__gt__",
        ">=": "__ge__",
        "like": "like",
        "startswith": "startswith",
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
