from __future__ import absolute_import, division, print_function

__metaclass__ = type


def find_duplicates(_input):
    duplicates = []
    checked = []
    for d in _input:
        if d in checked:
            duplicates.append(d)
        else:
            checked.append(d)

    return duplicates


class FilterModule(object):
    def filters(self):
        return {'find_duplicates': find_duplicates}
