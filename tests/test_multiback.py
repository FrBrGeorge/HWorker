#!/usr/bin/env python3
"""
Test for multibackend
"""
import pytest
import sys
import os
import importlib

DOCSTRING = "Sample method"
PARAMS = [[_ := list("ABC"[: i + 1]), _ if k else "_methods"] for i in range(3) for k in range(2)]
PARNAMES = ["-".join(("".join(p[0]), "".join(p[1]))) for p in PARAMS]


@pytest.fixture(params=PARAMS, ids=PARNAMES)
def genmodule(tmp_path, request):
    """Create a test package with one method in each backand"""
    modpath = tmp_path / "multiback_client"
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
    yield tmp_path, request.param[0]


class TestMultiback:
    def test_full(self, genmodule):
        """Import test package, call aggregated mtthods"""
        libdir, backends = genmodule
        sys.path[0] = os.path.join(libdir.absolute())
        import multiback_client

        importlib.reload(multiback_client)  # To prevent caching
        assert multiback_client.method.__doc__ == DOCSTRING
        res = multiback_client.method(0)
        assert res == (len(backends) * (len(backends) - 1)) // 2
