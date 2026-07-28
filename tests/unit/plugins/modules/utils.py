from __future__ import absolute_import, division, print_function

__metaclass__ = type

import json

from ansible.module_utils import basic
from ansible.module_utils.common.text.converters import to_bytes


def set_module_args(args):
    if "_ansible_remote_tmp" not in args:
        args["_ansible_remote_tmp"] = "/tmp"
    if "_ansible_keep_remote_files" not in args:
        args["_ansible_keep_remote_files"] = False

    args = json.dumps({"ANSIBLE_MODULE_ARGS": args})
    basic._ANSIBLE_ARGS = to_bytes(args)
    basic._ANSIBLE_PROFILE = "legacy"


def validate_output(out, expected_add, expected_update, expected_remove):
    assert out["to_add"] == expected_add
    assert out["to_update"] == expected_update
    assert out["to_remove"] == expected_remove
    for item in out["to_update"]:
        assert ".id" in item
    for item in out["to_remove"]:
        assert ".id" in item
