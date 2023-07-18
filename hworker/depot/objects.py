"""Interface objects for depot management"""
import inspect
from typing import Any


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


class Homework(StoreObject):
    data: dict[str, bytes]  # filename : file_content
    _is_versioned = True

    def __init__(self, data: dict[str, bytes] = None, **kwargs):
        super().__init__(**kwargs)
        self.data = data


class Test(StoreObject):
    obj: dict[str, str]  # just dict object, for storage just pickled
    category: str  # needs to be enum
    _is_versioned = True


class Solution(StoreObject):
    obj: dict[str, str]  # filename with path: file text
    tests: list[str]  # ?? or list[Test]?
    _is_versioned = True


class TestResult(StoreObject):
    obj: float
    category: str
    _is_versioned = False


class Plagiary(StoreObject):
    obj: list[str]  # ID's ?? or list[Homework] or list[Solution]


class ScoreFunction(StoreObject):
    obj: str
    _is_versioned = False


class PartialScore(StoreObject):
    obj: float
    _is_versioned = False


class Formula(StoreObject):
    obj: str
    _is_versioned = False


class Score(StoreObject):
    obj: str
    _is_versioned = False


def get_fields(obj: Any):
    if isinstance(obj, type):
        obj = obj()
    return obj.__dict__
