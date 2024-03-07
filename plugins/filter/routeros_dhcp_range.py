from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible.errors import AnsibleFilterError
from ansible.module_utils.basic import missing_required_lib

try:
    from netaddr import IPNetwork, IPAddress
except ImportError as imp_exc:
    NETADDR_IMPORT_ERROR = imp_exc
else:
    NETADDR_IMPORT_ERROR = None


def routeros_dhcp_range(net, reverse_order=False, skip_last=0, skip_first=0):
    if NETADDR_IMPORT_ERROR:
        raise AnsibleFilterError(
            missing_required_lib("netaddr")
        ) from NETADDR_IMPORT_ERROR
    try:
        net = IPNetwork(net)
    except Exception as e:
        raise AnsibleFilterError("routeros_dhcp_range: {0}".format(str(e)))
    last = net.last - skip_last
    first = net.first + skip_first
    if last < net.first or first > net.last:
        raise AnsibleFilterError(
            "routeros_dhcp_range: {0} is too small".format(str(net))
        )
    if reverse_order:
        return "{0}-{1}".format(
            str(IPAddress(last)),
            str(IPAddress(first)),
        )
    return "{0}-{1}".format(
        str(IPAddress(first)),
        str(IPAddress(last)),
    )


class FilterModule(object):
    def filters(self):
        return {"routeros_dhcp_range": routeros_dhcp_range}
