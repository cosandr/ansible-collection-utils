from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible.errors import AnsibleFilterError
from ansible.module_utils.basic import missing_required_lib
from ansible.module_utils.common.text.converters import to_text
from ansible_collections.andrei.utils.plugins.module_utils.network import (
    NetworkError,
    next_of_size,
    prefix_from_diff,
)

try:
    from netaddr import IPNetwork
except ImportError as imp_exc:
    NETADDR_IMPORT_ERROR = imp_exc
else:
    NETADDR_IMPORT_ERROR = None


def get_sizes_by_version(sizes, version):
    if isinstance(sizes, int):
        sizes = [sizes]
    if version == 4:
        return [s for s in sizes if abs(s) <= 32]
    return [s for s in sizes if abs(s) > 32]


def get_prefix_size_from_map(subnet_map, version):
    """Return prefix size from map if they're all the same"""
    all_sizes = set()
    for sizes in subnet_map.values():
        for s in get_sizes_by_version(sizes, version):
            all_sizes.add(s)
    if len(all_sizes) == 1:
        return all_sizes.pop()
    return None


def generate_subnets(net, subnet_map, start=0, prefix_size=None, prefix_skip=0):
    net = IPNetwork(net)
    ret = {k: [] for k in subnet_map.keys()}
    subs = set()
    if start:
        start = net.first + start
    elif prefix_skip:
        if not prefix_size:
            prefix_size = get_prefix_size_from_map(subnet_map, net.version)
        if not prefix_size:
            raise AnsibleFilterError(
                "v{0}_size is required if subnets are different sizes when using v{0}_prefix_skip".format(
                    net.version
                )
            )
        start = net.first + (2 ** prefix_from_diff(net, prefix_size)) * (
            prefix_skip - 1
        )
    for sub_name, sizes in subnet_map.items():
        sizes = get_sizes_by_version(sizes, net.version)
        if not sizes and prefix_size:
            sizes = [prefix_size]
        for s in sizes:
            try:
                tmp = next_of_size(net, subs, s, start)
            except NetworkError as e:
                raise AnsibleFilterError(to_text(e))
            ret[sub_name].append(str(tmp))
            subs.add(tmp)
    return ret


def subnets_from_map(
    net_def,
    subnet_map,
    v4_name="cidr",
    v6_name="cidr6",
    v4_size=None,
    v6_size=None,
    v4_start=0,
    v6_start=0,
    v4_prefix_skip=0,
    v6_prefix_skip=0,
):
    if NETADDR_IMPORT_ERROR:
        raise AnsibleFilterError(
            missing_required_lib("netaddr")
        ) from NETADDR_IMPORT_ERROR
    ret = {k: [] for k in subnet_map.keys()}
    v4_subs = {}
    v6_subs = {}
    if v4_name in net_def:
        v4_subs = generate_subnets(
            net_def[v4_name], subnet_map, v4_start, v4_size, v4_prefix_skip
        )
    if v6_name in net_def:
        v6_subs = generate_subnets(
            net_def[v6_name], subnet_map, v6_start, v6_size, v6_prefix_skip
        )
    for k in subnet_map.keys():
        for sub in v4_subs.get(k, []) + v6_subs.get(k, []):
            ret[k].append(sub)
    return ret


class FilterModule(object):
    def filters(self):
        return {"subnets_from_map": subnets_from_map}
