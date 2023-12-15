from __future__ import absolute_import, division, print_function

__metaclass__ = type


import re

from netaddr import IPAddress

from ansible.module_utils.basic import AnsibleModule


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

    data_tmp = data.copy()
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

    data_tmp = data.copy()
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
