#!/usr/bin/env python3
'''
Multibackend wrapper
'''
from . import config
from importlib import import_module


backends = [import_module(f"..back.{modname}", __name__) for modname in config()]


def method(message):
    return [back.method(message) for back in backends]
