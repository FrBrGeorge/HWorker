"""Parsing depot objects and basic execution functionality"""

import datetime
import tomllib
from tomllib import loads
from typing import Iterable

from ..check import check, get_result_ID
from ..config import (
    get_runtime_suffix,
    get_validate_suffix,
    get_check_name,
    get_remote_name,
    get_task_info,
    need_screenreplay,
    get_deadline_gap,
    user_checks,
)
from ..depot import store, search
from ..depot.objects import (
    Homework,
    Check,
    Solution,
    CheckCategoryEnum,
    Criteria,
    CheckResult,
    UpdateTime,
    FileObject,
    StoreObject,
)
from ..log import get_logger
from .screenplay import screenplay_all

_default_timestamp = datetime.datetime.fromisoformat("2009-05-17 20:09:00").timestamp()
type sometimes = datetime.datetime | datetime.date | float | int | StoreObject


def get_checks(hw: Homework) -> list[Check]:
    """Get homework checks list

    :param hw: homework object
    :return: checks list
    """
    get_logger(__name__).debug(f"Started check parsing for {hw.ID} homework")
    checks, seen = [], set()
    for check_path, check_content in hw.content.items():
        if check_path.startswith(get_check_name()):
            path_beg, _, suffix = check_path.rpartition(".")
            name = path_beg.rsplit("/", maxsplit=1)[-1]
            timestamp = _default_timestamp

            if name not in seen:
                content, category = {}, None
                if suffix in get_runtime_suffix():
                    category = CheckCategoryEnum.runtime
                    for suf in get_runtime_suffix():
                        # What to do if there is only one of the tests of in/out pair?
                        file = hw.content.get(f"{path_beg}.{suf}", FileObject(content=b"", timestamp=hw.timestamp))
                        content[f"{name}.{suf}"] = file.content
                        timestamp = max(timestamp, file.timestamp)
                elif suffix == get_validate_suffix():
                    file_content = b""
                    category = CheckCategoryEnum.validate
                    if isinstance(check_content, FileObject):
                        file_content = check_content.content
                        timestamp = max(timestamp, check_content.timestamp)
                    content = {f"{name}.{suffix}": file_content}
                else:
                    continue

                check = Check(
                    content=content,
                    category=category,
                    ID=f"{hw.USER_ID}:{hw.TASK_ID}/{name}",
                    TASK_ID=hw.TASK_ID,
                    USER_ID=hw.USER_ID,
                    timestamp=timestamp,
                )
                seen.add(name)
                checks.append(check)

    get_logger(__name__).debug(f"Extracted {[check.ID for check in checks]} checks from {hw.ID} homework")
    return checks


def get_solution(hw: Homework) -> Solution:
    """Get solution object from homework

    :param hw: homework object
    :return: solution object
    """
    get_logger(__name__).debug(f"Started solution parsing for {hw.ID} homework")
    content, remote_checks, timestamp = {}, [], _default_timestamp
    for path, path_content in hw.content.items():
        if not path.startswith(get_check_name()):
            content[path] = path_content.content
            timestamp = max(timestamp, path_content.timestamp)
    if need_screenreplay():
        content = screenplay_all(content)
    try:
        remote_file = hw.content.get(f"{get_check_name()}/{get_remote_name()}", None)
        remote_content = loads(remote_file.content.decode("utf-8")) if remote_file else {}
    except tomllib.TOMLDecodeError:
        remote_content = {}
        get_logger(__name__).warning(f"Incorrect remote content at {hw.ID} homework")

    remote_checks = remote_content.get("remote", {})
    own_checks = {check.ID: [] for check in get_checks(hw)} if user_checks() else {}
    config_checks = get_task_info(hw.TASK_ID).get("checks", {})
    solution_id = f"{hw.USER_ID}:{hw.TASK_ID}"

    get_logger(__name__).debug(f"Extracted {solution_id} solution from {hw.ID} homework")
    return Solution(
        content=content,
        checks=own_checks | remote_checks | config_checks,
        ID=solution_id,
        TASK_ID=hw.TASK_ID,
        USER_ID=hw.USER_ID,
        timestamp=timestamp,
    )


