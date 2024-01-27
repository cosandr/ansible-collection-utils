from __future__ import absolute_import, division, print_function

__metaclass__ = type


import pytest
import json

from ansible_collections.andrei.utils.plugins.modules import (
    mt_get_interface_sw_ingress,
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
        mt_get_interface_sw_ingress.main()
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
        mt_get_interface_sw_ingress.main()
    out, err = capfd.readouterr()
    out = json.loads(out)
    assert not err
    assert not out.get("failed", False)
    validate_output(out, expected_add, expected_update, expected_remove)


def test_add(capfd):
    set_module_args(
        {
            "existing": [],
            "networks": NETWORKS,
            "access_ports": [
                {
                    "vlan": "VM",
                    "ports": ["ether1"],
                },
                {
                    "vlan": "GENERAL",
                    "ports": ["ether2", "ether3"],
                },
                {
                    "vlan": "MGMT",
                    "ports": ["ether4"],
                },
            ],
        }
    )
    expected_add = [
        {
            "customer-vid": 0,
            "new-customer-vid": 10,
            "ports": "ether1",
        },
        {
            "customer-vid": 0,
            "new-customer-vid": 50,
            "ports": "ether2,ether3",
        },
        {
            "customer-vid": 0,
            "new-customer-vid": 100,
            "ports": "ether4",
        },
    ]
    expected_update = []
    expected_remove = []

    with pytest.raises(SystemExit):
        mt_get_interface_sw_ingress.main()
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
                    "customer-vid": 0,
                    "new-customer-vid": 10,
                    "ports": "ether1",
                },
                {
                    ".id": "2",
                    "customer-vid": 0,
                    "new-customer-vid": 50,
                    "ports": "ether2,ether3",
                },
                {
                    ".id": "3",
                    "customer-vid": 0,
                    "new-customer-vid": 100,
                    "ports": "ether4,ether5",
                },
            ],
            "networks": NETWORKS,
            "access_ports": [
                {
                    "vlan": "VM",
                    "ports": ["ether1"],
                },
                {
                    "vlan": "GENERAL",
                    "ports": ["ether2", "ether3"],
                },
                {
                    "vlan": "MGMT",
                    "ports": ["ether4"],
                },
            ],
        }
    )
    expected_add = []
    expected_update = [
        {
            ".id": "3",
            "customer-vid": 0,
            "new-customer-vid": 100,
            "ports": "ether4",
        },
    ]
    expected_remove = []

    with pytest.raises(SystemExit):
        mt_get_interface_sw_ingress.main()
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
                    "customer-vid": 0,
                    "new-customer-vid": 10,
                    "ports": "ether1",
                },
                {
                    ".id": "2",
                    "customer-vid": 0,
                    "new-customer-vid": 50,
                    "ports": "ether2,ether3",
                },
                {
                    ".id": "3",
                    "customer-vid": 0,
                    "new-customer-vid": 100,
                    "ports": "ether4",
                },
                {
                    ".id": "4",
                    "customer-vid": 0,
                    "new-customer-vid": 110,
                    "ports": "ether5",
                },
            ],
            "networks": NETWORKS,
            "access_ports": [
                {
                    "vlan": "VM",
                    "ports": ["ether1"],
                },
                {
                    "vlan": "GENERAL",
                    "ports": ["ether2", "ether3"],
                },
                {
                    "vlan": "MGMT",
                    "ports": ["ether4"],
                },
            ],
        }
    )
    expected_add = []
    expected_update = []
    expected_remove = [
        {
            ".id": "4",
            "customer-vid": 0,
            "new-customer-vid": 110,
            "ports": "ether5",
        },
    ]

    with pytest.raises(SystemExit):
        mt_get_interface_sw_ingress.main()
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
                    ".id": "2",
                    "customer-vid": 0,
                    "new-customer-vid": 50,
                    "ports": "ether4,ether10,sfp-sfpplus1,sfpplus2",
                },
                {
                    ".id": "3",
                    "customer-vid": 0,
                    "new-customer-vid": 100,
                    "ports": "ether5",
                },
                {
                    ".id": "4",
                    "customer-vid": 0,
                    "new-customer-vid": 110,
                    "ports": "ether5",
                },
            ],
            "networks": NETWORKS,
            "access_ports": [
                {
                    "vlan": "VM",
                    "ports": ["ether1", "sfpplus8", "sfpplus6", "sfp-sfpplus4"],
                },
                {
                    "vlan": "GENERAL",
                    "ports": ["ether4", "ether10", "sfp-sfpplus1", "sfpplus2"],
                },
                {
                    "vlan": "MGMT",
                    "ports": ["ether5", "ether6", "sfp-sfpplus3", "sfpplus3"],
                },
            ],
        }
    )
    expected_add = [
        {
            "customer-vid": 0,
            "new-customer-vid": 10,
            "ports": "ether1,sfpplus8,sfpplus6,sfp-sfpplus4",
        },
    ]
    expected_update = [
        {
            ".id": "3",
            "customer-vid": 0,
            "new-customer-vid": 100,
            "ports": "ether5,ether6,sfp-sfpplus3,sfpplus3",
        },
    ]
    expected_remove = [
        {
            ".id": "4",
            "customer-vid": 0,
            "new-customer-vid": 110,
            "ports": "ether5",
        },
    ]

    with pytest.raises(SystemExit):
        mt_get_interface_sw_ingress.main()
    out, err = capfd.readouterr()
    out = json.loads(out)
    assert not err
    assert not out.get("failed", False)
    validate_output(out, expected_add, expected_update, expected_remove)


def test_missing_vlan(capfd):
    set_module_args(
        {
            "existing": [],
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
        mt_get_interface_sw_ingress.main()
    out, err = capfd.readouterr()
    out = json.loads(out)
    assert not err
    assert out.get("failed", False)
    assert "Cannot find VLAN or its VID 'BAD'" == out["msg"]
