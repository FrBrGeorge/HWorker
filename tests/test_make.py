"""Tests from make functions"""

from datetime import datetime

import pytest

from hworker.config import create_config, process_configs
from hworker.depot import search, delete, store
from hworker.depot.objects import Homework, Check, CheckCategoryEnum, Solution, CheckResult, FileObject, StoreObject
from hworker.make import (
    get_checks,
    get_solution,
    parse_homework_and_store,
    parse_all_stored_homeworks,
    check_all_solutions,
    check_new_solutions,
)


def example_file_object(content: bytes, day: int = 1) -> FileObject:
    return FileObject(content, timestamp=int(datetime(year=2023, month=1, day=day).timestamp()))


@pytest.fixture(scope="function")
def example_homework():
    return Homework(
        content={
            "prog.py": example_file_object(b"a, b = eval(input())\n" b"print(max(a, b))"),
            "check/1.in": example_file_object(b"123, 345"),
            "check/1.out": example_file_object(b"345"),
            "check/validate.py": example_file_object(
                b"def timestamp_validator(solution) -> float:\n" b"    return 1.0 if solution.timestamp else 0.0"
            ),
        },
        ID="hw_ID",
        USER_ID="user_ID",
        TASK_ID="task_ID",
        timestamp=int(datetime(year=2023, month=1, day=1).timestamp()),
        is_broken=False,
    )


def clean_up_database():
    delete(Homework)
    delete(Solution)
    delete(Check)
    delete(CheckResult)


@pytest.fixture(scope="function")
def checked_example_homework(example_homework):
    clean_up_database()

    store(example_homework)
    parse_all_stored_homeworks()

    check_all_solutions()


@pytest.fixture(scope="function")
def example_homework_new_solution():
    return Homework(
        content={
            "prog.py": example_file_object(b"a, b = map(int, input().split(',')\n" b"print(max(a, b))", day=2),
            "check/1.in": example_file_object(b"123, 345"),
            "check/1.out": example_file_object(b"345"),
            "check/validate.py": example_file_object(
                b"def timestamp_validator(solution) -> float:\n" b"    return 1.0 if solution.timestamp else 0.0"
            ),
        },
        ID="hw_ID",
        USER_ID="user_ID",
        TASK_ID="task_ID",
        timestamp=int(datetime(year=2023, month=1, day=2).timestamp()),
        is_broken=False,
    )


@pytest.fixture(scope="function")
def example_homework_new_check():
    return Homework(
        content={
            "prog.py": example_file_object(b"a, b = eval(input())\n" b"print(max(a, b))"),
            "check/1.in": example_file_object(b"123, 345"),
            "check/1.out": example_file_object(b"345"),
            "check/2.in": example_file_object(b"789, 123", day=2),
            "check/2.out": example_file_object(b"789", day=2),
            "check/validate.py": example_file_object(
                b"def timestamp_validator(solution) -> float:\n" b"    return 1.0 if solution.timestamp else 0.0"
            ),
        },
        ID="hw_ID",
        USER_ID="user_ID",
        TASK_ID="task_ID",
        timestamp=int(datetime(year=2023, month=1, day=2).timestamp()),
        is_broken=False,
    )


@pytest.fixture(scope="function")
def example_homework_update_check():
    return Homework(
        content={
            "prog.py": example_file_object(b"a, b = eval(input())\n" b"print(max(a, b))"),
            "check/1.in": example_file_object(b"123, 3456", day=2),
            "check/1.out": example_file_object(b"3456", day=2),
            "check/validate.py": example_file_object(
                b"def timestamp_validator(solution) -> float:\n" b"    return 1.0 if solution.timestamp else 0.0"
            ),
        },
        ID="hw_ID",
        USER_ID="user_ID",
        TASK_ID="task_ID",
        timestamp=int(datetime(year=2023, month=1, day=2).timestamp()),
        is_broken=False,
    )


