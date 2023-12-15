from __future__ import absolute_import, division, print_function

__metaclass__ = type


import pytest
import json

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.andrei.utils.plugins.modules import mt_get_dns_entries
from ansible_collections.community.general.tests.unit.plugins.modules.utils import (
    set_module_args,
)


def validate_output(
    out: dict, expected_add: list, expected_update: list, expected_remove: list
):
    assert out["to_add"] == expected_add
    assert out["to_update"] == expected_update
    assert out["to_remove"] == expected_remove
    for item in out["to_update"]:
        assert ".id" in item
    for item in out["to_remove"]:
        assert ".id" in item


def test_missing_args(capfd):
    set_module_args({})
    with pytest.raises(SystemExit):
        mt_get_dns_entries.main()
    out, err = capfd.readouterr()
    out = json.loads(out)
    assert not err
    assert out.get("failed", False)
    assert "missing required arguments" in out["msg"]


def test_missing_data(capfd):
    set_module_args(
        {
            "existing": [],
        }
    )
    with pytest.raises(SystemExit):
        mt_get_dns_entries.main()
    out, err = capfd.readouterr()
    out = json.loads(out)
    assert not err
    assert out.get("failed", False)
    assert "missing required arguments" in out["msg"]


def test_missing_existing(capfd):
    set_module_args(
        {
            "data": [],
        }
    )
    with pytest.raises(SystemExit):
        mt_get_dns_entries.main()
    out, err = capfd.readouterr()
    out = json.loads(out)
    assert not err
    assert out.get("failed", False)
    assert "missing required arguments" in out["msg"]


def test_missing_primary_keys(capfd, mocker):
    set_module_args(
        {
            "data": [
                {
                    "address": "10.0.10.1",
                }
            ],
            "existing": [],
        }
    )
    mock = mocker.patch.object(AnsibleModule, "log")
    with pytest.raises(SystemExit):
        mt_get_dns_entries.main()
    out, err = capfd.readouterr()
    out = json.loads(out)
    assert not out.get("failed", False)
    assert not err
    mock.assert_called_with(
        "[WARNING] mt_get_dns_entries: Data missing 'name' and 'regexp', check for undefined variables."
    )


def test_exclusive_args(capfd):
    set_module_args(
        {
            "data": [],
            "existing": [],
            "comment_regex": "something",
            "exclude_comment_regex": "else",
        }
    )
    with pytest.raises(SystemExit):
        mt_get_dns_entries.main()
    out, err = capfd.readouterr()
    out = json.loads(out)
    assert not err
    assert out.get("failed", False)
    assert "parameters are mutually exclusive" in out["msg"]


def test_simple_add(capfd):
    set_module_args(
        {
            "data": [
                {
                    "name": "test.example.com",
                    "address": "10.0.10.1",
                },
            ],
            "existing": [],
        }
    )
    expected_add = [
        {
            "name": "test.example.com",
            "address": "10.0.10.1",
        },
    ]
    expected_update = []
    expected_remove = []

    with pytest.raises(SystemExit):
        mt_get_dns_entries.main()
    out, err = capfd.readouterr()
    out = json.loads(out)
    assert not err
    assert not out.get("failed", False)
    validate_output(out, expected_add, expected_update, expected_remove)


def test_simple_indempotency(capfd):
    set_module_args(
        {
            "data": [
                {
                    "name": "test.example.com",
                    "address": "10.0.10.1",
                },
            ],
            "existing": [
                {
                    ".id": "1",
                    "comment": None,
                    "name": "test.example.com",
                    "address": "10.0.10.1",
                },
            ],
        }
    )
    expected_add = []
    expected_update = []
    expected_remove = []

    with pytest.raises(SystemExit):
        mt_get_dns_entries.main()
    out, err = capfd.readouterr()
    out = json.loads(out)
    assert not err
    assert not out.get("failed", False)
    validate_output(out, expected_add, expected_update, expected_remove)


def test_simple_update(capfd):
    set_module_args(
        {
            "data": [
                {
                    "name": "test.example.com",
                    "address": "10.0.10.2",
                },
            ],
            "existing": [
                {
                    ".id": "1",
                    "comment": None,
                    "name": "test.example.com",
                    "address": "10.0.10.1",
                },
            ],
        }
    )
    expected_add = []
    expected_update = [
        {
            ".id": "1",
            "name": "test.example.com",
            "address": "10.0.10.2",
        },
    ]
    expected_remove = []

    with pytest.raises(SystemExit):
        mt_get_dns_entries.main()
    out, err = capfd.readouterr()
    out = json.loads(out)
    assert not err
    assert not out.get("failed", False)
    validate_output(out, expected_add, expected_update, expected_remove)


