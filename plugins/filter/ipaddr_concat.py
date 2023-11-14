from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.andrei.utils.plugins.module_utils.network import ipaddr_concat


class FilterModule(object):
    def filters(self):
        return {'ipaddr_concat': ipaddr_concat}
