import pytest

from hworker.config import create_config, process_configs


@pytest.fixture(scope="function")
def user_config(request, tmp_path):
    config = tmp_path / "test-config.toml"
    create_config(config, request.param)
    process_configs(str(config))