def test_simple_remove(capfd):
    set_module_args(
        {
            "data": [],
            "existing": [
                {
                    ".id": "1",
                    "comment": None,
                    "name": "test.example.com",
                    "address": "10.0.10.1",
                },
            ],
        }
    )
    expected_add = []
    expected_update = []
    expected_remove = [
        {
            ".id": "1",
            "comment": None,
            "name": "test.example.com",
            "address": "10.0.10.1",
        },
    ]

    with pytest.raises(SystemExit):
        mt_get_dns_entries.main()
    out, err = capfd.readouterr()
    out = json.loads(out)
    assert not err
    assert not out.get("failed", False)
    validate_output(out, expected_add, expected_update, expected_remove)


def test_simple_multiple(capfd):
    set_module_args(
        {
            "data": [
                {
                    "name": "test.example.com",
                    "address": "10.0.10.11",
                },
                {
                    "name": "test2.example.com",
                    "address": "10.0.10.2",
                },
            ],
            "existing": [
                {
                    ".id": "1",
                    "comment": None,
                    "name": "test.example.com",
                    "address": "10.0.10.1",
                },
                {
                    ".id": "3",
                    "comment": None,
                    "name": "test3.example.com",
                    "address": "10.0.10.3",
                },
            ],
        }
    )
    expected_add = [
        {
            "name": "test2.example.com",
            "address": "10.0.10.2",
        },
    ]
    expected_update = [
        {
            ".id": "1",
            "name": "test.example.com",
            "address": "10.0.10.11",
        },
    ]
    expected_remove = [
        {
            ".id": "3",
            "comment": None,
            "name": "test3.example.com",
            "address": "10.0.10.3",
        },
    ]

    with pytest.raises(SystemExit):
        mt_get_dns_entries.main()
    out, err = capfd.readouterr()
    out = json.loads(out)
    assert not err
    assert not out.get("failed", False)
    validate_output(out, expected_add, expected_update, expected_remove)


def test_simple_multiple_comment_regex(capfd):
    set_module_args(
        {
            "data": [
                {
                    "comment": "modify-me",
                    "name": "test.example.com",
                    "address": "10.0.10.11",
                },
                {
                    "comment": "modify-me",
                    "name": "test2.example.com",
                    "address": "10.0.10.2",
                },
            ],
            "existing": [
                {
                    ".id": "1",
                    "comment": "modify-me",
                    "name": "test.example.com",
                    "address": "10.0.10.1",
                },
                {
                    ".id": "3",
                    "comment": "modify-me",
                    "name": "test3.example.com",
                    "address": "10.0.10.3",
                },
                {
                    ".id": "4",
                    "comment": "something-else",
                    "name": "test3.example.com",
                    "address": "10.0.10.3",
                },
                {
                    ".id": "5",
                    "comment": None,
                    "name": "test4.example.com",
                    "address": "10.0.10.4",
                },
            ],
            "comment_regex": "^modify-.*",
        }
    )
    expected_add = [
        {
            "comment": "modify-me",
            "name": "test2.example.com",
            "address": "10.0.10.2",
        },
    ]
    expected_update = [
        {
            "comment": "modify-me",
            ".id": "1",
            "name": "test.example.com",
            "address": "10.0.10.11",
        },
    ]
    expected_remove = [
        {
            ".id": "3",
            "comment": "modify-me",
            "name": "test3.example.com",
            "address": "10.0.10.3",
        },
        {
            ".id": "5",
            "comment": None,
            "name": "test4.example.com",
            "address": "10.0.10.4",
        },
    ]

    with pytest.raises(SystemExit):
        mt_get_dns_entries.main()
    out, err = capfd.readouterr()
    out = json.loads(out)
    assert not err
    assert not out.get("failed", False)
    validate_output(out, expected_add, expected_update, expected_remove)


