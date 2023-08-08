"""Interface objects for depot management"""
import enum
from inspect import getmembers_static
from typing import Any
from collections.abc import Iterator


def is_field(name: str, obj: Any) -> bool:
    """Check if the object woth certain name can be treated as "public data field"

    @param name: Name of the object
    @obj: The object itself
    @return: If the object seems to be data field

    For now it just check fo obj not to be a callable and name not to start with '_'"""
    return bool(name) and not (name.startswith("_") or callable(obj))


class StoreObject:
    ID: str  # Unique ID
    USER_ID: str  # User name
    TASK_ID: str  # Task name
    timestamp: int  # Timestamp
    _is_versioned: bool
    _public_fields: set[str] = {"ID", "USER_ID", "TASK_ID", "timestamp"}

    def __init__(self, ID: str = None, USER_ID: str = None, TASK_ID: str = None, timestamp: int = None, **kwargs):
        super().__init__(**kwargs)
        self.ID = ID
        self.USER_ID = USER_ID
        self.TASK_ID = TASK_ID
        self.timestamp = timestamp

    def keys(self) -> Iterator[str]:
        """Returns all names of only public fields"""
        yield from self.items(0)

    def values(self) -> Iterator:
        """Returns all values of only public fields"""
        yield from self.items(1)

    def items(self, idx: int | slice = slice(0, 2)) -> Iterator:
        """Returns generator that yields only public fields"""
        return (kv[idx] for kv in getmembers_static(self) if kv[0] in self._public_fields)

    def __iter__(self):
        """Returns generator that yields ALL fields"""
        return (kv for kv in getmembers_static(self) if is_field(*kv))

    def __getitem__(self, idx: int | str) -> Any:
        match idx:
            case int(index):
                return list(self)[index]
            case str(name):
                return getattr(self, name)
        raise KeyError(f"Index type must be int ot str, not {idx.__class__}")

    def __str__(self):
        """Object representation with only public fields"""
        return ", ".join(f"{key}={value}" for key, value in self.items())

    def __repr__(self):
        """Object representation with ALL fields"""
        return ", ".join(f"{key}={value}" for key, value in self)

    def __eq__(self, other):
        """Compares objects by ALL fields"""
        return list(self) == list(other)

    def __matmul__(self, other):
        """Return True if self is almost equal (by comparing public fields only) to other"""
        return list(self.items()) == list(other.items())


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
    _public_fields: set[str] = StoreObject._public_fields | {"category"}

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
    passed = 0
    failed = 1


class CheckResult(StoreObject):
    rating: float
    category: CheckCategoryEnum
    check_ID: str
    solution_ID: str
    verdict: VerdictEnum
    stdout: bytes
    stderr: bytes
    _public_fields: set[str] = StoreObject._public_fields | {"category", "rating"}
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


class TaskQualify(StoreObject):
    """Calculates a TaskScore from all CheckResult's for certain TASK_ID, USER_ID pair"""
    content: str
    _is_versioned: bool = False


class TaskScore(StoreObject):
    """Scoring some aspect for TASK_ID, USER_ID"""
    rating: float
    _public_fields: set[str] = {"ID", "USER_ID", "TASK_ID", "timestamp", "content"}
    _is_versioned: bool = False


class UserQualify(StoreObject):
    """Calculates a userScore from all TaskScores's for certain USER_ID"""
    content: str
    _is_versioned: bool = False


class UserScore(StoreObject):
    """Scoring some aspect for USER_ID"""
    rating: float
    _public_fields: set[str] = {"ID", "USER_ID", "timestamp", "content"}
    _is_versioned: bool = False


class Formula(StoreObject):
    """Overall formulae over all UserScore's for certain USER_ID"""
    content: str
    _is_versioned: bool = False


class FinalScore(StoreObject):
    """Final user verdict"""
    rating: str
    _public_fields: set[str] = {"ID", "USER_ID", "timestamp", "content"}
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
