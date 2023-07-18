#!/usr/bin/env python3
"""
Simple if / import backend selector
"""
from importlib import import_module

backend = import_module(f".database", __name__)
store = backend.store
search = backend.search
delete = backend.delete
