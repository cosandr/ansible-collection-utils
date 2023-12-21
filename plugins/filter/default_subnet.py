from __future__ import absolute_import, division, print_function

__metaclass__ = type


from copy import deepcopy

from ansible.errors import AnsibleFilterError
from ansible.module_utils.basic import missing_required_lib
from ansible.utils.display import Display

try:
    from netaddr import IPNetwork
except ImportError as imp_exc:
    NETADDR_IMPORT_ERROR = imp_exc
else:
    NETADDR_IMPORT_ERROR = None


def split_network_v4(n, no_clients):
    """Returns IPv4 subnets from a CIDR"""
    if n.prefixlen > 24:
        Display().warning("default_subnet: '{}' too small".format(str(n)))
        return {}
    tmp = {
        "switches": [
            str(list(n.subnet(28))[0]),
        ],
        "hosts": [
            str(list(n.subnet(28))[1]),
        ],
        "vips": [
            str(list(n.subnet(27))[1]),
        ],
    }
    if not no_clients:
        tmp["clients"] = [
            str(list(n.subnet(26))[1]),
            str(list(n.subnet(25))[1]),
        ]
    return tmp


def split_network_v6(n, no_clients):
    """Returns IPv6 subnets from a CIDR"""
    if n.prefixlen != 64:
        Display().warning("default_subnet: '{}' must be of size /64".format(str(n)))
        return {}
    subnets = list(n.subnet(80, 4))
    tmp = {
        "switches": [
            str(subnets[0]),
        ],
        "hosts": [
            str(subnets[1]),
        ],
        "vips": [
            str(subnets[2]),
        ],
    }
    if not no_clients:
        tmp["clients"] = [
            str(subnets[3]),
        ]
    return tmp


def merge_dicts(one, two):
    ret = deepcopy(one)
    for k, v in two.items():
        if k in ret:
            ret[k] += v
        else:
            ret[k] = v
    return ret


def default_subnet(
    network_defs,
    no_clients=None,
    skip_nets=None,
    v4_name="cidr",
    v6_name="cidr6",
):
    """Generates the default subnet layout
    Input:
    "internal_net": {
        "ceph": {
            "cidr": "10.0.23.0/24",
            "cidr6": "fd00:23::0/56",
            "vlan": 23
        }
    }
    Output:
    "ceph": {
        "clients": [
            "10.0.23.64/26",
            "10.0.23.128/25",
            "fd00:23:0:3::/64"
        ],
        "hosts": [
            "10.0.23.16/28",
            "fd00:23:0:1::/64"
        ],
        "switches": [
            "10.0.23.0/28",
            "fd00:23::/64"
        ],
        "vips": [
            "10.0.23.32/27",
            "fd00:23:0:2::/64"
        ]
    }
    """
    if NETADDR_IMPORT_ERROR:
        raise AnsibleFilterError(
            missing_required_lib("netaddr")
        ) from NETADDR_IMPORT_ERROR
    ret = {}
    no_clients = no_clients or []
    skip_nets = skip_nets or []
    for k, v in network_defs.items():
        if k in skip_nets:
            continue
        k_nc = no_clients is True or k in no_clients
        v4_dict = {}
        v6_dict = {}
        if v4_name in v:
            v4_dict = split_network_v4(IPNetwork(v[v4_name]), k_nc)
        if v6_name in v:
            v6_dict = split_network_v6(IPNetwork(v[v6_name]), k_nc)
        ret[k] = merge_dicts(v4_dict, v6_dict)
    return ret


class FilterModule(object):
    def filters(self):
        return {"default_subnet": default_subnet}
