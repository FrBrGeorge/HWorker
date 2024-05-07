"""Interface objects for depot management"""
import datetime
import enum
from collections.abc import Iterator
from inspect import getmembers_static
from typing import Any
from numbers import Real


def is_field(name: str, obj: Any) -> bool:
    """Check if the object with certain name can be treated as "public data field"

    @param name: Name of the object
    @obj: The object itself
    @return: If the object seems to be data field

    For now, it just checks fo obj not to be a callable and name not to start with '_'"""
    return bool(name) and not (name.startswith("_") or callable(obj))


class StoreObject:
    ID: str  # Unique ID
    USER_ID: str  # User name
    TASK_ID: str  # Task name
    timestamp: float  # Timestamp
    _is_versioned: bool
    _public_fields: set[str] = {"ID", "USER_ID", "TASK_ID", "timestamp"}

    def __init__(self, ID: str = None, USER_ID: str = None, TASK_ID: str = None, timestamp: float = None, **kwargs):
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

    def is_versioned(self):
        """Returns _is_versioned fields"""
        return self._is_versioned

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

    def _stringify(self, key, value):
        """Make object field value representaion more human readable"""
        if key == "timestamp" and isinstance(value, Real):
            return str(datetime.datetime.fromtimestamp(value))
        return value

    def __str__(self):
        """Object representation with only public fields"""
        return ", ".join(f"{key}={self._stringify(key, value)}" for key, value in self.items())

    def __repr__(self):
        """Object representation with ALL fields"""
        return ", ".join(f"{key}={value}" for key, value in self)

    def __eq__(self, other):
        """Compares objects by ALL fields"""
        return list(self) == list(other)

    def __matmul__(self, other):
        """Return True if self is almost equal (by comparing public fields only) to other"""
        return list(self.items()) == list(other.items())


class RawData(StoreObject):
    content: bytes
    _is_versioned: bool = False

    def __init__(self, content: bytes = None, **kwargs):
        fields = {"USER_ID": ".", "TASK_ID": ".", "timestamp": datetime.datetime.now().timestamp()}
        super().__init__(**(fields | kwargs))
        self.content = content


class FileObject:
    content: bytes
    timestamp: float

    def __init__(self, content: bytes = None, timestamp: float = None):
        self.content = content
        self.timestamp = timestamp

    def __eq__(self, other):
        return isinstance(other, FileObject) and all(
            [getattr(self, field) == getattr(other, field) for field in ["content", "timestamp"]]
        )

    def __str__(self):
        return ", ".join(map(str, [self.content, self.timestamp]))

    def __repr__(self):
        return str(self)


class Homework(StoreObject):
    content: dict[str, FileObject]  # filepath : file_content
    is_broken: bool
    _is_versioned: bool = True

    def __init__(self, content: dict[str, FileObject] = None, is_broken: bool = None, **kwargs):
        super().__init__(**kwargs)
        self.content = content
        self.is_broken = is_broken


class CheckCategoryEnum(enum.Enum):
    runtime = 1
    validate = 2
    plagiary = 3


class Check(StoreObject):
    content: dict[str, bytes]  # filename : file_content
    category: CheckCategoryEnum
    _is_versioned: bool = False
    _public_fields: set[str] = StoreObject._public_fields | {"category"}

    def __init__(self, content: dict[str, bytes] = None, category: CheckCategoryEnum = None, **kwargs):
        super().__init__(**kwargs)
        self.content = content
        self.category = category


class Solution(StoreObject):
    content: dict[str, bytes]  # filepath : file_content
    checks: dict[str, list]  # list[ID]
    _is_versioned: bool = True

    def __init__(self, content: dict[str, bytes] = None, checks: dict[str] = None, **kwargs):
        super().__init__(**kwargs)
        self.content = content
        self.checks = checks


class VerdictEnum(enum.Enum):
    passed = 0
    failed = 1
    missing = -1


