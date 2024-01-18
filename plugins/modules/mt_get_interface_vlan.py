# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: mt_get_interface_vlan
author: Andrei Costescu (@cosandr)
version_added: "1.1.0"
short_description: Compute VLAN interfaces for MikroTik devices.
description: Compute VLAN interfaces for MikroTik devices.
options:
    networks:
        description: Network definition
        required: true
        type: dict
    bridge_name:
        description: Name of bridge to configure.
        required: false
        type: str
        default: bridge1
"""

EXAMPLES = r"""
- name: Get VLAN config
  andrei.utils.mt_get_interface_vlan:
    networks:
      example:
        vlan: 2
      another:
        vlan: 100
    bridge_name: "bridge2"
  register: __vlans

# Expected output:
# new_data = [
#     {
#         "interface": "bridge2",
#         "name": "example",
#         "vlan-id": 2
#     },
#     {
#         "interface": "bridge2",
#         "name": "another",
#         "vlan-id": 100
#     },
# ]

- name: Configure VLANs
  community.routeros.api_modify:
    path: interface vlan
    timeout: 20
    data: "{{ __vlans.new_data }}"
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


def main():
    argument_spec = dict(
        networks=dict(type="dict", required=True),
        bridge_name=dict(type="str", default="bridge1"),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    networks = module.params["networks"]
    bridge_name = module.params["bridge_name"]

    new_data = []
    for net_name, net_config in networks.items():
        if "vlan" not in net_config:
            continue
        comment = []
        if "cidr" in net_config:
            comment.append(net_config["cidr"])
        if "cidr6" in net_config:
            comment.append(net_config["cidr6"])
        comment = "; ".join(comment)
        new_data.append(
            {
                "interface": bridge_name,
                "name": net_name.upper(),
                "vlan-id": net_config["vlan"],
                "mtu": net_config.get("mtu", 1500),
                "comment": comment or None,
            }
        )

    result = dict(changed=False, new_data=new_data)

    module.exit_json(**result)


if __name__ == "__main__":
    main()
