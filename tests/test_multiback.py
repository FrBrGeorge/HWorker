#!/usr/bin/env python3
"""
Test for multibackend
"""
import importlib
import sys

import pytest

DOCSTRING = "Sample method"
PARAMS = [[_ := list("ABC"[: i + 1]), _ if k else "_methods"] for i in range(3) for k in range(2)]
PARNAMES = ["-".join(("".join(p[0]), "".join(p[1]))) for p in PARAMS]


@pytest.fixture(params=PARAMS, ids=PARNAMES)
def genmodule(tmp_path, request):
    """Create a test package with one method in each backand"""
    modpath = tmp_path / "multiback_client"
    sys.path.insert(0, str(tmp_path.absolute()))
    modpath.mkdir()
    (modpath / "__init__.py").write_text(
        f"""
from hworker.multiback import init_backends
def _methods():
    return {request.param[0]}

def method(arg: int) -> int:
    "{DOCSTRING}"
    return arg

init_backends({request.param[0]}, uniform=True)
"""
    )
    for n, back in enumerate(request.param[0]):
        (modpath / f"{back}.py").write_text(
            f"""
def method(i):
    return {n} + i
"""
        )
    yield request.param[0]
    sys.path.remove(str(tmp_path.absolute()))


class TestMultiback:
    def test_full(self, genmodule):
        """Import test package, call aggregated methods"""
        backends = genmodule
        import multiback_client

        importlib.reload(multiback_client)  # To prevent caching
        assert multiback_client.method.__doc__ == DOCSTRING
        res = multiback_client.method(0)
        assert res == (len(backends) * (len(backends) - 1)) // 2
