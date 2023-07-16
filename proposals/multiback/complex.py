#!/usr/bin/env python3
'''
Multibackend wrapper
'''
from . import config
from importlib import import_module
from functools import reduce, update_wrapper, WRAPPER_ASSIGNMENTS
from itertools import chain

METHODS = ["method"]
backends = [import_module(f"..back.{modname}", __name__) for modname in config()]


def aggregate(seq: list):
    uniq = {type(el): el for el in seq}
    if len(uniq) != 1:
        return seq
    utype, uniq = uniq.popitem()
    match uniq:
        case int() | float() | complex():
            return sum(seq)
        case list() | tuple():
            return utype(chain.from_iterable(seq))
        case dict() | set():
            return reduce(utype.__or__, seq)
        case None:
            return None
    return seq


def init():
    for m in METHODS:
        proto = getattr(backends[0], m)
        assign = tuple(set(WRAPPER_ASSIGNMENTS) - {'__module__'})

        def wrapper(*args, **kwds):
            return aggregate([getattr(back, m)(*args, **kwds) for back in backends])

        globals()[m] = update_wrapper(wrapper, proto, assign)


init()
