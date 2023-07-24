#!/usr/bin/env python3
'''
Test for multibackend
'''
import pytest
import sys
import os
import importlib


@pytest.fixture(params=[["A"], ["A", "B"], ["A", "B", "C"]])
def tmp_libdir(tmp_path, request):
    """Create a test package with one method in each backand"""
    modpath = tmp_path / "multiback_client"
    modpath.mkdir()
    (modpath / "__init__.py").write_text(f"""
from hworker.multiback import init_backends
init_backends({request.param}, ["method"], uniform=True)
""")
    for n, back in enumerate(request.param):
        (modpath / f"{back}.py").write_text(f"""
def method(i):
    return {n} + i
""")
    return tmp_path, request.param


def test_full(tmp_libdir):
    """Import test package, call aggregated mtthods"""
    libdir, backends = tmp_libdir
    sys.path[0] = os.path.join(libdir.absolute())
    import multiback_client
    importlib.reload(multiback_client)      # To prevent caching
    res = multiback_client.method(0)
    assert res == (len(backends) * (len(backends) - 1)) // 2
