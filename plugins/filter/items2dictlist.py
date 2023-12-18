#
# -*- coding: utf-8 -*-
# Copyright 2023 Andrei Costescu (@cosandr)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
#

"""
The items2dictlist filter plugin
"""
from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
    name: items2dictlist
    author: Andrei Costescu (@cosandr)
    version_added: "1.0.0"
    short_description: Transform a list of items to a list of dictionaries.
    positional: _input, key_name
    description:
        - Takes a list of items and transforms it into a list of dictionaries keyed by C(key_name).
    options:
        _input:
            description:
                - A list of items.
            type: list
            required: true
        key_name:
            description: The name of the key to use in each output dictionary.
            type: str
            required: true
    notes:
        - All other keyword arguments are added as key/value pairs to the output dictionaries.
"""

EXAMPLES = """
    # items => [ {"mykey": "one", "somearg": "somevalue"}, {"mykey": "two", "somearg": "somevalue"} ]
    items: "{{ ['one', 'two'] | andrei.utils.items2dictlist('mykey', somearg='somevalue') }}"
"""

RETURN = """
    _value:
        description: List of dictionaries.
        type: list
        elements: dict
"""


from ansible.errors import AnsibleFilterError, AnsibleFilterTypeError
from ansible.module_utils.common.collections import is_sequence


def items2dictlist(_input, key_name, **kwargs):
    """Convert a list of items to a list of dictionaries keyed by 'key_name'."""
    if not is_sequence(_input):
        raise AnsibleFilterTypeError(
            "items2dictlist requires a list, got %s instead." % type(_input)
        )
    if key_name in kwargs:
        raise AnsibleFilterError("items2dictlist: '%s' cannot be in kwargs" % key_name)
    ret = []
    for v in _input:
        ret.append({key_name: v, **kwargs})
    return ret


class FilterModule(object):
    """Ansible list filters"""

    def filters(self):
        return {
            "items2dictlist": items2dictlist,
        }