def parse_homework_and_store(hw: Homework) -> None:
    """Parse homework to Solution and Checks and store them with depot

    :param hw: homework object
    :return: -
    """
    for cur_check in get_checks(hw):
        store(cur_check)

    store(get_solution(hw))


def parse_all_stored_homeworks() -> None:
    """Parse all actual homeworks to Solution and Checks and store them with depot

    :return: -
    """
    get_logger(__name__).info("Parse and store all homeworks...")
    for hw in search(Homework, actual=True):
        for cur_check in get_checks(hw):
            store(cur_check)
    for hw in search(Homework, actual=False):
        store(get_solution(hw))
    # See https://github.com/FrBrGeorge/HWorker/issues/93
    for hw in search(Homework, actual=True):
        store(get_solution(hw))


def run_solution_checks_and_store(solution: Solution) -> None:
    """Run all given solution checks and store results in depot

    :param solution: solution to run checks
    :return: -
    """
    get_logger(__name__).debug(f"Run all checks of {solution.ID} solution")

    for check_name in solution.checks:
        checker = search(Check, Criteria("ID", "==", check_name), first=True)
        check_result = check(checker, solution)
        store(check_result)


def run_solution_checks(solution: Solution) -> dict[str:CheckResult]:
    """Run all given solution checks and store results in depot

    :param solution: solution to run checks
    :return: {check_name: CheckResult} dictionary
    """
    get_logger(__name__).debug(f"Run all checks of {solution.ID} solution")

    check_results = {}
    for check_name in solution.checks:
        checker = search(Check, Criteria("ID", "==", check_name), first=True)
        check_results[check_name] = check(checker, solution)
    return check_results


def check_all_solutions() -> None:
    """Run all solution checks for every actual solution and store results in depot

    :return: -
    """
    store(UpdateTime(name="Check run", timestamp=datetime.datetime.now().timestamp()))
    get_logger(__name__).info("Run all checks on all solutions...")

    solutions = search(Solution, actual=True)
    for solution in solutions:
        run_solution_checks_and_store(solution)


def check_new_solutions() -> None:
    """Run new solution checks for every actual solution and store results in depot

    :return: -
    """
    store(UpdateTime(name="Check run", timestamp=datetime.datetime.now().timestamp()))
    get_logger(__name__).info("Run new checks on all solutions...")

    solutions: Iterable[Solution] = search(Solution, actual=True)

    for solution in solutions:
        for check_name in solution.checks:
            checker: Check = search(Check, Criteria("ID", "==", check_name), first=True)

            if checker is None:
                get_logger(__name__).warn(f"Not found check named<{check_name}> from solution {solution}")
                continue

            result_obj: CheckResult = search(
                CheckResult, Criteria("ID", "==", get_result_ID(solution=solution, checker=checker)), first=True
            )

            if result_obj is None or max(solution.timestamp, checker.timestamp) > min(
                result_obj.solution_timestamp, result_obj.check_timestamp
            ):
                new_result = check(checker, solution)
                if new_result is None:
                    get_logger(__name__).warn(
                        f"Check returned empty object for check <{checker}> from solution {solution}"
                    )
                    continue
                store(new_result)


def anytime(moment: sometimes) -> datetime.datetime:
    match moment:
        case StoreObject():
            return datetime.datetime.fromtimestamp(moment.timestamp)
        case datetime.datetime():
            return moment
        case datetime.date():
            return datetime.datetime.combine(moment, datetime.time())
        case int() | float():
            return datetime.datetime.fromtimestamp(moment)
    return None


def fit_deadline(moment: sometimes, deadline: sometimes) -> bool:
    """Calculates if moment fits tomorrow deadline border."""
    final = datetime.datetime.combine(anytime(deadline).date(), get_deadline_gap()) + datetime.timedelta(days=1)
    return anytime(moment) <= final
