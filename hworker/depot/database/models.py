"""All database models."""
import datetime

from sqlalchemy import *
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from ..objects import CheckCategoryEnum, VerdictEnum

_default_datetime = datetime.datetime.fromisoformat("2009-05-17 20:09:00")


class Base(DeclarativeBase):
    """Base Class for all objects"""

    ID: Mapped[str] = mapped_column(String, primary_key=True, nullable=False)
    USER_ID: Mapped[str] = mapped_column(String, nullable=False)
    TASK_ID: Mapped[str] = mapped_column(String, nullable=False)
    timestamp: Mapped[float] = mapped_column(Float, primary_key=True, nullable=False)

    # noinspection PyTypeChecker
    def __init__(self, ID: str = None, USER_ID: str = None, TASK_ID: str = None, timestamp: int = None, **kwargs):
        """Initialise base object"""
        super().__init__(**kwargs)
        self.ID = ID
        self.USER_ID = USER_ID
        self.TASK_ID = TASK_ID
        self.timestamp = timestamp


class RawData(Base):
    __tablename__ = "rawdata"

    content: Mapped[bytes] = mapped_column(LargeBinary)

    # noinspection PyTypeChecker
    def __init__(self, content: bytes = None, **kwargs):
        super().__init__(**kwargs)
        self.content = content


class Homework(Base):
    __tablename__ = "homework"

    content: Mapped[dict] = mapped_column(PickleType)
    is_broken: Mapped[bool] = mapped_column(Boolean)

    # noinspection PyTypeChecker
    def __init__(self, content: dict = None, is_broken: bool = None, **kwargs):
        super().__init__(**kwargs)
        self.content = content
        self.is_broken = is_broken


class Check(Base):
    __tablename__ = "check"

    content: Mapped[dict] = mapped_column(PickleType)
    category: Mapped[CheckCategoryEnum] = mapped_column(Enum(CheckCategoryEnum))

    # noinspection PyTypeChecker
    def __init__(self, content: dict = None, category: CheckCategoryEnum = None, **kwargs):
        super().__init__(**kwargs)
        self.content = content
        self.category = category


class Solution(Base):
    __tablename__ = "solution"

    content: Mapped[dict] = mapped_column(PickleType)
    checks: Mapped[dict] = mapped_column(PickleType)

    # noinspection PyTypeChecker
    def __init__(self, content: dict = None, checks: dict = None, **kwargs):
        super().__init__(**kwargs)
        self.content = content
        self.checks = checks


class CheckResult(Base):
    __tablename__ = "check_result"

    rating: Mapped[float] = mapped_column(Float)
    category: Mapped[CheckCategoryEnum] = mapped_column(Enum(CheckCategoryEnum))
    check_ID: Mapped[str] = mapped_column(String)
    check_timestamp: Mapped[float] = mapped_column(Float)
    solution_ID: Mapped[str] = mapped_column(String)
    solution_timestamp: Mapped[float] = mapped_column(Float)
    verdict: Mapped[VerdictEnum] = mapped_column(Enum(VerdictEnum))
    stdout: Mapped[bytes] = mapped_column(LargeBinary)
    stderr: Mapped[bytes] = mapped_column(LargeBinary)

    # noinspection PyTypeChecker
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


class TaskQualifier(Base):
    __tablename__ = "task_qualifier"

    name: Mapped[str] = mapped_column(String)
    content: Mapped[str] = mapped_column(String)

    # noinspection PyTypeChecker
    def __init__(self, name: str = None, content: str = None, **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.content = content


class TaskScore(Base):
    __tablename__ = "task_score"

    name: Mapped[str] = mapped_column(String)
    rating: Mapped[float] = mapped_column(Float)

    # noinspection PyTypeChecker
    def __init__(self, name: str = None, rating: float = None, **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.rating = rating


class UserQualifier(Base):
    __tablename__ = "user_qualifier"

    name: Mapped[str] = mapped_column(String)
    content: Mapped[str] = mapped_column(String)

    # noinspection PyTypeChecker
    def __init__(self, name: str = None, content: str = None, **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.content = content


class UserScore(Base):
    __tablename__ = "user_score"

    name: Mapped[str] = mapped_column(String)
    rating: Mapped[float] = mapped_column(Float)

    # noinspection PyTypeChecker
    def __init__(self, name: str = None, rating: float = None, **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.rating = rating


class Formula(Base):
    __tablename__ = "formula"

    name: Mapped[str] = mapped_column(String)
    content: Mapped[str] = mapped_column(String)

    # noinspection PyTypeChecker
    def __init__(self, name: str = None, content: str = None, **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.content = content


class FinalScore(Base):
    __tablename__ = "final_score"

    name: Mapped[str] = mapped_column(String)
    rating: Mapped[str] = mapped_column(String)

    # noinspection PyTypeChecker
    def __init__(self, name: str = None, rating: str = None, **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.rating = rating


class UpdateTime(Base):
    __tablename__ = "update_time"

    name: Mapped[str] = mapped_column(String)

    # noinspection PyTypeChecker
    def __init__(self, name: str = None, update_datetime: datetime.datetime = None, **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.update_datetime = update_datetime
