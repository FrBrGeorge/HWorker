#!/usr/bin/env python3
'''
Multibackend module examples
'''


def config():
    import sys
    return sys.argv[1:] or ["A"]
