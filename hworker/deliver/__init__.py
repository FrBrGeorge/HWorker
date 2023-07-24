from ..config import get_deliver_modules
from ..multiback import init_backends

init_backends(backends=get_deliver_modules(), methods=["download_all"])
