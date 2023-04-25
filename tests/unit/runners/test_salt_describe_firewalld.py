# Copyright 2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
#
import logging
from pathlib import PosixPath
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
import saltext.salt_describe.runners.salt_describe_firewalld as salt_describe_firewalld_runner
import yaml

log = logging.getLogger(__name__)


@pytest.fixture
def configure_loader_modules():
    return {
        salt_describe_firewalld_runner: {
            "__salt__": {"salt.execute": MagicMock()},
            "__opts__": {},
        },
    }


@pytest.fixture
def firewalld_ret():
    yield {
        "minion": {
            "public": {
                "target": ["default"],
                "icmp-block-inversion": ["no"],
                "interfaces": [""],
                "sources": [""],
                "services": ["dhcpv6-client ssh"],
                "ports": [""],
                "protocols": [""],
                "forward": ["yes"],
                "masquerade": ["no"],
                "forward-ports": [""],
                "source-ports": [""],
                "icmp-blocks": [""],
                "rich rules": [""],
            }
        }
    }


def test_firewalld(firewalld_ret):
    """
    test describe.firewalld
    """
    firewalld_sls_contents = {
        "add_firewalld_rule_0": {
            "firewalld.present": [{"name": "public"}, {"services": ["dhcpv6-client", "ssh"]}]
        }
    }
    firewalld_sls = yaml.dump(firewalld_sls_contents)

    with patch.dict(
        salt_describe_firewalld_runner.__salt__,
        {"salt.execute": MagicMock(return_value=firewalld_ret)},
    ):
        with patch.object(salt_describe_firewalld_runner, "generate_files") as generate_mock:
            assert "Generated SLS file locations" in salt_describe_firewalld_runner.firewalld(
                "minion"
            )
            generate_mock.assert_called_with(
                {}, "minion", firewalld_sls, sls_name="firewalld", config_system="salt"
            )


def test_firewalld_unavailable():
    """
    test describe.firewalld
    """
    firewalld_ret = {
        "minion": "'firewalld' __virtual__ returned False: The firewalld execution module cannot be loaded: the firewall-cmd binary is not in the path."
    }

    with patch.dict(
        salt_describe_firewalld_runner.__salt__,
        {"salt.execute": MagicMock(return_value=firewalld_ret)},
    ):
        with patch.object(salt_describe_firewalld_runner, "generate_files") as generate_mock:
            ret = salt_describe_firewalld_runner.firewalld("minion")


def test_firewalld_permissioned_denied(minion_opts, caplog, firewalld_ret):
    with patch.dict(
        salt_describe_firewalld_runner.__salt__,
        {"salt.execute": MagicMock(return_value=firewalld_ret)},
    ):
        with patch.dict(salt_describe_firewalld_runner.__opts__, minion_opts):
            with patch.object(PosixPath, "mkdir", side_effect=PermissionError) as mock_mkdir:
                with caplog.at_level(logging.WARNING):
                    ret = salt_describe_firewalld_runner.firewalld("minion")
                    assert not ret
                    assert (
                        "Unable to create directory /srv/salt/minion.  "
                        "Check that the salt user has the correct permissions."
                    ) in caplog.text
