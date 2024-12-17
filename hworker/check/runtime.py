"""Isolated runtime tests and check results"""

import os
import platform
import subprocess
import sys
import time
from datetime import datetime
from difflib import diff_bytes, unified_diff
from functools import partial
from itertools import zip_longest
from math import isclose
from pathlib import Path
from subprocess import TimeoutExpired
from tempfile import NamedTemporaryFile
from tempfile import gettempdir
from typing import Iterator

from ._tools import get_result_ID
from ..config import get_check_directory, get_task_info, get_prog_name
from ..depot.database.functions import store
from ..depot.objects import Check, Solution, CheckResult, CheckCategoryEnum, VerdictEnum
from ..log import get_logger

if platform.system() != "Windows":
    try:
        import resource
    except ImportError:
        resource = None


def python_set_limits(time_limit: int, resource_limit: int) -> None:
    """Set limits for python program run

    :param time_limit: time limit in seconds, will be taken from config if not specified
    :param resource_limit: resource limit in bytes, will be taken from config if not specified
    """
    get_logger(__name__).debug("Set limits for python runner")

    resource.setrlimit(resource.RLIMIT_CPU, (time_limit, time_limit))
    # TODO: Causes Memory Error
    # resource.setrlimit(resource.RLIMIT_NPROC, (0, 0))
    resource.setrlimit(resource.RLIMIT_STACK, (resource_limit, resource_limit))
    resource.setrlimit(resource.RLIMIT_NOFILE, (30, 30))
    # TODO: Also Memory Error
    # if platform.system() == "Linux" or platform.system() == "Linux2":
    #     resource.setrlimit(resource.RLIMIT_AS, (1024 * 1024 * 15, 1024 * 1024 * 15))
    #     resource.setrlimit(resource.RLIMIT_FSIZE, (2048, 2048))


def python_runner(
    prog_path: str, input_path: str, time_limit: int, resource_limit: int
) -> tuple[bytes | None, bytes, int]:
    """Runs python program with given input and returns output info

    :param prog_path: python program path
    :param input_path: program input in io format
    :param time_limit:
    :param resource_limit:
    :return: tuple of program output, stderr and exit code
    """
    get_logger(__name__).debug(f"{prog_path} run")
    if not os.path.exists(get_check_directory()):
        os.makedirs(get_check_directory())
    with (
        open(input_path, encoding="utf-8") as prog_input,
        NamedTemporaryFile(dir=get_check_directory(), delete=False) as prog_output,
    ):
        try:
            result = subprocess.Popen(
                [sys.executable, prog_path],
                preexec_fn=(
                    partial(python_set_limits, time_limit, resource_limit) if platform.system() != "Windows" else None
                ),
                stdin=prog_input,
                stdout=prog_output,
                stderr=subprocess.PIPE,
            )
        except Exception as error:
            get_logger(__name__).warning(f"Runner {prog_path} crashed on {input_path} data:\n {error}")
            return b"", str(error), -1

    # TODO: wall clock should be limited separately
    try:
        exit_code = result.wait(time_limit * 2)
    except TimeoutExpired as E:
        result.terminate()
        stderr = f"TIMEOUT: {E.timeout}\n".encode(errors="replace")
        exit_code = -1
        get_logger(__name__).debug(f"Time limit on {prog_path} / {input_path}")
        sleep = 1
        while result.poll() is None:
            get_logger(__name__).warning(f"Waiting {sleep} seconds for {prog_path} to die")
            time.sleep(sleep)
            sleep *= 2
            if sleep > time_limit * 32:
                raise TimeoutError(f"Process {prog_path} is undead")
    else:
        get_logger(__name__).debug(f"Check passed: {prog_path} / {input_path}")
        stderr = b""
    with open(prog_output.name, "rb") as po:
        po = po.read()
    prog_output.close()
    os.unlink(prog_output.name)
    return po, stderr + result.stderr.read(), exit_code


