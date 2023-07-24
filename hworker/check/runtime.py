from ..log import get_logger
from ..config import get_max_test_size, get_check_directory, get_default_time_limit, get_default_resource_limit
from ..depot.objects import Check, CheckResult

import sys
import io
import os
from typing import Union
from difflib import diff_bytes, unified_diff
from os.path import getsize, basename
import resource
import subprocess
from subprocess import CompletedProcess, TimeoutExpired



def python_set_limits(time_limit: int = None, resource_limit: int = None):
    if time_limit is None:
        time_limit = get_default_time_limit()
    if resource_limit is None:
        resource_limit = get_default_resource_limit()

    resource.setrlimit(resource.RLIMIT_CPU, (time_limit, time_limit))
    resource.setrlimit(resource.RLIMIT_NPROC, (0, 0))
    resource.setrlimit(resource.RLIMIT_STACK, (resource_limit, resource_limit))
    resource.setrlimit(resource.RLIMIT_NOFILE, (30, 30))


def python_runner(prog_path: str, prog_input: io.BytesIO) -> tuple[io.BytesIO | None, bytes, int]:
    """

    :param prog_path:
    :param prog_input:
    :return:
    """
    # TODO
    with prog_input, io.BytesIO() as prog_output:
        try:
            result = subprocess.Popen([sys.executable, prog_path], preexec_fn=python_set_limits(), stdin=prog_input,
                                      stdout=prog_output,
                                      stderr=subprocess.PIPE)
        except TimeoutExpired as time_error:
            result = CompletedProcess(time_error.args, -1, stderr=str(time_error).encode(errors='replace'))
        exit_code = result.wait()
        return prog_output if prog_output else None, result.stderr.read(), exit_code




def checker(check: Check, check_num: int) -> float:
    """
    
    :param check:
    :param check_num:
    :return:
    """
    prog = check.content["prog.py"]
    checks = check.content["tests"]
    for check in checks:
        if check.endswith(".in"):
            prog_input = io.BytesIO(check)
        elif check.endswith(".out"):
            initial_output = check

    if not os.path.exists(get_check_directory()):
        os.makedirs(get_check_directory())
    prog_path = os.path.join(get_check_directory(), f"prog_{check_num}.py")
    with open(prog_path, mode="rb") as p:
        p.write(prog)


def choose_runner(check: Check):
    """Choose runner based on program type"""
    # TODO
    return python_runner


def test_check(actual: bytes, initial: bytes) -> Union[unified_diff, None]:
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


def choose_test_checker(actual: str, initial: str, test_type: str):
    """Chooses checker based on test type"""
    # TODO
    return test_check