@pytest.fixture(scope="function", autouse=True)
def example_config(tmp_path):
    config = tmp_path / "test-config.toml"
    create_config(
        config,
        {
            "tasks": {
                "task_ID": {
                    "deliver_ID": "20230101/01",
                    "open_date": datetime(year=2023, month=1, day=1),
                }
            }
        },
    )
    process_configs(str(config))


example_solution = Solution(
    ID="user_ID:task_ID",
    TASK_ID="task_ID",
    USER_ID="user_ID",
    checks={
        "user_ID:task_ID/1": [],
        "user_ID:task_ID/validate": [],
    },
    content={"prog.py": b"a, b = eval(input())\nprint(max(a, b))"},
    timestamp=int(datetime(year=2023, month=1, day=1).timestamp()),
)

runtime_check = Check(
    ID="user_ID:task_ID/1",
    TASK_ID="task_ID",
    USER_ID="user_ID",
    category=CheckCategoryEnum.runtime,
    content={"1.in": b"123, 345", "1.out": b"345"},
    timestamp=int(datetime(year=2023, month=1, day=1).timestamp()),
)

validate_check = Check(
    ID="user_ID:task_ID/validate",
    TASK_ID="task_ID",
    USER_ID="user_ID",
    category=CheckCategoryEnum.validate,
    content={
        "validate.py": b"def timestamp_validator(solution) -> float:\n" b"    return 1.0 if solution.timestamp else 0.0"
    },
    timestamp=int(datetime(year=2023, month=1, day=1).timestamp()),
)


def dump_search(mark: str, name: str, obj: StoreObject, **kwargs):
    print(f"\n{mark} {name}", *search(obj, **kwargs), sep=f"\n{mark} ")


class TestMake:
    def test_get_checks(self, example_homework):
        assert get_checks(example_homework) == [runtime_check, validate_check]

    def test_get_solution(self, example_homework):
        assert get_solution(example_homework) == example_solution

    def test_parse_homework_and_store(self, example_homework):
        parse_homework_and_store(example_homework)

        assert list(search(Solution)) == [
            example_solution,
        ]
        assert list(search(Check)) == [
            runtime_check,
            validate_check,
        ]
        delete(Solution)
        delete(Check)

    def test_parse_store_all_homeworks(self, example_homework):
        store(example_homework)
        parse_all_stored_homeworks()

        assert list(search(Solution)) == [
            example_solution,
        ]
        assert list(search(Check)) == [
            runtime_check,
            validate_check,
        ]
        delete(Solution)
        delete(Check)

    def test_parse_update_solution(self, checked_example_homework, example_homework_new_solution):
        old_checks_results: list[CheckResult] = list(search(CheckResult))

        store(example_homework_new_solution)
        parse_all_stored_homeworks()

        cur_timestamp = datetime.now().timestamp()

        check_new_solutions()

        new_checks_results: list[CheckResult] = list(search(CheckResult))

        assert len(old_checks_results) == len(new_checks_results)
        assert all([check_result.timestamp >= cur_timestamp for check_result in new_checks_results])

        clean_up_database()

    def test_parse_new_check(self, checked_example_homework, example_homework_new_check):
        old_checks_results: list[CheckResult] = list(search(CheckResult))

        store(example_homework_new_check)
        parse_all_stored_homeworks()

        check_new_solutions()

        new_checks_results: list[CheckResult] = list(search(CheckResult))

        assert len(old_checks_results) == len(new_checks_results) - 1
        assert all([old_result in new_checks_results for old_result in old_checks_results])

        clean_up_database()

    def test_parse_update_check(self, checked_example_homework, example_homework_update_check):
        old_checks_results: list[CheckResult] = list(search(CheckResult))

        store(example_homework_update_check)
        parse_all_stored_homeworks()

        check_new_solutions()

        new_checks_results: list[CheckResult] = list(search(CheckResult))

        assert len(old_checks_results) == len(new_checks_results)
        assert any([old_result not in new_checks_results for old_result in old_checks_results])
        assert not all([old_result not in new_checks_results for old_result in old_checks_results])

        clean_up_database()
