"""All database models."""
from sqlalchemy import *
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
import datetime

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

    content: Mapped[bytes] = mapped_column(LargeBinary)  # pickled dict

    # noinspection PyTypeChecker
    def __init__(self, content: bytes = None, **kwargs):
        """Initialise homework object"""
        super().__init__(**kwargs)
        self.content = content
