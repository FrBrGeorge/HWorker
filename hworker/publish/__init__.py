import os


from .app import app
from ..log import get_logger
from ..config import get_publish_info


def run_server():
    get_logger(__name__).info("Publish initialized...")
    host, port = get_publish_info()["host"], int(get_publish_info()["port"])
    if "DEBUG_ENVIRONMENT" in os.environ:
        host = "localhost"
        app.run(host=host, port=port, debug=True, use_debugger=True, use_reloader=False)
    else:
        app.run(host=host, port=port, debug=False, use_debugger=False, use_reloader=False)
