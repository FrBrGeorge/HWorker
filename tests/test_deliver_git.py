"""Tests for deliver.git"""

from hworker.deliver.git.git import get_homework_content

from unittest.mock import patch
import os
import shutil

import pytest
from git import Repo


@pytest.fixture()
def example_git_repo():
    repo_path = os.path.join(os.path.join(os.path.abspath(os.sep), "tmp", "test_repo"))
    os.mkdir(repo_path)
    repo = Repo.init(repo_path)
    with open(os.path.join(repo_path, "prog.py"), "wb") as p:
        p.write(b"a, b = eval(input())\n"
                b"print(max(a, b))")
    with open(os.path.join(repo_path, "URLS"), "wb") as urls:
        urls.write(b"https://github.com/Test/test/tree/main/20220913/1/tests")
    os.mkdir(os.path.join(repo_path, "tests"))
    with open(os.path.join(repo_path, "1.in"), "wb") as test_in:
        test_in.write(b"123, 345")
    with open(os.path.join(repo_path, "1.out"), "wb") as test_out:
        test_out.write(b"345")
    repo.git.add(".")
    repo.git.commit(message="test commit")

    yield repo_path

    shutil.rmtree(repo_path)


class TestDeliverGit:
    """"""
    def test_get_homework_content(self, example_git_repo):
        """"""
        assert get_homework_content(example_git_repo) == {
            "prog": b"a, b = eval(input())\n" b"print(max(a, b))",
            "URLS": b"https://github.com/Test/test/tree/main/20220913/1/tests",
            "tests": {"1.in": b"123, 345", "1.out": b"345"},
        }
