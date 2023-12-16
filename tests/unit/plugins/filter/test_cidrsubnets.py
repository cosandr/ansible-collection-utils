from __future__ import absolute_import, division, print_function

__metaclass__ = type

import unittest

from ansible_collections.andrei.utils.plugins.filter.cidrsubnets import cidrsubnets

from ansible.errors import AnsibleFilterError


class TestCidrSubnets(unittest.TestCase):
    def setUp(self):
        pass

    def test_same_size(self):
        data = "10.0.50.0/24"
        args = [27, 27, 27]
        output = [
            "10.0.50.0/27",
            "10.0.50.32/27",
            "10.0.50.64/27",
        ]
        result = cidrsubnets(data, *args)
        self.assertEqual(result, output)

    def test_same_size_v6(self):
        data = "fd00:172:27::/64"
        args = [80, 80, 80]
        output = [
            "fd00:172:27::/80",
            "fd00:172:27:0:1::/80",
            "fd00:172:27:0:2::/80",
        ]
        result = cidrsubnets(data, *args)
        self.assertEqual(result, output)

    def test_start_offset(self):
        data = "10.0.50.0/24"
        args = [27, 27, 27]
        output = [
            "10.0.50.32/27",
            "10.0.50.64/27",
            "10.0.50.96/27",
        ]
        result = cidrsubnets(data, *args, start=31)
        self.assertEqual(result, output)

    def test_prefix_skip(self):
        data = "10.0.50.0/24"
        args = [27, 27, 27]
        output = [
            "10.0.50.96/27",
            "10.0.50.128/27",
            "10.0.50.160/27",
        ]
        result = cidrsubnets(data, *args, prefix_skip=3, prefix_size=27)
        self.assertEqual(result, output)

    def test_mixed_size(self):
        data = "10.0.50.0/24"
        args = [27, 26, 30, 25]
        output = [
            "10.0.50.0/27",
            "10.0.50.64/26",
            "10.0.50.32/30",
            "10.0.50.128/25",
        ]
        result = cidrsubnets(data, *args)
        self.assertEqual(result, output)

    def test_fill(self):
        data = "10.0.50.0/24"
        args = [27, 28]
        output = [
            "10.0.50.0/27",
            "10.0.50.32/28",
            "10.0.50.48/28",
            "10.0.50.64/26",
            "10.0.50.128/25",
        ]
        result = cidrsubnets(data, *args, fill=True)
        self.assertEqual(result, output)

    def test_net_too_small(self):
        data = "10.0.50.0/24"
        args = [24, 24]
        with self.assertRaises(AnsibleFilterError) as error:
            cidrsubnets(data, *args)
        self.assertIn("is too small", str(error.exception))

    def test_net_too_small_v6(self):
        data = "fd00:172:27::/112"
        args = [112, 112]
        with self.assertRaises(AnsibleFilterError) as error:
            cidrsubnets(data, *args)
        self.assertIn("is too small", str(error.exception))
