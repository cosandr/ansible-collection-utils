# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: mt_get_interface_sw_vlan
author: Andrei Costescu (@cosandr)
version_added: "1.1.0"
short_description: Compute switch VLANs config for MikroTik devices.
description:
  - Compute switch VLANs config for MikroTik devices.
  - Only for CRS2xx devices.
options:
    existing:
        description: Existing data from MikroTik API.
        required: true
        type: list
        elements: dict
    networks:
        description: Network definition
        required: true
        type: dict
    trunk_ports:
        description:
          - List of ports to configure as tagged.
          - The switch chip is always included.
        required: false
        type: list
        elements: str
        default: []
    access_ports:
        description: List of ports to configure as access ports.
        required: false
        type: list
        elements: dict
        default: []
    switch_cpu:
        description: Name of switch chip to configure.
        required: false
        type: str
        default: switch1-cpu
"""

EXAMPLES = r"""
- name: Get switch VLANs
  check_mode: false
  changed_when: false
  community.routeros.api:
    path: interface ethernet switch vlan
    timeout: 20
    extended_query:
      attributes:
        - .id
        - dynamic
        - ports
        - vlan-id
      where:
        - attribute: "dynamic"
          is: "=="
          value: false
  register: __sw_vlans

- name: Get switch VLAN config
  andrei.utils.mt_get_interface_sw_vlan:
    existing: "{{ __sw_vlans.msg }}"
    networks:
      example:
        vlan: 10
    trunk_ports: [ether1, ether2]
    access_ports:
      - vlan: example
        ports: [ether3, ether4]
  register: __sw_vlan_egress_config

# Expected output:
# [
#     {
#         ".id": "*C",
#         "ports": "switch1-cpu,ether12,ether13,ether14,ether15,ether16,ether17,ether18,sfpplus2,sfp-sfpplus1",
#         "vlan-id": 10,
#     },
# ]
"""

RETURN = r"""
to_add:
    description: List of entries that need to be added.
    type: list
    elements: dict
    returned: success
to_update:
    description: List of entries that need to be updated.
    type: list
    elements: dict
    returned: success
to_remove:
    description: List of entries that need to be removed.
    type: list
    elements: dict
    returned: success
"""


from ansible.module_utils.basic import AnsibleModule
from ansible_collections.andrei.utils.plugins.module_utils.mt.utils import (
    make_add_update_remove,
    make_vid_map,
    sort_ports,
)


def main():
    argument_spec = dict(
        existing=dict(type="list", elements="dict", required=True),
        networks=dict(type="dict", required=True),
        trunk_ports=dict(type="list", elements="str", default=[]),
        access_ports=dict(type="list", elements="dict", default=[]),
        switch_cpu=dict(type="str", default="switch1-cpu"),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    existing = module.params["existing"]
    networks = module.params["networks"]
    trunk_ports = module.params["trunk_ports"]
    access_ports = module.params["access_ports"]
    switch_cpu = module.params["switch_cpu"]

    vid_map = make_vid_map(networks)
    vlan_ports = {name: [] for name in vid_map.keys()}
    new_data = []

    # Add access ports
    for cfg in access_ports:
        vlan = cfg["vlan"]
        if vlan not in vlan_ports:
            module.fail_json("Cannot find VLAN '{}'".format(vlan))
        vlan_ports[vlan] = cfg["ports"]

    # Add trunk ports
    if trunk_ports:
        for vlan in vlan_ports.keys():
            vlan_ports[vlan].extend(trunk_ports)

    # Create new data list
    for vlan, ports in vlan_ports.items():
        if not ports:
            continue
        new_data.append(
            {
                "ports": ",".join(sort_ports(ports, switch_cpu)),
                "vlan-id": vid_map[vlan],
            }
        )

    to_add, to_update, to_remove = make_add_update_remove(existing, new_data, "vlan-id")

    result = dict(
        changed=False, to_add=to_add, to_update=to_update, to_remove=to_remove
    )

    module.exit_json(**result)


if __name__ == "__main__":
    main()
