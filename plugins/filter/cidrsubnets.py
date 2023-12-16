from __future__ import absolute_import, division, print_function

__metaclass__ = type

from math import log2, trunc
from netaddr import IPNetwork
from ansible.errors import AnsibleFilterError


from ansible_collections.andrei.utils.plugins.module_utils.network import (
    prefix_from_diff,
    next_of_size,
)


def fill_remaining(net, subnets, start=0):
    if not subnets:
        return [net]
    subnets = sorted(subnets)
    size = 0
    # Look for gaps at the end
    gap = abs(net.last - subnets[-1].last)
    if gap > 1:
        size = prefix_from_diff(net, trunc(log2(gap)))
    else:
        # Look for gaps in the middle
        for i in range(len(subnets) - 1):
            gap = abs(subnets[i].last - subnets[i + 1].first)
            if gap > 1:
                if start > 0 and subnets[i].last < start:
                    continue
                size = prefix_from_diff(net, trunc(log2(gap)))
                break
    if size > 0:
        subnets.append(next_of_size(net, subnets, size, start))
        # Try again in case there are more
        return fill_remaining(net, subnets, start)
    return subnets


def cidrsubnets(
    net,
    *prefixes,
    fill=False,
    fill_only_end=True,
    start=0,
    num_prefixes=0,
    prefix_size=None,
    prefix_skip=0
):
    if prefixes and num_prefixes:
        raise AnsibleFilterError("prefixes and num_prefixes are mutually exclusive")
    if prefix_skip and not prefix_size:
        raise AnsibleFilterError("prefix_size is required for prefix_skip")
    if prefix_skip and start:
        raise AnsibleFilterError("prefix_skip and start are mutually exclusive")
    if num_prefixes and not prefix_size:
        raise AnsibleFilterError("prefix_size is required when using num_prefixes")

    net = IPNetwork(net)
    subnets = []
    if start:
        start = net.first + start
    elif prefix_skip:
        start = net.first + (2 ** prefix_from_diff(net, prefix_size)) * (
            prefix_skip - 1
        )
    if num_prefixes:
        prefixes = [prefix_size for _ in range(num_prefixes)]
    for p in prefixes:
        subnets.append(next_of_size(net, subnets, p, start))
    if fill:
        start = 0
        if fill_only_end and subnets:
            start = subnets[-1].last
        subnets = fill_remaining(net, subnets, start)
    return [str(s) for s in subnets]


class FilterModule(object):
    def filters(self):
        return {"cidrsubnets": cidrsubnets}
