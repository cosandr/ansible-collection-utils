from ansible.errors import AnsibleFilterError
from netaddr import IPNetwork, spanning_cidr


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
    for sub in net.subnet(size):
        if not net_overlaps(sub, subnets) and sub.first > start:
            return sub
    raise AnsibleFilterError("'{}' is too small".format(str(net)))


def ipaddr_concat_query(nets, host, query, prefixlen):
    # Validate, ensure they're in the same network
    if len(nets) > 1 and spanning_cidr(nets).prefixlen == 0:
        raise AnsibleFilterError("ipaddr_concat: CIDRs span the entire address range")
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
        raise AnsibleFilterError(
            "prefixlen cannot be used when mixing v4 and v6 networks."
        )
    ret = [
        addr
        for addr in (
            ipaddr_concat_query(v4_nets, host, query, prefixlen),
            ipaddr_concat_query(v6_nets, host, query, prefixlen),
        )
        if addr is not None
    ]
    if not ret:
        raise AnsibleFilterError("No addresses found")
    if len(ret) == 1 and not wantlist:
        return ret[0]
    return ret
