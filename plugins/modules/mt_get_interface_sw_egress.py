# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: mt_get_interface_sw_egress
author: Andrei Costescu (@cosandr)
version_added: "1.1.0"
short_description: Compute switch egress config for MikroTik devices.
description:
  - Compute switch egress config for MikroTik devices.
  - Only for CRS2xx devices.
  - Does not support multiple switch chips.
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
    switch_cpu:
        description: Name of switch chip to configure.
        required: false
        type: str
        default: switch1-cpu
"""

EXAMPLES = r"""
- name: Get egress VLAN tags
  check_mode: false
  changed_when: false
  community.routeros.api:
    path: interface ethernet switch egress-vlan-tag
    timeout: 20
    extended_query:
      attributes:
        - .id
        - dynamic
        - tagged-ports
        - vlan-id
      where:
        - attribute: "dynamic"
          is: "=="
          value: false
  register: __vlan_egress

- name: Get switch VLAN egress config
  andrei.utils.mt_get_interface_sw_egress:
    existing: "{{ __vlan_egress.msg }}"
    networks:
      example:
        vlan: 10
    trunk_ports: [ether1, ether2]
  register: __sw_vlan_egress_config

# Example element in returned lists:
# [
#     {
#         ".id": "*1",
#         "tagged-ports": "switch1-cpu,ether1,ether2",
#         "vlan-id": 10
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
    sort_trunks,
)


def main():
    argument_spec = dict(
        existing=dict(type="list", elements="dict", required=True),
        networks=dict(type="dict", required=True),
        trunk_ports=dict(type="list", elements="str", default=[]),
        switch_cpu=dict(type="str", default="switch1-cpu"),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    existing = module.params["existing"]
    networks = module.params["networks"]
    trunk_ports = module.params["trunk_ports"]
    switch_cpu = module.params["switch_cpu"]

    vid_map = make_vid_map(networks)
    new_data = []

    # Add trunk ports
    if trunk_ports:
        for vid in vid_map.values():
            new_data.append(
                {
                    "tagged-ports": ",".join(sort_trunks(trunk_ports, switch_cpu)),
                    "vlan-id": vid,
                }
            )

    to_add, to_update, to_remove = make_add_update_remove(existing, new_data, "vlan-id")

    result = dict(
        changed=False, to_add=to_add, to_update=to_update, to_remove=to_remove
    )

    module.exit_json(**result)


if __name__ == "__main__":
    main()
