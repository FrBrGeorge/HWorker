from ..config import get_deliver_modules as _backends
from .. import multiback


def download_all() -> None:
    """Download all homeworks from all backends"""


multiback.init_backends(backends=_backends, methods=["download_all"])
