""""""

from datetime import datetime

import pytest
from mergedeep import merge

from hworker.config import (
    repo_to_uid,
    uid_to_repo,
    uid_to_email,
    email_to_uid,
    get_imap_info,
    get_runtime_suffix,
    get_check_name,
    get_prog_name,
    get_remote_name,
    get_task_info,
    create_config,
    no_merge_processing,
)
from .user_config import user_config


@pytest.fixture(scope="function")
def tmp_config(request, tmp_path):
    config = tmp_path / "testconfig.toml"
    create_config(config, request.param)
    return config.as_posix()


class TestConfig:
    """"""

    _p_test_imap_info = {"host": "host", "folder": "folder", "username": "username", "password": "password"}

    @pytest.mark.parametrize("user_config", [{"imap": _p_test_imap_info}], indirect=True)
    def test_imap_info(self, user_config):
        assert get_imap_info() == {"letter_limit": -1, "port": 993, "users": {}} | self._p_test_imap_info

    def test_get_names(self):
        assert (get_prog_name(), get_remote_name(), get_runtime_suffix(), get_check_name()) == (
            "prog.py",
            "remote",
            ["in", "out"],
            "check",
        )

    @pytest.mark.parametrize("user_config", [{"imap": {"users": {"user_ID": "mail address"}}}], indirect=True)
    def test_mail_users(self, user_config):
        assert (uid_to_email("user_ID"), email_to_uid("mail address")) == ("mail address", "user_ID")

    @pytest.mark.parametrize("user_config", [{"git": {"users": {"user_ID": "repo"}}}], indirect=True)
    def test_git_users(self, user_config):
        assert (uid_to_repo("user_ID"), repo_to_uid("repo")) == ("repo", "user_ID")

    @pytest.mark.parametrize(
        "user_config",
        [{"tasks": {"task_ID": {"deliver_ID": "20230101/01", "open_date": datetime(year=2023, month=1, day=1)}}}],
        indirect=True,
    )
    def test_task_info(self, user_config):
        assert get_task_info("task_ID") == {
            "test_size": 100,
            "resource_limit": 3145728,
            "time_limit": 2,
            "deliver_ID": "20230101/01",
            "hard_deadline": datetime(2023, 1, 14, 0, 0),
            "hard_deadline_delta": "open_date+13d",
            "open_date": datetime(2023, 1, 1, 0, 0),
            "soft_deadline": datetime(2023, 1, 7, 0, 0),
            "soft_deadline_delta": "open_date+6d",
        }

    @pytest.mark.parametrize(
        "tmp_config",
        [
            {
                "tasks": {
                    "task_ID": {
                        "checks": {"The teacher:first/123": [], "The teacher:first/456": []},
                    }
                }
            }
        ],
        indirect=True,
    )
    def test_no_merge(self, tmp_config):
        final_content = {
            "formalization": {
                "no_merge": [
                    "checks",
                ]
            },
            "tasks": {"task_ID": {"checks": {"The teacher:first/deadline": [], "The teacher:first/attendance": []}}},
        }
        merge(
            final_content,
            {"tasks": {"task_ID": {"checks": {"The teacher:first/123": [], "The teacher:first/456": []}}}},
        )
        no_merge_processing(final_content, tmp_config, final_content["formalization"]["no_merge"], [])

        assert final_content["tasks"]["task_ID"]["checks"] == {"The teacher:first/123": [], "The teacher:first/456": []}
