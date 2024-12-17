#!/usr/bin/env python3
"""
Commandline interface
"""
import argparse
import atexit
import cmd
import datetime
import io
import logging
import os
import re
import secrets
import shlex
import shutil
import sys
import tempfile
from tomllib import load
from pathlib import Path
from pprint import pprint

from .. import deliver, config, control, depot, make, score, publish  # NoQA: F401
from ..depot.objects import Criteria as Rule
from ..log import get_logger
from ..make import anytime

try:
    import readline
except ModuleNotFoundError:
    from unittest.mock import MagicMock

    readline = MagicMock()

try:
    from .._version import version
except ModuleNotFoundError:
    version = "0.0.0"

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
            case ["task", task]:
                pprint(config.get_task_info(task))
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
            case ["task"]:
                return self.filtertext(config.get_tasks_list(), word, shift=delta, quote=quote)

    def show_objects(self, Type, *options, actual=True, flt=".*", dump=False):
        print(f"\t{Type.__name__}:")
        optnames = ("ID",)
        rules = {optname: Rule(optname, "==", opt) for optname, opt in zip(optnames, options)}
        for hw in depot.search(Type, *rules.values(), actual=actual):
            try:
                resflt = re.search(flt, hw["ID"])
            except Exception as E:
                log(f"Regexp error: {E}")
                return
            if resflt:
                print(hw)
                if ("ID" in rules or dump) and hasattr(hw, "content"):
                    for fname in hw.content:
                        try:
                            content = hw.content[fname].decode()
                        except Exception:
                            content = str(hw.content[fname])
                        print(f"\t{fname}:\n{content}" if dump else f"\t{fname}")
                if dump:
                    if hasattr(hw, "checks"):
                        pprint(getattr(hw, "checks"))
                    if stderr := getattr(hw, "stderr", None):
                        print(stderr.decode(errors="replace"))

    def do_show(self, arg):
        """Show objects or individual object"""
        args = self.shplit(arg)
        if len(args) > 0:
            if args[0] not in self.whatshow:
                log(f"Unknown object '{args[0]}'")
                return
        else:
            args = ["homework"]
        if dodump := "dump" in args:
            args.remove("dump")
        match args:
            case [Type]:
                self.show_objects(self.whatshow[Type], dump=dodump)
            case [Type, "all"]:
                self.show_objects(self.whatshow[Type], actual=False, dump=dodump)
            case [Type, ID]:
                if self.is_regexp(ID):
                    self.show_objects(self.whatshow[Type], flt=ID, dump=dodump)
                else:
                    self.show_objects(self.whatshow[Type], ID, dump=dodump)
            case [Type, ID, "all"]:
                if self.is_regexp(ID):
                    self.show_objects(self.whatshow[Type], actual=False, flt=ID, dump=dodump)
                else:
                    self.show_objects(self.whatshow[Type], ID, actual=False, dump=dodump)

    def help_show(self):
        res = f"""Show objects or individual object

show            - list homeworks
show TYPE       - list objects of type TYPE
show TYPE REGEX - list objects of type TYPE with ID matching REGEX
show TYPE ID    - print certain objects

Additionally:
                - "all" can be appended to show all versions of objects.
                - "dump" can be appended to show object contents

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
            case [Type, _]:
                return ["all", "dump"]

    def do_shell(self, arg):
        "Execute python code"
        try:
            print(eval(arg))
        except Exception as E:
            print(E)

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
            case [ID]:
                sol = depot.search(depot.objects.Solution, Rule("ID", "==", ID), actual=True, first=True)
                for name, result in make.run_solution_checks(sol).items():
                    print(f"{name}: {result}")

    def complete_check(self, text, line, begidx, endidx):
        (_, *args, word), delta, quote = self.qsplit(line, text, begidx, endidx)
        const = ["all", "new"]
        ids = [sol.ID for sol in depot.search(depot.objects.Solution, actual=True)]
        match args:
            case []:
                return self.filtertext(ids + const, word, shift=delta, quote=quote)

    def do_logging(self, arg):
        """Set console log level"""
        objnames = logging.getLevelNamesMapping()
        logger = logging.getLogger()
        handler = [hand for hand in logger.handlers if type(hand) is logging.StreamHandler][0]
        if arg:
            if arg in objnames:
                handler.setLevel(arg)
        else:
            print(logging.getLevelName(handler.level))

    def complete_logging(self, text, line, begidx, endidx):
        d = logging.getLevelNamesMapping()
        objnames = sorted(d, key=lambda x: d[x])
        return self.filtertext(objnames, text)

    def help_logging(self):
        res = "Set console log level\n\n" + ", ".join(
            f"{key}={val}" for key, val in logging.getLevelNamesMapping().items()
        )
        print(res, file=sys.stderr)

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

    do_exit = do_EOF

    def emptyline(self):
        pass


def copy_sample(path: Path) -> Path:
    """Copy sample project from inside package

    :param path: Destination path
    :return: Sample project config file name"""

    from .. import __path__ as module_path

    P = Path(path)
    shutil.copytree(Path(module_path[0]) / "example", P, dirs_exist_ok=True)
    CFile = P / "example.toml"
    with open(CFile, "rb") as f:
        cfg = load(f)
    # Hardcode times
    for gaps, userid in zip(((0, 0), (1, 2), (0, 3)), cfg["file"]["users"].values()):
        D = P / cfg["file"]["root_path"] / userid
        for gap, (taskname, task) in zip(gaps, cfg["tasks"].items()):
            custom = int((anytime(task["open_date"]) + datetime.timedelta(days=gap * 6)).timestamp())
            prog = D / taskname / "prog.py"
            if prog.exists():
                os.utime(prog, (custom, custom))
    return str(CFile)


def create_personal(path: Path, timelimit: str = "") -> Path:
    """Create temporary project for sngle task personal check

    :param path: Task directory
    :return: Temporary project config file name"""

    path = Path(path)
    user, task, cfgname = "user", path.name, "personal.toml"
    root = Path(tempfile.mkdtemp())
    repo = root / "repo"
    shutil.copytree(path, repo / user / task, dirs_exist_ok=True)

    conf = {
        "file": {"root_path": str(repo), "users": {"user": user}},
        "modules": {"deliver": ["file"]},
        "tasks": {task: {"open_date": datetime.date.today()}},
    }
    if timelimit:
        conf["tasks"][task]["time_limit"] = int(timelimit)
    config.create_config(root / cfgname, conf)
    return str(root / cfgname)


def shell():
    global logger

    parser = argparse.ArgumentParser(description="Homework checker")
    parser.add_argument(
        "-e",
        "--external",
        action="store_true",
        help="Treat config file as external one and use current directory as project path",
    )
    parser.add_argument("-c", "--command", action="append", help="Run a COMMAND")
    parser.add_argument("-p", "--personal", nargs="?", metavar="PATH", const=".", help="Check single task from PATH")
    parser.add_argument(
        "-s", "--sample", nargs="?", metavar="PATH", const="sample", help="Copy a sample project into PATH"
    )
    parser.add_argument(
        "-t", "--timelimit", metavar="NUMBER", default="", help="Set personal time limit to NUMBER seconds"
    )
    parser.add_argument("config", nargs="*", help="Configuration to parse (file path, prefix or 'key = vaule')")
    args = parser.parse_args()
    if args.sample:
        args.config.insert(0, copy_sample(args.sample))
        args.config.append(f'publish.SECRET_KEY = "{secrets.token_hex()}"')
    elif args.personal:
        args.config.insert(0, tmpcfg := create_personal(args.personal, args.timelimit))
        if not args.command:
            args.command = ["logging WARNING", "download", "check all", "show result .* dump"]
            if tmpcfg:
                atexit.register(lambda: shutil.rmtree(Path(tmpcfg).parent))
        else:
            print(args.config)
    if args.config:
        if "=" in args.config[0]:
            print(f"First config must be a file, not '{args.config[0]}'", file=sys.stderr)
            sys.exit(1)
        finalconf = config.process_configs(*args.config)
        if not args.external:
            os.chdir(finalconf.parent)
    logger = get_logger(__name__)
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
