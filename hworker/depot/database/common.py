import os
from functools import cache

from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker

from .models import Base

__all__ = ["get_engine", "get_Session"]

_database_path = "data.db"


def _create_database_tables(engine: Engine):
    Base.metadata.create_all(engine)


@cache
def get_engine():
    database_path = f"sqlite:///{os.path.abspath(_database_path)}"
    engine = create_engine(database_path, pool_size=10, max_overflow=40)

    _create_database_tables(engine)

    return engine


@cache
def get_Session():
    return sessionmaker(get_engine())
