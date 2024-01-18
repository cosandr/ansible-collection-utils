# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: mt_get_interface_sw_ingress
author: Andrei Costescu (@cosandr)
version_added: "1.1.0"
short_description: Compute switch ingress config for MikroTik devices.
description:
  - Compute switch ingress config for MikroTik devices.
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
    access_ports:
        description: List of ports to configure as access ports.
        required: false
        type: list
        elements: dict
        default: []
"""

EXAMPLES = r"""
- name: Get ingress VLAN translations
  check_mode: false
  changed_when: false
  community.routeros.api:
    path: interface ethernet switch ingress-vlan-translation
    timeout: 20
    extended_query:
      attributes:
        - .id
        - dynamic
        - ports
        - customer-vid
        - new-customer-vid
      where:
        - attribute: "dynamic"
          is: "=="
          value: false
  register: __vlan_ingress

- name: Get switch VLAN ingress config
  andrei.utils.mt_get_interface_sw_ingress:
    existing: "{{ __vlan_ingress.msg }}"
    networks:
      example:
        vlan: 50
    access_ports:
      - vlan: example
        ports: [ether1, ether2, ether3, ether4]
  register: __sw_vlan_egress_config

# Expected output:
# [
#     {
#         ".id": "*F",
#         "customer-vid": 0,
#         "new-customer-vid": 50,
#         "ports": "ether1,ether2,ether3,ether4"
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
)


def main():
    argument_spec = dict(
        existing=dict(type="list", elements="dict", required=True),
        networks=dict(type="dict", required=True),
        access_ports=dict(type="list", elements="dict", default=[]),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    existing = module.params["existing"]
    networks = module.params["networks"]
    access_ports = module.params["access_ports"]

    vid_map = make_vid_map(networks)
    new_data = []

    # Configure access ports
    for cfg in access_ports:
        vlan = cfg["vlan"]
        vid = vid_map.get(vlan)
        if not vid:
            module.fail_json("Cannot find VLAN or its VID '{}'".format(vlan))

        new_data.append(
            {
                "customer-vid": 0,
                "new-customer-vid": vid,
                "ports": ",".join(cfg["ports"]),
            }
        )

    to_add, to_update, to_remove = make_add_update_remove(
        existing, new_data, "new-customer-vid"
    )

    result = dict(
        changed=False, to_add=to_add, to_update=to_update, to_remove=to_remove
    )

    module.exit_json(**result)


if __name__ == "__main__":
    main()
