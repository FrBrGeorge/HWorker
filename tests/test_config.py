""""""

import pytest
from datetime import datetime

from hworker.config import (
    create_config,
    process_configs,
    repo_to_uid,
    uid_to_repo,
    uid_to_email,
    email_to_uid,
    get_imap_info,
    get_checks_suffix,
    get_checks_dir,
    get_prog_name,
    get_urls_name,
    get_task_info,
)


@pytest.fixture(scope="function")
def user_config(request, tmp_path):
    config = tmp_path / "testconfig.toml"
    create_config(config, request.param)
    process_configs(str(config))


class TestConfig:
    """"""

    _p_test_imap_info = {"host": "host", "folder": "folder", "username": "username", "password": "password"}

    @pytest.mark.parametrize("user_config", [{"imap": _p_test_imap_info}], indirect=True)
    def test_imap_info(self, user_config):
        assert get_imap_info() == {"letter_limit": -1, "port": 993, "users": {}} | self._p_test_imap_info

    def test_get_names(self):
        assert (get_prog_name(), get_urls_name(), get_checks_suffix(), get_checks_dir()) == (
            "prog.py",
            "remotes",
            "in/out",
            "checks",
        )

    @pytest.mark.parametrize("user_config", [{"imap": {"users": {"user_ID": "mail address"}}}], indirect=True)
    def test_mail_users(self, user_config):
        assert (uid_to_email("user_ID"), email_to_uid("mail address")) == ("mail address", "user_ID")

    @pytest.mark.parametrize("user_config", [{"git": {"users": {"user_ID": "repo"}}}], indirect=True)
    def test_git_users(self, user_config):
        assert (uid_to_repo("user_ID"), repo_to_uid("repo")) == ("repo", "user_ID")

    @pytest.mark.parametrize(
        "user_config",
        [{"tasks": {"task_ID": {"deliver_ID": "20240101/01", "open_date": datetime(year=2024, month=1, day=1)}}}],
        indirect=True,
    )
    def test_task_info(self, user_config):
        assert get_task_info("task_ID") == {
            "deliver_ID": "20240101/01",
            "hard_deadline": datetime(2024, 1, 14, 0, 0),
            "hard_deadline_delta": "open_date+13d",
            "open_date": datetime(2024, 1, 1, 0, 0),
            "soft_deadline": datetime(2024, 1, 7, 0, 0),
            "soft_deadline_delta": "open_date+6d",
        }
