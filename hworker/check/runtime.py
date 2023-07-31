from ..log import get_logger
from ..config import get_max_test_size, get_check_directory, get_default_time_limit, get_default_resource_limit
from ..depot.objects import Check, Solution, CheckResult, CheckCategoryEnum
from ..depot.database.functions import store

import sys
import io
import os
import platform
from math import isclose
from itertools import zip_longest
from typing import Iterator
from random import randint
from difflib import diff_bytes, unified_diff
from os.path import getsize, basename
from tempfile import NamedTemporaryFile
import resource
import subprocess
from subprocess import CompletedProcess, TimeoutExpired


def python_set_limits(time_limit: int = None, resource_limit: int = None) -> None:
    """Set limits for python program run

    :param time_limit: time limit in seconds, will be taken from config if not specified
    :param resource_limit: resource limit in bytes, will be taken from config if not specified
    """
    # TODO: limits for various platforms
    get_logger(__name__).info("Set limits for python runner")
    if time_limit is None:
        time_limit = get_default_time_limit()
    if resource_limit is None:
        resource_limit = get_default_resource_limit()

    resource.setrlimit(resource.RLIMIT_CPU, (time_limit, time_limit))
    resource.setrlimit(resource.RLIMIT_NPROC, (0, 0))
    resource.setrlimit(resource.RLIMIT_STACK, (resource_limit, resource_limit))
    resource.setrlimit(resource.RLIMIT_NOFILE, (30, 30))

    if platform.system() == "Linux" or platform.system() == "Linux2":
        resource.setrlimit(resource.RLIMIT_AS, (1024 * 1024 * 15, 1024 * 1024 * 15))
        resource.setrlimit(resource.RLIMIT_FSIZE, (2048, 2048))


def python_runner(prog_path: str, input_path: str) -> tuple[bytes | None, bytes, int]:
    """Runs python program with given input and returns output info

    :param prog_path: python program path
    :param input_path: program input in io format
    :return: tuple of program output, stderr and exit code
    """
    get_logger(__name__).info(f"{prog_path} run")
    if not os.path.exists(get_check_directory()):
        os.makedirs(get_check_directory())
    with open(input_path, encoding="utf-8") as prog_input, \
            NamedTemporaryFile(dir=get_check_directory(), delete=False) as prog_output:
        try:
            result = subprocess.Popen([sys.executable, prog_path],
                                      # preexec_fn=python_set_limits(),
                                      stdin=prog_input,
                                      stdout=prog_output,
                                      stderr=subprocess.PIPE)
        except TimeoutExpired as time_error:
            result = CompletedProcess(time_error.args, -1, stderr=str(time_error).encode(errors='replace'))
    exit_code = result.wait()
    with open(prog_output.name, "rb") as po:
        po = po.read()
    return po, result.stderr.read(), exit_code


def check(checker: Check, solution: Solution, check_num: int = 0) -> None:
    """ Run checker on a given solution

    :param checker: check object
    :param solution:
    :param check_num: number of check for parallel work
    """
    get_logger(__name__).info(f"Checking checker with: f{checker.ID} ID")
    if check_num == 0:
        check_num = randint(1, 1000000)
    prog = solution.content["prog.py"]
    prog_input, initial_output = io.BytesIO(), bytes()
    for name, b in checker.content:
        if name.endswith(".in"):
            prog_input = io.BytesIO(b)
        elif name.endswith(".out"):
            initial_output = b

    if not os.path.exists(get_check_directory()):
        os.makedirs(get_check_directory())
    prog_path = os.path.join(get_check_directory(), f"prog_{check_num}.py")
    with open(prog_path, mode="rb") as p:
        p.write(prog)

    runner = choose_runner(checker)
    actual_output, stderr, exit_code = runner(prog_path, prog_input)
    diff, score = choose_diff_score(actual_output, initial_output, checker.category)
    content = score(diff(actual_output, initial_output))
    check_result = CheckResult(content=content, category=checker.category)
    store(check_result)


def choose_runner(checker: Check):
    """Choose runner based on program type"""
    # TODO
    return python_runner


def bytes_diff(actual: bytes, initial: bytes) -> Iterator[bytes] | None:
    """Compares two test file without insignificant whitespaces

    :param actual: Output from program
    :param initial: Supposed output
    :return: unified_diff of files or None if outputs are the same
    """
    with open(actual, "rb") as act, open(initial, "rb") as init:
        act_lines = [line.strip() + b"\n" for line in act.readlines()]
        init_lines = [line.strip() + b"\n" for line in init.readlines()]
    if act_lines == init_lines:
        return None
    act_size, init_size = getsize(actual), getsize(initial)
    if act_size > get_max_test_size() or init_size > get_max_test_size():
        init_lines, act_lines = [f"Size differs: {init_size}\n"], ["Size differs: <output>\n"]
    return diff_bytes(unified_diff, init_lines, act_lines, basename(initial), b"<output>")


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
        yield f"{actual_num} " \
              f"{'=' if isclose(float(actual_num), float(initial_num), rel_tol=relative) else '!='} " \
              f"{initial_num}".encode("utf-8")


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