class CheckResult(StoreObject):
    rating: float
    category: CheckCategoryEnum
    check_ID: str
    check_timestamp: float
    solution_ID: str
    solution_timestamp: float
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
        check_timestamp: float = None,
        solution_ID: str = None,
        solution_timestamp: float = None,
        verdict: VerdictEnum = None,
        stdout: bytes = None,
        stderr: bytes = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.rating = rating
        self.category = category
        self.check_ID = check_ID
        self.check_timestamp = check_timestamp
        self.solution_ID = solution_ID
        self.solution_timestamp = solution_timestamp
        self.verdict = verdict
        self.stdout = stdout
        self.stderr = stderr


class TaskQualifier(StoreObject):
    """Calculates a TaskScore from all CheckResult's grouped by certain TASK_ID, USER_ID pair"""

    name: str
    # TODO to be deleted
    content: str
    _public_fields: set[str] = {"ID", "timestamp"}
    _is_versioned: bool = False

    def __init__(self, name: str = None, content: str = None, **kwargs):
        kwargs["USER_ID"] = ""
        kwargs["TASK_ID"] = ""
        super().__init__(**kwargs)
        self.name = name
        self.content = content


class TaskScore(StoreObject):
    """Scoring some aspect for TASK_ID, USER_ID"""

    name: str
    rating: float
    _public_fields: set[str] = {"ID", "USER_ID", "TASK_ID", "name", "rating", "timestamp"}
    _is_versioned: bool = False

    def __init__(self, name: str = None, rating: float = None, **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.rating = rating


class UserQualifier(StoreObject):
    """Calculates a userScore from all TaskScores's for certain USER_ID"""

    name: str
    # TODO to be deleted
    content: str
    _public_fields: set[str] = {"ID", "timestamp"}
    _is_versioned: bool = False

    def __init__(self, name: str = None, content: str = None, **kwargs):
        kwargs["USER_ID"] = ""
        kwargs["TASK_ID"] = ""
        super().__init__(**kwargs)
        self.name = name
        self.content = content


class UserScore(StoreObject):
    """Scoring some aspect for USER_ID"""

    name: str
    rating: float
    _public_fields: set[str] = {"ID", "USER_ID", "TASK_ID", "name", "rating", "timestamp"}
    _is_versioned: bool = False

    def __init__(self, name: str = None, rating: float = None, **kwargs):
        kwargs["TASK_ID"] = ""
        super().__init__(**kwargs)
        self.name = name
        self.rating = rating


class Formula(StoreObject):
    """Overall formulae over all UserScore's for certain USER_ID"""

    name: str
    # TODO to be deleted
    content: str
    _public_fields: set[str] = {"ID", "timestamp"}
    _is_versioned: bool = False

    def __init__(self, name: str = None, content: str = None, **kwargs):
        kwargs["USER_ID"] = ""
        kwargs["TASK_ID"] = ""
        super().__init__(**kwargs)
        self.name = "Final mark"
        self.content = content


class FinalScore(StoreObject):
    """Final user verdict"""

    name: str
    rating: str
    _public_fields: set[str] = {"ID", "USER_ID", "TASK_ID", "rating", "timestamp"}
    _is_versioned: bool = False

    def __init__(self, name: str = None, rating: str = None, **kwargs):
        kwargs["TASK_ID"] = ""
        super().__init__(**kwargs)
        self.name = "Final mark"
        self.rating = rating


class UpdateTime(StoreObject):
    """Latest update time for module"""

    name: str
    _public_fields: set[str] = {"ID", "timestamp"}
    _is_versioned: bool = False

    def __init__(self, name: str = None, **kwargs):
        kwargs["ID"] = f"{name}"
        kwargs["USER_ID"] = ""
        kwargs["TASK_ID"] = ""
        super().__init__(**kwargs)
        self.name = name


class Plagiary(StoreObject):
    content: list[str]  # ID's ?? or list[Homework] or list[Solution]


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
