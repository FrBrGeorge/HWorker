""""""

import os

import pytest
import tomli_w

from hworker.config import get_git_directory, get_repos, get_uids, repo_to_uid, uid_to_repo, \
    _default_config_content, _default_config_name


@pytest.fixture(scope="module")
def example_config(temp_git_config, config_info):
    with open(temp_git_config, "wb") as cfg:
        tomli_w.dump(config_info, cfg)
    yield temp_git_config
    os.remove(temp_git_config)


@pytest.mark.parametrize("example_config",
                         [
                             (_default_config_name, _default_config_content)
                         ],
                         indirect=True)
def test_git_backend(example_config):
    """"""
    assert get_git_directory() == "~/.cache/hworker_git"
    assert get_repos() == ["repo (example, fill it)", ]
    assert get_uids() == ["username",]
    assert uid_to_repo("username") == "repo (example, fill it)"
    assert repo_to_uid("repo (example, fill it)") == "username"
