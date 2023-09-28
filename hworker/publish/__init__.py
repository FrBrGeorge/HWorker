import os
import shutil
from pathlib import Path

from ..config import get_publish_info
from ..log import get_logger

from waitress import serve
from paste.translogger import TransLogger


_request_log_format = '%(REMOTE_ADDR)15s - "%(REQUEST_METHOD)s %(REQUEST_URI)-50s %(HTTP_VERSION)s" %(status)s'


def run_server():
    from .app import app

    get_logger(__name__).info("Publish initializing...")
    host, port = get_publish_info()["host"], int(get_publish_info()["port"])
    if "DEBUG_ENVIRONMENT1" in os.environ:
        host = "localhost"
        app.run(host=host, port=port, debug=True, use_debugger=True, use_reloader=False)
    else:
        if app.config.get("SECRET_KEY", "replace this") == "replace this":
            get_logger(__name__).error(
                "Aborting start because your publish SECRET_KEY in unset. "
                "Please run: python3 -c 'import secrets; print(secrets.token_hex())' "
                "And paste key to your config file"
            )
            return
        serve(TransLogger(app, setup_console_handler=False, format=_request_log_format), host=host, port=port)


def generate_static_html(root: Path):
    urls = ["/"]
    files = ["index.html"]

    package_root = Path(__path__[0])
    static_name = "static"

    shutil.copytree(package_root / static_name, root / static_name, dirs_exist_ok=True)

    with app.test_client() as client:
        for index, url in enumerate(urls):
            page = client.get(url).data
            with open(root.joinpath(files[index]), "wb") as f:
                f.write(page)
