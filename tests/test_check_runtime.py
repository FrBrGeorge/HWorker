"""Tests for check.runtime"""

from hworker.check.runtime import python_runner, check

from io import BytesIO
from unittest.mock import patch
import os
import shutil

import pytest


@pytest.fixture()
def tmp_prog():
    """"""
    prog_path = os.path.join(os.path.join(os.path.abspath(os.sep), "tmp", "prog.py"))
    test_path = os.path.join(os.path.join(os.path.abspath(os.sep), "tmp", "test.in"))
    with open(prog_path, "wb") as prog:
        prog.write(b"a, b = eval(input())\n" 
                   b"print(max(a, b))")
    with open(test_path, "wb") as test:
        test.write(b"123, 345")

    yield prog_path, test_path

    os.remove(prog_path)
    os.remove(test_path)


class TestCheckRuntime:
    """"""
    def test_python_runner(self, tmp_prog):
        print(python_runner(*tmp_prog))
        assert python_runner(*tmp_prog) == (b'345\n', b'', 0)

    def test_checker(self):
        """"""
        # TODO
        pass
