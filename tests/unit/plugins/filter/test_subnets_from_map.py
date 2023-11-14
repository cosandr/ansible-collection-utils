from __future__ import absolute_import, division, print_function

__metaclass__ = type

import unittest

from ansible_collections.andrei.utils.plugins.filter.subnets_from_map import \
    subnets_from_map


class TestSubnetsFromMap(unittest.TestCase):
    def setUp(self):
        pass

    def test_v4_only(self):
        data = {'cidr': '172.27.0.0/16'}
        args = [{'svc': 18, 'pod': 18, 'test': 18}]
        output = {
            "pod": [
                "172.27.64.0/18"
            ],
            "svc": [
                "172.27.0.0/18"
            ],
            "test": [
                "172.27.128.0/18"
            ]
        }
        result = subnets_from_map(data, *args)
        self.assertEqual(result, output)

    def test_v4_only_start(self):
        data = {'cidr': '172.27.0.0/16'}
        args = [{'svc': 18, 'pod': 18, 'test': 18}]
        kwargs = dict(
            v4_start=31,
        )
        output = {
            "pod": [
                "172.27.128.0/18"
            ],
            "svc": [
                "172.27.64.0/18"
            ],
            "test": [
                "172.27.192.0/18"
            ]
        }
        result = subnets_from_map(data, *args, **kwargs)
        self.assertEqual(result, output)

    def test_v4_only_skip(self):
        data = {'cidr': '172.27.0.0/16'}
        args = [{'svc': 24, 'pod': 24, 'test': 24}]
        kwargs = dict(
            v4_size=24,  # TODO: Remove
            v4_prefix_skip=2,
        )
        output = {
            "pod": [
                "172.27.3.0/24"
            ],
            "svc": [
                "172.27.2.0/24"
            ],
            "test": [
                "172.27.4.0/24"
            ]
        }
        result = subnets_from_map(data, *args, **kwargs)
        self.assertEqual(result, output)

    def test_v6_only(self):
        data = {'cidr6': 'fd00:172:27::/56'}
        args = [{'svc': 64, 'pod': 64, 'test': 64}]
        output = {
            "pod": [
                "fd00:172:27:1::/64"
            ],
            "svc": [
                "fd00:172:27::/64"
            ],
            "test": [
                "fd00:172:27:2::/64"
            ]
        }
        result = subnets_from_map(data, *args)
        self.assertEqual(result, output)

    def test_v6_only_start(self):
        data = {'cidr6': 'fd00:172:27::/112'}
        args = [{'svc': 114, 'pod': 114, 'test': 114}]
        kwargs = dict(
            v6_start=31,
        )
        output = {
            "pod": [
                "fd00:172:27::8000/114"
            ],
            "svc": [
                "fd00:172:27::4000/114"
            ],
            "test": [
                "fd00:172:27::c000/114"
            ]
        }
        result = subnets_from_map(data, *args, **kwargs)
        self.assertEqual(result, output)

    def test_v6_only_skip(self):
        data = {'cidr6': 'fd00:172:27::/56'}
        args = [{'svc': 64, 'pod': 64, 'test': 64}]
        kwargs = dict(
            v6_size=64,  # TODO: Remove
            v6_prefix_skip=2,
        )
        output = {
            "pod": [
                "fd00:172:27:3::/64"
            ],
            "svc": [
                "fd00:172:27:2::/64"
            ],
            "test": [
                "fd00:172:27:4::/64"
            ]
        }
        result = subnets_from_map(data, *args, **kwargs)
        self.assertEqual(result, output)

    def test_dual_stack(self):
        data = {'cidr': '172.27.0.0/16', 'cidr6': 'fd00:172:27::/112'}
        args = [{'svc': (18, 114), 'pod': (18, 114), 'test': (18, 114)}]
        output = {
            "pod": [
                "172.27.64.0/18",
                "fd00:172:27::4000/114"
            ],
            "svc": [
                "172.27.0.0/18",
                "fd00:172:27::/114"
            ],
            "test": [
                "172.27.128.0/18",
                "fd00:172:27::8000/114"
            ]
        }
        result = subnets_from_map(data, *args)
        self.assertEqual(result, output)

    def test_dual_stack_start(self):
        data = {'cidr': '172.27.0.0/16', 'cidr6': 'fd00:172:27::/112'}
        args = [{'svc': (18, 114), 'pod': (18, 114), 'test': (18, 114)}]
        kwargs = dict(
            v4_start=31,
            v6_start=31,
        )
        output = {
            "pod": [
                "172.27.128.0/18",
                "fd00:172:27::8000/114"
            ],
            "svc": [
                "172.27.64.0/18",
                "fd00:172:27::4000/114"
            ],
            "test": [
                "172.27.192.0/18",
                "fd00:172:27::c000/114"
            ]
        }
        result = subnets_from_map(data, *args, **kwargs)
        self.assertEqual(result, output)

    def test_dual_stack_skip(self):
        data = {'cidr': '172.27.0.0/16', 'cidr6': 'fd00:172:27::/56'}
        args = [{'svc': (24, 64), 'pod': (24, 64), 'test': (24, 64)}]
        kwargs = dict(
            v4_size=24,  # TODO: Remove
            v4_prefix_skip=2,
            v6_size=64,  # TODO: Remove
            v6_prefix_skip=2,
        )
        output = {
            "pod": [
                "172.27.3.0/24",
                "fd00:172:27:3::/64"
            ],
            "svc": [
                "172.27.2.0/24",
                "fd00:172:27:2::/64"
            ],
            "test": [
                "172.27.4.0/24",
                "fd00:172:27:4::/64"
            ]
        }
        result = subnets_from_map(data, *args, **kwargs)
        self.assertEqual(result, output)

    def test_dual_stack_default_size(self):
        data = {'cidr': '172.27.0.0/16', 'cidr6': 'fd00:172:27::/112'}
        args = [{'svc': 18, 'pod': 18, 'test': 18}]
        kwargs = dict(
            v6_size=114,
        )
        output = {
            "pod": [
                "172.27.64.0/18",
                "fd00:172:27::4000/114"
            ],
            "svc": [
                "172.27.0.0/18",
                "fd00:172:27::/114"
            ],
            "test": [
                "172.27.128.0/18",
                "fd00:172:27::8000/114"
            ]
        }
        result = subnets_from_map(data, *args, **kwargs)
        self.assertEqual(result, output)
