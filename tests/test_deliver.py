"""Tests for deliver.git"""

import os
import tempfile

import pytest
from git import Repo


@pytest.fixture()
def example_git_repo():
    with tempfile.TemporaryDirectory() as temp_dir:
        repo_path = os.path.join(os.path.join(temp_dir, "test_repo"))
        os.mkdir(repo_path)

        repo = Repo.init(repo_path)
        with open(os.path.join(repo_path, "prog.py"), "wb") as p:
            p.write(b"a, b = eval(input())\n" b"print(max(a, b))")
        with open(os.path.join(repo_path, "URLS"), "wb") as urls:
            urls.write(b"https://github.com/Test/test/tree/main/20220913/1/tests")
        test_path = os.path.join(repo_path, "checks")
        os.mkdir(test_path)
        with open(os.path.join(test_path, "1.in"), "wb") as test_in:
            test_in.write(b"123, 345")
        with open(os.path.join(test_path, "1.out"), "wb") as test_out:
            test_out.write(b"345")
        repo.git.add(".")
        repo.git.commit(message="test commit")

        yield repo_path



class TestDeliverGit:
    """"""

    def test_get_homework_content(self, example_git_repo):
        """"""
        from hworker.deliver.git import get_homework_content

        print(*get_homework_content(example_git_repo).items(), sep="\n")

        # todo should be relative paths from git root. actually without root folder name(test_repo) in this example
        assert get_homework_content(example_git_repo) == {
            "/test_repo/prog.py": b"a, b = eval(input())\n" b"print(max(a, b))",
            "/test_repo/URLS": b"https://github.com/Test/test/tree/main/20220913/1/tests",
            "/test_repo/checks/1.in": b"123, 345",
            "/test_repo/checks/1.out": b"345",
        }
