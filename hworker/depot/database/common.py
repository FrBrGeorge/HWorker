import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

__all__ = ["engine", "Session"]

__database_filename = os.environ.get("HWORKER_DATABASE_FILENAME", "data.db")

database_path = "sqlite:///" + os.path.abspath(f"./{__database_filename}")
engine = create_engine(database_path, pool_size=10, max_overflow=40)
Session = sessionmaker(engine)
