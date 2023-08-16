"""Database module initialisation."""
from .models import Base
from .common import get_engine
from .functions import store, search, delete


def init_db():
    models.Base.metadata.create_all(get_engine())
