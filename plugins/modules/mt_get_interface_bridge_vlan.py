# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: mt_get_interface_bridge_vlan
author: Andrei Costescu (@cosandr)
version_added: "1.1.0"
short_description: Compute interface bridge vlans for MikroTik devices.
description:
  - Compute interface bridge vlans for MikroTik devices.
  - Only for CRS3xx devices.
options:
    networks:
        description: Network definition
        required: true
        type: dict
    trunk_ports:
        description:
          - List of ports to configure as tagged.
          - May use the same format as I(access_ports).
          - The bridge interface is always included.
        required: false
        type: list
        elements: raw
        default: []
    access_ports:
        description: List of ports to configure as untagged.
        required: false
        type: list
        elements: dict
        default: []
    bridge_name:
        description: Name of bridge to configure.
        required: false
        type: str
        default: bridge1
"""

EXAMPLES = r"""
- name: Get add, update, remove lists
  andrei.utils.mt_get_interface_bridge_ports:
    networks:
      example:
        vlan: 2
      another:
        vlan: 100
    trunk_ports: [sfp-sfpplus1, ether2]
    access_ports:
      - vlan: another
        ports:
          - ether1
    bridge_name: bridge2
  register: __br_vlans

# Expected output:
# new_data = [
#     {
#         "bridge": "bridge2",
#         "tagged": "bridge2,sfp-sfpplus1,ether2",
#         "vlan-ids": 2
#     },
#     {
#         "bridge": "bridge2",
#         "tagged": "bridge2,sfp-sfpplus1,ether2",
#         "untagged": "ether1",
#         "vlan-ids": 100
#     }
# ]

- name: Configure bridge VLANs
  community.routeros.api_modify:
    path: interface bridge vlan
    data: "{{ __br_vlans.new_data }}"
    handle_absent_entries: remove
    handle_entries_content: remove_as_much_as_possible
"""

RETURN = r"""
new_data:
    description: List of entries that need to be added.
    type: list
    elements: dict
    returned: success
"""


from ansible.module_utils.basic import AnsibleModule
from ansible_collections.andrei.utils.plugins.module_utils.mt.utils import (
    make_vid_map,
    sort_ports,
)


def main():
    argument_spec = dict(
        networks=dict(type="dict", required=True),
        trunk_ports=dict(type="list", elements="raw", default=[]),
        access_ports=dict(type="list", elements="dict", default=[]),
        bridge_name=dict(type="str", default="bridge1"),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    networks = module.params["networks"]
    trunk_ports = module.params["trunk_ports"]
    access_ports = module.params["access_ports"]
    bridge_name = module.params["bridge_name"]

    vid_map = make_vid_map(networks)

    access_port_map = {}
    # Mapping to make processing easier
    new_data = {}
    # Add all VLANs
    for name, vid in vid_map.items():
        new_data[name] = {
            "bridge": bridge_name,
            "vlan-ids": vid,
        }
        access_port_map[name] = set()

    # Configure access ports
    for cfg in access_ports:
        vlan = cfg["vlan"]
        if vlan not in new_data:
            module.fail_json("Cannot find VLAN '{}'".format(vlan))
        access_port_map[vlan] = set(cfg["ports"])
        new_data[vlan]["untagged"] = ",".join(sort_ports(cfg["ports"]))

    # Configure trunk ports
    for vlan in new_data.keys():
        ports = []
        for idx, item in enumerate(trunk_ports):
            if isinstance(item, str):
                # Add plain ports to all VLANs
                ports.append(item)
            elif isinstance(item, dict):
                if item["vlan"] not in new_data:
                    module.fail_json("Cannot find VLAN '{}'".format(item["vlan"]))
                if vlan == item["vlan"]:
                    ports.extend(item["ports"])
            else:
                module.fail_json(
                    "Element at index {} type ({}) is unsupported".format(
                        idx, type(item).__name__
                    )
                )
        ports = [p for p in ports if p not in access_port_map[vlan]]
        if ports:
            new_data[vlan]["tagged"] = ",".join([bridge_name] + sort_ports(ports))

    result = dict(changed=False, new_data=list(new_data.values()))

    module.exit_json(**result)


if __name__ == "__main__":
    main()
