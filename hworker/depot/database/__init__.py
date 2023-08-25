"""Database module initialisation."""
from .common import get_engine
from .functions import store, search, delete
from .models import Base
