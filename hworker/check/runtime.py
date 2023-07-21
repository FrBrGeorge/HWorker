from ..log import get_logger
from ..config import get_max_test_size

from typing import Union
from difflib import unified_diff
from os.path import getsize, basename


def python_runner():
    # TODO
    pass


def choose_runner(prog: str, prog_type: str, prog_input: str):
    """Chooses runner based on program type"""
    # TODO
    return python_runner


def exact_test_check(actual: str, initial: str) -> Union[unified_diff, None]:
    """Compares two test file without insignificant whitespaces

    :param actual: Output from program
    :param initial: Supposed output
    :return: unified_diff of files or None if outputs are the same
    """
    with open(actual, encoding="utf-8") as act, open(initial, encoding="utf-8") as init:
        act_lines = [line.strip() + "\n" for line in act.readlines()]
        init_lines = [line.strip() + "\n" for line in init.readlines()]
    if act_lines == init_lines:
        return None
    act_size, init_size = getsize(actual), getsize(initial)
    if act_size > get_max_test_size() or init_size > get_max_test_size():
        init_lines, act_lines = [f"Size differs: {init_size}\n"], ["Size differs: <output>\n"]
    return unified_diff(init_lines, act_lines, basename(initial), "<output>")


def choose_checker(actual: str, initial: str, test_type: str):
    """Chooses checker based on test type"""
    # TODO
    return exact_test_check


