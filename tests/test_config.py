""""""

import os

import pytest

from hworker.config import get_git_directory, get_repos, get_git_uids, repo_to_uid, uid_to_repo, \
    _default_config_name, _user_config_name, _final_config_name, get_final_config, deliverid_to_taskid, \
    taskid_to_deliverid, uid_to_email, email_to_uid


def test_config():
    """"""
    # TODO: check all fields, add tests configs
    # test_config_name, test_final_config_name = map(lambda s: "test_" + s, (_user_config_name, _final_config_name))
    get_final_config(default_config=_default_config_name,)
                     # user_config=test_config_name,
                     # final_config=test_final_config_name)
    assert get_git_directory() == "/tmp/hworker_git"
    assert uid_to_email("user_ID") == "mail address"
    assert email_to_uid("mail address") == "user_ID"
    assert get_repos() == ["repo", ]
    assert get_git_uids() == ["user_ID", ]
    assert uid_to_repo("user_ID") == "repo"
    assert repo_to_uid("repo") == "user_ID"
    assert taskid_to_deliverid("task_ID") == "20240101/01"
    assert deliverid_to_taskid("20240101/01") == "task_ID"
    os.remove(_user_config_name)
    os.remove(_final_config_name)
