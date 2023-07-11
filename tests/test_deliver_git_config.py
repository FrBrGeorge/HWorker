""""""

import os

import pytest
import tomli_w

from hworker.deliver.git.config import get_git_directory, get_repos, get_ids, repo_to_id, id_to_repo


@pytest.fixture(scope="module")
def example_git_config(temp_git_config, config_info):
    with open(temp_git_config, "wb") as cfg:
        tomli_w.dump(config_info, cfg)
    yield temp_git_config
    os.remove(temp_git_config)


@pytest.mark.parametrize("example_git_config",
                         [
                             ("temp_git.toml",
                              {"directory": "test_directory",
                               "repos":
                                   {"user1": "repo1",
                                    "user2": "repo2"}})
                         ],
                         indirect=True)
def test_git_backend(example_git_config):
    """"""
    assert get_git_directory() == "test_directory"
    assert get_repos() == ["repo1", "repo2"]
    assert get_ids() == ["user1", "user2"]
    assert id_to_repo("user1") == "repo1"
    assert repo_to_id("repo2") == "user2"
