""""""

import os

import pytest

from hworker.config import get_git_directory, get_repos, get_uids, repo_to_uid, uid_to_repo, \
    _default_config_name, _user_config_name, _final_config_name, get_final_config


def test_config():
    """"""
    # TODO: check all fields, add tests configs
    # test_config_name, test_final_config_name = map(lambda s: "test_" + s, (_user_config_name, _final_config_name))
    get_final_config(default_config=_default_config_name,)
                     # user_config=test_config_name,
                     # final_config=test_final_config_name)
    assert get_git_directory() == "/tmp/hworker_git"
    assert get_repos() == ["repo", ]
    assert get_uids() == ["user_ID", ]
    assert uid_to_repo("user_ID") == "repo"
    assert repo_to_uid("repo") == "user_ID"
    # TODO: make path relative
    os.remove(os.path.join("hworker", "config", _user_config_name))
    os.remove(os.path.join("hworker", "config", _final_config_name))
