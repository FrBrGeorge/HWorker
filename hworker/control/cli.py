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
from pathlib import Path
from .. import deliver, config, control  # NoQA: F401
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

    def do_list(self, arg):
        "List some data TODO"
        args = self.shplit(arg)
        match args:
            case ["users", *_]:
                print("\n".join(config.get_uids()))

    def complete_list(self, text, line, begidx, endidx):
        objnames = ("users",)
        return [obj for obj in objnames if obj.startswith(text)]

    def do_shell(self, arg):
        "Execute python code"
        print(eval(arg))

    def complete_shell(self, text, line, begidx, endidx):
        objname, _, prefix = text.rpartition(".")
        if objname:
            return [f"{objname}.{w}" for w in dir(eval(objname)) if w.startswith(prefix)]
        else:
            return [w for w in globals() if w.startswith(prefix)]

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
