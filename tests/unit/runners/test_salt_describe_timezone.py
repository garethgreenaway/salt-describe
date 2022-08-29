import logging
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
import saltext.salt_describe.runners.salt_describe_timezone as salt_describe_timezone_runner
import yaml

log = logging.getLogger(__name__)


@pytest.fixture
def configure_loader_modules():
    return {
        salt_describe_timezone_runner: {
            "__salt__": {"salt.execute": MagicMock()},
            "__opts__": {},
        },
    }


def test_timezone():
    """
    test describe.timezone
    """
    timezone_list = {"minion": "America/Los_Angeles"}

    timezone_sls_contents = {"America/Los_Angeles": {"timezone.system": []}}
    timezone_sls = yaml.dump(timezone_sls_contents)

    with patch.dict(
        salt_describe_timezone_runner.__salt__,
        {"salt.execute": MagicMock(return_value=timezone_list)},
    ):
        with patch.object(salt_describe_timezone_runner, "generate_sls") as generate_mock:
            assert salt_describe_timezone_runner.timezone("minion") is True
            generate_mock.assert_called_with({}, "minion", timezone_sls, sls_name="timezone")
