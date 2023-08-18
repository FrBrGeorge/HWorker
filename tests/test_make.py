"""Tests from make functions"""

import os
import pytest
from datetime import datetime

from hworker.make import get_checks, get_solution, parse_store_homework, parse_store_all_homeworks
from hworker.depot.objects import Homework, Check, CheckCategoryEnum, Solution, Criteria
from hworker.depot import search, delete, store
from hworker.config import create_config, process_configs


_test_database_filename = "test.db"
os.environ["HWORKER_DATABASE_FILENAME"] = _test_database_filename


@pytest.fixture(scope="function")
def example_homework():
    return Homework(
        content={
            "prog.py": b"a, b = eval(input())\n" b"print(max(a, b))",
            "check/remote": b"User1:Task1\nUser2:Task1\nUser3:Task1",
            "check/1.in": b"123, 345",
            "check/1.out": b"345",
            "check/validate.py": b"def timestamp_validator(solution) -> float:\n"
            b"    return 1.0 if solution.timestamp else 0.0",
        },
        ID="hw_ID",
        USER_ID="user_ID",
        TASK_ID="task_ID",
        timestamp=int(datetime(year=2024, month=1, day=1).timestamp()),
        is_broken=False,
    )


@pytest.fixture(scope="function")
def example_config(tmp_path):
    config = tmp_path / "testconfig.toml"
    create_config(
        config,
        {
            "tasks": {
                "task_ID": {
                    "deliver_ID": "20240101/01",
                    "checks": ["User4:Task1"],
                    "open_date": datetime(year=2024, month=1, day=1),
                }
            }
        },
    )
    process_configs(str(config))


example_solution = Solution(
    ID="user_ID:task_ID",
    TASK_ID="task_ID",
    USER_ID="user_ID",
    checks=[
        "user_ID:task_ID/1",
        "user_ID:task_ID/validate",
        "User1:Task1",
        "User2:Task1",
        "User3:Task1",
        "User4:Task1",
    ],
    content={"prog.py": b"a, b = eval(input())\nprint(max(a, b))"},
    timestamp=int(datetime(year=2024, month=1, day=1).timestamp()),
)

runtime_check = Check(
    ID="user_ID:task_ID/1",
    TASK_ID="task_ID",
    USER_ID="user_ID",
    category=CheckCategoryEnum.runtime,
    content={"1.in": b"123, 345", "1.out": b"345"},
    timestamp=int(datetime(year=2024, month=1, day=1).timestamp()),
)

validate_check = Check(
    ID="user_ID:task_ID/validate",
    TASK_ID="task_ID",
    USER_ID="user_ID",
    category=CheckCategoryEnum.validate,
    content={
        "validate.py": b"def timestamp_validator(solution) -> float:\n" b"    return 1.0 if solution.timestamp else 0.0"
    },
    timestamp=int(datetime(year=2024, month=1, day=1).timestamp()),
)


class TestMake:
    def test_get_checks(self, example_homework):
        assert get_checks(example_homework) == [runtime_check, validate_check]

    def test_get_solution(self, example_config, example_homework):
        assert get_solution(example_homework) == example_solution

    def test_parse_store_homework(self, example_config, example_homework):
        parse_store_homework(example_homework)

        assert list(search(Solution)) == [
            example_solution,
        ]
        assert list(search(Check)) == [
            runtime_check,
            validate_check,
        ]
        delete(Solution)
        delete(Check)

    def test_parse_store_all_homeworks(self, example_config, example_homework):
        store(example_homework)
        parse_store_all_homeworks()

        assert list(search(Solution)) == [
            example_solution,
        ]
        assert list(search(Check)) == [
            runtime_check,
            validate_check,
        ]
        delete(Solution)
        delete(Check)
