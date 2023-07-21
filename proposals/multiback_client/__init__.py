#!/usr/bin/env python3
"""
"""

from hworker.multiback import init_backends
from .A import method  # NoQA F401

init_backends(["A", "B"], ["method"], uniform=True)
