from __future__ import absolute_import, division, print_function

__metaclass__ = type

import math

import yaml
from netaddr import IPAddress, IPNetwork

from ansible.errors import AnsibleLookupError
from ansible.module_utils.common.text.converters import to_native, to_text
from ansible.plugins.lookup import template
from ansible.utils.display import Display

# THIS IS MANDATORY!!!!
# Ansible appears to parse this to set defaults?
DOCUMENTATION = template.DOCUMENTATION


# https://stackoverflow.com/a/39681672
class MyDumper(yaml.SafeDumper):
    def increase_indent(self, flow=False, indentless=False):
        return super(MyDumper, self).increase_indent(flow, False)

    # https://github.com/yaml/pyyaml/issues/127#issuecomment-525800484
    # HACK: insert blank lines between top-level objects
    # inspired by https://stackoverflow.com/a/44284819/3786245
    def write_line_break(self, data=None):
        super().write_line_break(data)

        if len(self.indents) == 1:
            super().write_line_break()


# Ripped off ansible.plugins.filter.core
def to_nice_yaml(a, indent=4, *args, **kw):
    """Make verbose, human readable yaml"""
    try:
        transformed = yaml.dump(
            a,
            Dumper=MyDumper,
            indent=indent,
            allow_unicode=True,
            default_flow_style=False,
            **kw
        )
    except Exception as e:
        raise AnsibleLookupError("to_nice_yaml - %s" % to_native(e), orig_exc=e)
    return to_text(transformed)


def net_overlaps(net, others):
    for o in others:
        if net in o[0] or o[0] in net:
            return o
    return None


def check_net_overlaps(data):
    checked = []
    for var_name, var in data.items():
        if not var_name.endswith("_net"):
            continue
        for net_name, net_cfg in var.items():
            cidrs = (net_cfg.get("cidr"), net_cfg.get("cidr6"))
            for cidr in cidrs:
                if cidr is None:
                    continue
                net = IPNetwork(cidr)
                overlaps = net_overlaps(net, checked)
                if overlaps:
                    raise AnsibleLookupError(
                        "%s.%s: '%s' overlaps with %s.%s '%s'"
                        % (
                            var_name,
                            net_name,
                            str(net),
                            overlaps[2],
                            overlaps[1],
                            str(overlaps[0]),
                        )
                    )
                checked.append((net, var_name, net_name))


def check_subnet_overlaps(data):
    checked = []
    for net_name, net_subnets in data.get("subnets", {}).items():
        for sub_name, cidrs in net_subnets.items():
            for cidr in cidrs:
                net = IPNetwork(cidr)
                overlaps = net_overlaps(net, checked)
                if overlaps:
                    raise AnsibleLookupError(
                        "'%s' from %s [%s] overlaps with '%s' from %s [%s]"
                        % (
                            str(net),
                            sub_name,
                            net_name,
                            str(overlaps[0]),
                            overlaps[1],
                            overlaps[2],
                        )
                    )
                checked.append((net, sub_name, net_name))


def check_vip_duplicates(data):
    checked = []
    for net_name, vip_config in data.get("vips", {}).items():
        for vip_name, vip in vip_config.items():
            if vip in checked:
                raise AnsibleLookupError(
                    "VIP %s - '%s' in %s is a duplicate" % (vip_name, vip, net_name)
                )
            else:
                checked.append(vip)


def check_subnet_gaps(data):
    """Subnets MUST be in order!"""
    for net_name, net_subnets in data.get("subnets", {}).items():
        last_net = {}
        for sub_name, cidrs in net_subnets.items():
            for cidr in cidrs:
                net = IPNetwork(cidr)
                size = 32 if net.version == 4 else 128
                if last_net.get(net.version) is None:
                    last_net[net.version] = (sub_name, net)
                    continue
                last_net_name, last_net_ip = last_net[net.version]
                gap = math.trunc(math.log2(abs(net.first - last_net_ip.last)))
                if gap:
                    fit_net = "%s/%s" % (
                        str(IPAddress(last_net_ip.last + 1)),
                        size - gap,
                    )
                    Display().warning(
                        "%s: %s fits between %s [%s] and %s [%s]"
                        % (
                            net_name,
                            fit_net,
                            last_net_name,
                            str(last_net_ip),
                            sub_name,
                            str(net),
                        )
                    )
                last_net[net.version] = (sub_name, net)


class LookupModule(template.LookupModule):
    def run(self, terms, variables, **kwargs):
        acc_vars = dict()
        # Support list argument
        terms = terms[0]
        # Template one by one, parse as yaml and include them for next run
        for term in terms:
            kwargs["template_vars"] = acc_vars
            ret = super().run([term], variables, **kwargs)
            acc_vars |= yaml.safe_load(ret[0])

        # Check before removing reserved vars for more accuracy in the warning messages
        check_subnet_gaps(acc_vars)
        # Remove vars prefixed with _
        ret = {}
        for k, v in acc_vars.items():
            if k.startswith("_"):
                continue
            elif k == "subnets":
                subnets = {}
                for net_name, net_subnets in v.items():
                    subnets[net_name] = {
                        sub_name: cidrs
                        for sub_name, cidrs in net_subnets.items()
                        if not sub_name.startswith("_")
                    }
                ret[k] = subnets
            else:
                ret[k] = v

        check_net_overlaps(ret)
        check_subnet_overlaps(ret)
        check_vip_duplicates(ret)
        # Dump to YAML, with extra list indentations
        return [to_nice_yaml(ret, indent=2, sort_keys=False)]
