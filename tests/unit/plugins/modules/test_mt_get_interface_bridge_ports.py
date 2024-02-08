from __future__ import absolute_import, division, print_function

__metaclass__ = type


import pytest
import json

from ansible_collections.andrei.utils.plugins.modules import (
    mt_get_interface_bridge_ports,
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
        mt_get_interface_bridge_ports.main()
    out, err = capfd.readouterr()
    out = json.loads(out)
    assert not err
    assert out.get("failed", False)
    assert "missing required arguments" in out["msg"]


def test_simple_bridge(capfd):
    set_module_args(
        {
            "networks": NETWORKS,
            "all_ports": ["ether1", "ether2"],
        }
    )
    expected = [
        {
            "bridge": "bridge1",
            "interface": "ether1",
        },
        {
            "bridge": "bridge1",
            "interface": "ether2",
        },
    ]

    with pytest.raises(SystemExit):
        mt_get_interface_bridge_ports.main()
    out, err = capfd.readouterr()
    out = json.loads(out)
    assert not err
    assert not out.get("failed", False)
    assert out["new_data"] == expected


def test_all_args_crs2xx(capfd):
    set_module_args(
        {
            "networks": NETWORKS,
            "all_ports": ["ether1", "ether2"],
            "bridge_name": "bridge2",
            "port_params": {
                "hw": True,
            },
        }
    )
    expected = [
        {
            "bridge": "bridge2",
            "interface": "ether1",
            "hw": True,
        },
        {
            "bridge": "bridge2",
            "interface": "ether2",
            "hw": True,
        },
    ]

    with pytest.raises(SystemExit):
        mt_get_interface_bridge_ports.main()
    out, err = capfd.readouterr()
    out = json.loads(out)
    assert not err
    assert not out.get("failed", False)
    assert out["new_data"] == expected


def test_all_args_crs3xx(capfd):
    set_module_args(
        {
            "networks": NETWORKS,
            "all_ports": ["ether1", "ether2", "ether3", "ether4"],
            "trunk_ports": ["ether1", "ether3"],
            "access_ports": [
                {
                    "vlan": "GENERAL",
                    "ports": ["ether2"],
                },
            ],
            "bridge_name": "bridge2",
            "port_params": {
                "hw": True,
            },
        }
    )
    expected = [
        {
            "bridge": "bridge2",
            "interface": "ether1",
            "frame-types": "admit-only-vlan-tagged",
            "hw": True,
        },
        {
            "bridge": "bridge2",
            "interface": "ether2",
            "pvid": 50,
            "hw": True,
        },
        {
            "bridge": "bridge2",
            "interface": "ether3",
            "frame-types": "admit-only-vlan-tagged",
            "hw": True,
        },
        {
            "bridge": "bridge2",
            "interface": "ether4",
            "hw": True,
        },
    ]

    with pytest.raises(SystemExit):
        mt_get_interface_bridge_ports.main()
    out, err = capfd.readouterr()
    out = json.loads(out)
    assert not err
    assert not out.get("failed", False)
    assert out["new_data"] == expected


def test_bad_networks(capfd):
    set_module_args(
        {
            "networks": NETWORKS,
            "all_ports": ["ether1", "ether2"],
            "access_ports": [
                {
                    "vlan": "BAD",
                    "ports": ["ether2"],
                },
            ],
        }
    )
    with pytest.raises(SystemExit):
        mt_get_interface_bridge_ports.main()
    out, err = capfd.readouterr()
    out = json.loads(out)
    assert not err
    assert out.get("failed", False)
    assert "Cannot find VID for 'BAD'" in out["msg"]


def test_bad_ports_access(capfd):
    set_module_args(
        {
            "networks": NETWORKS,
            "all_ports": ["ether1", "ether2"],
            "access_ports": [
                {
                    "vlan": "GENERAL",
                    "ports": ["ether100"],
                },
            ],
        }
    )
    with pytest.raises(SystemExit):
        mt_get_interface_bridge_ports.main()
    out, err = capfd.readouterr()
    out = json.loads(out)
    assert not err
    assert out.get("failed", False)
    assert "'ether100' is not a bridge port" in out["msg"]


def test_bad_ports_trunk(capfd):
    set_module_args(
        {
            "networks": NETWORKS,
            "all_ports": ["ether1", "ether2"],
            "trunk_ports": ["ether101"],
        }
    )
    with pytest.raises(SystemExit):
        mt_get_interface_bridge_ports.main()
    out, err = capfd.readouterr()
    out = json.loads(out)
    assert not err
    assert out.get("failed", False)
    assert "'ether101' is not a bridge port" in out["msg"]


def test_selective_trunk(capfd):
    set_module_args(
        {
            "networks": NETWORKS,
            "all_ports": ["ether1", "ether2", "ether3", "ether4"],
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
            "interface": "ether1",
            "frame-types": "admit-only-vlan-tagged",
        },
        {
            "bridge": "bridge1",
            "interface": "ether2",
        },
        {
            "bridge": "bridge1",
            "interface": "ether3",
        },
        {
            "bridge": "bridge1",
            "interface": "ether4",
            "frame-types": "admit-only-vlan-tagged",
        },
    ]

    with pytest.raises(SystemExit):
        mt_get_interface_bridge_ports.main()
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
            "all_ports": ["ether1", "ether2", "ether3", "ether4"],
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
            "interface": "ether1",
            "frame-types": "admit-only-vlan-tagged",
        },
        {
            "bridge": "bridge1",
            "interface": "ether2",
            "frame-types": "admit-only-vlan-tagged",
        },
        {
            "bridge": "bridge1",
            "interface": "ether3",
        },
        {
            "bridge": "bridge1",
            "interface": "ether4",
            "frame-types": "admit-only-vlan-tagged",
        },
    ]

    with pytest.raises(SystemExit):
        mt_get_interface_bridge_ports.main()
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
            "all_ports": ["ether1", "ether2"],
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
        mt_get_interface_bridge_ports.main()
    out, err = capfd.readouterr()
    out = json.loads(out)
    assert not err
    assert out.get("failed", False)
    assert "Element at index 1 type (int) is unsupported" == out["msg"]


def test_hybrid_crs3xx(capfd):
    set_module_args(
        {
            "networks": NETWORKS,
            "all_ports": ["ether1", "ether2", "ether3", "ether4"],
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
            "interface": "ether1",
            "pvid": 50,
        },
        {
            "bridge": "bridge1",
            "interface": "ether2",
            "frame-types": "admit-only-vlan-tagged",
        },
        {
            "bridge": "bridge1",
            "interface": "ether3",
            "pvid": 10,
        },
        {
            "bridge": "bridge1",
            "interface": "ether4",
            "pvid": 50,
        },
    ]

    with pytest.raises(SystemExit):
        mt_get_interface_bridge_ports.main()
    out, err = capfd.readouterr()
    out = json.loads(out)
    assert not err
    assert not out.get("failed", False)
    assert out["new_data"] == expected
