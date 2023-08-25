#!/usr/bin/env python3
"""
Multi-backend infrastructure

Function init_backends() provided here does following:
- Scans module from which it was called and collect list of it's methods,
  eliminating names started with "_".
- Replaces each of those methods with a new one. The new method determines a list of
  backends available and calls a method with the same name from each of them.
- Backend list can be determined by list of strings or by callable returning a list of strings.
  In latter case backand determitation is deferred until corresponded method is called.
- Wrapper method can optionally aggregate list of retuirned values into one appropriate object.
"""

import functools
import importlib
import inspect
import itertools
from typing import Any, Callable


def aggregate(seq: list) -> Any:
    """Convert list of backend results to single result, if possible.
    Aggregation supported:
    - list[list] → list
    - list[dict] → dict
    - list[None] → None
    - list[Numeric] → sum(list)

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
    backends: Callable[[], list[str]] | list[str],
    backpath: str = "",
    uniform: bool = False,
) -> None:
    """Replace each method from caller module with multiple calls
    of backend methods with the same name.

    @param backends: list of backend names or function returning that list
    @param backpath: path to backends location
    @param uniform: do we need to aggregate the results
    """
    module = inspect.getmodule(inspect.stack()[1][0])
    for _m in dir(module):
        if _m.startswith("_"):
            continue
        proto = getattr(module, _m)
        if not callable(proto):
            continue
        assign = tuple(set(functools.WRAPPER_ASSIGNMENTS) - {"__module__"})

        def wrapper(*args, _m=_m, **kwds):
            backlist = [
                importlib.import_module(f"{backpath}.{modname}", module.__name__)
                for modname in (backends() if callable(backends) else backends)
            ]
            if uniform:
                return aggregate([getattr(back, _m)(*args, **kwds) for back in backlist])
            else:
                return [getattr(back, _m)(*args, **kwds) for back in backlist]

        module.__dict__[_m] = functools.update_wrapper(wrapper, proto, assign)
