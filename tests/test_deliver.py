"""Tests for deliver.git"""

import os
import tempfile

import pytest
from git import Repo

from hworker.deliver.git import get_homework_content


@pytest.fixture()
def example_git_repo():
    with tempfile.TemporaryDirectory() as temp_dir:
        repo_path = os.path.join(os.path.join(temp_dir, "test_repo"))
        os.mkdir(repo_path)

        repo = Repo.init(repo_path)
        repo.config_writer().set_value("user", "name", "myusername").release()
        repo.config_writer().set_value("user", "email", "myemail").release()
        with open(os.path.join(repo_path, "prog.py"), "wb") as p:
            p.write(b"a, b = eval(input())\n" b"print(max(a, b))")
        test_path = os.path.join(repo_path, "check")
        os.mkdir(test_path)
        with open(os.path.join(test_path, "1.in"), "wb") as test_in:
            test_in.write(b"123, 345")
        with open(os.path.join(test_path, "1.out"), "wb") as test_out:
            test_out.write(b"345")
        with open(os.path.join(test_path, "remote"), "wb") as urls:
            urls.write(b"UserN:TaskN")
        repo.git.add(".")
        repo.git.commit(message="test commit")

        yield repo_path


class TestDeliverGit:
    """"""

    def test_get_homework_content(self, example_git_repo):
        """"""

        assert get_homework_content(example_git_repo) == {
            "prog.py": b"a, b = eval(input())\n" b"print(max(a, b))",
            "check/remote": b"UserN:TaskN",
            "check/1.in": b"123, 345",
            "check/1.out": b"345",
        }
