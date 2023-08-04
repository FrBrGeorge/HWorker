#!/usr/bin/env python3
'''
Commandline interface
'''
import cmd
import shlex
import sys
from .. import deliver, config, control     # NoQA: F401
from ..log import get_logger

logger = get_logger(__name__)


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
        "TODO"
        args = self.shplit(arg)
        print(args)

    def do_EOF(self, arg):
        """Press Ctrl+D to exit"""
        return True

    doexit = do_EOF

    def emptyline(self):
        pass

    # TODO history


def shell():
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
