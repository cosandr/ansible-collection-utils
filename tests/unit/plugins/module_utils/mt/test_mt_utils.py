from __future__ import absolute_import, division, print_function

__metaclass__ = type


from ansible_collections.andrei.utils.plugins.module_utils.mt import utils


def test_make_vid_map():
    networks = {
        "general": {
            "vlan": 50,
            "cidr": "10.0.50.0/24",
        },
        "mgmt": {
            "vlan": 100,
            "cidr": "10.0.100.0/24",
        },
    }

    expected = {
        "GENERAL": 50,
        "MGMT": 100,
    }

    actual = utils.make_vid_map(networks)
    assert actual == expected


def test_make_add_update_remove_noop():
    existing = [
        {
            ".id": "1",
            "tagged-ports": "ether1,ether2",
            "vlan-id": 50,
        },
        {
            ".id": "2",
            "tagged-ports": "ether3,ether4",
            "vlan-id": 100,
        },
    ]
    new_data = [
        {
            "tagged-ports": "ether1,ether2",
            "vlan-id": 50,
        },
        {
            "tagged-ports": "ether3,ether4",
            "vlan-id": 100,
        },
    ]
    check_key = "vlan-id"

    expected_add = []
    expected_update = []
    expected_remove = []

    to_add, to_update, to_remove = utils.make_add_update_remove(
        existing, new_data, check_key
    )

    assert to_add == expected_add
    assert to_update == expected_update
    assert to_remove == expected_remove


def test_make_add_update_remove():
    existing = [
        {
            ".id": "1",
            "tagged-ports": "ether1,ether2",
            "vlan-id": 50,
        },
        {
            ".id": "1",
            "tagged-ports": "ether5",
            "vlan-id": 12,
        },
    ]
    new_data = [
        {
            "tagged-ports": "ether1",
            "vlan-id": 50,
        },
        {
            "tagged-ports": "ether3,ether4",
            "vlan-id": 100,
        },
    ]
    check_key = "vlan-id"

    expected_add = [
        {
            "tagged-ports": "ether3,ether4",
            "vlan-id": 100,
        },
    ]
    expected_update = [
        {
            ".id": "1",
            "tagged-ports": "ether1",
            "vlan-id": 50,
        },
    ]
    expected_remove = [
        {
            ".id": "1",
            "tagged-ports": "ether5",
            "vlan-id": 12,
        },
    ]

    to_add, to_update, to_remove = utils.make_add_update_remove(
        existing, new_data, check_key
    )

    assert to_add == expected_add
    assert to_update == expected_update
    assert to_remove == expected_remove


def test_sort_ports_sorted():
    trunk_ports = [
        "ether1",
        "sfp-sfpplus1",
        "ether2",
        "sfpplus1",
        "sfpplus2",
        "ether3",
        "ether5",
        "sfp-sfpplus2",
    ]

    expected = [
        "ether1",
        "ether2",
        "ether3",
        "ether5",
        "sfpplus1",
        "sfpplus2",
        "sfp-sfpplus1",
        "sfp-sfpplus2",
    ]
    actual = utils.sort_ports(trunk_ports)

    assert actual == expected


def test_sort_ports_unsorted():
    trunk_ports = [
        "sfp-sfpplus100",
        "ether1",
        "sfp-sfpplus1",
        "ether3",
        "sfpplus2",
        "sfpplus1",
        "sfpplus123",
        "ether5",
        "ether2",
        "ether100",
        "sfp-sfpplus2",
    ]

    expected = [
        "ether1",
        "ether2",
        "ether3",
        "ether5",
        "ether100",
        "sfpplus1",
        "sfpplus2",
        "sfpplus123",
        "sfp-sfpplus1",
        "sfp-sfpplus2",
        "sfp-sfpplus100",
    ]
    actual = utils.sort_ports(trunk_ports)

    assert actual == expected
