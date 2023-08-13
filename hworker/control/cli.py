#!/usr/bin/env python3
"""
Commandline interface
"""
import argparse
import atexit
import cmd
import shlex
import sys
import io
from pprint import pprint
from pathlib import Path
from .. import deliver, config, control, depot  # NoQA: F401
from ..log import get_logger

try:
    import readline
except ModuleNotFoundError:
    from unittest.mock import MagicMock as readline

logger = get_logger(__name__)
HISTFILE = ".history"


def log(message, severity="error"):
    getattr(logger, severity.lower())(message)
    if severity.lower() == "critical":
        raise RuntimeError(message)


class HWorker(cmd.Cmd):
    # TODO version
    intro = "HomeWorker shell. Type ? for help.\n"
    prompt = "hw> "

    def filtertext(self, seq, part, fmt="{}"):
        """Universal completion matcher"""
        match part:
            case str(_):
                flt = lambda txt: txt.startswith(part)  # Noqa E731
            case _:  # Must be callable
                flt = part
        res = [fmt.format(el) for el in filter(flt, seq)]
        return res

    @staticmethod
    def shplit(string):
        """Try to shlex.split(string) or print an error"""
        try:
            return shlex.split(string)
        except ValueError as E:
            log(E)
            return string.split()

    def do_download(self, arg):
        "Download all homeworks"
        deliver.download_all()

    def do_config(self, arg):
        "Print (some) information from config file"
        args = self.shplit(arg)
        match args:
            case ["users", *_]:
                print("\n".join(config.get_uids()))
            case ["tasks", *_]:
                print("\n".join(config.get_tasks_list()))
            case []:
                pprint(config.config())

    def complete_config(self, text, line, begidx, endidx):
        objnames = ("users", "tasks")
        return self.filtertext(objnames, text)

    def do_shell(self, arg):
        "Execute python code"
        print(eval(arg))

    def complete_shell(self, text, line, begidx, endidx):
        objname, _, prefix = text.rpartition(".")
        if objname:
            return self.filtertext(dir(eval(objname)), prefix, f"{objname}.{{}}")
        else:
            return self.filtertext(globals(), prefix)

    def do_EOF(self, arg):
        """Press Ctrl+D to exit"""
        if self.use_rawinput:
            print()
        return True

    doexit = do_EOF

    def emptyline(self):
        pass


def shell():
    parser = argparse.ArgumentParser(description="Homework checker")
    parser.add_argument("-c", "--command", action="append", help="Run a command")
    parser.add_argument("config", nargs="*", help="Configuration file to parse")
    args = parser.parse_args()
    if args.config:
        config.process_configs(*args.config)
    if args.command:
        with io.StringIO("\n".join(args.command) + "\n") as stdin:
            runner = HWorker(stdin=stdin)
            runner.use_rawinput = False
            runner.prompt = ""
            return runner.cmdloop(intro="")
    else:
        if not (hist := Path(HISTFILE)).is_file():
            hist.write_bytes(b"")
        readline.read_history_file(HISTFILE)
        atexit.register(lambda: readline.write_history_file(HISTFILE))
        for errors in range(100):
            try:
                HWorker().cmdloop()
                break
            except KeyboardInterrupt:
                print("^C", file=sys.stderr)
            else:
                break
        else:
            log("Too many errors")
