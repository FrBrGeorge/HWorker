#!/usr/bin/env python3
""""""
import pytest
import hworker.config


@pytest.fixture(scope="session", autouse=True)
def global_user_config(tmp_path_factory):
    config = tmp_path_factory.getbasetemp() / "testconfig.toml"
    hworker.config.create_config(config, {})
    hworker.config.process_configs(str(config))
