"""Downloads solutions from repos"""

import os
from collections import namedtuple, defaultdict

import git

from ..depot import store_object
from ..config import get_git_directory, get_repos, get_ids, repo_to_id, id_to_repo
from ..log import get_logger
from ..deliver import Backend


# Temporary
StorageObject = namedtuple("StorageObject", ["storage_type",
                                             "content",
                                             "student_id",
                                             "homework_id",
                                             "version"])


def local_path(student_id: str) -> str:
    """

    :param student_id:
    :return:
    """
    git_directory = get_git_directory()
    return os.path.join(git_directory, student_id)


def clone(repo: str) -> None:
    """

    :param repo:
    :return:
    """
    get_logger(__name__).log(f"Cloning {repo} repo")
    try:
        git.Repo.clone_from(repo, local_path(repo_to_id(repo)))
    except git.GitError as git_error:
        get_logger(__name__).warn(f"Can't clone {repo} repo: {git_error}")


def pull(repo: str) -> None:
    """

    :param repo:
    :return:
    """
    get_logger(__name__).log(f"Pulling {repo} repo")
    try:
        g = git.cmd.Git(local_path(repo_to_id(repo)))
        g.pull()
    except git.GitError as git_error:
        get_logger(__name__).warn(f"Can't pull {repo} repo: {git_error}")


def update_all() -> None:
    """"""
    repos = get_repos()
    for repo in repos:
        if not os.path.exists(local_path(repo)):
            clone(repo)
        else:
            pull(repo)


def get_homework_content(path: str) -> defaultdict:
    """

    :param path:
    :return:
    """
    content = defaultdict(None)
    content["tests"] = []

    if os.path.isfile(os.path.join(path, "main.py")):
        with open(os.path.join(path, "main.py"), "rb") as prog:
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
    """

    :param path:
    :return:
    """
    g = git.cmd.Git(path)
    commits = [tuple(_.split()) for _ in g.log("--format", "%H %ct", "--date", "default").split("\n")]
    return commits


class GitBackend(Backend):
    """"""
    def download_all(self) -> None:
        """"""
        update_all()
        for student_id in get_ids():
            for lesson in os.listdir(local_path(student_id)):
                for task in os.listdir(os.path.join(local_path(student_id), lesson)):
                    task_path = os.path.join(local_path(student_id), lesson, task)
                    commits = get_commits(task_path)
                    for commit in commits:
                        repo = git.Repo(local_path(student_id))
                        repo.git.checkout(commit[0])
                        content = get_homework_content(task_path)

                        store_object(StorageObject("homework",
                                                   content,
                                                   student_id,
                                                   os.path.join(task, lesson),
                                                   commits[0] + commits[1]))

