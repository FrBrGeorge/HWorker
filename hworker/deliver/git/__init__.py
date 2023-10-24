"""Downloads solutions from repos"""
import datetime
import os
from pathlib import Path
from tempfile import gettempdir

import git

from ... import depot
from ...config import get_git_directory, get_repos, get_git_uids, repo_to_uid, get_tasks_list, get_task_info
from ...depot import store
from ...depot.objects import Homework, FileObject
from ...log import get_logger

_depot_prefix = "g"


def local_path(student_id: str) -> str:
    """Convert student id to local repo path

    :param student_id: student id received by name from the config
    :return: local repo path
    """
    git_directory = get_git_directory()
    return os.path.join(gettempdir(), git_directory, student_id)


def clone(repo: str) -> None:
    """Clone given repo to local directory

    :param repo: student repo path
    :return: -
    """
    get_logger(__name__).debug(f"Cloning {repo} repo")
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
    get_logger(__name__).debug(f"Pulling {repo} repo")
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
    get_logger(__name__).info("Updating all repos")
    for repo in repos:
        if not os.path.exists(local_path(repo_to_uid(repo))):
            clone(repo)
        else:
            pull(repo)


def get_homework_content(repo: git.Repo, root: Path, commit: str) -> dict:
    """Extracts tests, solution and URLS from homework and pack into dict

    :param root: local path to homework
    :return: dict with "prog", "tests" and "urls" keys
    """
    get_logger(__name__).debug(f"Getting {root} content")
    content = {
        path.relative_to(root).as_posix(): FileObject(
            content=repo.git.show("--no-patch", commit, path),
            timestamp=float(repo.git.log("-1", "--format=%ct", "--date=default", "--", commit, path)),
        )
        for path in map(lambda p: Path(root, p), repo.git.ls_tree(commit, root, r=True, name_only=True).split("\n"))
        if path.is_file() and f"{os.sep}." not in str(path.relative_to(root.parent))
    }
    return content


def get_commits(repo: git.Repo, path: Path) -> list[tuple[str, str]]:
    """Get list of all commits (with timestamps) for a given directory

    :param repo: repo local path
    :param path: homework local path
    :return: list of (commit hash, timestamp) pairs
    """
    get_logger(__name__).debug(f"Getting {path} commits")
    commits = [
        tuple(_.split()) for _ in repo.git.log("--format=%H %ct", "--date=default", "--", path.as_posix()).split("\n")
    ]
    return commits


# TODO: task_id from config
def download_all() -> None:
    """Update all solutions and store every version in depot"""
    depot.store(depot.objects.UpdateTime(name="Git deliver", timestamp=datetime.datetime.now().timestamp()))
    get_logger(__name__).info("Downloading (or updating) all repos and store them")
    update_all()
    for student_id in get_git_uids():
        repo = git.Repo(local_path(student_id))
        if not repo.heads:
            get_logger(__name__).warning(f"Got empty repo from {student_id} student!")
            continue
        for task in get_tasks_list():
            if os.path.isdir((task_path := Path(local_path(student_id), get_task_info(task).get("deliver_ID", "")))):
                commits = [_ for _ in get_commits(repo, task_path) if _]
                for commit in commits:
                    content = get_homework_content(repo, task_path, commit[0])
                    store(
                        Homework(
                            content=content,
                            ID=f"{_depot_prefix}.{student_id}/{task}",
                            USER_ID=student_id,
                            TASK_ID=os.path.join(task),
                            timestamp=float(commit[1]),
                            is_broken=False,
                        )
                    )
