import os
from functools import cache

from sqlalchemy import create_engine, Engine, event
from sqlalchemy.orm import sessionmaker

from .models import Base

__all__ = ["get_engine", "get_Session"]

from ... import config

_database_path = "data.db"


def _create_database_tables(engine: Engine):
    Base.metadata.create_all(engine)


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.close()


@cache
def get_engine():
    global _database_path
    if not _database_path.endswith("test.db"):
        _database_path = config.get_depot_info()["database_path"]
    database_path = f"sqlite:///{os.path.abspath(_database_path)}"
    engine = create_engine(database_path, pool_size=10, max_overflow=40, isolation_level="AUTOCOMMIT")

    _create_database_tables(engine)

    return engine


@cache
def get_Session():
    return sessionmaker(get_engine())
