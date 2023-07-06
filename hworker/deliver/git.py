"""Downloads solutions from repos"""

import os
import datetime as dt
from collections import namedtuple

import git

# from ..depot import store_git
# from ..config import get_git_directory, get_repos
# from ..log import logger


DepotInfo = namedtuple("DepotInfo", ["type", "path", "first_commit", "last_commit"])


def username(repo: str) -> str:
    """

    :param repo:
    :return:
    """
    return repo.split("/", 2)[-1]


def local_path(user: str) -> str:
    """

    :param user:
    :return:
    """
    git_directory = get_git_directory()
    return os.path.join(git_directory, user)


def clone(repo: str) -> bool:
    """

    :param repo:
    :return:
    """
    try:
        git.Repo.clone_from(repo, local_path(username(repo)))
    except git.GitError:
        # log
        return False
    return True


def pull(repo: str) -> bool:
    """

    :param repo:
    :return:
    """
    try:
        g = git.cmd.Git(local_path(username(repo)))
        g.pull()
    except git.GitError:
        # log
        return False
    return True


def clone_all() -> bool:
    """

    :return:
    """
    repos, results = get_repos(), []
    for repo in repos:
        results.append(clone(repo))
    return all(results)


def pull_all() -> bool:
    """

    :return:
    """
    repos, results = get_repos(), []
    for repo in repos:
        results.append(pull(repo))
    return all(results)


def get_runtime_tests(user: str, lesson: str, task: str) -> DepotInfo | None:
    """

    :param user:
    :param lesson:
    :param task:
    :return:
    """
    if os.path.isdir(os.path.join(local_path(user), lesson, task, "tests")):
        tests = os.path.join(local_path(user), lesson, task, "tests")
        g = git.cmd.Git(local_path(user))
        commits = g.log('--follow', '--format=%ct', '--date', 'default',
                        os.path.join(os.getcwd(), task, "tests")).split("\n")
        first_commit = dt.date.fromtimestamp(int(commits[-1]))
        last_commit = dt.date.fromtimestamp(int(commits[0]))
        return DepotInfo("tests", tests, first_commit, last_commit)
    return None


def get_solution(user: str, lesson: str, task: str) -> DepotInfo | None:
    """

    :param user:
    :param lesson:
    :param task:
    :return:
    """
    if os.path.isfile(os.path.join(local_path(user), lesson, task, "main.py")):
        main = os.path.join(local_path(user), lesson, task, "main")
        g = git.cmd.Git(local_path(user))
        commits = g.log('--follow', '--format=%ct', '--date', 'default',
                        os.path.join(os.getcwd(), task, "main.py")).split("\n")
        first_commit = dt.date.fromtimestamp(int(commits[-1]))
        last_commit = dt.date.fromtimestamp(int(commits[0]))
        return DepotInfo("solution", main, first_commit, last_commit)
    return None


def deliver() -> None:
    """

    :return:
    """
    repos = get_repos()
    for repo in repos:
        if not os.path.exists(local_path(repo)):
            clone(repo)
    pull_all()
    # TODO
