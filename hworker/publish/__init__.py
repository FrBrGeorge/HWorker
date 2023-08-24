import os
from pathlib import Path
import shutil

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
