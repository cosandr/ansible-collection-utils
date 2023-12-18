# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: mt_get_dns_entries
author: Andrei Costescu (@cosandr)
version_added: "1.0.0"
short_description: Compute static DNS entries for MikroTik devices.
description: Compute static DNS entries for MikroTik devices.
options:
    existing:
        description: Existing data fetched using community.routeros.api_info
        required: true
        type: list
        elements: dict
    data:
        description: Expected data in the same format as existing data.
        required: true
        type: list
        elements: dict
    comment_regex:
        description: Include only entries whose comments match regex.
        required: false
        type: str
        default: ''
    exclude_comment_regex:
        description: Exclude entries whose comments match regex.
        required: false
        type: str
        default: ''
    remove_without_comment:
        description: Remove entries not present in I(data) missing comments.
        required: false
        default: true
        type: bool
"""

EXAMPLES = r"""
- name: Get all DNS entries
  community.routeros.api_info:
    path: ip dns static
    handle_disabled: null-value
  register: __mt_dns

- name: Get add, update, remove lists
  andrei.utils.mt_get_dns_entries:
    existing: "{{ __mt_dns.result }}"
    data:
      - name: example.com
        address: 10.0.1.2
    exclude_comment_regex: "^dhcp-.*"
  register: __dns_lists

- name: Add missing entries
  community.routeros.api_modify:
    path: ip dns static
    data: "{{ __dns_lists.to_add }}"

- name: Delete old DNS entries
  community.routeros.api:
    path: ip dns static
    remove: "{{ item['.id'] }}"
  loop: "{{ __dns_lists.to_remove }}"

- name: Update DNS entries
  community.routeros.api_find_and_modify:
    path: ip dns static
    find:
      ".id": "{{ item['.id'] }}"
    values: "{{ item }}"
    require_matches_min: 1
    require_matches_max: 1
  loop: "{{ __dns_lists.to_update }}"
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

import re
import traceback

from ansible.module_utils.basic import AnsibleModule, missing_required_lib

try:
    from netaddr import IPAddress
except ImportError:
    HAS_NETADDR = False
    NETADDR_IMPORT_ERROR = traceback.format_exc()
else:
    HAS_NETADDR = True
    NETADDR_IMPORT_ERROR = None


def get_entry(data, entry, strict=False):
    name = entry.get("name")
    regexp = entry.get("regexp")
    other_address = entry.get("address")
    for d in data:
        self_address = d.get("address")
        # Skip if it's the wrong family
        if (
            self_address
            and other_address
            and IPAddress(self_address).version != IPAddress(other_address).version
        ):
            continue
        if name and d.get("name") == name:
            if not strict or (strict and self_address == other_address):
                return d
        if regexp and d.get("regexp") == regexp:
            if not strict or (strict and self_address == other_address):
                return d
    return None


def get_entry_eq(data, entry):
    """Get entry, exact match"""
    for d in data:
        if entries_eq(d, entry):
            return d
    return None


def entries_eq(old, new):
    for k, v in new.items():
        if k not in old:
            return False
        if old[k] != v:
            return False

    return True


def main():
    argument_spec = dict(
        existing=dict(type="list", elements="dict", required=True),
        data=dict(type="list", elements="dict", required=True),
        comment_regex=dict(type="str", default=""),
        exclude_comment_regex=dict(type="str", default=""),
        remove_without_comment=dict(type="bool", default=True),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        mutually_exclusive=[["comment_regex", "exclude_comment_regex"]],
    )

    if not HAS_NETADDR:
        module.fail_json(
            msg=missing_required_lib("netaddr"), exception=NETADDR_IMPORT_ERROR
        )

    existing = module.params["existing"]
    data = module.params["data"]
    comment_regex = module.params["comment_regex"]
    exclude_comment_regex = module.params["exclude_comment_regex"]
    remove_without_comment = module.params["remove_without_comment"]

    if comment_regex:
        comment_regex = re.compile(comment_regex)

    if exclude_comment_regex:
        exclude_comment_regex = re.compile(exclude_comment_regex)

    to_add = []
    to_update = []
    to_remove = []

    existing_managed = []
    for d in existing:
        if d["comment"]:
            if comment_regex and not comment_regex.match(d["comment"]):
                continue
            if exclude_comment_regex and exclude_comment_regex.match(d["comment"]):
                continue
        existing_managed.append(d)

    # Python 2.7 doesn't have list.copy()
    data_tmp = list(data)
    data = []
    # Remove invalid data
    for d in data_tmp:
        if "name" not in d and "regexp" not in d:
            module.warn(
                "mt_get_dns_entries: Data missing 'name' and 'regexp', check for undefined variables."
            )
            continue
        old = get_entry_eq(existing_managed, d)
        if old:
            existing_managed.remove(old)
        else:
            data.append(d)

    data_tmp = list(data)
    data = []
    # Find entries update strictly
    for d in data_tmp:
        old = get_entry(existing_managed, d, strict=True)
        # Update if name/regexp + address match but some other field does not
        if old and not entries_eq(old, d):
            # Add ID for faster editing
            d[".id"] = old[".id"]
            to_update.append(d)
            existing_managed.remove(old)
        # Process further if we didn't find a match
        elif not old:
            data.append(d)
        # Skip it if we found it and it was already up to date
        else:
            existing_managed.remove(d)

    # Find entries to update loosely or to add
    for d in data:
        old = get_entry(existing_managed, d, strict=False)
        if not old:
            to_add.append(d)
        elif not entries_eq(old, d):
            # Add ID for faster editing
            d[".id"] = old[".id"]
            to_update.append(d)
            existing_managed.remove(old)
        else:
            existing_managed.remove(old)

    # Find entries to delete
    for d in existing_managed:
        if not get_entry(data, d):
            if not d["comment"] and not remove_without_comment:
                continue
            to_remove.append(d)

    result = dict(
        changed=False, to_add=to_add, to_update=to_update, to_remove=to_remove
    )

    module.exit_json(**result)


if __name__ == "__main__":
    main()
