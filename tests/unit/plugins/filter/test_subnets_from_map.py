from __future__ import absolute_import, division, print_function

__metaclass__ = type

import unittest

from ansible_collections.andrei.utils.plugins.filter.subnets_from_map import (
    subnets_from_map,
)


class TestSubnetsFromMap(unittest.TestCase):
    def setUp(self):
        pass

    def test_v4_only_auto(self):
        data = {"cidr": "172.27.0.0/16"}
        args = [{"svc": (), "pod": (), "test": ()}]
        kwargs = dict(
            v4_size=24,
        )
        output = {
            "svc": ["172.27.0.0/24"],
            "pod": ["172.27.1.0/24"],
            "test": ["172.27.2.0/24"],
        }
        result = subnets_from_map(data, *args, **kwargs)
        self.assertEqual(result, output)

    def test_v4_only(self):
        data = {"cidr": "172.27.0.0/16"}
        args = [{"svc": 18, "pod": 18, "test": 18}]
        output = {
            "svc": ["172.27.0.0/18"],
            "pod": ["172.27.64.0/18"],
            "test": ["172.27.128.0/18"],
        }
        result = subnets_from_map(data, *args)
        self.assertEqual(result, output)

    def test_v4_only_start(self):
        data = {"cidr": "172.27.0.0/16"}
        args = [{"svc": 18, "pod": 18, "test": 18}]
        kwargs = dict(
            v4_start=31,
        )
        output = {
            "svc": ["172.27.64.0/18"],
            "pod": ["172.27.128.0/18"],
            "test": ["172.27.192.0/18"],
        }
        result = subnets_from_map(data, *args, **kwargs)
        self.assertEqual(result, output)

    def test_v4_only_skip(self):
        data = {"cidr": "172.27.0.0/16"}
        args = [{"svc": 24, "pod": 24, "test": 24}]
        kwargs = dict(
            v4_prefix_skip=2,
        )
        output = {
            "svc": ["172.27.2.0/24"],
            "pod": ["172.27.3.0/24"],
            "test": ["172.27.4.0/24"],
        }
        result = subnets_from_map(data, *args, **kwargs)
        self.assertEqual(result, output)

    def test_v4_only_mixed(self):
        data = {"cidr": "172.27.0.0/16"}
        args = [{"svc": 27, "pod": 26, "test": 30, "test2": 25}]
        kwargs = {}
        output = {
            "svc": ["172.27.0.0/27"],
            "pod": ["172.27.0.64/26"],
            "test": ["172.27.0.32/30"],
            "test2": ["172.27.0.128/25"],
        }
        result = subnets_from_map(data, *args, **kwargs)
        self.assertEqual(result, output)

    def test_v4_only_mixed_multiple(self):
        data = {"cidr": "172.27.0.0/16"}
        args = [{"svc": (27, 27, 28), "pod": 26, "test": (30, 29), "test2": (27, 25)}]
        kwargs = {}
        output = {
            "svc": ["172.27.0.0/27", "172.27.0.32/27", "172.27.0.64/28"],
            "pod": ["172.27.0.128/26"],
            "test": ["172.27.0.80/30", "172.27.0.88/29"],
            "test2": ["172.27.0.96/27", "172.27.1.0/25"],
        }
        result = subnets_from_map(data, *args, **kwargs)
        self.assertEqual(result, output)

    def test_v6_only_auto(self):
        data = {"cidr6": "fd00:172:27::/56"}
        args = [{"svc": (), "pod": (), "test": ()}]
        kwargs = dict(
            v6_size=80,
        )
        output = {
            "svc": ["fd00:172:27::/80"],
            "pod": ["fd00:172:27:0:1::/80"],
            "test": ["fd00:172:27:0:2::/80"],
        }
        result = subnets_from_map(data, *args, **kwargs)
        self.assertEqual(result, output)

    def test_v6_only(self):
        data = {"cidr6": "fd00:172:27::/56"}
        args = [{"svc": 64, "pod": 64, "test": 64}]
        output = {
            "svc": ["fd00:172:27::/64"],
            "pod": ["fd00:172:27:1::/64"],
            "test": ["fd00:172:27:2::/64"],
        }
        result = subnets_from_map(data, *args)
        self.assertEqual(result, output)

    def test_v6_only_start(self):
        data = {"cidr6": "fd00:172:27::/112"}
        args = [{"svc": 114, "pod": 114, "test": 114}]
        kwargs = dict(
            v6_start=31,
        )
        output = {
            "svc": ["fd00:172:27::4000/114"],
            "pod": ["fd00:172:27::8000/114"],
            "test": ["fd00:172:27::c000/114"],
        }
        result = subnets_from_map(data, *args, **kwargs)
        self.assertEqual(result, output)

    def test_v6_only_skip(self):
        data = {"cidr6": "fd00:172:27::/56"}
        args = [{"svc": 64, "pod": 64, "test": 64}]
        kwargs = dict(
            v6_prefix_skip=2,
        )
        output = {
            "svc": ["fd00:172:27:2::/64"],
            "pod": ["fd00:172:27:3::/64"],
            "test": ["fd00:172:27:4::/64"],
        }
        result = subnets_from_map(data, *args, **kwargs)
        self.assertEqual(result, output)

    def test_v6_only_mixed(self):
        data = {"cidr6": "fd00:172:27::/56"}
        # Big differences are very slow
        args = [{"svc": (64, 64), "pod": (64, 77, 80), "test": (64, 65, 70)}]
        kwargs = {}
        output = {
            "svc": ["fd00:172:27::/64", "fd00:172:27:1::/64"],
            "pod": ["fd00:172:27:2::/64", "fd00:172:27:3::/77", "fd00:172:27:3:8::/80"],
            "test": [
                "fd00:172:27:4::/64",
                "fd00:172:27:3:8000::/65",
                "fd00:172:27:3:400::/70",
            ],
        }
        result = subnets_from_map(data, *args, **kwargs)
        self.assertEqual(result, output)

    def test_dual_stack_auto(self):
        data = {"cidr": "172.27.0.0/16", "cidr6": "fd00:172:27::/56"}
        args = [{"svc": (), "pod": (), "test": ()}]
        kwargs = dict(
            v4_size=27,
            v6_size=88,
        )
        output = {
            "svc": ["172.27.0.0/27", "fd00:172:27::/88"],
            "pod": ["172.27.0.32/27", "fd00:172:27::100:0:0/88"],
            "test": ["172.27.0.64/27", "fd00:172:27::200:0:0/88"],
        }

        result = subnets_from_map(data, *args, **kwargs)
        self.assertEqual(result, output)

    def test_dual_stack(self):
        data = {"cidr": "172.27.0.0/16", "cidr6": "fd00:172:27::/112"}
        args = [{"svc": (18, 114), "pod": (18, 114), "test": (18, 114)}]
        output = {
            "svc": ["172.27.0.0/18", "fd00:172:27::/114"],
            "pod": ["172.27.64.0/18", "fd00:172:27::4000/114"],
            "test": ["172.27.128.0/18", "fd00:172:27::8000/114"],
        }
        result = subnets_from_map(data, *args)
        self.assertEqual(result, output)

    def test_dual_stack_start(self):
        data = {"cidr": "172.27.0.0/16", "cidr6": "fd00:172:27::/112"}
        args = [{"svc": (18, 114), "pod": (18, 114), "test": (18, 114)}]
        kwargs = dict(
            v4_start=31,
            v6_start=31,
        )
        output = {
            "svc": ["172.27.64.0/18", "fd00:172:27::4000/114"],
            "pod": ["172.27.128.0/18", "fd00:172:27::8000/114"],
            "test": ["172.27.192.0/18", "fd00:172:27::c000/114"],
        }
        result = subnets_from_map(data, *args, **kwargs)
        self.assertEqual(result, output)

    def test_dual_stack_skip(self):
        data = {"cidr": "172.27.0.0/16", "cidr6": "fd00:172:27::/56"}
        args = [{"svc": (24, 64), "pod": (24, 64), "test": (24, 64)}]
        kwargs = dict(
            v4_prefix_skip=2,
            v6_prefix_skip=2,
        )
        output = {
            "svc": ["172.27.2.0/24", "fd00:172:27:2::/64"],
            "pod": ["172.27.3.0/24", "fd00:172:27:3::/64"],
            "test": ["172.27.4.0/24", "fd00:172:27:4::/64"],
        }
        result = subnets_from_map(data, *args, **kwargs)
        self.assertEqual(result, output)

    def test_dual_stack_mixed(self):
        data = {"cidr": "172.27.0.0/16", "cidr6": "fd00:172:27::/56"}
        args = [{"svc": (27, 80), "pod": (26, 64), "test": (30, 96), "test2": (25, 60)}]
        kwargs = {}
        output = {
            "svc": [
                "172.27.0.0/27",
                "fd00:172:27::/80",
            ],
            "pod": [
                "172.27.0.64/26",
                "fd00:172:27:1::/64",
            ],
            "test": [
                "172.27.0.32/30",
                "fd00:172:27:0:1::/96",
            ],
            "test2": [
                "172.27.0.128/25",
                "fd00:172:27:10::/60",
            ],
        }
        result = subnets_from_map(data, *args, **kwargs)
        self.assertEqual(result, output)

    def test_dual_stack_mixed_multiple(self):
        data = {"cidr": "172.27.0.0/16", "cidr6": "fd00:172:27::/56"}
        args = [
            {
                "svc": (27, 29, 80),
                "pod": 64,
                "test": (30, 96, 100),
                "test2": (25, 27, 28, 60, 64, 78),
            }
        ]
        kwargs = {}
        output = {
            "svc": ["172.27.0.0/27", "172.27.0.32/29", "fd00:172:27::/80"],
            "pod": ["fd00:172:27:1::/64"],
            "test": [
                "172.27.0.40/30",
                "fd00:172:27:0:1::/96",
                "fd00:172:27:0:1:1::/100",
            ],
            "test2": [
                "172.27.0.128/25",
                "172.27.0.64/27",
                "172.27.0.48/28",
                "fd00:172:27:10::/60",
                "fd00:172:27:2::/64",
                "fd00:172:27:0:4::/78",
            ],
        }
        result = subnets_from_map(data, *args, **kwargs)
        self.assertEqual(result, output)

    def test_dual_stack_default_size(self):
        data = {"cidr": "172.27.0.0/16", "cidr6": "fd00:172:27::/112"}
        args = [{"svc": 18, "pod": 18, "test": 18}]
        kwargs = dict(
            v6_size=114,
        )
        output = {
            "svc": ["172.27.0.0/18", "fd00:172:27::/114"],
            "pod": ["172.27.64.0/18", "fd00:172:27::4000/114"],
            "test": ["172.27.128.0/18", "fd00:172:27::8000/114"],
        }
        result = subnets_from_map(data, *args, **kwargs)
        self.assertEqual(result, output)
