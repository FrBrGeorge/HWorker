import os
import shutil
from pathlib import Path

from paste.translogger import TransLogger
from waitress import serve

from ..config import get_publish_info
from ..log import get_logger

_request_log_format = '%(REMOTE_ADDR)15s - "%(REQUEST_METHOD)s %(REQUEST_URI)-50s %(HTTP_VERSION)s" %(status)s'


def _get_app():
    from .app import app

    return app


def run_server():
    app = _get_app()

    get_logger(__name__).info("Publish initializing...")
    host, port = get_publish_info()["host"], int(get_publish_info()["port"])
    if "DEBUG_ENVIRONMENT" in os.environ:
        host = "localhost"
        app.run(host=host, port=port, debug=True, use_debugger=True, use_reloader=False)
    else:
        if not 1 < len(set(app.config.get("SECRET_KEY", "replace this junky text"))) < 17:
            get_logger(__name__).error(
                "Aborting publishing because your publish SECRET_KEY is unset. "
                "Please run\n    python3 -c 'import secrets; print(secrets.token_hex())'\n"
                "and paste key to your config file like this:\n"
                '    [publish]\n    …\n    SECRET_KEY = "64 hexadecimal digits"'
            )
            return
        serve(TransLogger(app, setup_console_handler=False, format=_request_log_format), host=host, port=port)


def generate_static_html(root: Path):
    urls = ["/"]
    files = ["index.html"]

    package_root = Path(__path__[0])
    static_name = "static"

    shutil.copytree(package_root / static_name, root / static_name, dirs_exist_ok=True)

    with _get_app().test_client() as client:
        for index, url in enumerate(urls):
            page = client.get(url).data
            with open(root.joinpath(files[index]), "wb") as f:
                f.write(page)
