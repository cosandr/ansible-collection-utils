from __future__ import absolute_import, division, print_function

__metaclass__ = type


import pytest
import json

from ansible_collections.andrei.utils.plugins.modules import (
    mt_get_interface_sw_egress,
)
from ansible_collections.andrei.utils.tests.unit.plugins.modules.utils import (
    validate_output,
)
from ansible_collections.community.general.tests.unit.plugins.modules.utils import (
    set_module_args,
)


NETWORKS = {
    "vm": {
        "vlan": 10,
    },
    "general": {
        "vlan": 50,
    },
    "mgmt": {
        "vlan": 100,
    },
}


def test_missing_args(capfd):
    set_module_args({})
    with pytest.raises(SystemExit):
        mt_get_interface_sw_egress.main()
    out, err = capfd.readouterr()
    out = json.loads(out)
    assert not err
    assert out.get("failed", False)
    assert "missing required arguments" in out["msg"]


def test_noop(capfd):
    set_module_args(
        {
            "existing": [],
            "networks": NETWORKS,
        }
    )
    expected_add = []
    expected_update = []
    expected_remove = []

    with pytest.raises(SystemExit):
        mt_get_interface_sw_egress.main()
    out, err = capfd.readouterr()
    out = json.loads(out)
    assert not err
    assert not out.get("failed", False)
    validate_output(out, expected_add, expected_update, expected_remove)


def test_add(capfd):
    set_module_args(
        {"existing": [], "networks": NETWORKS, "trunk_ports": ["ether1", "ether2"]}
    )
    expected_add = [
        {
            "vlan-id": 10,
            "tagged-ports": "switch1-cpu,ether1,ether2",
        },
        {
            "vlan-id": 50,
            "tagged-ports": "switch1-cpu,ether1,ether2",
        },
        {
            "vlan-id": 100,
            "tagged-ports": "switch1-cpu,ether1,ether2",
        },
    ]
    expected_update = []
    expected_remove = []

    with pytest.raises(SystemExit):
        mt_get_interface_sw_egress.main()
    out, err = capfd.readouterr()
    out = json.loads(out)
    assert not err
    assert not out.get("failed", False)
    validate_output(out, expected_add, expected_update, expected_remove)


def test_update(capfd):
    set_module_args(
        {
            "existing": [
                {
                    ".id": "1",
                    "vlan-id": 10,
                    "tagged-ports": "switch1-cpu,ether1,ether2",
                },
                {
                    ".id": "2",
                    "vlan-id": 50,
                    "tagged-ports": "switch1-cpu,ether1",
                },
                {
                    ".id": "3",
                    "vlan-id": 100,
                    "tagged-ports": "switch1-cpu,ether2",
                },
            ],
            "networks": NETWORKS,
            "trunk_ports": ["ether1", "ether2"],
        }
    )
    expected_add = []
    expected_update = [
        {
            ".id": "2",
            "vlan-id": 50,
            "tagged-ports": "switch1-cpu,ether1,ether2",
        },
        {
            ".id": "3",
            "vlan-id": 100,
            "tagged-ports": "switch1-cpu,ether1,ether2",
        },
    ]
    expected_remove = []

    with pytest.raises(SystemExit):
        mt_get_interface_sw_egress.main()
    out, err = capfd.readouterr()
    out = json.loads(out)
    assert not err
    assert not out.get("failed", False)
    validate_output(out, expected_add, expected_update, expected_remove)


def test_remove(capfd):
    set_module_args(
        {
            "existing": [
                {
                    ".id": "1",
                    "vlan-id": 10,
                    "tagged-ports": "switch1-cpu,ether1,ether2",
                },
                {
                    ".id": "2",
                    "vlan-id": 50,
                    "tagged-ports": "switch1-cpu,ether1,ether2",
                },
                {
                    ".id": "3",
                    "vlan-id": 100,
                    "tagged-ports": "switch1-cpu,ether1,ether2",
                },
                {
                    ".id": "5",
                    "vlan-id": 110,
                    "tagged-ports": "switch1-cpu,ether2",
                },
            ],
            "networks": NETWORKS,
            "trunk_ports": ["ether1", "ether2"],
        }
    )
    expected_add = []
    expected_update = []
    expected_remove = [
        {
            ".id": "5",
            "vlan-id": 110,
            "tagged-ports": "switch1-cpu,ether2",
        },
    ]

    with pytest.raises(SystemExit):
        mt_get_interface_sw_egress.main()
    out, err = capfd.readouterr()
    out = json.loads(out)
    assert not err
    assert not out.get("failed", False)
    validate_output(out, expected_add, expected_update, expected_remove)


def test_all(capfd):
    set_module_args(
        {
            "existing": [
                {
                    ".id": "1",
                    "vlan-id": 10,
                    "tagged-ports": "switch2-cpu,ether1,ether2,sfpplus1,sfp-sfpplus1",
                },
                {
                    ".id": "3",
                    "vlan-id": 100,
                    "tagged-ports": "switch2-cpu,ether1,ether2",
                },
                {
                    ".id": "5",
                    "vlan-id": 110,
                    "tagged-ports": "switch2-cpu,ether2",
                },
            ],
            "networks": NETWORKS,
            "trunk_ports": ["ether1", "sfp-sfpplus1", "ether2", "sfpplus1"],
            "switch_cpu": "switch2-cpu",
        }
    )
    expected_add = [
        {
            "vlan-id": 50,
            "tagged-ports": "switch2-cpu,ether1,ether2,sfpplus1,sfp-sfpplus1",
        },
    ]
    expected_update = [
        {
            ".id": "3",
            "vlan-id": 100,
            "tagged-ports": "switch2-cpu,ether1,ether2,sfpplus1,sfp-sfpplus1",
        },
    ]
    expected_remove = [
        {
            ".id": "5",
            "vlan-id": 110,
            "tagged-ports": "switch2-cpu,ether2",
        },
    ]

    with pytest.raises(SystemExit):
        mt_get_interface_sw_egress.main()
    out, err = capfd.readouterr()
    out = json.loads(out)
    assert not err
    assert not out.get("failed", False)
    validate_output(out, expected_add, expected_update, expected_remove)
