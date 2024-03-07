from __future__ import absolute_import, division, print_function


__metaclass__ = type

import pytest

from ansible.errors import AnsibleFilterError

from ansible_collections.andrei.utils.plugins.filter.routeros_dhcp_range import (
    routeros_dhcp_range,
)


def test_simple():
    kwargs = {
        "net": "10.0.50.0/24",
    }
    expected = "10.0.50.0-10.0.50.255"
    actual = routeros_dhcp_range(**kwargs)

    assert actual == expected


def test_skip():
    kwargs = {
        "net": "10.0.50.0/24",
        "skip_last": 1,
        "skip_first": 2,
    }
    expected = "10.0.50.2-10.0.50.254"
    actual = routeros_dhcp_range(**kwargs)

    assert actual == expected


def test_simple_reverse():
    kwargs = {
        "net": "10.0.50.0/24",
        "reverse_order": True,
    }
    expected = "10.0.50.255-10.0.50.0"
    actual = routeros_dhcp_range(**kwargs)

    assert actual == expected


def test_skip_reverse():
    kwargs = {
        "net": "10.0.50.0/24",
        "skip_last": 1,
        "skip_first": 2,
        "reverse_order": True,
    }
    expected = "10.0.50.254-10.0.50.2"
    actual = routeros_dhcp_range(**kwargs)

    assert actual == expected


def test_bad_network():
    kwargs = {
        "net": "10.0.50.0/33",
        "skip_last": 1,
        "skip_first": 2,
    }
    with pytest.raises(AnsibleFilterError) as e:
        routeros_dhcp_range(**kwargs)
    assert "routeros_dhcp_range: invalid IPNetwork 10.0.50.0/33" == str(e.value)


def test_small_network():
    kwargs = {
        "net": "10.0.50.0/31",
        "skip_last": 1,
        "skip_first": 2,
    }
    with pytest.raises(AnsibleFilterError) as e:
        routeros_dhcp_range(**kwargs)
    assert "routeros_dhcp_range: 10.0.50.0/31 is too small" == str(e.value)
