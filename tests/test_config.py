""""""

import os

import pytest
import tomli_w

from hworker.config import get_git_directory, get_repos, get_uids, repo_to_uid, uid_to_repo, _default_name, read_config


def test_config():
    """"""
    # TODO: check all fields
    test_config_name = "test_config.toml"
    read_config(default_config=_default_name, config_name=test_config_name)
    assert get_git_directory() == "/tmp/hworker_git"
    assert get_repos() == ["repo", ]
    assert get_uids() == ["username", ]
    assert uid_to_repo("username") == "repo"
    assert repo_to_uid("repo") == "username"
    os.remove(test_config_name)
