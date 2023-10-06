#!/usr/bin/env python3
"""
Common tools
"""
from ..depot.objects import Check, Solution


def get_result_ID(checker: Check, solution: Solution) -> str:
    """CheckResult ID generator

    :param checker: check object
    :param solution: solution object
    :return: CheckResult ID
    """
    return f"{checker.ID}@{solution.ID}"
