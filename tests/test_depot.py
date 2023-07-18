"""Tests for depot"""

from hworker.depot import store, search, delete
from hworker.depot.objects import *


class TestDepot:
    h1 = Homework(ID="10", USER_ID="11", TASK_ID="12", timestamp=12345, content={"lalala": b"dasdada"})

    def test_store(self):
        store(self.h1)
        assert self.h1 in list(search(Homework))

    def test_delete(self):
        delete(Homework)
        assert len(list(search(Homework))) == 0
