from __future__ import absolute_import, division, print_function


__metaclass__ = type

import unittest

from ansible.errors import AnsibleFilterError, AnsibleFilterTypeError

from ansible_collections.andrei.utils.plugins.filter.items2dictlist import items2dictlist


class TestItems2DictList(unittest.TestCase):
    def setUp(self):
        pass

    def test_items2dictlist_filter_plugin(self):
        data = [
            "10.0.0.0/24",
            "10.1.0.0/24",
            "10.2.0.0/24",
        ]
        output = [
            {
                "address": "10.0.0.0/24",
            },
            {
                "address": "10.1.0.0/24",
            },
            {
                "address": "10.2.0.0/24",
            },
        ]
        result = items2dictlist(data, "address")
        self.assertEqual(result, output)

    def test_items2dictlist_filter_plugin_params(self):
        data = [
            "10.0.0.0/24",
            "10.1.0.0/24",
            "10.2.0.0/24",
        ]
        output = [
            {
                "address": "10.0.0.0/24",
                "comment": "some comment",
                "list": "www",
            },
            {
                "address": "10.1.0.0/24",
                "comment": "some comment",
                "list": "www",
            },
            {
                "address": "10.2.0.0/24",
                "comment": "some comment",
                "list": "www",
            },
        ]
        result = items2dictlist(data, "address", comment="some comment", list="www")
        self.assertEqual(result, output)

    def test_invalid_data_type(self):
        data = "some string"
        with self.assertRaises(AnsibleFilterTypeError) as error:
            items2dictlist(data, "address")
        self.assertIn("items2dictlist requires a list", str(error.exception))

    def test_invalid_parameter(self):
        data = ["some string"]
        with self.assertRaises(AnsibleFilterError) as error:
            items2dictlist(data, "address", address="test")
        self.assertEqual("items2dictlist: 'address' cannot be in kwargs", str(error.exception))
