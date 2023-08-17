"""Tests for deliver.git"""

import pytest
from git import Repo

from hworker.deliver.git import get_homework_content
from hworker import config


@pytest.fixture()
def example_git_repo(tmp_path_factory):
    repo_path = tmp_path_factory.mktemp("test_repo")
    repo = Repo.init(repo_path)
    repo.config_writer().set_value("user", "name", "myusername").release()
    repo.config_writer().set_value("user", "email", "myemail").release()
    (repo_path / "prog.py").write_bytes(b"a, b = eval(input())\nprint(max(a, b))")
    test_path = repo_path / config.get_check_name()
    test_path.mkdir()
    (test_path / "1.in").write_bytes(b"123, 345")
    (test_path / "1.out").write_bytes(b"345")
    (test_path / config.get_remote_name()).write_bytes(b"UserN:TaskN\n")
    repo.git.add(".")
    repo.git.commit(message="test commit")
    return str(repo_path)


class TestDeliverGit:
    """"""

    def test_get_homework_content(self, example_git_repo):
        """"""

        assert get_homework_content(example_git_repo) == {
            "prog.py": b"a, b = eval(input())\n" b"print(max(a, b))",
            "check/remote": b"UserN:TaskN\n",
            "check/1.in": b"123, 345",
            "check/1.out": b"345",
        }
