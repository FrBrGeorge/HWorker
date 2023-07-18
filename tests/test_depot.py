"""Tests for depot"""

import pytest

from hworker.depot import store, search, delete
from hworker.depot.objects import *


class TestDepot:
    def test_store(self):
        h = Homework(ID="10", USER_ID="11", TASK_ID="12", timestamp=12345, data={"lalala": b"dasdada"})
        store(h)
        assert h in list(search(Homework))
