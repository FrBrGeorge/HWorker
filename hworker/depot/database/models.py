"""All database models."""
from sqlalchemy import *
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
import datetime

from ..objects import CheckCategoryEnum, VerdictEnum

_default_datetime = datetime.datetime.fromisoformat("2009-05-17 20:09:00")


class Base(DeclarativeBase):
    """Base Class for all objects"""

    ID: Mapped[str] = mapped_column(String, primary_key=True, nullable=False)
    USER_ID: Mapped[str] = mapped_column(String, nullable=False)
    TASK_ID: Mapped[str] = mapped_column(String, nullable=False)
    timestamp: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)

    # noinspection PyTypeChecker
    def __init__(self, ID: str = None, USER_ID: str = None, TASK_ID: str = None, timestamp: int = None, **kwargs):
        """Initialise base object"""
        super().__init__(**kwargs)
        self.ID = ID
        self.USER_ID = USER_ID
        self.TASK_ID = TASK_ID
        self.timestamp = timestamp


class Homework(Base):
    """Class for homework from one student for one task"""

    __tablename__ = "homework"

    content: Mapped[dict] = mapped_column(PickleType)
    is_broken: Mapped[bool] = mapped_column(Boolean)

    # noinspection PyTypeChecker
    def __init__(self, content: dict = None, is_broken: bool = None, **kwargs):
        """Initialise Homework object"""
        super().__init__(**kwargs)
        self.content = content
        self.is_broken = is_broken


class Check(Base):
    """Class for homework from one student for one task"""

    __tablename__ = "check"

    name: Mapped[str] = mapped_column(String)
    content: Mapped[dict] = mapped_column(PickleType)
    category: Mapped[CheckCategoryEnum] = mapped_column(Enum(CheckCategoryEnum))

    # noinspection PyTypeChecker
    def __init__(self, content: dict = None, category: CheckCategoryEnum = None, **kwargs):
        """Initialise Check object"""
        super().__init__(**kwargs)
        self.content = content
        self.category = category


class Solution(Base):
    """Class for homework from one student for one task"""

    __tablename__ = "solution"

    content: Mapped[dict] = mapped_column(PickleType)
    checks: Mapped[list] = mapped_column(PickleType)

    # noinspection PyTypeChecker
    def __init__(self, content: dict = None, checks: list = None, **kwargs):
        """Initialise Solution object"""
        super().__init__(**kwargs)
        self.content = content
        self.checks = checks


class CheckResult(Base):
    """Class for homework from one student for one task"""

    __tablename__ = "check_result"

    rating: Mapped[float] = mapped_column(Float)
    category: Mapped[CheckCategoryEnum] = mapped_column(Enum(CheckCategoryEnum))
    check_ID: Mapped[str] = mapped_column(String)
    solution_ID: Mapped[str] = mapped_column(String)
    verdict: Mapped[VerdictEnum] = mapped_column(Enum(VerdictEnum))
    stdout: Mapped[bytes] = mapped_column(LargeBinary)
    stderr: Mapped[bytes] = mapped_column(LargeBinary)

    # noinspection PyTypeChecker
    def __init__(
        self,
        rating: float = None,
        category: CheckCategoryEnum = None,
        check_ID: str = None,
        solution_ID: str = None,
        verdict: VerdictEnum = None,
        stdout: bytes = None,
        stderr: bytes = None,
        **kwargs
    ):
        """Initialise CheckResult object"""
        super().__init__(**kwargs)
        self.rating = rating
        self.category = category
        self.check_ID = check_ID
        self.solution_ID = solution_ID
        self.verdict = verdict
        self.stdout = stdout
        self.stderr = stderr
