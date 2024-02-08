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


def test_selective_trunk(capfd):
    set_module_args(
        {
            "existing": [],
            "networks": NETWORKS,
            "trunk_ports": [
                {
                    "vlan": "GENERAL",
                    "ports": ["ether1"],
                },
            ],
        }
    )
    expected_add = [
        {
            "vlan-id": 50,
            "tagged-ports": "switch1-cpu,ether1",
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


def test_mixed_trunk(capfd):
    set_module_args(
        {
            "existing": [],
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
    expected_add = [
        {
            "vlan-id": 10,
            "tagged-ports": "switch1-cpu,ether1,ether4",
        },
        {
            "vlan-id": 50,
            "tagged-ports": "switch1-cpu,ether1,ether2,ether4",
        },
        {
            "vlan-id": 100,
            "tagged-ports": "switch1-cpu,ether1,ether4",
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


def test_mixed_trunk_all(capfd):
    set_module_args(
        {
            "existing": [
                {
                    ".id": "1",
                    "vlan-id": 10,
                    "tagged-ports": "switch1-cpu,ether1",
                },
                {
                    ".id": "2",
                    "vlan-id": 50,
                    "tagged-ports": "switch1-cpu,ether1,ether4",
                },
                {
                    ".id": "4",
                    "vlan-id": 20,
                    "tagged-ports": "switch1-cpu,ether1,ether4",
                },
            ],
            "networks": NETWORKS,
            "trunk_ports": [
                "ether1",
                {
                    "vlan": "GENERAL",
                    "ports": ["ether2", "ether4"],
                },
                {
                    "vlan": "MGMT",
                    "ports": ["ether5"],
                },
            ],
        }
    )
    expected_add = [
        {
            "vlan-id": 100,
            "tagged-ports": "switch1-cpu,ether1,ether5",
        },
    ]
    expected_update = [
        {
            ".id": "2",
            "vlan-id": 50,
            "tagged-ports": "switch1-cpu,ether1,ether2,ether4",
        },
    ]
    expected_remove = [
        {
            ".id": "4",
            "vlan-id": 20,
            "tagged-ports": "switch1-cpu,ether1,ether4",
        },
    ]

    with pytest.raises(SystemExit):
        mt_get_interface_sw_egress.main()
    out, err = capfd.readouterr()
    out = json.loads(out)
    assert not err
    assert not out.get("failed", False)
    validate_output(out, expected_add, expected_update, expected_remove)


def test_bad_trunk_type(capfd):
    set_module_args(
        {
            "existing": [],
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
        mt_get_interface_sw_egress.main()
    out, err = capfd.readouterr()
    out = json.loads(out)
    assert not err
    assert out.get("failed", False)
    assert "Element at index 1 type (int) is unsupported" == out["msg"]


def test_missing_trunk_vlan(capfd):
    set_module_args(
        {
            "existing": [],
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
        mt_get_interface_sw_egress.main()
    out, err = capfd.readouterr()
    out = json.loads(out)
    assert not err
    assert out.get("failed", False)
    assert "Cannot find VLAN 'BAD'" == out["msg"]


def test_hybrid(capfd):
    set_module_args(
        {
            "existing": [],
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
    expected_add = [
        {
            "vlan-id": 10,
            "tagged-ports": "switch1-cpu,ether1,ether2",
        },
        {
            "vlan-id": 50,
            "tagged-ports": "switch1-cpu,ether2",
        },
        {
            "vlan-id": 100,
            "tagged-ports": "switch1-cpu,ether1,ether2,ether4",
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
