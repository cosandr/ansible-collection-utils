from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible.errors import AnsibleFilterError
from ansible.module_utils.basic import missing_required_lib

try:
    from netaddr import IPNetwork
except ImportError as imp_exc:
    NETADDR_IMPORT_ERROR = imp_exc
else:
    NETADDR_IMPORT_ERROR = None


def sort_subnets(subnets):
    if NETADDR_IMPORT_ERROR:
        raise AnsibleFilterError(
            missing_required_lib("netaddr")
        ) from NETADDR_IMPORT_ERROR
    ret = {}
    for net, subs in subnets.items():
        sorted_keys = sorted(
            subs.keys(),
            key=lambda item: min([IPNetwork(net).first for net in subs[item]]),
        )
        ret[net] = {k: subs[k] for k in sorted_keys}
    return ret


class FilterModule(object):
    def filters(self):
        return {"sort_subnets": sort_subnets}
