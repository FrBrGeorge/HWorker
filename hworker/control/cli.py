#!/usr/bin/env python3
"""
Commandline interface
"""
import argparse
import atexit
import cmd
import io
import re
import shlex
import sys
from pathlib import Path
from pprint import pprint

from .. import deliver, config, control, depot, make  # NoQA: F401
from ..depot.objects import Criteria as Rule
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
    DELIMETERS = set(' \t\n`~!@#$%^&*()-=+[{]}\\|;:",<>/?')

    def qsplit(self, line, text, begidx, endidx):
        try:  # All quotes are closed
            res = shlex.split(line[:endidx]) + ([""] if line[endidx - 1] == " " else [])
        except ValueError:  # Unclosed quote
            res = shlex.split(line[:endidx] + "'")
        except Exception as E:
            log(E, "error")
        delta = len(res[-1]) - len(text)
        return res, delta, line[begidx - delta - 1]

    def filtertext(self, seq, part, fmt="{}", shift=0, quote="'"):
        """Universal completion matcher"""
        match part:
            case str(_):
                flt = lambda txt: txt.startswith(part)  # Noqa E731
            case _:  # Must be callable
                flt = part
        res = [
            fmt.format(el[shift:]) if quote == "'" or not el[shift:] else shlex.quote(fmt.format(el[shift:]))
            for el in filter(flt, seq)
        ]
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
        """Download all homeworks (do not parse if "only" parmeter is given)"""
        args = self.shplit(arg)
        deliver.download_all()
        if args != ["only"]:
            make.make.parse_all_stored_homeworks()

    def complete_download(self, text, line, begidx, endidx):
        objnames = ("only",)
        return self.filtertext(objnames, text)

    def do_config(self, arg):
        "Print (some) information from config file"
        args = self.shplit(arg)
        match args:
            case ["users"] | ["user"]:
                print("\n".join(config.get_uids()))
            case ["user", uidp]:
                print(
                    "\n".join(
                        f"{uid}: {deluid}"
                        for uid, deluid in config.get_users().items()
                        if re.search(uidp, uid) or re.search(uidp, deluid)
                    )
                )
            case ["tasks"] | ["task"]:
                print("\n".join(config.get_tasks_list()))
            case []:
                pprint(config.config())

    def complete_config(self, text, line, begidx, endidx):
        objnames = ("user", "task", "users", "tasks")
        (_, *args, word), delta, quote = self.qsplit(line, text, begidx, endidx)
        match args:
            case []:
                return self.filtertext(objnames, word, shift=delta)
            case ["user"]:
                return self.filtertext(config.get_uids(), word, shift=delta, quote=quote)

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

    def complete_show(self, text, line, begidx, endidx):
        objnames = ("homework",)
        (_, *args, word), delta, quote = self.qsplit(line, text, begidx, endidx)
        # print("\n→", args, text, delta)
        match args:
            case []:
                return self.filtertext(objnames, word, shift=delta)
            case ["homework"]:
                ids = [hw.ID for hw in depot.search(depot.objects.Homework, actual=True)]
                return self.filtertext(ids, word, shift=delta, quote=quote)

    def do_shell(self, arg):
        "Execute python code"
        print(eval(arg))

    def complete_shell(self, text, line, begidx, endidx):
        objname, _, prefix = text.rpartition(".")
        if objname:
            return self.filtertext(dir(eval(objname)), prefix, f"{objname}.{{}}")
        else:
            return self.filtertext(globals(), prefix)

    def do_publish(self, arg):
        """Start publisher"""
        # TODO check if is anything to publish
        control.start_publish()

    def do_run(self, arg):
        """Download, check, core and publish at once"""
        control.big_red_button()

    def do_echo(self, arg):
        """Print a line"""
        print(arg)

    def do_fake(self, arg):
        args = self.shplit(arg)
        match args:
            case ["score"]:
                control.generate_scores()

    def complete_fake(self, text, line, begidx, endidx):
        objnames = ("score",)
        return self.filtertext(objnames, text)

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
