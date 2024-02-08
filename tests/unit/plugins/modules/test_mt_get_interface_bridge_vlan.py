from __future__ import absolute_import, division, print_function

__metaclass__ = type


import pytest
import json

from ansible_collections.andrei.utils.plugins.modules import (
    mt_get_interface_bridge_vlan,
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
        mt_get_interface_bridge_vlan.main()
    out, err = capfd.readouterr()
    out = json.loads(out)
    assert not err
    assert out.get("failed", False)
    assert "missing required arguments" in out["msg"]


def test_simple_bridge(capfd):
    set_module_args(
        {
            "networks": NETWORKS,
        }
    )
    expected = [
        {
            "bridge": "bridge1",
            "vlan-ids": 10,
        },
        {
            "bridge": "bridge1",
            "vlan-ids": 50,
        },
        {
            "bridge": "bridge1",
            "vlan-ids": 100,
        },
    ]

    with pytest.raises(SystemExit):
        mt_get_interface_bridge_vlan.main()
    out, err = capfd.readouterr()
    out = json.loads(out)
    assert not err
    assert not out.get("failed", False)
    assert out["new_data"] == expected


def test_trunk_ports(capfd):
    set_module_args({"networks": NETWORKS, "trunk_ports": ["ether1", "ether2"]})
    expected = [
        {
            "bridge": "bridge1",
            "tagged": "bridge1,ether1,ether2",
            "vlan-ids": 10,
        },
        {
            "bridge": "bridge1",
            "tagged": "bridge1,ether1,ether2",
            "vlan-ids": 50,
        },
        {
            "bridge": "bridge1",
            "tagged": "bridge1,ether1,ether2",
            "vlan-ids": 100,
        },
    ]

    with pytest.raises(SystemExit):
        mt_get_interface_bridge_vlan.main()
    out, err = capfd.readouterr()
    out = json.loads(out)
    assert not err
    assert not out.get("failed", False)
    assert out["new_data"] == expected


def test_access_ports(capfd):
    set_module_args(
        {
            "networks": NETWORKS,
            "access_ports": [
                {
                    "vlan": "GENERAL",
                    "ports": ["ether3"],
                },
                {
                    "vlan": "MGMT",
                    "ports": ["ether4"],
                },
            ],
        }
    )
    expected = [
        {
            "bridge": "bridge1",
            "vlan-ids": 10,
        },
        {
            "bridge": "bridge1",
            "untagged": "ether3",
            "vlan-ids": 50,
        },
        {
            "bridge": "bridge1",
            "untagged": "ether4",
            "vlan-ids": 100,
        },
    ]

    with pytest.raises(SystemExit):
        mt_get_interface_bridge_vlan.main()
    out, err = capfd.readouterr()
    out = json.loads(out)
    assert not err
    assert not out.get("failed", False)
    assert out["new_data"] == expected


def test_all_args(capfd):
    set_module_args(
        {
            "networks": NETWORKS,
            "trunk_ports": ["ether1", "ether2"],
            "access_ports": [
                {
                    "vlan": "GENERAL",
                    "ports": ["ether3"],
                },
                {
                    "vlan": "MGMT",
                    "ports": ["ether4"],
                },
            ],
            "bridge_name": "bridge2",
        }
    )
    expected = [
        {
            "bridge": "bridge2",
            "tagged": "bridge2,ether1,ether2",
            "vlan-ids": 10,
        },
        {
            "bridge": "bridge2",
            "tagged": "bridge2,ether1,ether2",
            "untagged": "ether3",
            "vlan-ids": 50,
        },
        {
            "bridge": "bridge2",
            "tagged": "bridge2,ether1,ether2",
            "untagged": "ether4",
            "vlan-ids": 100,
        },
    ]

    with pytest.raises(SystemExit):
        mt_get_interface_bridge_vlan.main()
    out, err = capfd.readouterr()
    out = json.loads(out)
    assert not err
    assert not out.get("failed", False)
    assert out["new_data"] == expected


def test_missing_vlan(capfd):
    set_module_args(
        {
            "networks": NETWORKS,
            "access_ports": [
                {
                    "vlan": "GENERAL",
                    "ports": ["ether3"],
                },
                {
                    "vlan": "BAD",
                    "ports": ["ether4"],
                },
            ],
        }
    )
    with pytest.raises(SystemExit):
        mt_get_interface_bridge_vlan.main()
    out, err = capfd.readouterr()
    out = json.loads(out)
    assert not err
    assert out.get("failed", False)
    assert "Cannot find VLAN 'BAD'" == out["msg"]


def test_selective_trunk(capfd):
    set_module_args(
        {
            "networks": NETWORKS,
            "trunk_ports": [
                {
                    "vlan": "GENERAL",
                    "ports": ["ether1", "ether4"],
                },
            ],
        }
    )
    expected = [
        {
            "bridge": "bridge1",
            "vlan-ids": 10,
        },
        {
            "bridge": "bridge1",
            "tagged": "bridge1,ether1,ether4",
            "vlan-ids": 50,
        },
        {
            "bridge": "bridge1",
            "vlan-ids": 100,
        },
    ]

    with pytest.raises(SystemExit):
        mt_get_interface_bridge_vlan.main()
    out, err = capfd.readouterr()
    out = json.loads(out)
    print(out)
    assert not err
    assert not out.get("failed", False)
    assert out["new_data"] == expected


def test_mixed_trunk(capfd):
    set_module_args(
        {
            "networks": NETWORKS,
            "trunk_ports": [
                "ether1",
                {
                    "vlan": "GENERAL",
                    "ports": ["ether2"],
                },
                "ether4",
            ],
        }
    )
    expected = [
        {
            "bridge": "bridge1",
            "vlan-ids": 10,
            "tagged": "bridge1,ether1,ether4",
        },
        {
            "bridge": "bridge1",
            "tagged": "bridge1,ether1,ether2,ether4",
            "vlan-ids": 50,
        },
        {
            "bridge": "bridge1",
            "tagged": "bridge1,ether1,ether4",
            "vlan-ids": 100,
        },
    ]

    with pytest.raises(SystemExit):
        mt_get_interface_bridge_vlan.main()
    out, err = capfd.readouterr()
    out = json.loads(out)
    print(out)
    assert not err
    assert not out.get("failed", False)
    assert out["new_data"] == expected


def test_bad_trunk_type(capfd):
    set_module_args(
        {
            "networks": NETWORKS,
            "trunk_ports": [
                {
                    "vlan": "GENERAL",
                    "ports": ["ether1"],
                },
                123,
            ],
        }
    )
    with pytest.raises(SystemExit):
        mt_get_interface_bridge_vlan.main()
    out, err = capfd.readouterr()
    out = json.loads(out)
    assert not err
    assert out.get("failed", False)
    assert "Element at index 1 type (int) is unsupported" == out["msg"]


def test_missing_trunk_vlan(capfd):
    set_module_args(
        {
            "networks": NETWORKS,
            "trunk_ports": [
                {
                    "vlan": "GENERAL",
                    "ports": ["ether3"],
                },
                {
                    "vlan": "BAD",
                    "ports": ["ether4"],
                },
            ],
        }
    )
    with pytest.raises(SystemExit):
        mt_get_interface_bridge_vlan.main()
    out, err = capfd.readouterr()
    out = json.loads(out)
    assert not err
    assert out.get("failed", False)
    assert "Cannot find VLAN 'BAD'" == out["msg"]


def test_hybrid(capfd):
    set_module_args(
        {
            "networks": NETWORKS,
            "trunk_ports": [
                "ether1",
                "ether2",
                {
                    "vlan": "VM",
                    "ports": ["ether3"],
                },
                {
                    "vlan": "MGMT",
                    "ports": ["ether4"],
                },
            ],
            "access_ports": [
                {
                    "vlan": "GENERAL",
                    "ports": ["ether1", "ether4"],
                },
                {
                    "vlan": "VM",
                    "ports": ["ether3"],
                },
            ],
        }
    )
    expected = [
        {
            "bridge": "bridge1",
            "tagged": "bridge1,ether1,ether2",
            "untagged": "ether3",
            "vlan-ids": 10,
        },
        {
            "bridge": "bridge1",
            "tagged": "bridge1,ether2",
            "untagged": "ether1,ether4",
            "vlan-ids": 50,
        },
        {
            "bridge": "bridge1",
            "tagged": "bridge1,ether1,ether2,ether4",
            "vlan-ids": 100,
        },
    ]

    with pytest.raises(SystemExit):
        mt_get_interface_bridge_vlan.main()
    out, err = capfd.readouterr()
    out = json.loads(out)
    print(out)
    assert not err
    assert not out.get("failed", False)
    assert out["new_data"] == expected
