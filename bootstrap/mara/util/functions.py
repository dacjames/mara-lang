'''Simple Utility Functions'''

from collections import defaultdict

_unique_ids = defaultdict(lambda: 0)


def unique_id(prefix=None):
    '''Return a unique identifier, optionally prefixed with a string.'''
    if prefix is None:
        prefix = ''

    new_id = prefix + '_' + str(_unique_ids[prefix])
    _unique_ids[prefix] += 1
    return new_id


def anonymous_name(kind):
    '''Return a unique name for a entity of the given type.'''
    new_name = '_anon_{id}'.format(id=unique_id(kind))
    return new_name
