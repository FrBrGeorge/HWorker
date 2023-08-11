#!/usr/bin/env python3
'''
Commandline interface
'''
import atexit
import cmd
import shlex
import sys
import io
from pathlib import Path
from .. import deliver, config, control     # NoQA: F401
from ..log import get_logger
from ..config import get_uids
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
            case ["users", *tail]:
                print("\n".join(get_uids()))


    def complete_list(self, text, line, begidx, endidx):
        objnames = "users",
        return [obj for obj in objnames if obj.startswith(text)]


    def do_EOF(self, arg):
        """Press Ctrl+D to exit"""
        if self.use_rawinput:
            print()
        return True

    doexit = do_EOF

    def emptyline(self):
        pass


def shell():
    # TODO optparse
    if len(sys.argv) > 1 and sys.argv[1] == "-c":
        with io.StringIO("\n".join(sys.argv[2:]) + "\n") as stdin:
            runner = HWorker(stdin=stdin)
            runner.use_rawinput = False
            runner.prompt = ""
            res = runner.cmdloop(intro="")
    else:
        if not (hist := Path(HISTFILE)).is_file():
            hist.write_bytes(b'')
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
