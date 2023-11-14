from __future__ import absolute_import, division, print_function

__metaclass__ = type

from netaddr import IPNetwork

from ansible.errors import AnsibleFilterError
from ansible_collections.andrei.utils.plugins.module_utils.network import (
    next_of_size, prefix_from_diff)


def generate_subnets(net, prefixes, start=0, prefix_size=None, prefix_skip=0):
    if prefix_skip and not prefix_size:
        raise AnsibleFilterError("prefix_size is required for prefix_skip")
    if prefix_skip and start:
        raise AnsibleFilterError("prefix_skip and start are mutually exclusive")

    net = IPNetwork(net)
    subnets = []
    if start:
        start = net.first + start
    elif prefix_skip:
        start = net.first + (2 ** prefix_from_diff(net, prefix_size)) * (prefix_skip - 1)
    for p in prefixes:
        subnets.append(next_of_size(net, subnets, p, start))
    return [str(s) for s in subnets]


def get_prefixes_from_map(subnet_map, version, size=None):
    prefixes = []
    for sizes in subnet_map.values():
        if isinstance(sizes, int):
            sizes = [sizes]
        if version == 4:
            tmp = [s for s in sizes if s <= 32]
        else:
            tmp = [s for s in sizes if s > 32]
        if not tmp:
            if not size and prefixes:
                raise AnsibleFilterError("Provide all IPv{0} subnet sizes or v{0}_size.".format(version))
            elif size:
                tmp.append(size)
        prefixes.extend(tmp)
    return prefixes


def subnets_from_map(net, subnet_map, v4_size=None, v6_size=None, v4_start=0, v6_start=0, v4_prefix_skip=0, v6_prefix_skip=0):
    v4_prefixes = get_prefixes_from_map(subnet_map, 4, v4_size)
    v6_prefixes = get_prefixes_from_map(subnet_map, 6, v6_size)
    ret = {k: [] for k in subnet_map.keys()}
    if 'cidr' in net and v4_prefixes:
        v4_subnets = generate_subnets(net['cidr'], v4_prefixes, v4_start, v4_size, v4_prefix_skip)
        for k, v in zip(subnet_map.keys(), v4_subnets, strict=True):
            ret[k].append(v)
    if 'cidr6' in net and v6_prefixes:
        v6_subnets = generate_subnets(net['cidr6'], v6_prefixes, v6_start, v6_size, v6_prefix_skip)
        for k, v in zip(subnet_map.keys(), v6_subnets, strict=True):
            ret[k].append(v)
    return ret


class FilterModule(object):
    def filters(self):
        return {'subnets_from_map': subnets_from_map}