def test_simple_multiple_comment_regex_keep_without_comment(capfd):
    set_module_args(
        {
            "data": [
                {
                    "comment": "modify-me",
                    "name": "test.example.com",
                    "address": "10.0.10.11",
                },
                {
                    "comment": "modify-me",
                    "name": "test2.example.com",
                    "address": "10.0.10.2",
                },
            ],
            "existing": [
                {
                    ".id": "1",
                    "comment": "modify-me",
                    "name": "test.example.com",
                    "address": "10.0.10.1",
                },
                {
                    ".id": "3",
                    "comment": "modify-me",
                    "name": "test3.example.com",
                    "address": "10.0.10.3",
                },
                {
                    ".id": "4",
                    "comment": "something-else",
                    "name": "test3.example.com",
                    "address": "10.0.10.3",
                },
                {
                    ".id": "5",
                    "comment": None,
                    "name": "test4.example.com",
                    "address": "10.0.10.4",
                },
            ],
            "comment_regex": "^modify-.*",
            "remove_without_comment": False,
        }
    )
    expected_add = [
        {
            "comment": "modify-me",
            "name": "test2.example.com",
            "address": "10.0.10.2",
        },
    ]
    expected_update = [
        {
            "comment": "modify-me",
            ".id": "1",
            "name": "test.example.com",
            "address": "10.0.10.11",
        },
    ]
    expected_remove = [
        {
            ".id": "3",
            "comment": "modify-me",
            "name": "test3.example.com",
            "address": "10.0.10.3",
        },
    ]

    with pytest.raises(SystemExit):
        mt_get_dns_entries.main()
    out, err = capfd.readouterr()
    out = json.loads(out)
    assert not err
    assert not out.get("failed", False)
    validate_output(out, expected_add, expected_update, expected_remove)


def test_simple_multiple_exclude_comment_regex(capfd):
    set_module_args(
        {
            "data": [
                {
                    "comment": "modify-me",
                    "name": "test.example.com",
                    "address": "10.0.10.11",
                },
                {
                    "comment": "modify-me",
                    "name": "test2.example.com",
                    "address": "10.0.10.2",
                },
            ],
            "existing": [
                {
                    ".id": "1",
                    "comment": "modify-me",
                    "name": "test.example.com",
                    "address": "10.0.10.1",
                },
                {
                    ".id": "3",
                    "comment": None,
                    "name": "test3.example.com",
                    "address": "10.0.10.3",
                },
                {
                    ".id": "4",
                    "comment": "keep-me",
                    "name": "test3.example.com",
                    "address": "10.0.10.3",
                },
                {
                    ".id": "5",
                    "comment": "keep-me",
                    "name": "test.example.com",
                    "address": "10.0.10.1",
                },
            ],
            "exclude_comment_regex": "^keep-.*",
        }
    )
    expected_add = [
        {
            "comment": "modify-me",
            "name": "test2.example.com",
            "address": "10.0.10.2",
        },
    ]
    expected_update = [
        {
            "comment": "modify-me",
            ".id": "1",
            "name": "test.example.com",
            "address": "10.0.10.11",
        },
    ]
    expected_remove = [
        {
            ".id": "3",
            "comment": None,
            "name": "test3.example.com",
            "address": "10.0.10.3",
        },
    ]

    with pytest.raises(SystemExit):
        mt_get_dns_entries.main()
    out, err = capfd.readouterr()
    out = json.loads(out)
    assert not err
    assert not out.get("failed", False)
    validate_output(out, expected_add, expected_update, expected_remove)


def test_add_name_regexp(capfd):
    set_module_args(
        {
            "data": [
                {
                    "name": "test.example.com",
                    "address": "10.0.10.1",
                },
                {
                    "regexp": ".*\\.test\\.example\\.com",
                    "address": "10.0.10.1",
                },
            ],
            "existing": [],
        }
    )
    expected_add = [
        {
            "name": "test.example.com",
            "address": "10.0.10.1",
        },
        {
            "regexp": ".*\\.test\\.example\\.com",
            "address": "10.0.10.1",
        },
    ]
    expected_update = []
    expected_remove = []

    with pytest.raises(SystemExit):
        mt_get_dns_entries.main()
    out, err = capfd.readouterr()
    out = json.loads(out)
    assert not err
    assert not out.get("failed", False)
    validate_output(out, expected_add, expected_update, expected_remove)


def test_edit_name_keep_regexp(capfd):
    set_module_args(
        {
            "data": [
                {
                    "name": "test.example.com",
                    "address": "10.0.10.11",
                },
                {
                    "regexp": ".*\\.test\\.example\\.com",
                    "address": "10.0.10.1",
                },
            ],
            "existing": [
                {
                    ".id": "1",
                    "comment": None,
                    "name": "test.example.com",
                    "address": "10.0.10.1",
                },
                {
                    ".id": "2",
                    "comment": None,
                    "regexp": ".*\\.test\\.example\\.com",
                    "address": "10.0.10.1",
                },
            ],
        }
    )
    expected_add = []
    expected_update = [
        {
            ".id": "1",
            "name": "test.example.com",
            "address": "10.0.10.11",
        },
    ]
    expected_remove = []

    with pytest.raises(SystemExit):
        mt_get_dns_entries.main()
    out, err = capfd.readouterr()
    out = json.loads(out)
    assert not err
    assert not out.get("failed", False)
    validate_output(out, expected_add, expected_update, expected_remove)


