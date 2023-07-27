"""Tests for depot"""
import datetime

import pytest

from hworker.depot import *
from hworker.depot.objects import *


class TestDepotFunctions:
    h1 = Homework(ID="10", USER_ID="11", TASK_ID="12", timestamp=12345, content={"lalala": b"dasdada"}, is_broken=False)

    def test_store(self):
        store(self.h1)
        assert self.h1 in list(search(Homework))

    def test_delete(self):
        delete(Homework)
        assert len(list(search(Homework))) == 0


@pytest.fixture
def homeworks():
    for i in range(3):
        for name in ["Vanya", "Petya", "IIIGOR"]:
            store(
                Homework(
                    ID=f"{i}-{name}",
                    USER_ID=name,
                    TASK_ID="1",
                    timestamp=int(datetime.datetime(2023, 3 + i * 2, 5).timestamp()),
                    content={"1": b"2"},
                    is_broken=False,
                )
            )
    yield
    delete(Homework)


class TestDepotFunctionsWithCriteria:
    def test_get_all_homework(self, homeworks):
        assert len(list(search(Homework))) == 9

    def test_get_all_homework_from_user(self, homeworks):
        assert len(list(search(Homework, Criteria("USER_ID", "==", "IIIGOR")))) == 3

    def test_get_all_homework_for_current_year(self, homeworks):
        assert (
            len(
                list(
                    search(
                        Homework,
                        Criteria("timestamp", ">=", datetime.datetime(2023, 2, 1).timestamp()),
                        Criteria("timestamp", "<=", datetime.datetime(2023, 6, 30).timestamp()),
                    )
                )
            )
            == 6
        )

    def test_del_all_homework_from_user(self, homeworks):
        delete(Homework, Criteria("USER_ID", "==", "IIIGOR"))
        assert len(list(search(Homework))) == 6

    def test_del_all_homework_for_current_year(self, homeworks):
        delete(
            Homework,
            Criteria("timestamp", ">=", datetime.datetime(2023, 2, 1).timestamp()),
            Criteria("timestamp", "<=", datetime.datetime(2023, 6, 30).timestamp()),
        )
        assert len(list(search(Homework))) == 3
