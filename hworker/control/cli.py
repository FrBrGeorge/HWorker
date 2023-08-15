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
from .. import deliver, config, control, depot, make  # NoQA: F401
from ..log import get_logger
from ..depot.objects import Criteria as Rule

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
    DELIMETERS = set(' \t\n`~!@#$%^&*()-=+[{]}\\|;:",<>/?')

    def filtertext(self, seq, part, fmt="{}", shift=0):
        """Universal completion matcher"""
        match part:
            case str(_):
                flt = lambda txt: txt.startswith(part)  # Noqa E731
            case _:  # Must be callable
                flt = part
        res = [fmt.format(el[shift:]) for el in filter(flt, seq)]
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

    def do_show(self, arg):
        """Show objects or individual object"""
        args = self.shplit(arg)
        match args:
            case [] | ["homework"]:
                for hw in depot.search(depot.objects.Homework):
                    print(hw)
            case ["homework", ID]:
                hw = depot.search(depot.objects.Homework, Rule("ID", "==", ID), first=True, actual=True)
                print(hw)
                if hw:
                    for fname in hw.content:
                        print(f"\t{fname}")

    def qsplit(self, line, text, endidx):
        try:  # All quotes are closed
            res = shlex.split(line[:endidx]) + ([""] if line[endidx - 1] == " " else [])
        except ValueError:  # Unclosed quote
            res = shlex.split(line[:endidx] + "'")
            # print(f"\n@{res}")
        except Exception as E:
            log(E, "error")
        return res, len(res[-1]) - len(text)

    def complete_show(self, text, line, begidx, endidx):
        objnames = ("homework",)
        (_, *args, word), delta = self.qsplit(line, text, endidx)
        # print("\n→", args, text, delta)
        match args:
            case []:
                return self.filtertext(objnames, word, shift=delta)
            case ["homework"]:
                ids = [hw.ID for hw in depot.search(depot.objects.Homework, actual=True)]
                return self.filtertext(ids, word, shift=delta)

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
