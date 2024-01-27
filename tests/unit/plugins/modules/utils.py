from __future__ import absolute_import, division, print_function

__metaclass__ = type


def validate_output(out, expected_add, expected_update, expected_remove):
    assert out["to_add"] == expected_add
    assert out["to_update"] == expected_update
    assert out["to_remove"] == expected_remove
    for item in out["to_update"]:
        assert ".id" in item
    for item in out["to_remove"]:
        assert ".id" in item
