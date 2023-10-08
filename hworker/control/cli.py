#!/usr/bin/env python3
"""
Commandline interface
"""
import argparse
import atexit
import cmd
import io
import re
import secrets
import shlex
import sys
import os
import shutil
from pathlib import Path
from pprint import pprint

from .. import deliver, config, control, depot, make, score, publish  # NoQA: F401
from ..depot.objects import Criteria as Rule
from ..log import get_logger

try:
    import readline
except ModuleNotFoundError:
    from unittest.mock import MagicMock as readline

try:
    from .._version import version
except ModuleNotFoundError:
    version = "0.0.0"

logger = get_logger(__name__)
HISTFILE = ".history"


def log(message, severity="error"):
    getattr(logger, severity.lower())(message)
    if severity.lower() == "critical":
        raise RuntimeError(message)


class HWorker(cmd.Cmd):
    intro = f"HomeWorker v{version} shell. Type ? for help.\n"
    prompt = "hw> "
    DELIMETERS = set(' \t\n`~!@#$%^&*()-=+[{]}\\|;:",<>/?')
    whatshow = {
        "homework": depot.objects.Homework,
        "solution": depot.objects.Solution,
        "check": depot.objects.Check,
        "result": depot.objects.CheckResult,
        "taskscore": depot.objects.TaskScore,
        "userscore": depot.objects.UserScore,
    }

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
    def is_regexp(string):
        """Check if regexp is given instead of just string"""
        return string.startswith(".") or "*" in string

    @staticmethod
    def shplit(string):
        """Try to shlex.split(string) or print an error"""
        try:
            return shlex.split(string)
        except ValueError as E:
            log(E)
            return string.split()

    def do_config(self, arg):
        """Print (some) information from config file"""
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

    def show_objects(self, Type, *options, actual=True, flt=".*"):
        print("@@", Type)
        optnames = ("ID",)
        rules = {optname: Rule(optname, "==", opt) for optname, opt in zip(optnames, options)}
        for hw in depot.search(Type, *rules.values(), actual=actual):
            if re.search(flt, hw["ID"]):
                print(hw)
                if "ID" in rules and hasattr(hw, "content"):
                    for fname in hw.content:
                        print(f"\t{fname}")

    def do_show(self, arg):
        """Show objects or individual object"""
        args = self.shplit(arg)
        if len(args) > 0:
            if args[0] not in self.whatshow:
                log(f"Unknown object '{args[0]}'")
                return
        else:
            args = ["homework"]
        match args:
            case [Type]:
                self.show_objects(self.whatshow[Type])
            case [Type, "all"]:
                self.show_objects(self.whatshow[Type], actual=False)
            case [Type, ID]:
                if self.is_regexp(ID):
                    self.show_objects(self.whatshow[Type], flt=ID)
                else:
                    self.show_objects(self.whatshow[Type], ID)
            case [Type, ID, "all"]:
                if self.is_regexp(ID):
                    self.show_objects(self.whatshow[Type], actual=False, flt=ID)
                else:
                    self.show_objects(self.whatshow[Type], ID, actual=False)

    def help_show(self):
        res = f"""Show objects or individual object

show            - list homeworks
show TYPE       - list objects of type TYPE
show TYPE REGEX - list objects of type TYPE with ID matching REGEX
show TYPE ID    - print certain objects

Additionally, "all" can be appended to show all versions of objects.

TYPE can be {', '.join(self.whatshow)}
        """
        print(res, file=sys.stderr)

    def complete_show(self, text, line, begidx, endidx):
        (_, *args, word), delta, quote = self.qsplit(line, text, begidx, endidx)
        # print("\n→", args, text, delta)
        match args:
            case []:
                return self.filtertext(self.whatshow, word, shift=delta)
            case [Type]:
                if Type in self.whatshow:
                    ids = [hw.ID for hw in depot.search(self.whatshow[Type], actual=True)]
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

    def do_download(self, arg):
        """Download all homeworks (do not parse if "only" parmeter is given)"""
        args = self.shplit(arg)
        deliver.download_all()
        if args != ["only"]:
            make.parse_all_stored_homeworks()

    def complete_download(self, text, line, begidx, endidx):
        objnames = ("only",)
        return self.filtertext(objnames, text)

    def do_score(self, arg):
        """Calculate scores"""
        control.do_score()

    # TODO delete()

    def do_check(self, arg):
        # TODO individual
        """Check new (default) or all homeworks"""
        args = self.shplit(arg)
        match args:
            case [] | ["new"]:
                make.check_new_solutions()
            case ["all"]:
                make.check_all_solutions()

    def complete_check(self, text, line, begidx, endidx):
        objnames = ("all", "new")
        return self.filtertext(objnames, text)

    def do_publish(self, arg):
        """Start publisher"""
        # TODO check if is anything to publish
        control.start_publish()

    def do_update(self, arg):
        """Download, check and score (for periodical run)"""
        control.update_all()

    def do_run(self, arg):
        """Download, check, score and publish at once"""
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


def copy_sample(path: Path) -> Path:
    """Copy sample project from inside package

    :param path: Destination path
    :return: Sample project config file name"""

    from .. import __path__ as module_path

    P = Path(path)
    shutil.copytree(Path(module_path[0]) / "example", P, dirs_exist_ok=True)
    return str(P / "example.toml")


def shell():
    parser = argparse.ArgumentParser(description="Homework checker")
    parser.add_argument(
        "-e",
        "--external",
        action="store_true",
        help="Treat config file as external one and use current directory as project path",
    )
    parser.add_argument("-c", "--command", action="append", help="Run a COMMAND")
    parser.add_argument(
        "-s", "--sample", nargs="?", metavar="PATH", const="sample", help="Copy a sample project into PATH"
    )
    parser.add_argument("config", nargs="*", help="Configuration to parse (file path, prefix or 'key = vaule')")
    args = parser.parse_args()
    if args.sample:
        args.config.insert(0, copy_sample(args.sample))
        args.config.append(f'publish.SECRET_KEY = "{secrets.token_hex()}"')
    if args.config:
        if "=" in args.config[0]:
            log(f"Fist config must be a file, not '{args.config[0]}'", "critical")
        finalconf = config.process_configs(*args.config)
        if not args.external:
            os.chdir(finalconf.parent)
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
