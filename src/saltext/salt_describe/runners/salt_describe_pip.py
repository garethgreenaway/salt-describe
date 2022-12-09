"""
Module for building state file

.. versionadded:: 3006

"""
import logging
import sys

import yaml
from saltext.salt_describe.utils.init import generate_files

__virtualname__ = "describe"


log = logging.getLogger(__name__)


def __virtual__():
    return __virtualname__


def _parse_salt(minion, pip_list, **kwargs):
    """
    Parse the returned pip commands and return
    salt data.
    """

    state_name = "installed_pip_libraries"
    state_fun = "pip.installed"

    state_contents = {state_name: {state_fun: [{"pkgs": pip_list}]}}
    return state_contents


def _parse_ansible(minion, pip_list, **kwargs):
    """
    Parse the returned pip commands and return
    ansible data.
    """
    state_contents = []
    data = {"tasks": []}
    if not kwargs.get("hosts"):
        log.error(
            "Hosts was not passed. You will need to manually edit the playbook with the hosts entry"
        )
    else:
        data["hosts"] = kwargs.get("hosts")
    data["tasks"].append(
        {
            "name": f"installed_pip_libraries",
            "ansible.builtin.pip": {
                "name": pip_list,
            },
        }
    )
    state_contents.append(data)
    return state_contents


def pip(tgt, tgt_type="glob", bin_env=None, config_system="salt", **kwargs):
    """
    Gather installed pip libraries and build a state file.

    CLI Example:

    .. code-block:: bash

        salt-run describe.pip minion-tgt

    """

    ret = __salt__["salt.execute"](
        tgt,
        "pip.freeze",
        tgt_type=tgt_type,
        bin_env=bin_env,
    )

    for minion in list(ret.keys()):
        minion_pip_list = ret[minion]
        state_contents = getattr(sys.modules[__name__], f"_parse_{config_system}")(
            minion, minion_pip_list, **kwargs
        )
        state = yaml.dump(state_contents)

        generate_files(__opts__, minion, state, sls_name="pip", config_system=config_system)

    return True
