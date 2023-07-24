#!/usr/bin/env python3
"""
Multi-backend infrastructure
"""

from typing import Any
import itertools
import functools
import importlib
import inspect


def aggregate(seq: list) -> Any:
    """Convert list of backend results to single result, if possible.

    :param seq: List of backend results
    :return: Possibly aggregated results"""
    uniq = {type(el): el for el in seq}
    if len(uniq) != 1:
        return seq
    utype, uniq = uniq.popitem()
    match uniq:
        case int() | float() | complex():
            return sum(seq)
        case list() | tuple():
            return utype(itertools.chain.from_iterable(seq))
        case dict() | set():
            return functools.reduce(utype.__or__, seq)
        case None:
            return None
    return seq


def init_backends(
    backends: list[str],
    methods: list[str],
    backpath: str = "",
    uniform: bool = False,
) -> None:
    """Wrap every method from each backend to single one and store it to module namespace.

    @param backends: list of backend names
    @param methods: list of methods to be wrapped
    @param backpath: path to backends location
    @param uniform: do we need to aggregate the results
    """
    module = inspect.getmodule(inspect.stack()[1][0])
    backends = [
        importlib.import_module(f"{backpath}.{modname}", module.__name__)
        for modname in backends
    ]
    for m in methods:
        proto = getattr(backends[0], m)
        assign = tuple(set(functools.WRAPPER_ASSIGNMENTS) - {"__module__"})

        def wrapper(*args, **kwds):
            if uniform:
                return aggregate([getattr(back, m)(*args, **kwds) for back in backends])
            else:
                return [getattr(back, m)(*args, **kwds) for back in backends]

        module.__dict__[m] = functools.update_wrapper(wrapper, proto, assign)
