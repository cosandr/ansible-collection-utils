# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: ceph_fs_snap_schedule
author: Andrei Costescu (@cosandr)
version_added: "1.2.0"
short_description: Configure fs snapshot schedules on CephFS.
description: Configure fs snapshot schedules on CephFS.
options:
    state:
        description: State of retention for this path
        required: false
        type: str
        default: present
        choices: ["present", "absent"]
    fs:
        description: File system name
        required: false
        type: str
    path:
        description: Path to manipulate
        required: true
        type: str
    schedule:
        description: Schedule for path
        required: false
        type: str
        default: 1h
    retention:
        description: List of retention settings for path
        required: true
        type: dict
        suboptions:
            hours:
                description: Number of hours to keep
                type: int
                required: false
            days:
                description: Number of days to keep
                type: int
                required: false
            weeks:
                description: Number of weeks to keep
                type: int
                required: false
            months:
                description: Number of months to keep
                type: int
                required: false
            years:
                description: Number of years to keep
                type: int
                required: false
"""

EXAMPLES = r"""
- name: Configure snapshots
  andrei.utils.ceph_fs_snap_schedule:
    fs: cephfs
    schedule: 1h
    path: /
    retention:
      days: 2
      weeks: 1
"""

RETURN = r"""
fs:
    description: Name of edited filesystem.
    type: str
    returned: on success if fs is provided
add_spec:
    description: Snapshot spec that has been added.
    type: str
    returned: success
    sample: 2d1w
remove_spec:
    description: Snapshot spec that has been removed.
    type: str
    returned: success
    sample: 2h1y
"""

import json
from ansible.module_utils.basic import AnsibleModule


def get_schedule(module: AnsibleModule, path: str, fs: str) -> dict:
    """Get schedule for path on filesystem"""
    cmd = [
        "ceph",
        "fs",
        "snap-schedule",
        "list",
        path,
        "--format",
        "json",
    ]
    if fs:
        cmd.extend(["--fs", fs])
    rc, stdout, stderr = module.run_command(cmd)
    if rc != 0:
        module.fail_json(
            msg="Failed to list snap schedules", rc=rc, stdout=stdout, stderr=stderr
        )
    return json.loads(stdout)


def change_schedule(module: AnsibleModule, command: str, path: str, fs: str, spec: str):
    cmd = [
        "ceph",
        "fs",
        "snap-schedule",
        command,
        path,
        spec,
    ]
    if fs:
        cmd.extend(["--fs", fs])
    rc, stdout, stderr = module.run_command(cmd)
    if rc != 0:
        module.fail_json(
            msg=f"Failed to {command} snap schedule",
            rc=rc,
            stdout=stdout,
            stderr=stderr,
        )


def change_retention(
    module: AnsibleModule, command: str, path: str, fs: str, spec: str
):
    cmd = [
        "ceph",
        "fs",
        "snap-schedule",
        "retention",
        command,
        path,
        spec,
    ]
    if fs:
        cmd.extend(["--fs", fs])
    rc, stdout, stderr = module.run_command(cmd)
    if rc != 0:
        module.fail_json(
            msg=f"Failed to {command} snap retention",
            rc=rc,
            stdout=stdout,
            stderr=stderr,
        )


def main():
    argument_spec = dict(
        fs=dict(type="str", required=False),
        state=dict(type="str", default="present", choices=["present", "absent"]),
        path=dict(type="str", required=True),
        schedule=dict(type="str", default="1h"),
        retention=dict(
            type="dict",
            required=True,
            options=dict(
                hours=dict(type="int"),
                days=dict(type="int"),
                weeks=dict(type="int"),
                months=dict(type="int"),
                years=dict(type="int"),
            ),
        ),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    fs = module.params["fs"]
    path = module.params["path"]
    schedule = module.params["schedule"]
    retention = module.params["retention"]

    changed = False
    result = dict(path=path)
    if fs:
        result["fs"] = fs

    existing = get_schedule(module, path, fs)
    # Convert input retention to format expected by Ceph
    retention_conv_map = {
        "hours": "h",
        "days": "d",
        "weeks": "w",
        "months": "M",
        "years": "y",
    }
    set_retention = {}
    for k, v in retention.items():
        if v:
            set_retention[retention_conv_map[k]] = v

    existing_retention = existing["retention"][0]
    existing_schedule = existing["schedule"][0]

    add_spec = ""
    remove_spec = ""
    if existing_retention != set_retention:
        changed = True
        for k, v in existing_retention.items():
            # Remove if it's no longer present or if it's different
            if k not in set_retention or v != set_retention[k]:
                remove_spec += f"{v}{k}"
        for k, v in set_retention.items():
            if k not in existing_retention or v != existing_retention[k]:
                add_spec += f"{v}{k}"

    result["changed"] = changed
    result["add_spec"] = add_spec
    result["remove_spec"] = remove_spec

    # Format diff
    before = dict(schedule=existing_schedule, retention="")
    after = dict(schedule=schedule, retention="")
    # Maintain order for consistency
    for k in retention_conv_map.values():
        if existing_retention.get(k):
            before["retention"] += f"{existing_retention[k]}{k}"
        if set_retention.get(k):
            after["retention"] += f"{set_retention[k]}{k}"
    result["diff"] = dict(
        before=before,
        after=after,
    )

    # Stop before changing anything
    if module.check_mode:
        module.exit_json(**result)

    # Add new schedule before removing old one so we don't lose retention settings
    if existing_schedule != schedule:
        change_schedule(module, "add", path, fs, schedule)
        change_schedule(module, "remove", path, fs, existing_schedule)

    if remove_spec:
        change_retention(module, "remove", path, fs, remove_spec)
    if add_spec:
        change_retention(module, "add", path, fs, add_spec)

    module.exit_json(**result)


if __name__ == "__main__":
    main()
