"""Database module initialisation."""
from .models import Base
from .common import engine, Session
from .functions import store, search, delete

models.Base.metadata.create_all(engine)
