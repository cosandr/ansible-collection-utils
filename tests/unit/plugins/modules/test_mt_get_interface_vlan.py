from __future__ import absolute_import, division, print_function

__metaclass__ = type


import pytest
import json

from ansible_collections.andrei.utils.plugins.modules import (
    mt_get_interface_vlan,
)
from ansible_collections.community.general.tests.unit.plugins.modules.utils import (
    set_module_args,
)


def test_missing_args(capfd):
    set_module_args({})
    with pytest.raises(SystemExit):
        mt_get_interface_vlan.main()
    out, err = capfd.readouterr()
    out = json.loads(out)
    assert not err
    assert out.get("failed", False)
    assert "missing required arguments" in out["msg"]


def test_simple(capfd):
    set_module_args(
        {
            "networks": {
                "vm": {
                    "vlan": 10,
                },
                "general": {
                    "vlan": 50,
                },
                "mgmt": {
                    "vlan": 100,
                },
            },
        }
    )
    expected = [
        {
            "interface": "bridge1",
            "name": "VM",
            "vlan-id": 10,
            "mtu": 1500,
            "comment": None,
        },
        {
            "interface": "bridge1",
            "name": "GENERAL",
            "vlan-id": 50,
            "mtu": 1500,
            "comment": None,
        },
        {
            "interface": "bridge1",
            "name": "MGMT",
            "vlan-id": 100,
            "mtu": 1500,
            "comment": None,
        },
    ]

    with pytest.raises(SystemExit):
        mt_get_interface_vlan.main()
    out, err = capfd.readouterr()
    out = json.loads(out)
    assert not err
    assert not out.get("failed", False)
    assert out["new_data"] == expected


def test_all(capfd):
    set_module_args(
        {
            "networks": {
                "vm": {
                    "vlan": 10,
                    "cidr": "10.0.10.0/24",
                },
                "general": {
                    "vlan": 50,
                    "cidr": "10.0.50.0/24",
                    "cidr6": "fd00:50::0/64",
                },
                "mgmt": {
                    "vlan": 100,
                    "mtu": 9000,
                },
                "test": {
                    "vlan": 55,
                    "cidr": "10.0.55.0/24",
                    "cidr6": "fd00:55::0/64",
                    "mtu": 9000,
                },
            },
            "bridge_name": "bridge2",
        }
    )
    expected = [
        {
            "interface": "bridge2",
            "name": "VM",
            "vlan-id": 10,
            "mtu": 1500,
            "comment": "10.0.10.0/24",
        },
        {
            "interface": "bridge2",
            "name": "GENERAL",
            "vlan-id": 50,
            "mtu": 1500,
            "comment": "10.0.50.0/24; fd00:50::0/64",
        },
        {
            "interface": "bridge2",
            "name": "MGMT",
            "vlan-id": 100,
            "mtu": 9000,
            "comment": None,
        },
        {
            "interface": "bridge2",
            "name": "TEST",
            "vlan-id": 55,
            "mtu": 9000,
            "comment": "10.0.55.0/24; fd00:55::0/64",
        },
    ]

    with pytest.raises(SystemExit):
        mt_get_interface_vlan.main()
    out, err = capfd.readouterr()
    out = json.loads(out)
    assert not err
    assert not out.get("failed", False)
    assert out["new_data"] == expected
