#!/usr/bin/env python3
'''
Simple if / import backend selector
'''
from . import config
from importlib import import_module


backend = import_module(f"..back.{config()[0]}", __name__)
method = backend.method
