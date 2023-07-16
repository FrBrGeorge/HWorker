"""Downloads solutions from repos"""

import os
from collections import namedtuple, defaultdict

import git

from ...depot import store_object
from .config import get_git_directory, get_repos, get_ids, repo_to_id, id_to_repo
from ...log import get_logger
from ...deliver import Backend


# Temporary
StorageObject = namedtuple("StorageObject", ["storage_type",
                                             "content",
                                             "student_id",
                                             "homework_id",
                                             "version"])


def local_path(student_id: str) -> str:
    """Convert student id to local repo path

    :param student_id: student id received by name from the config
    :return: local repo path
    """
    git_directory = get_git_directory()
    return os.path.join(git_directory, student_id)


def clone(repo: str) -> None:
    """Clone given repo to local directory

    :param repo: student repo path
    :return: -
    """
    get_logger(__name__).log(f"Cloning {repo} repo")
    if not os.path.exists(local_path(repo_to_id(repo))):
        os.makedirs(local_path(repo_to_id(repo)))

    try:
        git.Repo.clone_from(repo, local_path(repo_to_id(repo)))
    except git.GitError as git_error:
        get_logger(__name__).warn(f"Can't clone {repo} repo: {git_error}")


def pull(repo: str) -> None:
    """Pull given repo in local directory

    :param repo: student repo path
    :return: -
    """
    get_logger(__name__).log(f"Pulling {repo} repo")
    try:
        repo = git.Repo(local_path(repo_to_id(repo)))
        repo.git.pull()
    except git.GitError as git_error:
        get_logger(__name__).warn(f"Can't pull {repo} repo: {git_error}")


def update_all() -> None:
    """Pull every repo from config list (or clone if not downloaded)"""
    repos = get_repos()
    get_logger(__name__).log(f"Updating all repos")
    for repo in repos:
        if not os.path.exists(local_path(repo_to_id(repo))):
            clone(repo)
        else:
            pull(repo)


def get_homework_content(path: str) -> defaultdict:
    """Extracts tests, solution and URLS from homework and pack into dict

    :param path: local path to homework
    :return: dict with "prog", "tests" and "urls" keys
    """
    get_logger(__name__).log(f"Getting {path} content")
    content = defaultdict(None)
    content["tests"] = {}

    if os.path.isfile(os.path.join(path, "prog.py")):
        with open(os.path.join(path, "prog.py"), "rb") as prog:
            content["prog"] = prog.read()

    tests_path = os.path.join(path, "tests")
    if os.path.isdir(tests_path):
        for test_name in os.listdir(tests_path):
            with open(os.path.join(tests_path, test_name), "rb") as test:
                content["tests"][test_name] = test.read()

    if os.path.isfile(os.path.join(path, "URLS")):
        with open(os.path.join(path, "URLS"), "rb") as urls:
            content["urls"] = urls.read()

    return content


def get_commits(path: str) -> list[tuple[str, str]]:
    """Get list of all commits (with timestamps) for a given directory

    :param path: homework local path
    :return: list of (commit hash, timestamp) pairs
    """
    get_logger(__name__).log(f"Getting {path} commits")
    g = git.cmd.Git(path)
    commits = [tuple(_.split()) for _ in g.log("--format=%H %ct", "--date=default").split("\n")]
    return commits


class GitBackend(Backend):
    """Backend class for git"""
    def download_all(self) -> None:
        """Update all solutions and store every version in depot"""
        get_logger(__name__).log(f"Downloading (or updating) all repos and store them")
        update_all()
        for student_id in get_ids():
            repo = git.Repo(local_path(student_id))
            for lesson in os.listdir(local_path(student_id)):
                if lesson.isnumeric():
                    for task in os.listdir(os.path.join(local_path(student_id), lesson)):
                        task_path = os.path.join(local_path(student_id), lesson, task)
                        commits = get_commits(task_path)
                        for commit in commits:
                            repo.git.checkout(commit[0])
                            content = get_homework_content(task_path)

                            store_object(StorageObject("homework",
                                                       content,
                                                       student_id,
                                                       os.path.join(task, lesson),
                                                       commit[0] + commit[1]))