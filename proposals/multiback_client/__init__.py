#!/usr/bin/env python3
"""
"""

from ..multiback import init_backends

init_backends(["A", "B"], ["method"], uniform=True)
