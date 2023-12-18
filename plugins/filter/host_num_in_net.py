from __future__ import absolute_import, division, print_function

__metaclass__ = type


from ansible.errors import AnsibleFilterError
from ansible.module_utils.basic import missing_required_lib

try:
    from netaddr import IPAddress, IPNetwork
except ImportError as imp_exc:
    NETADDR_IMPORT_ERROR = imp_exc
else:
    NETADDR_IMPORT_ERROR = None


def host_num_in_net(address, net=None):
    """Return address's number in net, if not given it assumes /24 and /64 for IPv4 and IPv6 respectively"""
    if NETADDR_IMPORT_ERROR:
        raise AnsibleFilterError(
            missing_required_lib("netaddr")
        ) from NETADDR_IMPORT_ERROR
    address = IPAddress(address)
    if net is not None:
        net = IPNetwork(net)
    elif address.version == 4:
        net = IPNetwork(str(address) + "/24")
    elif address.version == 6:
        net = IPNetwork(str(address) + "/64")
    else:
        raise AnsibleFilterError(
            "host_num_in_net: Unknown error, cannot determine network"
        )
    if address not in net:
        raise AnsibleFilterError(
            "host_num_in_net: Address '{0}' is not in network '{1}'".format(
                str(address), str(net)
            )
        )
    return int(address) - net.first


class FilterModule(object):
    def filters(self):
        return {"host_num_in_net": host_num_in_net}
