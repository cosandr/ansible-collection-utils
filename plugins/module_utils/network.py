from __future__ import absolute_import, division, print_function

__metaclass__ = type

try:
    from netaddr import IPNetwork, spanning_cidr
except ImportError:
    pass


class NetworkError(Exception):
    pass


def net_overlaps(net, others):
    for o in others:
        if net in o or o in net:
            return True
    return False


def prefix_from_diff(net, diff):
    if net.version == 4:
        return 32 - diff
    return 128 - diff


def next_of_size(net, subnets, size, start=0):
    from_end = size < 0
    if from_end:
        size *= -1
    ret = None
    gen = net.subnet(size)
    # NOTE: from_end is very inefficient, would take for ever with most IPv6 subnets
    while True:
        try:
            sub = next(gen)
        except StopIteration:
            break
        if not net_overlaps(sub, subnets) and sub.first > start:
            ret = sub
            if not from_end:
                break
    if ret is None:
        raise NetworkError("'{}' is too small".format(str(net)))
    return ret


def ipaddr_concat_query(nets, host, query, prefixlen):
    # Validate, ensure they're in the same network
    if len(nets) > 1 and spanning_cidr(nets).prefixlen == 0:
        raise NetworkError("CIDRs span the entire address range")
    if prefixlen is not None:
        query = "address"
    nets.sort()
    for n in nets:
        if host >= n.size:
            host -= n.size
            continue
        if query in ["", "host"]:
            return str(n[host])
        elif query == "address":
            return str(n[host]) + "/" + str(prefixlen or n.prefixlen)
    return None


def ipaddr_concat(ips, host, query="", prefixlen=None, wantlist=False):
    """Given a list of CIDRs, returns the nth host as if it was a single continous range
    Examples:
    ['10.0.50.0/28', '10.0.50.128/25'] | andrei.utils.ipaddr_concat(15) => 10.0.50.15
    ['10.0.50.0/28', '10.0.50.128/25'] | andrei.utils.ipaddr_concat(16) => 10.0.50.128
    ['10.0.50.0/28', '10.0.50.128/25'] | andrei.utils.ipaddr_concat(15, 'address') => 10.0.50.15/28
    ['10.0.50.0/28', '10.0.50.128/25'] | andrei.utils.ipaddr_concat(16, 'address') => 10.0.50.128/25
    """
    host = int(host)
    nets = []
    if isinstance(ips, list):
        # Create IPNetwork objects
        nets = [IPNetwork(v) for v in ips]
    else:
        nets = [IPNetwork(ips)]
    v4_nets = [net for net in nets if net.version == 4]
    v6_nets = [net for net in nets if net.version == 6]
    if v4_nets and v6_nets and prefixlen:
        raise NetworkError("prefixlen cannot be used when mixing v4 and v6 networks.")
    ret = [
        addr
        for addr in (
            ipaddr_concat_query(v4_nets, host, query, prefixlen),
            ipaddr_concat_query(v6_nets, host, query, prefixlen),
        )
        if addr is not None
    ]
    if not ret:
        raise NetworkError("No addresses found")
    if len(ret) == 1 and not wantlist:
        return ret[0]
    return ret
