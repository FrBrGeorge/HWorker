#!/usr/bin/env python3
'''
'''

from .simple import method

method("simple")

from .multi import method   # NoQA: E402

method("multi")

from .complex import method   # NoQA: E402

method("complex")
