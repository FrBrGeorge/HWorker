"""Tests for check.runtime"""

from hworker.check.runtime import python_runner, check_wo_store
from hworker.check.validate import validate_wo_store
from hworker.depot.objects import Check, Solution, CheckResult, CheckCategoryEnum, VerdictEnum

import os
import time
from datetime import date

import pytest


@pytest.fixture()
def tmp_prog():
    """"""
    prog_path = os.path.join(os.path.join(os.path.abspath(os.sep), "tmp", "prog.py"))
    test_path = os.path.join(os.path.join(os.path.abspath(os.sep), "tmp", "test.in"))
    with open(prog_path, "wb") as prog:
        prog.write(b"a, b = eval(input())\n" b"print(max(a, b))")
    with open(test_path, "wb") as test:
        test.write(b"123, 345")

    yield prog_path, test_path

    os.remove(prog_path)
    os.remove(test_path)


class TestCheckRuntime:
    """"""

    def test_python_runner(self, tmp_prog):
        """"""
        assert python_runner(*tmp_prog) == (b"345\n", b"", 0)

    def test_checker(self):
        """"""
        # TODO: Change to parametrize
        checker = Check(
            content={"1.in": b"123, 345", "1.out": b"345\n"}, category=CheckCategoryEnum.runtime, ID="checker_ID"
        )
        solution = Solution(
            content={"prog.py": b"a, b = eval(input())\n" b"print(max(a, b))"},
            checks=[
                checker.ID,
            ],
            ID="solution_ID",
            USER_ID="user_ID",
            TASK_ID="task_Id",
        )
        result = check_wo_store(checker, solution)

        assert result == CheckResult(
            ID=checker.ID + solution.ID,
            USER_ID=solution.USER_ID,
            TASK_ID=solution.TASK_ID,
            timestamp=result.timestamp,
            rating=1.0,
            category=checker.category,
            stderr=b"",
            stdout=b"345\n",
            check_ID=checker.ID,
            solution_ID=solution.ID,
            verdict=VerdictEnum.passed,
        )


class TestCheckValidate:
    """"""

    # TODO: change to parametrize
    def test_timestamp(self):
        """"""
        validator = Check(
            content={
                "timestamp_validator": b"def timestamp_validator(solution) -> float:\n"
                b"    return 1.0 if solution.timestamp else 0.0"
            },
            category=CheckCategoryEnum.validate,
            ID="checker_ID",
        )

        solution = Solution(
            content={"prog.py": b"a, b = eval(input())\n" b"print(max(a, b))"},
            timestamp=date.fromtimestamp(time.time()),
            checks=[
                validator.ID,
            ],
            ID="solution_ID",
            USER_ID="user_ID",
            TASK_ID="task_ID",
        )
        result = validate_wo_store(validator, solution)

        assert result == CheckResult(
            ID=validator.ID + solution.ID,
            USER_ID=solution.USER_ID,
            TASK_ID=solution.TASK_ID,
            timestamp=date.fromtimestamp(time.time()),
            rating=1.0,
            category=validator.category,
            stderr=b"",
            check_ID=validator.ID,
            solution_ID=solution.ID,
            verdict=VerdictEnum.passed,
        )

    def test_regexp(self):
        validator = Check(
            content={
                "timestamp_validator": b"def regexp_validator(solution) -> float:\n"
                b"    return 1.0 if b'import itertools' in "
                b"list(solution.content.values())[0] else 0.0"
            },
            category=CheckCategoryEnum.validate,
            ID="checker_ID",
        )

        solution = Solution(
            content={"prog.py": b"import itertools\n" b"a, b = eval(input())\n" b"print(max(a, b))"},
            timestamp=date.fromtimestamp(time.time()),
            checks=[
                validator.ID,
            ],
            ID="solution_ID",
            USER_ID="user_ID",
            TASK_ID="task_ID",
        )
        result = validate_wo_store(validator, solution)

        assert result == CheckResult(
            ID=validator.ID + solution.ID,
            USER_ID=solution.USER_ID,
            TASK_ID=solution.TASK_ID,
            timestamp=date.fromtimestamp(time.time()),
            rating=1.0,
            category=validator.category,
            stderr=b"",
            check_ID=validator.ID,
            solution_ID=solution.ID,
            verdict=VerdictEnum.passed,
        )
