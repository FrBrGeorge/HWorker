""""""
import pytest
from datetime import datetime

from hworker.make import get_checks
from hworker.depot.objects import Homework, Check, CheckCategoryEnum


@pytest.fixture(scope="function")
def homework(request):
    return Homework(
        content=request.param,
        ID="hw_ID",
        USER_ID="user_ID",
        TASK_ID="task_ID",
        timestamp=datetime(year=2024, month=1, day=1),
        is_broken=False,
    )


class TestMake:
    @pytest.mark.parametrize(
        "homework",
        [
            {
                "/tmp/test_repo/prog.py": b"a, b = eval(input())\n" b"print(max(a, b))",
                "/tmp/test_repo/URLS": b"https://github.com/Test/test/tree/main/20220913/1/tests",
                "/tmp/test_repo/checks/1.in": b"123, 345",
                "/tmp/test_repo/checks/1.out": b"345",
                "/tmp/test_repo/checks/validate.py": b"def timestamp_validator(solution) -> float:\n"
                b"    return 1.0 if solution.timestamp else 0.0",
            }
        ],
        indirect=True,
    )
    def test_get_checks(self, homework):
        assert get_checks(homework) == [
            Check(
                ID="user_ID:task_ID/1.in",
                TASK_ID="task_ID",
                USER_ID="user_ID",
                category=CheckCategoryEnum.runtime,
                content={"1.in": b"123, 345", "1.out": b"345"},
                timestamp=datetime(year=2024, month=1, day=1),
            ),
            Check(
                ID="user_ID:task_ID/validate.py",
                TASK_ID="task_ID",
                USER_ID="user_ID",
                category=CheckCategoryEnum.validate,
                content={
                    "validate.py": b"def timestamp_validator(solution) -> float:\n"
                    b"    return 1.0 if solution.timestamp else 0.0"
                },
                timestamp=datetime(year=2024, month=1, day=1),
            ),
        ]