def test_edit_regexp_keep_name(capfd):
    set_module_args(
        {
            "data": [
                {
                    "name": "test.example.com",
                    "address": "10.0.10.1",
                },
                {
                    "regexp": ".*\\.test\\.example\\.com",
                    "address": "10.0.10.11",
                },
            ],
            "existing": [
                {
                    ".id": "1",
                    "comment": None,
                    "name": "test.example.com",
                    "address": "10.0.10.1",
                },
                {
                    ".id": "2",
                    "comment": None,
                    "regexp": ".*\\.test\\.example\\.com",
                    "address": "10.0.10.1",
                },
            ],
        }
    )
    expected_add = []
    expected_update = [
        {
            ".id": "2",
            "regexp": ".*\\.test\\.example\\.com",
            "address": "10.0.10.11",
        },
    ]
    expected_remove = []

    with pytest.raises(SystemExit):
        mt_get_dns_entries.main()
    out, err = capfd.readouterr()
    out = json.loads(out)
    assert not err
    assert not out.get("failed", False)
    validate_output(out, expected_add, expected_update, expected_remove)


def test_add_dualstack(capfd):
    set_module_args(
        {
            "data": [
                {
                    "name": "test.example.com",
                    "address": "10.0.10.1",
                },
                {
                    "name": "test.example.com",
                    "address": "2001:db8::10:1",
                    "type": "AAAA",
                },
            ],
            "existing": [],
        }
    )
    expected_add = [
        {
            "name": "test.example.com",
            "address": "10.0.10.1",
        },
        {
            "name": "test.example.com",
            "address": "2001:db8::10:1",
            "type": "AAAA",
        },
    ]
    expected_update = []
    expected_remove = []

    with pytest.raises(SystemExit):
        mt_get_dns_entries.main()
    out, err = capfd.readouterr()
    out = json.loads(out)
    assert not err
    assert not out.get("failed", False)
    validate_output(out, expected_add, expected_update, expected_remove)


def test_edit_dualstack_a(capfd):
    set_module_args(
        {
            "data": [
                {
                    "name": "test.example.com",
                    "address": "10.0.10.11",
                },
                {
                    "name": "test.example.com",
                    "address": "2001:db8::10:1",
                    "type": "AAAA",
                },
            ],
            "existing": [
                {
                    ".id": "1",
                    "comment": None,
                    "name": "test.example.com",
                    "address": "10.0.10.1",
                },
                {
                    ".id": "2",
                    "comment": None,
                    "name": "test.example.com",
                    "address": "2001:db8::10:1",
                    "type": "AAAA",
                },
            ],
        }
    )
    expected_add = []
    expected_update = [
        {
            ".id": "1",
            "name": "test.example.com",
            "address": "10.0.10.11",
        },
    ]
    expected_remove = []

    with pytest.raises(SystemExit):
        mt_get_dns_entries.main()
    out, err = capfd.readouterr()
    out = json.loads(out)
    assert not err
    assert not out.get("failed", False)
    validate_output(out, expected_add, expected_update, expected_remove)


def test_edit_dualstack_aaaa(capfd):
    set_module_args(
        {
            "data": [
                {
                    "name": "test.example.com",
                    "address": "10.0.10.1",
                },
                {
                    "name": "test.example.com",
                    "address": "2001:db8::10:11",
                    "type": "AAAA",
                },
            ],
            "existing": [
                {
                    ".id": "1",
                    "comment": None,
                    "name": "test.example.com",
                    "address": "10.0.10.1",
                },
                {
                    ".id": "2",
                    "comment": None,
                    "name": "test.example.com",
                    "address": "2001:db8::10:1",
                    "type": "AAAA",
                },
            ],
        }
    )
    expected_add = []
    expected_update = [
        {
            ".id": "2",
            "name": "test.example.com",
            "address": "2001:db8::10:11",
            "type": "AAAA",
        },
    ]
    expected_remove = []

    with pytest.raises(SystemExit):
        mt_get_dns_entries.main()
    out, err = capfd.readouterr()
    out = json.loads(out)
    assert not err
    assert not out.get("failed", False)
    validate_output(out, expected_add, expected_update, expected_remove)


