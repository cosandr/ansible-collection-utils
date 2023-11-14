from __future__ import absolute_import, division, print_function

__metaclass__ = type


from netaddr import IPNetwork


def sort_subnets(subnets):
    ret = {}
    for net, subs in subnets.items():
        sorted_keys = sorted(subs.keys(), key=lambda item: min([IPNetwork(net).first for net in subs[item]]))
        ret[net] = {k: subs[k] for k in sorted_keys}
    return ret


class FilterModule(object):
    def filters(self):
        return {'sort_subnets': sort_subnets}
