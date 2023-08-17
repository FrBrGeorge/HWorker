import os
from functools import cache

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

__all__ = ["get_engine", "get_Session"]


@cache
def get_engine():
    __database_filename = os.environ.get("HWORKER_DATABASE_FILENAME", "data.db")
    database_path = "sqlite:///" + os.path.abspath(f"./{__database_filename}")
    return create_engine(database_path, pool_size=10, max_overflow=40)


@cache
def get_Session():
    return sessionmaker(get_engine())
