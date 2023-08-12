#!/usr/bin/env python3
"""
"""

from hworker import multiback


def method(par: str) -> int:
    """Sample method"""
    return -1


multiback.init_backends(["A", "B"], uniform=True)
