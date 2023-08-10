#!/usr/bin/env python3
'''
Commandline interface
'''
import cmd
import shlex
import sys
import io
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
        match args:
            case ["users", *tail]:
                print(tail)


    def complete_list(self, text, line, begidx, endidx):
        objnames = "users",
        return [obj for obj in objnames if obj.startswith(text)]


    def do_EOF(self, arg):
        """Press Ctrl+D to exit"""
        return True

    doexit = do_EOF

    def emptyline(self):
        pass

    # TODO history


def shell():
    # TODO optparse
    if len(sys.argv) > 1 and sys.argv[1] == "-c":
        with io.StringIO("\n".join(sys.argv[2:]) + "\n") as stdin:
            runner = HWorker(stdin=stdin)
            runner.use_rawinput = False
            runner.prompt = ""
            res = runner.cmdloop(intro="")
    else:
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
