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
    def __init__(self, ID: str, USER_ID: str, TASK_ID: str, timestamp: int, **kwargs):
        """Initialise base object"""
        super().__init__(**kwargs)
        self.ID = ID
        self.USER_ID = USER_ID
        self.TASK_ID = TASK_ID
        self.timestamp = timestamp

    def __str__(self):
        return f"ID = {self.ID:>10}, USER_ID={self.USER_ID:>10}, TASK_ID={self.TASK_ID:>10}, timestamp={self.timestamp:>10}"

    def __repr__(self):
        return self.__str__()


class Homework(Base):
    """Class for homework from one student for one task"""

    __tablename__ = "homework"

    data: Mapped[bytes] = mapped_column(LargeBinary)  # pickled dict

    # noinspection PyTypeChecker
    def __init__(self, data: bytes, **kwargs):
        """Initialise homework object"""
        super().__init__(**kwargs)
        self.data = data

    def __str__(self):
        return super().__str__() + f", data={self.data[:10]}"

    def __repr__(self):
        return self.__str__()
