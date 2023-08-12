from .. import config
from .. import multiback


def download_all() -> None:
    """Download all homeworks from all backends"""


multiback.init_backends(backends=config.get_deliver_modules)
