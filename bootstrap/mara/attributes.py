'''
Attributes represent a nested dictionary of node attributes.

By default, attributes can only be set once and will throw a NodeAttributeError
if inadvertantly set twice.  Attributes can be overriden either "soft",
where the new value must be equal to the old, or "hard", which alway sets the attribute.
Hard overrides should be avoided except for testing or depreciation purposes.
'''

import collections
from util.reflection import deriving


class Attributes(object):
    def __init__(self, members=None):
        self.members = {}

        try:
            for key, value in members.iteritems():
                self[key] = value

        except AttributeError:
            pass

    def __delitem__(self, key):
        return self.members.__delitem__(key)

    def __contains__(self, key):
        return self.has_key(key)  # noqa

    def keys(self):
        return self.members.keys()

    def values(self):
        return self.members.values()

    def items(self):
        return self.members.items()

    def has_key(self, key):
        # pylint: disable=E1101
        return self.members.has_key(key)  # noqa

    def clear(self):
        return self.members.clear()

    def iterkeys(self):
        # pylint: disable=E1101
        return self.members.iterkeys()

    def itervalues(self):
        # pylint: disable=E1101
        return self.members.itervalues()

    def iteritems(self):
        # pylint: disable=E1101
        return self.members.iteritems()

    def copy(self):
        return self.members.copy()

    def get(self, key, default=None):
        return self.members.get(key, default)

    ##########################################################################

    def __eq__(self, other):
        try:
            return sorted(self.iteritems()) == sorted(other.iteritems())
        except AttributeError:
            return False

    def __repr__(self):
        items = sorted(self.members.items())
        field_str = ', '.join([
            '{k}: {v}'.format(k=key, v=value)
            for key, value in items
        ])

        return "Attributes({{{f}}})".format(f=field_str)

    def __str__(self):
        return self.__repr__()

    def __setitem__(self, key, value):
        try:
            self.members.__getitem__(key)

        except KeyError:

            if self._ispath(key):
                self._setpath(key, value)
                return

            if isinstance(value, collections.Mapping):
                value = Attributes(value)

            self.members.__setitem__(key, value)
            return

        raise KeyError(key)

    def __getitem__(self, key):
        if self._ispath(key):
            return self._getpath(key)
        else:
            return self.members.__getitem__(key)

    def get(self, key, default):
        try:
            return self.__getitem__(key)
        except AttributeError:
            return default

    def set_soft(self, key, value):
        '''
        Set and possibly override an attribute.
        Only overrides if the new value is equal to the old value,
        raises a KeyError otherwise.
        '''
        valid = True

        try:
            old_value = self.members.__getitem__(key)
            if old_value != value:
                valid = False

        except KeyError:
            self.members.__setitem__(key, value)

        if not valid:
            raise KeyError

    def set_hard(self, key, value):
        '''
        Set and always override an attribute
        '''
        self.members.__setitem__(key, value)

    def _ispath(self, value):
        ispath = '/' in value
        return ispath

    def _setpath(self, key, value):
        steps = list(reversed(key.split('/')))

        step = steps.pop()
        while len(steps) > 0:
            try:
                current = self[step]
            except KeyError:
                current = Attributes()
                self[step] = current

            step = steps.pop()

        current[step] = value

    def _getpath(self, key):

        steps = key.split('/')

        current = self
        for step in steps:
            current = current[step]

        return current
