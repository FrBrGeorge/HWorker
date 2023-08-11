"""Downloads solutions from repos"""

import os
from functools import reduce

import git

from ...depot.objects import Homework
from ...depot import store
from ...config import get_git_directory, get_repos, get_git_uids, repo_to_uid, get_tasks_list
from ...log import get_logger


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
    get_logger(__name__).info(f"Cloning {repo} repo")
    if not os.path.exists(local_path(repo_to_uid(repo))):
        os.makedirs(local_path(repo_to_uid(repo)))

    try:
        git.Repo.clone_from(repo, local_path(repo_to_uid(repo)))
    except git.GitError as git_error:
        get_logger(__name__).warning(f"Can't clone {repo} repo: {git_error}")


def pull(repo: str) -> None:
    """Pull given repo in local directory

    :param repo: student repo path
    :return: -
    """
    get_logger(__name__).info(f"Pulling {repo} repo")
    try:
        repo = git.Repo(local_path(repo_to_uid(repo)))
        repo.git.pull("origin", "main")
    except git.GitError:
        try:
            repo.git.pull("origin", "master")
        except git.GitError as git_error:
            get_logger(__name__).warning(f"Can't pull {repo} repo: {git_error}")


def update_all() -> None:
    """Pull every repo from config list (or clone if not downloaded)"""
    repos = get_repos()
    get_logger(__name__).info(f"Updating all repos")
    for repo in repos:
        if not os.path.exists(local_path(repo_to_uid(repo))):
            clone(repo)
        else:
            pull(repo)


def get_file_content(path: str) -> bytes:
    """

    :param path:
    :return:
    """
    with open(path, "rb") as file:
        content = file.read()

    return content


def get_homework_content(root: str) -> dict:
    """Extracts tests, solution and URLS from homework and pack into dict

    :param root: local path to homework
    :return: dict with "prog", "tests" and "urls" keys
    """
    get_logger(__name__).info(f"Getting {root} content")

    # Modified https://code.activestate.com/recipes/577879-create-a-nested-dictionary-from-oswalk/
    content = {}
    root = root.rstrip(os.sep)
    start = root.rfind(os.sep) + 1
    for path, dirs, files in os.walk(root):
        if all(map(lambda s: not s.startswith("."), path.split(os.sep))):
            folders = path[start:].split(os.sep)
            subdir = {file: get_file_content(os.path.join(path, file)) for file in files}
            parent = reduce(dict.get, folders[:-1], content)
            parent[folders[-1]] = subdir
    return content


def get_commits(repo: git.Repo, path: str) -> list[tuple[str, str]]:
    """Get list of all commits (with timestamps) for a given directory

    :param repo: repo local path
    :param path: homework local path
    :return: list of (commit hash, timestamp) pairs
    """
    get_logger(__name__).info(f"Getting {path} commits")
    commits = [tuple(_.split()) for _ in repo.git.log("--format=%H %ct", "--date=default", "--", path).split("\n")]
    # get_logger(__name__).info(commits)
    return commits


# TODO: task_id from config
def download_all() -> None:
    """Update all solutions and store every version in depot"""
    get_logger(__name__).info(f"Downloading (or updating) all repos and store them")
    update_all()
    for student_id in get_git_uids():
        repo = git.Repo(local_path(student_id))
        for task in get_tasks_list():
            if os.path.isdir((task_path := os.path.join(local_path(student_id), task))):
                commits = get_commits(repo, task_path)
                for commit in commits:
                    repo.git.checkout(commit[0])
                    content = get_homework_content(task_path)
                    # get_logger(__name__).info(content)
                    store(
                        Homework(
                            content=content,
                            ID=commit[0],
                            USER_ID=student_id,
                            TASK_ID=os.path.join(task),
                            timestamp=commit[1],
                            is_broken=False,
                        )
                    )
