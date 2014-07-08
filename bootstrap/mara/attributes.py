'''
Attributes represent a nested dictionary of node attributes.

By default, attributes can only be set once and will throw a NodeAttributeError
if inadvertantly set twice.  Attributes can be overriden either "soft",
where the new value must be equal to the old, or "hard", which alway sets the attribute.
Hard overrides should be avoided except for testing or depreciation purposes.
'''

from util.reflection import deriving


class Attributes(deriving('show', 'eq')):
    def __init__(self):
        self.members = {}

    def __getitem__(self, key):
        return self.members.__getitem__(key)

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

    def __setitem__(self, key, value):
        try:
            self.members.__getitem__(key)

        except KeyError:
            self.members.__setitem__(key, value)
            return

        raise KeyError(key)

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