def runtime_wo_store(checker: Check, solution: Solution, check_num: int = 0) -> CheckResult:
    """Run checker on a given solution and returns result object

    :param checker: check object
    :param solution:
    :param check_num: number of check for parallel work
    """
    if get_prog_name() in solution.content:
        prog = solution.content.get(get_prog_name())
    else:
        prog = ([None] + [solution.content[name] for name in solution.content if name.endswith(".py")])[-1]
    prog_input, initial_output = b"", b""
    for name, b in checker.content.items():
        if name.endswith(".in"):
            prog_input = b
        elif name.endswith(".out"):
            initial_output = b

    content, stderr, actual_output, verdict = 0.0, b"", b"", VerdictEnum.missing
    check_dir = Path(gettempdir(), get_check_directory())
    if prog is not None:
        check_dir.mkdir(parents=True, exist_ok=True)
        qualname = f"{solution.USER_ID}/{solution.TASK_ID}".replace("/", "_")
        prog_path = check_dir / f"{qualname}.py"
        input_path = check_dir / f"{qualname}.in"
        prog_path.write_bytes(prog)
        input_path.write_bytes(prog_input)

        runner = choose_runner(checker)
        task_info = get_task_info(solution.TASK_ID)
        time_limit, resource_limit = task_info["time_limit"], task_info["resource_limit"]
        actual_output, stderr, exit_code = runner(prog_path, input_path, time_limit, resource_limit)
        diff, score = choose_diff_score(actual_output, initial_output, checker.category)
        if diffresult := diff(actual_output, initial_output, task_info["test_size"]):
            stderr += b"".join(diffresult)
        content = score(diffresult)
        verdict = VerdictEnum.passed if not exit_code else VerdictEnum.failed
        input_path.unlink()
        prog_path.unlink()

    return CheckResult(
        ID=get_result_ID(checker, solution),
        USER_ID=solution.USER_ID,
        TASK_ID=solution.TASK_ID,
        timestamp=datetime.now().timestamp(),
        rating=content,
        category=checker.category,
        stderr=stderr,
        stdout=actual_output,
        check_ID=checker.ID,
        check_timestamp=checker.timestamp,
        solution_ID=solution.ID,
        solution_timestamp=solution.timestamp,
        verdict=verdict,
    )


def runtime(checker: Check, solution: Solution, check_num: int = 0) -> None:
    """Run checker on a given solution and save result object

    :param checker: check object
    :param solution:
    :param check_num: number of check for parallel work
    """
    get_logger(__name__).debug(f"Checking solution {solution.ID} with {checker.ID} checker")
    if checker.category == CheckCategoryEnum.runtime:
        result = runtime_wo_store(checker, solution, check_num)
        store(result)
    else:
        get_logger(__name__).warning(f"The {checker.ID} object given to check is not a checker")


def choose_runner(checker: Check):
    """Choose runner based on program type"""
    # TODO
    return python_runner


def bytes_diff(actual: bytes, initial: bytes, test_size: int) -> Iterator[bytes] | None:
    """Compares two test file without insignificant whitespaces

    :param actual: Output from program
    :param initial: Supposed output
    :return: unified_diff of files or None if outputs are the same
    """
    act_lines = [line.strip() + b"\n" for line in actual.split()]
    init_lines = [line.strip() + b"\n" for line in initial.split()]
    if act_lines == init_lines:
        return None
    act_size, init_size = len(actual), len(initial)
    if act_size > test_size or init_size > test_size:
        init_lines, act_lines = [f"Size differs: {init_size}\n".encode()], [f"Size differs: {act_size}\n".encode()]
    return diff_bytes(unified_diff, init_lines, act_lines, b"<expect>", b"<actual>")


def exact_score(diff: Iterator[bytes] | None) -> float:
    """Score exact tests similarity

    :param diff: actual and initial outputs diff (result of test_check work)
    :return: score [0, 1]
    """
    return 1.0 if diff is None else 0.0


def float_diff(actual: bytes, initial: bytes, relative: int = 1e-09) -> Iterator[bytes] | None:
    """

    :param actual:
    :param initial:
    :param relative:
    :return:
    """
    # TODO: clear non-digit symbols
    for actual_num, initial_num in zip_longest(actual.split(), initial.split(), fillvalue=None):
        chk = isclose(float(actual_num), float(initial_num), rel_tol=relative)
        yield f"{actual_num} {'=' if chk else '!='} {initial_num}".encode("utf-8")


def float_score(diff: Iterator[bytes]) -> float:
    """

    :param diff:
    :return:
    """
    return 1.0 if all(map(lambda s: "!" not in s, diff)) else 0.0


# TODO: go to check.comparison_type
def choose_diff_score(actual: bytes, initial: bytes, test_type: CheckCategoryEnum):
    """Chooses checker based on test type"""
    # TODO
    return bytes_diff, exact_score
