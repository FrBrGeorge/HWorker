import datetime
import importlib
import inspect
import os
from pathlib import Path


from .. import depot, config

_module_names = ["task_qualifier", "user_qualifier", "formula"]
_module_objects = [
    depot.objects.TaskQualifier,
    depot.objects.UserQualifier,
    depot.objects.Formula,
]
_filename_template = "{0}.py"


def create_files():
    for name in _module_names:
        filename = f"{name}.py"
        if not Path(filename).exists():
            with open(filename, "x") as fp:
                pass


def _get_functions_from_module(name: str):
    module = importlib.import_module(f"{name}")

    found_funcs = dict()
    for key, value in inspect.getmembers(module):
        if not key.startswith("_") and inspect.isfunction(value):
            print(key)
            found_funcs[key] = value

    return found_funcs


def read_and_import():
    for index, name in enumerate(_module_names):
        found_funcs = _get_functions_from_module(name)

        file_timestamp = os.path.getmtime(_filename_template.format(name))
        for f_name in found_funcs:
            depot.store(
                _module_objects[index](
                    ID=f"{f_name}",
                    timestamp=file_timestamp,
                    name=f_name,
                    content="",
                )
            )


def perform_qualifiers():
    _current_timestamp = datetime.datetime.now().timestamp()
    for USER_ID in config.get_uids():
        for TASK_ID in config.get_tasks_list():
            inputs = list(
                depot.search(
                    depot.objects.CheckResult,
                    depot.objects.Criteria("USER_ID", "==", USER_ID),
                    depot.objects.Criteria("TASK_ID", "==", TASK_ID),
                )
            )
            for f_name, func in _get_functions_from_module("task_qualifier"):
                rating = func(inputs)
                depot.store(
                    depot.objects.TaskScore(
                        ID=f"{USER_ID}/{TASK_ID}/{f_name}",
                        USER_ID=USER_ID,
                        TASK_ID=TASK_ID,
                        timestamp=_current_timestamp,
                        name=f_name,
                        rating=rating,
                    )
                )

        inputs = list(depot.search(depot.objects.TaskScore, depot.objects.Criteria("USER_ID", "==", USER_ID)))
        for f_name, func in _get_functions_from_module("user_qualifier"):
            rating = func(inputs)
            depot.store(
                depot.objects.UserScore(
                    ID=f"{USER_ID}/{f_name}", USER_ID=USER_ID, timestamp=_current_timestamp, name=f_name, rating=rating
                )
            )

        inputs = list(depot.search(depot.objects.UserScore, depot.objects.Criteria("USER_ID", "==", USER_ID)))
        for f_name, func in _get_functions_from_module("formula"):
            rating = func(inputs)
            depot.store(
                depot.objects.FinalScore(ID=f"{USER_ID}", USER_ID=USER_ID, timestamp=_current_timestamp, rating=rating)
            )