def test_remove_dualstack_a(capfd):
    set_module_args(
        {
            "data": [
                {
                    "name": "test.example.com",
                    "address": "2001:db8::10:1",
                    "type": "AAAA",
                },
            ],
            "existing": [
                {
                    ".id": "1",
                    "comment": None,
                    "name": "test.example.com",
                    "address": "10.0.10.1",
                },
                {
                    ".id": "2",
                    "comment": None,
                    "name": "test.example.com",
                    "address": "2001:db8::10:1",
                    "type": "AAAA",
                },
            ],
        }
    )
    expected_add = []
    expected_update = []
    expected_remove = [
        {
            ".id": "1",
            "comment": None,
            "name": "test.example.com",
            "address": "10.0.10.1",
        },
    ]

    with pytest.raises(SystemExit):
        mt_get_dns_entries.main()
    out, err = capfd.readouterr()
    out = json.loads(out)
    assert not err
    assert not out.get("failed", False)
    validate_output(out, expected_add, expected_update, expected_remove)


def test_remove_dualstack_aaaa(capfd):
    set_module_args(
        {
            "data": [
                {
                    "name": "test.example.com",
                    "address": "10.0.10.1",
                },
            ],
            "existing": [
                {
                    ".id": "1",
                    "comment": None,
                    "name": "test.example.com",
                    "address": "10.0.10.1",
                },
                {
                    ".id": "2",
                    "comment": None,
                    "name": "test.example.com",
                    "address": "2001:db8::10:1",
                    "type": "AAAA",
                },
            ],
        }
    )
    expected_add = []
    expected_update = []
    expected_remove = [
        {
            ".id": "2",
            "comment": None,
            "name": "test.example.com",
            "address": "2001:db8::10:1",
            "type": "AAAA",
        },
    ]

    with pytest.raises(SystemExit):
        mt_get_dns_entries.main()
    out, err = capfd.readouterr()
    out = json.loads(out)
    assert not err
    assert not out.get("failed", False)
    validate_output(out, expected_add, expected_update, expected_remove)


def test_dualstack_multiple(capfd):
    set_module_args(
        {
            "data": [
                {
                    "name": "test.example.com",
                    "address": "10.0.10.11",
                },
                {
                    "name": "test2.example.com",
                    "address": "10.0.10.2",
                },
                {
                    "name": "test.example.com",
                    "address": "2001:db8::10:11",
                    "type": "AAAA",
                },
                {
                    "name": "test2.example.com",
                    "address": "2001:db8::10:2",
                    "type": "AAAA",
                },
                {
                    "name": "test3.example.com",
                    "address": "2001:db8::10:3",
                    "type": "AAAA",
                },
            ],
            "existing": [
                {
                    ".id": "1",
                    "comment": None,
                    "name": "test.example.com",
                    "address": "10.0.10.1",
                },
                {
                    ".id": "2",
                    "comment": None,
                    "name": "test3.example.com",
                    "address": "10.0.10.3",
                },
                {
                    ".id": "3",
                    "comment": None,
                    "name": "test.example.com",
                    "address": "2001:db8::10:1",
                    "type": "AAAA",
                },
                {
                    ".id": "5",
                    "comment": None,
                    "name": "test3.example.com",
                    "address": "2001:db8::10:3",
                    "type": "AAAA",
                },
                {
                    ".id": "6",
                    "comment": None,
                    "name": "test4.example.com",
                    "address": "2001:db8::10:4",
                    "type": "AAAA",
                },
            ],
        }
    )
    expected_add = [
        {
            "name": "test2.example.com",
            "address": "10.0.10.2",
        },
        {
            "name": "test2.example.com",
            "address": "2001:db8::10:2",
            "type": "AAAA",
        },
    ]
    expected_update = [
        {
            ".id": "1",
            "name": "test.example.com",
            "address": "10.0.10.11",
        },
        {
            ".id": "3",
            "name": "test.example.com",
            "address": "2001:db8::10:11",
            "type": "AAAA",
        },
    ]
    expected_remove = [
        {
            ".id": "2",
            "comment": None,
            "name": "test3.example.com",
            "address": "10.0.10.3",
        },
        {
            ".id": "6",
            "comment": None,
            "name": "test4.example.com",
            "address": "2001:db8::10:4",
            "type": "AAAA",
        },
    ]

    with pytest.raises(SystemExit):
        mt_get_dns_entries.main()
    out, err = capfd.readouterr()
    out = json.loads(out)
    assert not err
    assert not out.get("failed", False)
    validate_output(out, expected_add, expected_update, expected_remove)
