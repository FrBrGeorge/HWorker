import os


from .app import app
from ..log import get_logger


def run_server():
    get_logger(__name__).info("Publish initialized...")
    if "DEBUG_ENVIRONMENT" in os.environ:
        app.run(debug=True, use_debugger=True, use_reloader=False)
