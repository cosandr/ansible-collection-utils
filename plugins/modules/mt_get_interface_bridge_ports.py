# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: mt_get_interface_bridge_ports
author: Andrei Costescu (@cosandr)
version_added: "1.1.0"
short_description: Compute interface bridge ports for MikroTik devices.
description: Compute interface bridge ports for MikroTik devices.
options:
    networks:
        description: Network definition
        required: true
        type: dict
    all_ports:
        description: List of switch ports to add to bridge.
        required: true
        type: list
        elements: str
    trunk_ports:
        description:
          - List of ports to configure admit-only-vlan-tagged for.
          - Only for CRS3xx devices.
        required: false
        type: list
        elements: str
        default: []
    access_ports:
        description:
          - List of ports to configure pvid for.
          - Only for CRS3xx devices.
        required: false
        type: list
        elements: dict
        default: []
    bridge_name:
        description: Name of bridge to configure.
        required: false
        type: str
        default: bridge1
    port_params:
        description: Name of bridge to configure.
        required: false
        type: dict
        default: {}
"""

EXAMPLES = r"""
- name: Get add, update, remove lists
  andrei.utils.mt_get_interface_bridge_ports:
    networks:
      example:
        vlan: 10
    all_ports: [ether1, ether2, ether3]
    # Only use these two if on CRS3xx
    trunk_ports: [ether1]
    access_ports:
      - vlan: example
        ports:
          - ether2
    bridge_name: bridge2
    port_params:
      hw: true
  register: __br_ports

# Expected output:
# new_data = [
#     {
#         "bridge": "bridge2",
#         "frame-types": "admit-only-vlan-tagged",
#         "interface": "ether1",
#         "hw": true
#     },
#     {
#         "bridge": "bridge2",
#         "interface": "ether2",
#         "pvid": 10,
#         "hw": true
#     },
#     {
#         "bridge": "bridge2",
#         "interface": "ether3",
#         "hw": true
#     }
# ]

- name: Configure bridge ports
  community.routeros.api_modify:
    path: interface bridge port
    timeout: 20
    data: "{{ __br_ports.new_data }}"
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
from ansible_collections.andrei.utils.plugins.module_utils.mt.utils import make_vid_map


def main():
    argument_spec = dict(
        networks=dict(type="dict", required=True),
        all_ports=dict(type="list", elements="str", required=True),
        trunk_ports=dict(type="list", elements="str", default=[]),
        access_ports=dict(type="list", elements="dict", default=[]),
        bridge_name=dict(type="str", default="bridge1"),
        port_params=dict(type="dict", default={}),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    networks = module.params["networks"]
    all_ports = module.params["all_ports"]
    trunk_ports = module.params["trunk_ports"]
    access_ports = module.params["access_ports"]
    bridge_name = module.params["bridge_name"]
    port_params = module.params["port_params"]

    vid_map = make_vid_map(networks)

    # Mapping to make processing easier
    new_data = {}
    # Add all ports
    for p in all_ports:
        new_data[p] = {
            "bridge": bridge_name,
            "interface": p,
        }
        for k, v in port_params.items():
            new_data[p][k] = v
    # Configure access ports
    for cfg in access_ports:
        vid = vid_map.get(cfg["vlan"])
        if not vid:
            module.fail_json("Cannot find VID for '{}'".format(cfg["vlan"]))
        for p in cfg["ports"]:
            if p not in new_data:
                module.fail_json("'{}' is not a bridge port".format(p))
            new_data[p]["pvid"] = vid

    # Configure trunk ports
    for p in trunk_ports:
        if p not in new_data:
            module.fail_json("'{}' is not a bridge port".format(p))
        new_data[p]["frame-types"] = "admit-only-vlan-tagged"

    result = dict(changed=False, new_data=list(new_data.values()))

    module.exit_json(**result)


if __name__ == "__main__":
    main()
