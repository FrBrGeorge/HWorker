"""Tests for check.runtime"""

from datetime import datetime

import pytest

from hworker.check.runtime import python_runner, runtime_wo_store
from hworker.check.validate import validate_wo_store
from hworker.check import get_result_ID
from hworker.depot.objects import Check, Solution, CheckResult, CheckCategoryEnum, VerdictEnum
from .user_config import user_config  # NoQA F401


@pytest.fixture()
def tmp_prog(tmp_path_factory):
    """"""
    prog_path = tmp_path_factory.getbasetemp() / "prog.py"
    test_path = tmp_path_factory.getbasetemp() / "test.in"
    prog_path.write_bytes(b"a, b = eval(input())\nprint(max(a, b), end='')")
    test_path.write_bytes(b"123, 345")
    return prog_path, test_path


class TestCheckRuntime:
    """"""

    def test_python_runner(self, tmp_prog):
        """"""
        assert python_runner(*tmp_prog, time_limit=2, resource_limit=3145728) == (b"345", b"", 0)

    @pytest.mark.parametrize(
        "user_config",
        [{"tasks": {"task_ID": {"deliver_ID": "20230101/01", "open_date": datetime(year=2023, month=1, day=1)}}}],
        indirect=True,
    )
    def test_checker(self, user_config):  # NoQA F811
        """"""
        # TODO: Change to parametrize
        checker = Check(
            content={"1.in": b"123, 345", "1.out": b"345"}, category=CheckCategoryEnum.runtime, ID="checker_ID"
        )
        solution = Solution(
            content={"prog.py": b"a, b = eval(input())\n" b"print(max(a, b), end='')"},
            checks={
                checker.ID: [],
            },
            ID="solution_ID",
            USER_ID="user_ID",
            TASK_ID="task_ID",
        )
        result = runtime_wo_store(checker, solution)

        assert result == CheckResult(
            ID=get_result_ID(checker, solution),
            USER_ID=solution.USER_ID,
            TASK_ID=solution.TASK_ID,
            timestamp=result.timestamp,
            rating=1.0,
            category=checker.category,
            stderr=b"",
            stdout=b"345",
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
                "timestamp_validator.py": b"def validator(solution) -> float:\n"
                b"    return 1.0 if solution.timestamp else 0.0"
            },
            category=CheckCategoryEnum.validate,
            ID="checker_ID",
        )

        solution = Solution(
            content={"prog.py": b"a, b = eval(input())\n" b"print(max(a, b))"},
            timestamp=datetime.now().timestamp(),
            checks={
                validator.ID: [],
            },
            ID="solution_ID",
            USER_ID="user_ID",
            TASK_ID="task_ID",
        )
        result = validate_wo_store(validator, solution)

        assert result == CheckResult(
            ID=get_result_ID(validator, solution),
            USER_ID=solution.USER_ID,
            TASK_ID=solution.TASK_ID,
            timestamp=result.timestamp,
            rating=1.0,
            category=validator.category,
            stdout=b"",
            stderr=b"",
            check_ID=validator.ID,
            check_timestamp=validator.timestamp,
            solution_ID=solution.ID,
            solution_timestamp=solution.timestamp,
            verdict=VerdictEnum.passed,
        )

    def test_regexp(self):
        validator = Check(
            content={
                "regexp_validator.py": b"def validator(solution) -> float:\n"
                b"    return 1.0 if b'import itertools' in "
                b"list(solution.content.values())[0] else 0.0"
            },
            category=CheckCategoryEnum.validate,
            ID="checker_ID",
        )

        solution = Solution(
            content={"prog.py": b"import itertools\n" b"a, b = eval(input())\n" b"print(max(a, b))"},
            timestamp=datetime.now().timestamp(),
            checks={
                validator.ID: [],
            },
            ID="solution_ID",
            USER_ID="user_ID",
            TASK_ID="task_ID",
        )
        result = validate_wo_store(validator, solution)

        assert result == CheckResult(
            ID=get_result_ID(validator, solution),
            USER_ID=solution.USER_ID,
            TASK_ID=solution.TASK_ID,
            timestamp=result.timestamp,
            rating=1.0,
            category=validator.category,
            stdout=b"",
            stderr=b"",
            check_ID=validator.ID,
            check_timestamp=validator.timestamp,
            solution_ID=solution.ID,
            solution_timestamp=solution.timestamp,
            verdict=VerdictEnum.passed,
        )
