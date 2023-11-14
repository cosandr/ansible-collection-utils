from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible.errors import AnsibleLookupError
from ansible.plugins.lookup import LookupBase
from ansible_collections.ansible.utils.plugins.filter import ipv4, ipv6
from netaddr import IPAddress

from ansible_collections.andrei.utils.plugins.module_utils.network import ipaddr_concat


def check_ip_duplicates(data):
    # List if tuples containg (name, ip)
    # Allows for more useful error messages than just IPs
    checked = []

    def _check_ip(ip):
        for other_name, other_ip in checked:
            if ip == other_ip:
                return other_name
        return None

    for name, ips in data.items():
        for ip in ips.values():
            dup = _check_ip(ip)
            if dup is not None:
                raise AnsibleLookupError("%s duplicated for %s and %s" % (ip, name, dup))
            checked.append((name, ip))


class LookupModule(LookupBase):

    def run(self, terms, variables, **kwargs):

        ret = []

        managed_ips = {}

        self.set_options(var_options=variables, direct=kwargs)

        for name, hv in variables['hostvars'].items():
            tmp = {}
            # Populate dict
            if 'host_num' in hv:
                if 'host_net' not in hv or 'host_subnet' not in hv:
                    raise AnsibleLookupError('host_net and host_subnet must be defined for %s' % name)
                v4_subnet = ipv4.ipv4(hv['subnets'][hv['host_net']][hv['host_subnet']])
                if v4_subnet:
                    tmp['ansible_host'] = ipaddr_concat(v4_subnet, hv['host_num'])
                v6_subnet = ipv6.ipv6(hv['subnets'][hv['host_net']][hv['host_subnet']])
                if v6_subnet:
                    host_num6 = hv['host_num'] + 1
                    if 'host_num6_offset' in hv and hv['host_num6_offset'].lower() in ('false', 'no'):
                        host_num6 = hv['host_num']
                    tmp['ansible_host6'] = ipaddr_concat(v6_subnet, host_num6)
            if 'host_wg_num' in hv:
                if 'host_wg_net' not in hv or 'host_wg_subnet' not in hv:
                    raise AnsibleLookupError('host_wg_net and host_wg_subnet must be defined for %s' % name)
                v4_subnet = ipv4.ipv4(hv['subnets'][hv['host_wg_net']][hv['host_wg_subnet']])
                if v4_subnet:
                    tmp['wireguard_ip'] = ipaddr_concat(v4_subnet, hv['host_wg_num'])
                v6_subnet = ipv6.ipv6(hv['subnets'][hv['host_wg_net']][hv['host_wg_subnet']])
                if v6_subnet:
                    host_wg_num6 = hv['host_wg_num'] + 1
                    if 'host_wg_num6_offset' in hv and hv['host_wg_num6_offset'].lower() in ('false', 'no'):
                        host_wg_num6 = hv['host_wg_num']
                    tmp['wireguard_ip6'] = ipaddr_concat(v6_subnet, host_wg_num6)
            # Skip if host isn't managed
            if not tmp:
                continue
            managed_ips[name] = tmp
        # Check for duplicates
        check_ip_duplicates(managed_ips)
        # Sort by ansible_host or wireguard_ip

        def sort_func(x):
            tmp = []
            if 'ansible_host' in managed_ips[x]:
                tmp.append(IPAddress(managed_ips[x]['ansible_host']).value)
            if 'wireguard_ip' in managed_ips[x]:
                tmp.append(IPAddress(managed_ips[x]['wireguard_ip']).value)
            return tuple(tmp)

        sorted_keys = sorted(managed_ips.keys(), key=sort_func)

        col_map = {}
        # Construct string
        for name in sorted_keys:
            config = managed_ips[name]
            tmp = [name]
            for k, v in config.items():
                if v:
                    tmp.append('%s="%s"' % (k, v))
            col_map[name] = tmp
        max_lengths = []
        max_cols = len(max(col_map.values(), key=len))
        # Find max lengths of each column
        for i in range(max_cols):
            length = 0
            for cols in col_map.values():
                if i >= len(cols):
                    continue
                if len(cols[i]) > length:
                    length = len(cols[i])
            max_lengths.append(length)

        for name, cols in col_map.items():
            # Construct final host string with padding
            host_str = cols[0]
            for i in range(1, len(cols)):
                # Pad with length of previous term + 1
                padding = max_lengths[i-1] - len(cols[i-1]) + 1
                host_str += ' ' * padding + cols[i]
            ret.append(host_str)
        return ['\n'.join(ret)]
